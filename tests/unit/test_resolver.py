"""Tests for resolver-only gateway behavior."""

from pathlib import Path

from app.domain import (
    IdentityContext,
    ModelCapabilities,
    ModelDescriptor,
    ModelProfile,
    ModelProfileRequirements,
    ModelRoute,
    ResolveModelRequest,
)
from app.gateway.events import JsonlEventSink
from app.gateway.registry import ModelRegistry, ProfileRegistry, ProviderRegistry
from app.gateway.resolver import ModelResolver
from app.gateway.router import CapabilityRouter
from app.providers.fake_provider import FakeProvider


def test_resolver_returns_selected_model_and_emits_event(tmp_path: Path) -> None:
    """The resolver selects a model without calling a provider."""
    event_sink = JsonlEventSink(tmp_path / "events.jsonl")
    resolver = ModelResolver(_router(), event_sink)
    request = ResolveModelRequest(
        model_profile="coding_high",
        identity=_identity(),
    )

    result = resolver.resolve(request)

    assert result.selected.provider == "fake"
    assert result.selected.model == "fake-coding-model"
    assert result.policy.budget_scope == "department:payments"
    assert event_sink.recent()[0].event_type == "model_resolved"


def _router() -> CapabilityRouter:
    profile = ModelProfile(
        name="coding_high",
        requirements=ModelProfileRequirements(
            structured_output=True,
            minimum_context_window=32_000,
        ),
        routes=[ModelRoute(provider="fake", model="fake-coding-model")],
    )
    model = ModelDescriptor(
        provider="fake",
        model="fake-coding-model",
        capabilities=ModelCapabilities(
            structured_output=True,
            max_context_window=64_000,
        ),
    )
    providers = ProviderRegistry({"fake": FakeProvider()})
    return CapabilityRouter(ProfileRegistry([profile]), ModelRegistry([model]), providers)


def _identity() -> IdentityContext:
    return IdentityContext(
        tenant_id="acme",
        department_id="payments",
        team_id="checkout-platform",
        user_id="user_123",
        agent_id="pr-reviewer",
        agent_version="0.1.0",
        agent_instance_id="repo:payments-api:pr-reviewer",
        agent_run_id="run_test",
        environment="test",
    )
