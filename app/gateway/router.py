"""Deterministic capability-based model router."""

from pydantic import BaseModel, ConfigDict, Field

from app.domain.capabilities import ModelCapabilities
from app.domain.models import ModelDescriptor, ModelRequest
from app.gateway.errors import ModelNotFoundError, NoEligibleModelError, ProviderNotFoundError
from app.gateway.registry import ModelRegistry, ProfileRegistry, ProviderRegistry


class RejectedCandidate(BaseModel):
    """A rejected route and the reason it was not selected."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str
    reason: str


class RoutingDecision(BaseModel):
    """Structured routing decision emitted by the router."""

    model_config = ConfigDict(extra="forbid")

    profile: str
    selected_provider: str
    selected_model: str
    rejected_candidates: list[RejectedCandidate] = Field(default_factory=list)
    requirements: dict[str, object] = Field(default_factory=dict)


class RouteSelection(BaseModel):
    """A selected model descriptor and its routing metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    descriptor: ModelDescriptor
    decision: RoutingDecision


class CapabilityRouter:
    """Resolve logical profiles to the first eligible concrete model."""

    def __init__(
        self,
        profiles: ProfileRegistry,
        models: ModelRegistry,
        providers: ProviderRegistry,
    ) -> None:
        """Create a router from profile, model, and provider registries."""
        self._profiles = profiles
        self._models = models
        self._providers = providers

    def resolve(self, request: ModelRequest) -> RouteSelection:
        """Resolve the requested model profile to an eligible route."""
        profile = self._profiles.get(request.model_profile)
        rejected: list[RejectedCandidate] = []

        for route in profile.routes:
            try:
                descriptor = self._models.get(route.provider, route.model)
                self._providers.get(route.provider)
            except (ModelNotFoundError, ProviderNotFoundError) as exc:
                rejected.append(
                    RejectedCandidate(
                        provider=route.provider,
                        model=route.model,
                        reason=str(exc),
                    )
                )
                continue

            reason = self._rejection_reason(descriptor, request)
            if reason is not None:
                rejected.append(
                    RejectedCandidate(provider=route.provider, model=route.model, reason=reason)
                )
                continue

            return RouteSelection(
                descriptor=descriptor,
                decision=RoutingDecision(
                    profile=profile.name,
                    selected_provider=route.provider,
                    selected_model=route.model,
                    rejected_candidates=rejected,
                    requirements=profile.requirements.model_dump(mode="json"),
                ),
            )

        rejected_dump = [candidate.model_dump(mode="json") for candidate in rejected]
        raise NoEligibleModelError(profile.name, rejected_dump)

    def _rejection_reason(self, descriptor: ModelDescriptor, request: ModelRequest) -> str | None:
        profile = self._profiles.get(request.model_profile)
        requirements = profile.requirements
        capabilities = descriptor.capabilities

        if requirements.tool_calling and not capabilities.tool_calling:
            return "model does not support required tool calling"
        if requirements.structured_output and not capabilities.structured_output:
            return "model does not support required structured output"
        if capabilities.max_context_window < requirements.minimum_context_window:
            return "model context window is below profile minimum"
        if not set(descriptor.data_classifications).intersection(
            requirements.allowed_data_classifications
        ):
            return "model is not allowed for profile data classifications"
        if (
            requirements.max_cost_usd is not None
            and descriptor.cost_per_1k_tokens_usd is not None
            and descriptor.cost_per_1k_tokens_usd > requirements.max_cost_usd
        ):
            return "model cost exceeds profile maximum"

        constraints = request.constraints
        if constraints is None:
            return None
        if (
            constraints.minimum_context_window is not None
            and capabilities.max_context_window < constraints.minimum_context_window
        ):
            return "model context window is below request minimum"
        if (
            constraints.data_classification is not None
            and constraints.data_classification not in descriptor.data_classifications
        ):
            return "model is not allowed for request data classification"
        if (
            constraints.max_cost_usd is not None
            and descriptor.cost_per_1k_tokens_usd is not None
            and descriptor.cost_per_1k_tokens_usd > constraints.max_cost_usd
        ):
            return "model cost exceeds request maximum"
        if constraints.required_capabilities is not None:
            return _capability_rejection_reason(capabilities, constraints.required_capabilities)
        return None


def _capability_rejection_reason(
    available: ModelCapabilities, required: ModelCapabilities
) -> str | None:
    """Return a rejection reason when request capabilities are not satisfied."""
    if required.tool_calling and not available.tool_calling:
        return "model does not support request tool calling"
    if required.structured_output and not available.structured_output:
        return "model does not support request structured output"
    if required.streaming and not available.streaming:
        return "model does not support request streaming"
    if available.max_context_window < required.max_context_window:
        return "model context window is below request capability minimum"
    return None
