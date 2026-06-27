"""Typed runtime errors."""


class RuntimeErrorBase(Exception):
    """Base class for agent runtime failures."""


class AgentLoadError(RuntimeErrorBase):
    """Raised when an agent definition or referenced file cannot be loaded."""


class OverlayError(RuntimeErrorBase):
    """Raised when an overlay violates the base agent customization policy."""


class OutputValidationError(RuntimeErrorBase):
    """Raised when model output does not match the configured schema."""
