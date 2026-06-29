"""HTTP API integration tests."""

from fastapi.testclient import TestClient

from app.api import app


def test_profiles_and_models_endpoints() -> None:
    """The API exposes configured profiles and models."""
    client = TestClient(app)

    profiles = client.get("/v1/profiles")
    models = client.get("/v1/models")

    assert profiles.status_code == 200
    profile_names = {profile["name"] for profile in profiles.json()["profiles"]}
    assert "coding_high" in profile_names
    assert "coding_fast_openai" in profile_names
    assert models.status_code == 200
    assert any(model["provider"] == "fake" for model in models.json()["models"])


def test_generate_endpoint_uses_fake_provider() -> None:
    """The generation endpoint returns normalized model output and routing metadata."""
    client = TestClient(app)

    response = client.post(
        "/v1/generate",
        json={
            "model_profile": "coding_high",
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "Review payment retry flow"}],
                }
            ],
            "output_schema": {"type": "object"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["routing"]["selected_provider"] == "fake"
    assert payload["response"]["provider_metadata"]["provider"] == "fake"


def test_agent_run_endpoint_executes_fake_provider() -> None:
    """The agent-run endpoint uses the runtime and validates structured output."""
    client = TestClient(app)

    response = client.post(
        "/v1/agents/run",
        json={
            "agent_path": "agents/pr-reviewer/agent.yaml",
            "overlay_path": "agents/overlays/payments-team.yaml",
            "input": {"summary": "Adds payment idempotency checks."},
        },
    )

    assert response.status_code == 200
    payload = response.json()["result"]
    assert payload["agent"]["name"] == "pr-reviewer"
    assert payload["structured_output"]["risk_level"] == "medium"


def test_generate_endpoint_reports_no_eligible_model() -> None:
    """No eligible models are reported as typed routing failures."""
    client = TestClient(app)

    response = client.post(
        "/v1/generate",
        json={
            "model_profile": "coding_tiny",
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "hello"}],
                }
            ],
        },
    )

    assert response.status_code == 422
    assert "rejected_candidates" in response.json()["detail"]


def test_resolve_endpoint_returns_model_without_provider_call() -> None:
    """The resolver endpoint selects a model and records identity context."""
    client = TestClient(app)

    response = client.post(
        "/v1/resolve",
        json={
            "model_profile": "coding_high",
            "constraints": {
                "data_classification": "internal",
                "minimum_context_window": 32_000,
            },
            "identity": {
                "tenant_id": "acme",
                "department_id": "payments",
                "team_id": "checkout-platform",
                "user_id": "user_123",
                "agent_id": "pr-reviewer",
                "agent_version": "0.1.0",
                "agent_instance_id": "repo:payments-api:pr-reviewer",
                "agent_run_id": "run_01JABC",
                "environment": "test",
            },
        },
    )

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["selected"] == {"provider": "fake", "model": "fake-coding-model"}
    assert result["policy"]["budget_scope"] == "department:payments"
    assert result["identity"]["agent_run_id"] == "run_01JABC"


def test_events_and_dashboard_endpoints() -> None:
    """Recent events and the HTML dashboard are exposed for local observability."""
    client = TestClient(app)

    events = client.get("/v1/events/recent")
    dashboard = client.get("/dashboard")

    assert events.status_code == 200
    assert "events" in events.json()
    assert dashboard.status_code == 200
    assert "Agent Model Gateway" in dashboard.text
