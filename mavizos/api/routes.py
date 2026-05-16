"""FastAPI route definitions."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from mavizos.models.alert import Alert, AlertSeverity, AlertSource
from mavizos.orchestrator.orchestrator import Orchestrator

router = APIRouter()
_orchestrator: Orchestrator | None = None


def get_orchestrator() -> Orchestrator:
    """Lazy singleton orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


class TriageRequest(BaseModel):
    """Request body for alert triage."""

    title: str
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    source: AlertSource = AlertSource.SIEM
    source_system: str = "splunk"
    host: str | None = None
    user: str | None = None
    ip_address: str | None = None
    process: str | None = None
    file_hash: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class InvestigateRequest(BaseModel):
    """Request body for full investigation."""

    alerts: list[TriageRequest]


class HuntRequest(BaseModel):
    """Request body for threat hunting."""

    hypothesis: str
    context: dict[str, Any] = Field(default_factory=dict)


class ApprovalActionRequest(BaseModel):
    """Approve or deny a pending action."""

    resolved_by: str = "analyst"


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "mavizos"}


@router.get("/agents")
async def list_agents() -> list[dict[str, str]]:
    """List registered agents."""
    return get_orchestrator().list_agents()


@router.post("/alerts/triage")
async def triage_alert(request: TriageRequest) -> dict[str, Any]:
    """Triage a single security alert."""
    alert = Alert(**request.model_dump())
    return await get_orchestrator().triage_alert(alert)


@router.post("/investigate")
async def investigate(request: InvestigateRequest) -> dict[str, Any]:
    """Run full investigation workflow on alerts."""
    alerts = [Alert(**a.model_dump()) for a in request.alerts]
    if not alerts:
        raise HTTPException(status_code=400, detail="At least one alert required")
    return await get_orchestrator().investigate(alerts)


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str) -> dict[str, Any]:
    """Retrieve incident by ID."""
    incident = get_orchestrator().get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.model_dump(mode="json")


@router.post("/hunt")
async def hunt(request: HuntRequest) -> dict[str, Any]:
    """Execute threat hunting with a hypothesis."""
    return await get_orchestrator().hunt(request.hypothesis, request.context)


@router.post("/detections/generate")
async def generate_detection(request: TriageRequest) -> dict[str, Any]:
    """Generate detection rules from alert context."""
    alert = Alert(**request.model_dump())
    return await get_orchestrator().generate_detection(alert)


@router.get("/approvals/pending")
async def list_pending_approvals() -> list[dict[str, Any]]:
    """List pending approval requests."""
    orch = get_orchestrator()
    return [r.model_dump(mode="json") for r in orch.approval_gate.list_pending()]


@router.post("/approvals/{request_id}/approve")
async def approve_action(request_id: str, body: ApprovalActionRequest) -> dict[str, Any]:
    """Approve a destructive action."""
    req = get_orchestrator().approval_gate.approve(request_id, body.resolved_by)
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")
    get_orchestrator().audit_logger.log(
        actor=body.resolved_by,
        action="approval_granted",
        target=request_id,
        outcome="approved",
        incident_id=req.incident_id,
    )
    return req.model_dump(mode="json")


@router.post("/approvals/{request_id}/deny")
async def deny_action(request_id: str, body: ApprovalActionRequest) -> dict[str, Any]:
    """Deny a destructive action."""
    req = get_orchestrator().approval_gate.deny(request_id, body.resolved_by)
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return req.model_dump(mode="json")


@router.get("/audit")
async def get_audit_log(incident_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """Retrieve audit log entries."""
    entries = get_orchestrator().audit_logger.get_entries(incident_id=incident_id, limit=limit)
    return [e.model_dump(mode="json") for e in entries]
