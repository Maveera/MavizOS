"""Bootloader Integrity Agent — BCD/GRUB tampering, unsigned components."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.boot_alert import OSType
from bootguardai.models.workflow import BootAnalysisContext


class BootloaderIntegrityAgent(BaseAgent):
    name = "bootloader_integrity"
    description = "BCD/GRUB integrity, unsigned boot component checks"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        findings: list[str] = []
        for alert in context.alerts:
            raw = alert.raw_data
            if raw.get("unsigned_boot_component"):
                findings.append(
                    f"[simulated] Unsigned boot component: {raw.get('component', 'unknown')}"
                )
                context.bootloader_findings.append("unsigned_boot_component")
            if raw.get("secure_boot") is False and context.secure_boot is not False:
                findings.append("[simulated] Secure Boot disabled or inconsistent state")
                context.bootloader_findings.append("secure_boot_disabled")
        if context.os_type == OSType.WINDOWS:
            findings.append("BCD store integrity check guidance: bcdedit /enum all (analyst)")
        elif context.os_type == OSType.LINUX:
            findings.append("GRUB integrity: verify /boot/grub/grub.cfg signatures (analyst)")
        context.bootloader_findings.extend(findings)
        return self._success(
            summary="Bootloader integrity assessment complete",
            findings=findings,
            confidence=0.75 if findings else 0.55,
        )
