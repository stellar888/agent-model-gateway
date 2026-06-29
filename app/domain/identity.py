"""Identity context for agent and gateway requests."""

from pydantic import BaseModel, ConfigDict, Field


class IdentityContext(BaseModel):
    """Caller, owner, and run identity used for audit and quota decisions."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: str = Field(min_length=1)
    department_id: str = Field(min_length=1)
    team_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    agent_version: str = Field(min_length=1)
    agent_instance_id: str = Field(min_length=1)
    agent_run_id: str = Field(min_length=1)
    environment: str = Field(default="development", min_length=1)
    source: str | None = None
    correlation_id: str | None = None
