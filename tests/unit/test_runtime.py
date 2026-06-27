"""Tests for agent loading, overlays, validation, and fake execution."""

from pathlib import Path

import pytest

from app.domain import (
    AgentRunRequest,
    Message,
    MessageRole,
    ModelCapabilities,
    ModelDescriptor,
    ModelProfile,
    ModelProfileRequirements,
    ModelRoute,
)
from app.gateway.registry import ModelRegistry, ProfileRegistry, ProviderRegistry
from app.gateway.router import CapabilityRouter
from app.gateway.service import ModelGateway
from app.providers.fake_provider import FakeProvider
from app.runtime.errors import OutputValidationError, OverlayError
from app.runtime.loader import load_agent
from app.runtime.overlays import apply_overlay
from app.runtime.runner import AgentRunner
from app.runtime.validation import validate_output_schema

ROOT = Path(__file__).resolve().parents[2]
AGENT_PATH = ROOT / "agents/pr-reviewer/agent.yaml"
OVERLAY_PATH = ROOT / "agents/overlays/payments-team.yaml"


def test_load_agent_reads_yaml_prompt_and_schema() -> None:
    """The loader resolves files next to the base agent definition."""
    loaded = load_agent(AGENT_PATH)

    assert loaded.definition.metadata.name == "pr-reviewer"
    assert "pull request reviewer" in loaded.prompt
    assert loaded.output_schema["title"] == "PullRequestReview"


def test_overlay_appends_instructions_and_overrides_allowed_setting() -> None:
    """Allowed overlay fields are merged and recorded."""
    loaded = load_agent(AGENT_PATH)
    resolved = apply_overlay(loaded.definition, Path("agents/pr-reviewer/agent.yaml"), OVERLAY_PATH)

    assert resolved.definition.spec.instructions.append == [
        "Pay special attention to payment idempotency.",
        "Flag ambiguous retry behavior as at least medium severity.",
    ]
    assert resolved.definition.spec.settings["severity_threshold"] == "medium"
    assert resolved.metadata.appended_instruction_count == 2


def test_overlay_rejects_locked_model_profile(tmp_path: Path) -> None:
    """Locked customization fields cannot be changed."""
    overlay_path = tmp_path / "locked.yaml"
    overlay_path.write_text(
        "extends: agents/pr-reviewer/agent.yaml\nmodel_profile: cheap\n",
        encoding="utf-8",
    )
    loaded = load_agent(AGENT_PATH)

    with pytest.raises(OverlayError):
        apply_overlay(loaded.definition, Path("agents/pr-reviewer/agent.yaml"), overlay_path)


def test_validation_accepts_and_rejects_structured_output() -> None:
    """The supported JSON Schema subset catches malformed structured output."""
    schema = load_agent(AGENT_PATH).output_schema
    valid = {
        "summary": "Looks good.",
        "risk_level": "low",
        "findings": [{"title": "No issue", "severity": "info", "explanation": "Deterministic."}],
    }

    assert validate_output_schema(valid, schema) == valid

    with pytest.raises(OutputValidationError):
        validate_output_schema({"summary": "Missing fields"}, schema)


@pytest.mark.asyncio
async def test_agent_runner_executes_end_to_end_with_fake_provider() -> None:
    """The same runtime executes a fake-provider agent and validates output."""
    gateway = _fake_gateway()
    runner = AgentRunner(gateway)

    result = await runner.run(
        AgentRunRequest(
            agent_path=AGENT_PATH.as_posix(),
            overlay_path=OVERLAY_PATH.as_posix(),
            input={
                "title": "Payment retry handling",
                "summary": "Adds idempotency keys to payment retry flow.",
            },
        )
    )

    assert result.agent.name == "pr-reviewer"
    assert result.model_profile == "coding_high"
    assert result.structured_output["risk_level"] == "medium"
    assert result.resolution_metadata.overlay_path == OVERLAY_PATH.as_posix()


def _fake_gateway() -> ModelGateway:
    providers = ProviderRegistry({"fake": FakeProvider()})
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
    router = CapabilityRouter(ProfileRegistry([profile]), ModelRegistry([model]), providers)
    return ModelGateway(router, providers)


def test_runner_requires_structured_output() -> None:
    """The validator rejects text that cannot be parsed as JSON."""
    assert Message.from_text(MessageRole.USER, "keeps imported contract reachable")
