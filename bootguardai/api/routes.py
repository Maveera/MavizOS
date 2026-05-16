"""BootGuardAI FastAPI routes."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from bootguardai.models.boot_alert import BootAlert, BootMode, OSType
from bootguardai.orchestrator.orchestrator import Orchestrator

router = APIRouter()
_orchestrator: Orchestrator | None = None


def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


class BootAlertRequest(BaseModel):
    title: str
    description: str = ""
    os_type: OSType = OSType.UNKNOWN
    boot_mode: BootMode = BootMode.UNKNOWN
    host: str | None = None
    secure_boot: bool | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    alerts: list[BootAlertRequest]
    os_type: OSType | None = None


class ApprovalActionRequest(BaseModel):
    resolved_by: str = "analyst"


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "bootguardai"}


@router.get("/agents")
async def list_agents() -> list[dict[str, str]]:
    return get_orchestrator().list_agents()


@router.post("/boot/analyze")
async def boot_analyze(request: AnalyzeRequest) -> dict[str, Any]:
    alerts = [BootAlert(**a.model_dump()) for a in request.alerts]
    return await get_orchestrator().analyze(alerts, os_type=request.os_type)


@router.post("/boot/windows")
async def boot_windows(request: AnalyzeRequest) -> dict[str, Any]:
    alerts = [BootAlert(**{**a.model_dump(), "os_type": OSType.WINDOWS}) for a in request.alerts]
    return await get_orchestrator().analyze_windows(alerts)


@router.post("/boot/linux")
async def boot_linux(request: AnalyzeRequest) -> dict[str, Any]:
    alerts = [BootAlert(**{**a.model_dump(), "os_type": OSType.LINUX}) for a in request.alerts]
    return await get_orchestrator().analyze_linux(alerts)


@router.get("/reports/{analysis_id}")
async def get_report(analysis_id: str) -> dict[str, Any]:
    report = get_orchestrator().get_report(analysis_id)
    if not report:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return report


@router.post("/persistence/hunt")
async def persistence_hunt(request: AnalyzeRequest) -> dict[str, Any]:
    alerts = [BootAlert(**a.model_dump()) for a in request.alerts]
    return await get_orchestrator().persistence_hunt(alerts)


@router.get("/approvals")
async def list_approvals() -> list[dict[str, Any]]:
    return [r.model_dump() for r in get_orchestrator().approval_gate.list_pending()]
