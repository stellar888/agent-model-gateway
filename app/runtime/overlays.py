"""Agent overlay merge helpers."""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from app.domain.agent import AgentDefinition, AgentResolutionMetadata
from app.runtime.errors import OverlayError


class AgentOverlay(BaseModel):
    """A deliberately limited overlay for a base agent definition."""

    model_config = ConfigDict(extra="forbid")

    extends: str
    instructions: dict[str, list[str]] = Field(default_factory=dict)
    settings: dict[str, object] = Field(default_factory=dict)
    model_profile: str | None = None
    tools: list[dict[str, object]] = Field(default_factory=list)


class ResolvedAgent(BaseModel):
    """A resolved agent definition and merge metadata."""

    definition: AgentDefinition
    metadata: AgentResolutionMetadata


def load_overlay(path: Path) -> AgentOverlay:
    """Load and validate an overlay YAML file."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise OverlayError(f"overlay {path} must be a YAML object")
    return AgentOverlay.model_validate(raw)


def apply_overlay(base: AgentDefinition, base_path: Path, overlay_path: Path) -> ResolvedAgent:
    """Apply a supported overlay to an agent definition."""
    overlay = load_overlay(overlay_path)
    if Path(overlay.extends).resolve() != base_path.resolve():
        raise OverlayError("overlay extends does not match the loaded base agent")

    resolved = base.model_copy(deep=True)
    appended = overlay.instructions.get("append", [])
    if appended:
        if resolved.spec.customization.append_instructions != "allowed":
            raise OverlayError("base agent does not allow appended instructions")
        resolved.spec.instructions.append.extend(appended)

    if overlay.model_profile is not None:
        if resolved.spec.customization.model_profile != "allowed":
            raise OverlayError("model_profile is locked by the base agent")
        resolved.spec.model_profile = overlay.model_profile

    if overlay.tools and resolved.spec.customization.tools_add != "allowed":
        raise OverlayError("tool additions are locked by the base agent")

    settings_overrides: dict[str, object] = {}
    for key, value in overlay.settings.items():
        _ensure_scalar(value, key)
        if resolved.spec.customization.settings.get(key) != "allowed":
            raise OverlayError(f"setting {key!r} is locked by the base agent")
        resolved.spec.settings[key] = value
        settings_overrides[key] = value

    return ResolvedAgent(
        definition=resolved,
        metadata=AgentResolutionMetadata(
            base_path=base_path.as_posix(),
            overlay_path=overlay_path.as_posix(),
            appended_instruction_count=len(appended),
            settings_overrides=settings_overrides,
        ),
    )


def resolve_without_overlay(base: AgentDefinition, base_path: Path) -> ResolvedAgent:
    """Return a base agent with resolution metadata and no overlay."""
    return ResolvedAgent(
        definition=base,
        metadata=AgentResolutionMetadata(base_path=base_path.as_posix()),
    )


def _ensure_scalar(value: object, key: str) -> None:
    """Reject nested setting values to keep overlay semantics simple."""
    if isinstance(value, dict | list):
        raise OverlayError(f"setting {key!r} must be a scalar value")
