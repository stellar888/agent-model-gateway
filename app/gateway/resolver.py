"""Resolver-only model gateway service."""

from time import perf_counter
from uuid import uuid4

from app.domain.messages import Message, MessageRole
from app.domain.models import ModelRequest
from app.domain.resolution import (
    PolicyDecision,
    ResolveModelRequest,
    ResolveModelResult,
    SelectedModel,
)
from app.gateway.errors import NoEligibleModelError
from app.gateway.events import GatewayEvent, JsonlEventSink, default_event_sink
from app.gateway.router import CapabilityRouter


class ModelResolver:
    """Resolve logical model profiles without executing provider calls."""

    def __init__(
        self,
        router: CapabilityRouter,
        event_sink: JsonlEventSink | None = None,
    ) -> None:
        """Create a resolver with a router and optional event sink."""
        self._router = router
        self._event_sink = event_sink or default_event_sink()

    def resolve(self, request: ResolveModelRequest) -> ResolveModelResult:
        """Resolve a model profile and emit a structured decision event."""
        decision_id = f"route_{uuid4().hex}"
        started = perf_counter()
        model_request = ModelRequest(
            model_profile=request.model_profile,
            messages=[Message.from_text(MessageRole.USER, "resolve model profile")],
            constraints=request.constraints,
        )

        try:
            selection = self._router.resolve(model_request)
        except NoEligibleModelError as exc:
            self._event_sink.emit(
                GatewayEvent(
                    event_type="model_resolution_failed",
                    decision_id=decision_id,
                    identity=request.identity,
                    model_profile=request.model_profile,
                    status="rejected",
                    reason=str(exc),
                    latency_ms=_elapsed_ms(started),
                    metadata={"rejected_candidates": exc.rejected_candidates},
                )
            )
            raise

        result = ResolveModelResult(
            decision_id=decision_id,
            selected=SelectedModel(
                provider=selection.descriptor.provider,
                model=selection.descriptor.model,
            ),
            routing=selection.decision.model_dump(mode="json"),
            policy=PolicyDecision(
                allowed=True,
                budget_scope=f"department:{request.identity.department_id}",
            ),
            identity=request.identity,
        )
        self._event_sink.emit(
            GatewayEvent(
                event_type="model_resolved",
                decision_id=decision_id,
                identity=request.identity,
                model_profile=request.model_profile,
                selected_provider=result.selected.provider,
                selected_model=result.selected.model,
                status="allowed",
                latency_ms=_elapsed_ms(started),
                metadata={
                    "budget_scope": result.policy.budget_scope,
                    "rejected_candidates": result.routing.get("rejected_candidates", []),
                },
            )
        )
        return result


def _elapsed_ms(started: float) -> int:
    """Return elapsed milliseconds since a monotonic timestamp."""
    return int((perf_counter() - started) * 1000)
