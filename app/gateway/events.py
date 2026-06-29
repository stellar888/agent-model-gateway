"""Structured gateway events and JSONL persistence."""

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain.identity import IdentityContext

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class GatewayEvent(BaseModel):
    """Redacted event emitted by resolver and gateway operations."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: f"evt_{uuid4().hex}")
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    decision_id: str | None = None
    identity: IdentityContext | None = None
    model_profile: str | None = None
    selected_provider: str | None = None
    selected_model: str | None = None
    status: str
    reason: str | None = None
    latency_ms: int | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class JsonlEventSink:
    """Append-only JSONL event sink suitable for the local proof of concept."""

    def __init__(self, path: Path | None = None) -> None:
        """Create an event sink at the configured path."""
        self.path = path or PROJECT_ROOT / "logs/gateway-events.jsonl"

    def emit(self, event: GatewayEvent) -> None:
        """Persist a gateway event as one JSON line."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(event.model_dump_json() + "\n")

    def recent(self, limit: int = 50) -> list[GatewayEvent]:
        """Return the most recent events, newest last."""
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [
            GatewayEvent.model_validate(json.loads(line)) for line in lines[-limit:] if line.strip()
        ]


def default_event_sink() -> JsonlEventSink:
    """Return the default local JSONL event sink."""
    return JsonlEventSink()
