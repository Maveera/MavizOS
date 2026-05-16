"""14-section investigation report model."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from mavizos.models.alert import AlertSeverity
from mavizos.models.ioc import IOC
from mavizos.models.timeline import TimelineEvent


class InvestigationReport(BaseModel):
    """Structured investigation output with 14 required sections."""

    incident_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # 14 sections
    executive_summary: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    confidence: float = 0.0
    technical_findings: list[str] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    affected_assets: list[str] = Field(default_factory=list)
    iocs: list[IOC] = Field(default_factory=list)
    mitre_mapping: list[dict[str, str]] = Field(default_factory=list)
    root_cause_analysis: str = ""
    recommended_actions: list[str] = Field(default_factory=list)
    automated_actions_taken: list[str] = Field(default_factory=list)
    detection_opportunities: list[str] = Field(default_factory=list)
    analyst_notes: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize report to API-friendly dictionary."""
        return self.model_dump(mode="json")
