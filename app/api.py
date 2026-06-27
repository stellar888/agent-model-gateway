"""HTTP API entrypoint for the proof-of-concept service."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import PROJECT_ROOT, build_gateway, build_runner
from app.domain.agent import AgentRunRequest
from app.domain.models import ModelRequest
from app.gateway.errors import GatewayError, NoEligibleModelError
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


@app.post("/v1/agents/run")
async def run_agent(request: AgentRunRequest) -> dict[str, object]:
    """Run an agent through the runtime using the configured gateway."""
    try:
        result = await build_runner().run(request)
    except (GatewayError, RuntimeErrorBase) as exc:
        raise HTTPException(status_code=422, detail={"message": str(exc)}) from exc

    return {"result": result.model_dump(mode="json")}
