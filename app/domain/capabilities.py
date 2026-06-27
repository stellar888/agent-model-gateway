"""Provider-neutral model capability and profile domain models."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelCapabilities(BaseModel):
    """Capabilities exposed by a concrete model."""

    model_config = ConfigDict(extra="forbid")

    tool_calling: bool = False
    structured_output: bool = False
    streaming: bool = False
    max_context_window: int = Field(gt=0)
    input_modalities: list[str] = Field(default_factory=lambda: ["text"])
    output_modalities: list[str] = Field(default_factory=lambda: ["text"])


class ModelProfileRequirements(BaseModel):
    """Requirements that a model must satisfy for a logical profile."""

    model_config = ConfigDict(extra="forbid")

    tool_calling: bool = False
    structured_output: bool = False
    minimum_context_window: int = Field(gt=0)
    allowed_data_classifications: list[str] = Field(default_factory=lambda: ["public"])
    max_cost_usd: float | None = Field(default=None, ge=0)

    def is_satisfied_by(
        self,
        capabilities: ModelCapabilities,
        data_classifications: list[str],
        cost_per_1k_tokens_usd: float | None,
    ) -> bool:
        """Return whether a concrete model satisfies these requirements."""
        if self.tool_calling and not capabilities.tool_calling:
            return False
        if self.structured_output and not capabilities.structured_output:
            return False
        if capabilities.max_context_window < self.minimum_context_window:
            return False
        if not set(data_classifications).intersection(self.allowed_data_classifications):
            return False
        return not (
            self.max_cost_usd is not None
            and cost_per_1k_tokens_usd is not None
            and cost_per_1k_tokens_usd > self.max_cost_usd
        )


class ModelRoute(BaseModel):
    """A provider/model candidate listed by a logical profile."""

    model_config = ConfigDict(extra="forbid")

    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)


class ModelProfile(BaseModel):
    """A logical model profile used by agents instead of provider model names."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    requirements: ModelProfileRequirements
    routes: list[ModelRoute] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_routes(self) -> "ModelProfile":
        """Reject duplicate routes within a profile."""
        seen: set[tuple[str, str]] = set()
        for route in self.routes:
            key = (route.provider, route.model)
            if key in seen:
                raise ValueError(f"duplicate route {route.provider}/{route.model}")
            seen.add(key)
        return self
