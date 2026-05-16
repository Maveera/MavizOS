"""Investigation workflow context models."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from mavizos.models.alert import Alert
from mavizos.models.agent_result import AgentResult
from mavizos.models.incident import Incident
from mavizos.models.investigation_report import InvestigationReport
from mavizos.models.ioc import IOC
from mavizos.models.timeline import TimelineEvent


class WorkflowStep(str):
    """Investigation pipeline step identifiers."""

    INTAKE = "intake"
    TRIAGE = "triage"
    ENRICHMENT = "enrichment"
    TELEMETRY_CORRELATION = "telemetry_correlation"
    MALWARE_ANALYSIS = "malware_analysis"
    ATTACK_MAPPING = "attack_mapping"
    THREAT_HUNTING = "threat_hunting"
    COMPLIANCE_CHECK = "compliance_check"
    REMEDIATION_PLANNING = "remediation_planning"
    REPORTING = "reporting"
    MEMORY_SYNC = "memory_sync"


class InvestigationContext(BaseModel):
    """Shared context passed between agents during investigation."""

    incident_id: str
    alerts: list[Alert] = Field(default_factory=list)
    incident: Incident | None = None
    agent_results: dict[str, AgentResult] = Field(default_factory=dict)
    iocs: list[IOC] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    affected_assets: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    automated_actions: list[str] = Field(default_factory=list)
    detection_opportunities: list[str] = Field(default_factory=list)
    analyst_notes: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    report: InvestigationReport | None = None
