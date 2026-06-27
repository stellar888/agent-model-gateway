"""Tests for provider-neutral domain contracts."""

import pytest
from pydantic import ValidationError

from app.domain import (
    AgentDefinition,
    ContentBlock,
    Message,
    MessageRole,
    ModelCapabilities,
    ModelDescriptor,
    ModelProfile,
    ModelProfileRequirements,
    ModelRequest,
    ModelResponse,
    ModelRoute,
    TokenUsage,
    ToolCall,
)


def test_model_request_serializes_provider_neutral_contract() -> None:
    """A model request can be serialized without provider-specific types."""
    request = ModelRequest(
        model_profile="coding_high",
        messages=[Message.from_text(MessageRole.USER, "Review this change")],
        output_schema={"type": "object"},
    )

    dumped = request.model_dump(mode="json")

    assert dumped["model_profile"] == "coding_high"
    assert dumped["messages"][0]["role"] == "user"
    assert dumped["messages"][0]["content"][0]["text"] == "Review this change"
    assert "openai" not in str(dumped).lower()


def test_model_response_contains_normalized_tool_calls_and_usage() -> None:
    """A normalized response preserves content, tool calls, usage, and metadata."""
    response = ModelResponse(
        content=[ContentBlock.json_block({"summary": "ok"})],
        tool_calls=[ToolCall(id="call-1", name="lookup", arguments={"id": "123"})],
        usage=TokenUsage(prompt_tokens=2, completion_tokens=3, total_tokens=5),
        stop_reason="stop",
        provider_metadata={"provider": "fake"},
    )

    assert response.tool_calls[0].arguments == {"id": "123"}
    assert response.provider_metadata == {"provider": "fake"}


def test_capability_values_are_validated() -> None:
    """Context windows and token usage reject invalid values."""
    with pytest.raises(ValidationError):
        ModelCapabilities(max_context_window=0)

    with pytest.raises(ValidationError):
        TokenUsage(prompt_tokens=2, completion_tokens=2, total_tokens=3)


def test_profile_requirements_match_model_capabilities() -> None:
    """Profile requirements can be checked against concrete model capabilities."""
    requirements = ModelProfileRequirements(
        tool_calling=True,
        structured_output=True,
        minimum_context_window=32_000,
        allowed_data_classifications=["public", "internal"],
    )
    descriptor = ModelDescriptor(
        provider="fake",
        model="fake-coding-model",
        capabilities=ModelCapabilities(
            tool_calling=True,
            structured_output=True,
            max_context_window=64_000,
        ),
        data_classifications=["internal"],
    )

    assert requirements.is_satisfied_by(
        descriptor.capabilities,
        descriptor.data_classifications,
        descriptor.cost_per_1k_tokens_usd,
    )


def test_profile_rejects_duplicate_routes() -> None:
    """Profiles keep routing order explicit and reject duplicate candidates."""
    with pytest.raises(ValidationError):
        ModelProfile(
            name="coding_high",
            requirements=ModelProfileRequirements(
                structured_output=True,
                minimum_context_window=32_000,
            ),
            routes=[
                ModelRoute(provider="fake", model="fake-coding-model"),
                ModelRoute(provider="fake", model="fake-coding-model"),
            ],
        )


def test_agent_definition_validates_nested_contract() -> None:
    """Agent definitions validate nested model profile and output settings."""
    agent = AgentDefinition.model_validate(
        {
            "api_version": "agents.example.io/v1",
            "kind": "Agent",
            "metadata": {
                "name": "pr-reviewer",
                "version": "0.1.0",
                "owner": "developer-platform",
                "description": "Reviews pull requests.",
            },
            "spec": {
                "model_profile": "coding_high",
                "instructions": {"system_file": "prompt.md"},
                "capabilities": {
                    "required": {
                        "tool_calling": False,
                        "structured_output": True,
                        "minimum_context_window": 32_000,
                    }
                },
                "tools": [],
                "output": {"schema_file": "output.schema.json"},
                "policies": {
                    "max_iterations": 1,
                    "max_cost_usd": 1.0,
                    "writes_allowed": False,
                },
                "customization": {
                    "append_instructions": "allowed",
                    "settings": {"severity_threshold": "allowed"},
                    "model_profile": "locked",
                    "tools_add": "locked",
                },
                "settings": {"severity_threshold": "low"},
            },
        }
    )

    assert agent.metadata.name == "pr-reviewer"
    assert agent.spec.model_profile == "coding_high"
