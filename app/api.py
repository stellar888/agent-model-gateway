"""HTTP API entrypoint for the proof-of-concept service."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.config import PROJECT_ROOT, build_gateway, build_resolver, build_runner
from app.domain.agent import AgentRunRequest
from app.domain.models import ModelRequest
from app.domain.resolution import ResolveModelRequest
from app.gateway.errors import GatewayError, NoEligibleModelError
from app.gateway.events import default_event_sink
from app.gateway.registry import load_models, load_profiles
from app.runtime.errors import RuntimeErrorBase


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: str


app = FastAPI(
    title="Agent Model Gateway",
    description="Provider-neutral agent runtime and model gateway proof of concept.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service health for load balancers and smoke tests."""
    return HealthResponse(status="ok")


@app.get("/v1/profiles")
async def profiles() -> dict[str, object]:
    """Return configured logical model profiles."""
    registry = load_profiles(PROJECT_ROOT / "config/model-profiles.yaml")
    return {"profiles": [profile.model_dump(mode="json") for profile in registry.list()]}


@app.get("/v1/models")
async def models() -> dict[str, object]:
    """Return configured concrete provider models."""
    registry = load_models(PROJECT_ROOT / "config/models.yaml")
    return {"models": [model.model_dump(mode="json") for model in registry.list()]}


@app.post("/v1/generate")
async def generate(request: ModelRequest) -> dict[str, object]:
    """Route one provider-neutral model request through the gateway."""
    try:
        result = await build_gateway().generate(request)
    except NoEligibleModelError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(exc),
                "rejected_candidates": exc.rejected_candidates,
            },
        ) from exc
    except GatewayError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc

    return {
        "response": result.response.model_dump(mode="json"),
        "routing": result.routing.model_dump(mode="json"),
    }


@app.post("/v1/resolve")
async def resolve_model(request: ResolveModelRequest) -> dict[str, object]:
    """Resolve a model profile without executing a provider call."""
    try:
        result = build_resolver().resolve(request)
    except NoEligibleModelError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(exc),
                "rejected_candidates": exc.rejected_candidates,
            },
        ) from exc
    except GatewayError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc

    return {"result": result.model_dump(mode="json")}


@app.post("/v1/agents/run")
async def run_agent(request: AgentRunRequest) -> dict[str, object]:
    """Run an agent through the runtime using the configured gateway."""
    try:
        result = await build_runner().run(request)
    except (GatewayError, RuntimeErrorBase) as exc:
        raise HTTPException(status_code=422, detail={"message": str(exc)}) from exc

    return {"result": result.model_dump(mode="json")}


@app.get("/v1/events/recent")
async def recent_events(limit: int = 50) -> dict[str, object]:
    """Return recent local gateway events for the proof-of-concept dashboard."""
    bounded_limit = max(1, min(limit, 500))
    events = default_event_sink().recent(bounded_limit)
    return {"events": [event.model_dump(mode="json") for event in events]}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    """Return a tiny live dashboard backed by the recent events endpoint."""
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Agent Model Gateway Dashboard</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
    th, td { border-bottom: 1px solid #d5dde5; padding: 0.5rem; text-align: left; }
    th { background: #f4f7fb; }
    code { background: #f4f7fb; padding: 0.1rem 0.25rem; }
  </style>
</head>
<body>
  <h1>Agent Model Gateway</h1>
  <p>Recent resolver and gateway events from <code>/v1/events/recent</code>.</p>
  <table>
    <thead>
      <tr>
        <th>Time</th><th>Event</th><th>Status</th><th>Agent</th>
        <th>Department</th><th>Profile</th><th>Selected</th><th>Decision</th>
      </tr>
    </thead>
    <tbody id="events"></tbody>
  </table>
  <script>
    async function refresh() {
      const response = await fetch('/v1/events/recent?limit=100');
      const data = await response.json();
      const rows = data.events.slice().reverse().map((event) => {
        const identity = event.identity || {};
        const selected = [event.selected_provider, event.selected_model].filter(Boolean).join('/');
        return `<tr>
          <td>${event.timestamp}</td>
          <td>${event.event_type}</td>
          <td>${event.status}</td>
          <td>${identity.agent_id || ''}</td>
          <td>${identity.department_id || ''}</td>
          <td>${event.model_profile || ''}</td>
          <td>${selected}</td>
          <td>${event.decision_id || ''}</td>
        </tr>`;
      }).join('');
      document.getElementById('events').innerHTML =
        rows || '<tr><td colspan="8">No events yet.</td></tr>';
    }
    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>
"""
