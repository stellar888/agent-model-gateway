"""HTTP API entrypoint for the proof-of-concept service."""

from fastapi import FastAPI
from pydantic import BaseModel


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
