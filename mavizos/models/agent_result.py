"""Agent execution result models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent execution status."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING_APPROVAL = "pending_approval"


class AgentResult(BaseModel):
    """Standardized output from any MavizOS agent."""

    agent_name: str
    status: AgentStatus = AgentStatus.SUCCESS
    summary: str = ""
    findings: list[str] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    requires_approval: bool = False
    approval_request_id: str | None = None
    errors: list[str] = Field(default_factory=list)
