"""Agent execution result models."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentResult(BaseModel):
    agent_name: str
    status: AgentStatus = AgentStatus.SUCCESS
    summary: str = ""
    findings: list[str] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    errors: list[str] = Field(default_factory=list)
    simulated: bool = True
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
