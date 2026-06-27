"""Provider-neutral model request and descriptor domain models."""

from pydantic import BaseModel, ConfigDict, Field

from app.domain.capabilities import ModelCapabilities
from app.domain.messages import Message
from app.domain.responses import ToolCall


class ToolDefinition(BaseModel):
    """A provider-neutral tool definition that can be passed to a model."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str
    input_schema: dict[str, object] = Field(default_factory=dict)


class ModelDescriptor(BaseModel):
    """A concrete provider/model entry and its routing metadata."""

    model_config = ConfigDict(extra="forbid")

    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    capabilities: ModelCapabilities
    data_classifications: list[str] = Field(default_factory=lambda: ["public"])
    cost_per_1k_tokens_usd: float | None = Field(default=None, ge=0)


class RequestConstraints(BaseModel):
    """Per-request constraints that further restrict profile routing."""

    model_config = ConfigDict(extra="forbid")

    required_capabilities: ModelCapabilities | None = None
    minimum_context_window: int | None = Field(default=None, gt=0)
    data_classification: str | None = None
    max_cost_usd: float | None = Field(default=None, ge=0)


class ModelRequest(BaseModel):
    """A provider-neutral request for one model interaction."""

    model_config = ConfigDict(extra="forbid")

    model_profile: str = Field(min_length=1)
    messages: list[Message] = Field(min_length=1)
    tools: list[ToolDefinition] = Field(default_factory=list)
    tool_choice: str | None = None
    output_schema: dict[str, object] | None = None
    constraints: RequestConstraints | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class ModelRequestResult(BaseModel):
    """A normalized model result plus gateway routing metadata."""

    model_config = ConfigDict(extra="forbid")

    response_id: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
