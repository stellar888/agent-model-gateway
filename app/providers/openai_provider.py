"""OpenAI provider adapter.

OpenAI SDK types are intentionally isolated inside this module.
"""

from typing import Any

from app.domain.messages import ContentBlock, ContentBlockType, Message
from app.domain.models import ModelRequest
from app.domain.responses import ModelResponse, TokenUsage, ToolCall


class OpenAIProvider:
    """Provider adapter that normalizes OpenAI responses."""

    def __init__(self, client: Any | None = None, api_key: str | None = None) -> None:
        """Create an adapter with dependency-injected or lazily constructed client."""
        if client is not None:
            self._client = client
            return

        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key)

    async def generate(self, model: str, request: ModelRequest) -> ModelResponse:
        """Call OpenAI and translate the response into the normalized contract."""
        instructions = "\n\n".join(
            block.text or ""
            for message in request.messages
            if message.role.value == "system"
            for block in message.content
            if block.text
        )
        input_items = [
            _message_to_openai(message)
            for message in request.messages
            if message.role.value != "system"
        ]
        payload: dict[str, object] = {
            "model": model,
            "input": input_items,
        }
        tools = [tool.model_dump(mode="json") for tool in request.tools]
        text_format = _text_format(request.output_schema)
        if tools:
            payload["tools"] = tools
        if text_format is not None:
            payload["text"] = text_format
        if instructions:
            payload["instructions"] = instructions

        result = await self._client.responses.create(**payload)
        return self._normalize_response(model, result)

    def _normalize_response(self, model: str, result: Any) -> ModelResponse:
        content: list[ContentBlock] = []
        output_parsed = _read(result, "output_parsed")
        output_text = _read(result, "output_text")

        if isinstance(output_parsed, dict):
            content.append(ContentBlock.json_block(output_parsed))
        elif isinstance(output_text, str) and output_text:
            content.append(ContentBlock(type=ContentBlockType.TEXT, text=output_text))

        usage_raw = _read(result, "usage") or {}
        input_tokens = int(_read(usage_raw, "input_tokens") or 0)
        output_tokens = int(_read(usage_raw, "output_tokens") or 0)
        total_tokens = int(_read(usage_raw, "total_tokens") or input_tokens + output_tokens)

        tool_calls = _extract_tool_calls(_read(result, "output") or [])
        return ModelResponse(
            content=content,
            tool_calls=tool_calls,
            usage=TokenUsage(
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                total_tokens=total_tokens,
            ),
            stop_reason=str(_read(result, "status") or "stop"),
            provider_metadata={"provider": "openai", "model": model},
        )


def _message_to_openai(message: Message) -> dict[str, object]:
    """Convert an internal message to a minimal OpenAI input item."""
    text = "\n".join(block.text or "" for block in message.content if block.text)
    return {"role": message.role.value, "content": text}


def _text_format(output_schema: dict[str, object] | None) -> dict[str, object] | None:
    """Build a Responses API text format for JSON schema output."""
    if output_schema is None:
        return None
    return {
        "format": {
            "type": "json_schema",
            "name": "agent_output",
            "schema": output_schema,
            "strict": True,
        }
    }


def _read(value: Any, key: str) -> Any:
    """Read an attribute or mapping key from an SDK object without exposing its type."""
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)


def _extract_tool_calls(output: object) -> list[ToolCall]:
    """Extract normalized function tool calls from provider output items."""
    calls: list[ToolCall] = []
    if not isinstance(output, list):
        return calls

    for item in output:
        item_type = _read(item, "type")
        if item_type not in {"function_call", "tool_call"}:
            continue
        arguments = _read(item, "arguments") or {}
        if not isinstance(arguments, dict):
            arguments = {}
        calls.append(
            ToolCall(
                id=str(_read(item, "id") or _read(item, "call_id") or ""),
                name=str(_read(item, "name") or ""),
                arguments=arguments,
            )
        )
    return calls
