"""Tests for local gateway event persistence."""

from pathlib import Path

from app.domain.identity import IdentityContext
from app.gateway.events import GatewayEvent, JsonlEventSink


def test_jsonl_event_sink_round_trips_recent_events(tmp_path: Path) -> None:
    """Events are persisted as JSONL and can be read back in order."""
    sink = JsonlEventSink(tmp_path / "events.jsonl")
    event = GatewayEvent(
        event_type="model_resolved",
        decision_id="route_test",
        status="allowed",
        identity=IdentityContext(
            tenant_id="acme",
            department_id="payments",
            team_id="checkout-platform",
            user_id="user_123",
            agent_id="pr-reviewer",
            agent_version="0.1.0",
            agent_instance_id="repo:payments-api:pr-reviewer",
            agent_run_id="run_test",
            environment="test",
        ),
        model_profile="coding_high",
        selected_provider="fake",
        selected_model="fake-coding-model",
    )

    sink.emit(event)

    recent = sink.recent()
    assert len(recent) == 1
    assert recent[0].decision_id == "route_test"
    assert recent[0].identity is not None
    assert recent[0].identity.department_id == "payments"
