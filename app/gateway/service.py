"""Model gateway orchestration service."""

from app.domain.models import ModelRequest
from app.domain.responses import ModelResponse
from app.gateway.errors import RetryableProviderError
from app.gateway.registry import ProviderRegistry
from app.gateway.router import CapabilityRouter, RoutingDecision


class GatewayResult:
    """Normalized model response with structured routing metadata."""

    def __init__(self, response: ModelResponse, routing: RoutingDecision) -> None:
        """Create a gateway result."""
        self.response = response
        self.routing = routing


class ModelGateway:
    """Execute one provider-neutral model request through an eligible provider."""

    def __init__(
        self,
        router: CapabilityRouter,
        providers: ProviderRegistry,
        retry_limit: int = 1,
    ) -> None:
        """Create a gateway with a deterministic router and provider registry."""
        self._router = router
        self._providers = providers
        self._retry_limit = retry_limit

    async def generate(self, request: ModelRequest) -> GatewayResult:
        """Route and execute one model request without running agent tools."""
        selection = self._router.resolve(request)
        provider = self._providers.get(selection.descriptor.provider)

        attempts = 0
        while True:
            try:
                response = await provider.generate(selection.descriptor.model, request)
                return GatewayResult(response=response, routing=selection.decision)
            except RetryableProviderError:
                attempts += 1
                if attempts > self._retry_limit:
                    raise
