"""Typed model gateway and routing errors."""


class GatewayError(Exception):
    """Base class for model gateway failures."""


class ProfileNotFoundError(GatewayError):
    """Raised when a logical model profile is not configured."""


class ModelNotFoundError(GatewayError):
    """Raised when a configured route references an unknown model."""


class ProviderNotFoundError(GatewayError):
    """Raised when a configured route references an unregistered provider."""


class NoEligibleModelError(GatewayError):
    """Raised when every route in a profile is rejected."""

    def __init__(self, profile: str, rejected_candidates: list[dict[str, object]]) -> None:
        """Create an error with structured rejection details."""
        self.profile = profile
        self.rejected_candidates = rejected_candidates
        super().__init__(f"no eligible model found for profile {profile!r}")


class ProviderError(GatewayError):
    """Raised when a provider adapter fails."""


class RetryableProviderError(ProviderError):
    """Raised for provider failures that may succeed after a short retry."""
