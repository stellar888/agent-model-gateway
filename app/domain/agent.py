"""Provider-neutral agent definition and run domain models."""

from pydantic import BaseModel, ConfigDict, Field

from app.domain.capabilities import ModelProfileRequirements
from app.domain.models import ToolDefinition
from app.domain.responses import ModelResponse, TokenUsage


class AgentMetadata(BaseModel):
    """Human-readable metadata for an agent definition."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    description: str


class AgentInstructions(BaseModel):
    """Instruction file references and overlay-appended text."""

    model_config = ConfigDict(extra="forbid")

    system_file: str
    append: list[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    """Structured output configuration for an agent."""

    model_config = ConfigDict(extra="forbid")

    schema_file: str


class AgentPolicies(BaseModel):
    """Execution policy limits for an agent run."""

    model_config = ConfigDict(extra="forbid")

    max_iterations: int = Field(default=1, ge=1)
    max_cost_usd: float = Field(default=1.0, ge=0)
    writes_allowed: bool = False


class CustomizationPolicy(BaseModel):
    """Limited customization switches enforced by the overlay resolver."""

    model_config = ConfigDict(extra="forbid")

    append_instructions: str = "locked"
    settings: dict[str, str] = Field(default_factory=dict)
    model_profile: str = "locked"
    tools_add: str = "locked"


class AgentSpec(BaseModel):
    """The executable part of an agent definition."""

    model_config = ConfigDict(extra="forbid")

    model_profile: str = Field(min_length=1)
    instructions: AgentInstructions
    capabilities: dict[str, ModelProfileRequirements]
    tools: list[ToolDefinition] = Field(default_factory=list)
    output: AgentOutput
    policies: AgentPolicies
    customization: CustomizationPolicy
    settings: dict[str, object] = Field(default_factory=dict)


class AgentDefinition(BaseModel):
    """A versioned provider-neutral agent definition."""

    model_config = ConfigDict(extra="forbid")

    api_version: str = Field(min_length=1)
    kind: str = "Agent"
    metadata: AgentMetadata
    spec: AgentSpec


class AgentRunRequest(BaseModel):
    """Request to run an agent with optional overlay and input payload."""

    model_config = ConfigDict(extra="forbid")

    agent_path: str
    input: dict[str, object]
    overlay_path: str | None = None


class AgentResolutionMetadata(BaseModel):
    """Metadata describing how an agent definition was resolved."""

    model_config = ConfigDict(extra="forbid")

    base_path: str
    overlay_path: str | None = None
    appended_instruction_count: int = 0
    settings_overrides: dict[str, object] = Field(default_factory=dict)


class AgentRunResult(BaseModel):
    """Result returned by the agent runtime after schema validation."""

    model_config = ConfigDict(extra="forbid")

    agent: AgentMetadata
    model_profile: str
    structured_output: dict[str, object]
    model_response: ModelResponse
    token_usage: TokenUsage
    routing_metadata: dict[str, object]
    resolution_metadata: AgentResolutionMetadata
