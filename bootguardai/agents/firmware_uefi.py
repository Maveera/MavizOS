"""Firmware/UEFI Agent — Secure Boot, TPM, EFI partition."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.workflow import BootAnalysisContext


class FirmwareUEFIAgent(BaseAgent):
    name = "firmware_uefi"
    description = "Secure Boot, TPM, EFI partition posture"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        findings: list[str] = []
        sb = context.secure_boot
        if sb is True:
            findings.append("[simulated] Secure Boot reported enabled")
        elif sb is False:
            findings.append("[simulated] Secure Boot disabled — elevated bootkit risk")
            context.detected_risks.append("secure_boot_off")
        for alert in context.alerts:
            if alert.raw_data.get("efi_partition_anomaly"):
                findings.append("[simulated] EFI partition layout anomaly in demo telemetry")
        return self._success(
            summary="Firmware/UEFI posture assessed",
            findings=findings or ["No UEFI anomalies in simulated input"],
            confidence=0.65,
        )
