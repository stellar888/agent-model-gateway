"""Agent definition loading helpers."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

from app.domain.agent import AgentDefinition
from app.runtime.errors import AgentLoadError


class LoadedAgent(BaseModel):
    """Agent definition plus source files needed by the runtime."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    definition: AgentDefinition
    source_path: Path
    prompt: str
    output_schema: dict[str, object]


def load_agent(path: Path) -> LoadedAgent:
    """Load an agent YAML file, prompt file, and output schema."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        definition = AgentDefinition.model_validate(raw)
        prompt = _read_relative(path, definition.spec.instructions.system_file)
        schema_raw = yaml.safe_load(
            (path.parent / definition.spec.output.schema_file).read_text(encoding="utf-8")
        )
    except Exception as exc:
        raise AgentLoadError(f"failed to load agent from {path}") from exc

    if not isinstance(schema_raw, dict):
        raise AgentLoadError(f"output schema in {path} must be a JSON object")

    return LoadedAgent(
        definition=definition,
        source_path=path,
        prompt=prompt,
        output_schema=_dict_str_object(schema_raw),
    )


def _read_relative(base_path: Path, relative_path: str) -> str:
    """Read a UTF-8 file relative to an agent definition."""
    return (base_path.parent / relative_path).read_text(encoding="utf-8")


def _dict_str_object(value: dict[Any, Any]) -> dict[str, object]:
    """Convert YAML mapping keys to strings for domain contracts."""
    return {str(key): item for key, item in value.items()}
