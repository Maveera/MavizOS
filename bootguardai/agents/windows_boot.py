"""Windows Boot Agent — UEFI, BCD, bootmgfw, winload, ntoskrnl chain."""

from bootguardai.agents.base import BaseAgent
from bootguardai.knowledge.boot_flows import WINDOWS_UEFI_BOOT_CHAIN
from bootguardai.models.agent_result import AgentResult, AgentStatus
from bootguardai.models.boot_alert import OSType
from bootguardai.models.workflow import BootAnalysisContext


class WindowsBootAgent(BaseAgent):
    name = "windows_boot"
    description = "Windows UEFI boot chain: ESP, bootmgfw, BCD, winload, ntoskrnl, HAL"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        if context.os_type != OSType.WINDOWS:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SKIPPED,
                summary="Skipped — not a Windows boot context",
                simulated=True,
            )
        context.boot_stages = list(WINDOWS_UEFI_BOOT_CHAIN)
        findings: list[str] = []
        for alert in context.alerts:
            raw = alert.raw_data
            if raw.get("bcd_modified"):
                findings.append(
                    f"[simulated] BCD store modification flagged on {alert.host or 'host'}"
                )
                context.detected_risks.append("bcd_tampering_indicator")
            if raw.get("bootmgfw_hash_mismatch"):
                findings.append("[simulated] bootmgfw.efi hash mismatch vs baseline")
                context.detected_risks.append("bootmgfw_integrity")
        if not findings:
            findings.append(
                "Windows boot chain stages mapped (reference knowledge — no live EFI read)"
            )
        context.technical_findings.extend(findings)
        return self._success(
            summary=f"Windows boot analysis: {len(context.boot_stages)} stages",
            findings=findings,
            artifacts={"boot_chain": context.boot_stages},
            confidence=0.8 if findings else 0.6,
        )
