"""Base provider adapter interfaces."""

from typing import Protocol

from app.domain.models import ModelRequest
from app.domain.responses import ModelResponse


class ModelProvider(Protocol):
    """Protocol implemented by concrete provider adapters."""

    async def generate(self, model: str, request: ModelRequest) -> ModelResponse:
        """Generate one normalized model response without executing tools."""
