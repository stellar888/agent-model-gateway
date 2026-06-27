"""Tests for model gateway routing and provider normalization."""

from types import SimpleNamespace

import pytest

from app.domain import (
    Message,
    MessageRole,
    ModelCapabilities,
    ModelDescriptor,
    ModelProfile,
    ModelProfileRequirements,
    ModelRequest,
    ModelRoute,
    RequestConstraints,
)
from app.gateway.errors import NoEligibleModelError
from app.gateway.registry import ModelRegistry, ProfileRegistry, ProviderRegistry
from app.gateway.router import CapabilityRouter
from app.gateway.service import ModelGateway
from app.providers.fake_provider import FakeProvider
from app.providers.openai_provider import OpenAIProvider


def _request(profile: str = "coding_high") -> ModelRequest:
    return ModelRequest(
        model_profile=profile,
        messages=[Message.from_text(MessageRole.USER, "Review payment idempotency")],
        output_schema={"type": "object"},
    )


def _router(
    profiles: list[ModelProfile],
    models: list[ModelDescriptor],
    providers: ProviderRegistry | None = None,
) -> CapabilityRouter:
    provider_registry = providers or ProviderRegistry(
        {"fake": FakeProvider(), "openai": FakeProvider()}
    )
    return CapabilityRouter(ProfileRegistry(profiles), ModelRegistry(models), provider_registry)


def test_router_selects_first_eligible_route_after_rejections() -> None:
    """Routing order is stable and records ineligible candidates."""
    profile = ModelProfile(
        name="coding_high",
        requirements=ModelProfileRequirements(
            structured_output=True,
            minimum_context_window=32_000,
        ),
        routes=[
            ModelRoute(provider="fake", model="small"),
            ModelRoute(provider="fake", model="large"),
        ],
    )
    router = _router(
        [profile],
        [
            ModelDescriptor(
                provider="fake",
                model="small",
                capabilities=ModelCapabilities(
                    structured_output=True,
                    max_context_window=8_000,
                ),
            ),
            ModelDescriptor(
                provider="fake",
                model="large",
                capabilities=ModelCapabilities(
                    structured_output=True,
                    max_context_window=64_000,
                ),
            ),
        ],
    )

    selection = router.resolve(_request())

    assert selection.descriptor.model == "large"
    assert selection.decision.rejected_candidates[0].model == "small"
    assert "context window" in selection.decision.rejected_candidates[0].reason


def test_router_applies_request_constraints() -> None:
    """Per-request constraints can reject an otherwise eligible model."""
    profile = ModelProfile(
        name="coding_high",
        requirements=ModelProfileRequirements(
            structured_output=True,
            minimum_context_window=8_000,
        ),
        routes=[ModelRoute(provider="fake", model="public-only")],
    )
    router = _router(
        [profile],
        [
            ModelDescriptor(
                provider="fake",
                model="public-only",
                capabilities=ModelCapabilities(
                    structured_output=True,
                    max_context_window=64_000,
                ),
                data_classifications=["public"],
            )
        ],
    )
    request = _request()
    request.constraints = RequestConstraints(data_classification="internal")

    with pytest.raises(NoEligibleModelError) as exc_info:
        router.resolve(request)

    assert "data classification" in exc_info.value.rejected_candidates[0]["reason"]


def test_router_raises_when_no_candidate_is_eligible() -> None:
    """A typed error includes structured rejection metadata."""
    profile = ModelProfile(
        name="coding_high",
        requirements=ModelProfileRequirements(
            tool_calling=True,
            structured_output=True,
            minimum_context_window=32_000,
        ),
        routes=[ModelRoute(provider="fake", model="basic")],
    )
    router = _router(
        [profile],
        [
            ModelDescriptor(
                provider="fake",
                model="basic",
                capabilities=ModelCapabilities(
                    tool_calling=False,
                    structured_output=True,
                    max_context_window=64_000,
                ),
            )
        ],
    )

    with pytest.raises(NoEligibleModelError) as exc_info:
        router.resolve(_request())

    assert exc_info.value.profile == "coding_high"
    assert exc_info.value.rejected_candidates[0]["model"] == "basic"


@pytest.mark.asyncio
async def test_gateway_returns_fake_provider_normalized_response() -> None:
    """The gateway returns the fake provider's normalized response and routing metadata."""
    profile = ModelProfile(
        name="coding_high",
        requirements=ModelProfileRequirements(
            structured_output=True,
            minimum_context_window=8_000,
        ),
        routes=[ModelRoute(provider="fake", model="fake-coding-model")],
    )
    models = [
        ModelDescriptor(
            provider="fake",
            model="fake-coding-model",
            capabilities=ModelCapabilities(
                structured_output=True,
                max_context_window=64_000,
            ),
        )
    ]
    providers = ProviderRegistry({"fake": FakeProvider()})
    gateway = ModelGateway(_router([profile], models, providers), providers)

    result = await gateway.generate(_request())

    assert result.routing.selected_provider == "fake"
    assert result.response.provider_metadata["deterministic"] is True
    assert result.response.content[0].data["risk_level"] == "medium"  # type: ignore[index]


@pytest.mark.asyncio
async def test_openai_provider_normalizes_mocked_response() -> None:
    """The OpenAI adapter maps SDK-shaped data into internal contracts using mocks only."""

    class Responses:
        async def create(self, **_: object) -> object:
            return SimpleNamespace(
                output_parsed={"summary": "ok"},
                output_text=None,
                output=[],
                usage=SimpleNamespace(input_tokens=10, output_tokens=4, total_tokens=14),
                status="completed",
            )

    client = SimpleNamespace(responses=Responses())
    provider = OpenAIProvider(client=client)

    response = await provider.generate("gpt-test", _request())

    assert response.content[0].data == {"summary": "ok"}
    assert response.usage.total_tokens == 14
    assert response.provider_metadata == {"provider": "openai", "model": "gpt-test"}
