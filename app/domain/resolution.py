"""Resolver-only gateway contracts."""

from pydantic import BaseModel, ConfigDict, Field

from app.domain.identity import IdentityContext
from app.domain.models import RequestConstraints


class ResolveModelRequest(BaseModel):
    """Request to resolve a profile without executing a provider call."""

    model_config = ConfigDict(extra="forbid")

    model_profile: str = Field(min_length=1)
    constraints: RequestConstraints | None = None
    identity: IdentityContext


class SelectedModel(BaseModel):
    """Provider/model selected by a resolver decision."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str


class PolicyDecision(BaseModel):
    """Policy result returned with a resolver decision."""

    model_config = ConfigDict(extra="forbid")

    allowed: bool = True
    budget_scope: str
    reason: str | None = None


class ResolveModelResult(BaseModel):
    """Resolver-only decision returned to callers."""

    model_config = ConfigDict(extra="forbid")

    decision_id: str
    selected: SelectedModel
    routing: dict[str, object]
    policy: PolicyDecision
    identity: IdentityContext
