"""Provider-neutral normalized model response domain models."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.messages import ContentBlock


class ToolCall(BaseModel):
    """A normalized tool call requested by a model."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    arguments: dict[str, object] = Field(default_factory=dict)


class TokenUsage(BaseModel):
    """Normalized token usage for one model interaction."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_total_tokens(self) -> "TokenUsage":
        """Ensure total usage includes prompt and completion usage."""
        minimum_total = self.prompt_tokens + self.completion_tokens
        if self.total_tokens < minimum_total:
            raise ValueError("total_tokens must be at least prompt_tokens + completion_tokens")
        return self


class ModelResponse(BaseModel):
    """A normalized provider response returned by the model gateway."""

    model_config = ConfigDict(extra="forbid")

    content: list[ContentBlock] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    usage: TokenUsage
    stop_reason: str = Field(min_length=1)
    provider_metadata: dict[str, object] = Field(default_factory=dict)
