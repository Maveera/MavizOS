"""Boot analysis workflow context."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from bootguardai.models.agent_result import AgentResult
from bootguardai.models.boot_alert import BootAlert, BootMode, OSType
from bootguardai.models.boot_report import BootAnalysisReport


class WorkflowStep(str, Enum):
    COLLECT_CONTEXT = "collect_boot_context"
    STAGE_IDENTIFICATION = "stage_identification"
    BOOTLOADER_ANALYSIS = "bootloader_analysis"
    KERNEL_INIT_ANALYSIS = "kernel_init_analysis"
    DRIVER_MODULE_ANALYSIS = "driver_module_analysis"
    PERSISTENCE_SCAN = "persistence_scan"
    THREAT_CORRELATION = "threat_correlation"
    INTEGRITY_ASSESSMENT = "integrity_assessment"
    REMEDIATION_PLANNING = "remediation_planning"
    REPORT_GENERATION = "report_generation"


class BootAnalysisContext(BaseModel):
    """Shared state across boot analysis agents and workflow."""

    analysis_id: str
    alerts: list[BootAlert] = Field(default_factory=list)
    os_type: OSType = OSType.UNKNOWN
    boot_mode: BootMode = BootMode.UNKNOWN
    secure_boot: bool | None = None
    boot_stages: list[str] = Field(default_factory=list)
    agent_results: dict[str, AgentResult] = Field(default_factory=dict)
    loaded_components: list[str] = Field(default_factory=list)
    persistence_indicators: list[str] = Field(default_factory=list)
    detected_risks: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    detection_opportunities: list[str] = Field(default_factory=list)
    soc_notes: list[str] = Field(default_factory=list)
    kernel_findings: list[str] = Field(default_factory=list)
    bootloader_findings: list[str] = Field(default_factory=list)
    technical_findings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    report: BootAnalysisReport | None = None
    simulated: bool = True
