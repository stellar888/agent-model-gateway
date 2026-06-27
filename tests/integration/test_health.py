"""Health endpoint tests."""

from fastapi.testclient import TestClient

from app.api import app


def test_health_endpoint() -> None:
    """The health endpoint reports the service as ready."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
