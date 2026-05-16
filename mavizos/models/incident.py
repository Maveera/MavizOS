"""Incident domain models."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from mavizos.models.alert import Alert, AlertSeverity


class IncidentStatus(str, Enum):
    """Incident lifecycle status."""

    NEW = "new"
    TRIAGING = "triaging"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Incident(BaseModel):
    """Security incident aggregating alerts and investigation artifacts."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    status: IncidentStatus = IncidentStatus.NEW
    severity: AlertSeverity = AlertSeverity.MEDIUM
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    alerts: list[Alert] = Field(default_factory=list)
    affected_assets: list[str] = Field(default_factory=list)
    iocs: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    report_id: str | None = None
