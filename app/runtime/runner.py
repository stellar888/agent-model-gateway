"""Agent execution runtime."""

import json
from pathlib import Path

from app.domain.agent import AgentRunRequest, AgentRunResult
from app.domain.capabilities import ModelCapabilities, ModelProfileRequirements
from app.domain.messages import ContentBlockType, Message, MessageRole
from app.domain.models import ModelRequest, RequestConstraints
from app.gateway.service import ModelGateway
from app.runtime.errors import OutputValidationError
from app.runtime.loader import load_agent
from app.runtime.overlays import apply_overlay, resolve_without_overlay
from app.runtime.validation import validate_output_schema


class AgentRunner:
    """Run a loaded agent through the model gateway."""

    def __init__(self, gateway: ModelGateway) -> None:
        """Create a runner with an injected gateway service."""
        self._gateway = gateway

    async def run(self, request: AgentRunRequest) -> AgentRunResult:
        """Execute one agent run and validate its structured output."""
        agent_path = Path(request.agent_path)
        loaded = load_agent(agent_path)
        resolved = (
            apply_overlay(loaded.definition, agent_path, Path(request.overlay_path))
            if request.overlay_path
            else resolve_without_overlay(loaded.definition, agent_path)
        )
        definition = resolved.definition
        instructions = _render_instructions(loaded.prompt, definition.spec.instructions.append)
        model_request = ModelRequest(
            model_profile=definition.spec.model_profile,
            messages=[
                Message.from_text(MessageRole.SYSTEM, instructions),
                Message.from_text(MessageRole.USER, json.dumps(request.input, sort_keys=True)),
            ],
            tools=definition.spec.tools,
            output_schema=loaded.output_schema,
            constraints=_constraints_for_agent(definition.spec.capabilities["required"]),
            metadata={"agent": definition.metadata.name, "version": definition.metadata.version},
        )

        # Future tool loops belong here in the runtime, after inspecting normalized tool calls.
        gateway_result = await self._gateway.generate(model_request)
        structured_output = validate_output_schema(
            _extract_structured_output(gateway_result.response.content),
            loaded.output_schema,
        )

        return AgentRunResult(
            agent=definition.metadata,
            model_profile=definition.spec.model_profile,
            structured_output=structured_output,
            model_response=gateway_result.response,
            token_usage=gateway_result.response.usage,
            routing_metadata=gateway_result.routing.model_dump(mode="json"),
            resolution_metadata=resolved.metadata,
        )


def _render_instructions(prompt: str, appended: list[str]) -> str:
    """Render base and appended instructions deterministically."""
    if not appended:
        return prompt
    return (
        prompt
        + "\n\nAdditional instructions:\n"
        + "\n".join(f"- {instruction}" for instruction in appended)
    )


def _constraints_for_agent(required: ModelProfileRequirements) -> RequestConstraints:
    """Translate agent capability requirements into request constraints."""
    minimum_context_window = required.minimum_context_window
    return RequestConstraints(
        minimum_context_window=minimum_context_window,
        required_capabilities=ModelCapabilities(
            tool_calling=required.tool_calling,
            structured_output=required.structured_output,
            max_context_window=minimum_context_window,
        ),
    )


def _extract_structured_output(content: object) -> object:
    """Extract the first JSON object from normalized content blocks."""
    if not isinstance(content, list):
        raise OutputValidationError("model response content must be a list")
    for block in content:
        if block.type == ContentBlockType.JSON:
            return block.data
        if block.type == ContentBlockType.TEXT and block.text:
            try:
                return json.loads(block.text)
            except json.JSONDecodeError as exc:
                raise OutputValidationError("text response did not contain valid JSON") from exc
    raise OutputValidationError("model response did not include structured output")
