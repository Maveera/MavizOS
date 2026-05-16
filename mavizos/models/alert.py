"""Alert domain models."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Normalized alert severity."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class AlertSource(str, Enum):
    """Source system for an alert."""

    SIEM = "siem"
    EDR = "edr"
    EMAIL = "email"
    CLOUD = "cloud"
    FIREWALL = "firewall"
    IDENTITY = "identity"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class Alert(BaseModel):
    """Security alert ingested for triage and investigation."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    source: AlertSource = AlertSource.UNKNOWN
    source_system: str = "unknown"
    rule_name: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    raw_data: dict[str, Any] = Field(default_factory=dict)
    host: str | None = None
    user: str | None = None
    ip_address: str | None = None
    process: str | None = None
    file_hash: str | None = None
    tags: list[str] = Field(default_factory=list)
    false_positive_score: float | None = None
    classification: str | None = None
    priority_score: int | None = None
