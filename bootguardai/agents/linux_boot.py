"""Linux Boot Agent — GRUB2, kernel, initramfs, systemd."""

from bootguardai.agents.base import BaseAgent
from bootguardai.knowledge.boot_flows import LINUX_UEFI_BOOT_CHAIN
from bootguardai.models.agent_result import AgentResult, AgentStatus
from bootguardai.models.boot_alert import OSType
from bootguardai.models.workflow import BootAnalysisContext


class LinuxBootAgent(BaseAgent):
    name = "linux_boot"
    description = "Linux UEFI boot: GRUB2, kernel, initramfs, systemd, rootfs"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        if context.os_type != OSType.LINUX:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SKIPPED,
                summary="Skipped — not a Linux boot context",
                simulated=True,
            )
        context.boot_stages = list(LINUX_UEFI_BOOT_CHAIN)
        findings: list[str] = []
        for alert in context.alerts:
            raw = alert.raw_data
            if raw.get("grub_cfg_modified"):
                findings.append(
                    f"[simulated] GRUB configuration change on {alert.host or 'host'}"
                )
                context.detected_risks.append("grub_tampering")
            if raw.get("initramfs_anomaly"):
                findings.append("[simulated] initramfs size/hash anomaly vs baseline")
        if not findings:
            findings.append("Linux boot chain stages mapped (reference — no live GRUB read)")
        context.technical_findings.extend(findings)
        return self._success(
            summary=f"Linux boot analysis: {len(context.boot_stages)} stages",
            findings=findings,
            artifacts={"boot_chain": context.boot_stages},
            confidence=0.8 if findings else 0.6,
        )
