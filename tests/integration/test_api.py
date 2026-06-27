"""HTTP API integration tests."""

from fastapi.testclient import TestClient

from app.api import app


def test_profiles_and_models_endpoints() -> None:
    """The API exposes configured profiles and models."""
    client = TestClient(app)

    profiles = client.get("/v1/profiles")
    models = client.get("/v1/models")

    assert profiles.status_code == 200
    assert profiles.json()["profiles"][0]["name"] == "coding_high"
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
