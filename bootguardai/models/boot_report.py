"""12-section boot analysis report model."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from bootguardai.models.boot_alert import OSType


class BootAnalysisReport(BaseModel):
    """Structured boot forensic output — 12 required sections."""

    analysis_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    os_type: OSType = OSType.UNKNOWN
    simulated: bool = True

    executive_summary: str = ""
    boot_process_stage: list[str] = Field(default_factory=list)
    technical_findings: list[str] = Field(default_factory=list)
    loaded_components: list[str] = Field(default_factory=list)
    detected_risks: list[str] = Field(default_factory=list)
    persistence_indicators: list[str] = Field(default_factory=list)
    kernel_analysis: list[str] = Field(default_factory=list)
    bootloader_analysis: list[str] = Field(default_factory=list)
    security_assessment: str = ""
    recommended_actions: list[str] = Field(default_factory=list)
    detection_opportunities: list[str] = Field(default_factory=list)
    soc_notes: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def section_names(cls) -> list[str]:
        return [
            "executive_summary",
            "boot_process_stage",
            "technical_findings",
            "loaded_components",
            "detected_risks",
            "persistence_indicators",
            "kernel_analysis",
            "bootloader_analysis",
            "security_assessment",
            "recommended_actions",
            "detection_opportunities",
            "soc_notes",
        ]
