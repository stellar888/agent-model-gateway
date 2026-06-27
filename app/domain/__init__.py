"""Provider-neutral domain contracts."""

from app.domain.agent import (
    AgentDefinition,
    AgentInstructions,
    AgentMetadata,
    AgentOutput,
    AgentPolicies,
    AgentResolutionMetadata,
    AgentRunRequest,
    AgentRunResult,
    AgentSpec,
    CustomizationPolicy,
)
from app.domain.capabilities import (
    ModelCapabilities,
    ModelProfile,
    ModelProfileRequirements,
    ModelRoute,
)
from app.domain.messages import ContentBlock, ContentBlockType, Message, MessageRole
from app.domain.models import (
    ModelDescriptor,
    ModelRequest,
    ModelRequestResult,
    RequestConstraints,
    ToolDefinition,
)
from app.domain.responses import ModelResponse, TokenUsage, ToolCall

__all__ = [
    "AgentDefinition",
    "AgentInstructions",
    "AgentMetadata",
    "AgentOutput",
    "AgentPolicies",
    "AgentResolutionMetadata",
    "AgentRunRequest",
    "AgentRunResult",
    "AgentSpec",
    "ContentBlock",
    "ContentBlockType",
    "CustomizationPolicy",
    "Message",
    "MessageRole",
    "ModelCapabilities",
    "ModelDescriptor",
    "ModelProfile",
    "ModelProfileRequirements",
    "ModelRequest",
    "ModelRequestResult",
    "ModelResponse",
    "ModelRoute",
    "RequestConstraints",
    "TokenUsage",
    "ToolCall",
    "ToolDefinition",
]
