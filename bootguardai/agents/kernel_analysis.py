"""Kernel Analysis Agent — modules, patching, integrity."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.workflow import BootAnalysisContext


class KernelAnalysisAgent(BaseAgent):
    name = "kernel_analysis"
    description = "Kernel modules, patching indicators, integrity heuristics"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        findings: list[str] = []
        for alert in context.alerts:
            raw = alert.raw_data
            mods = raw.get("suspicious_modules") or []
            for mod in mods:
                findings.append(f"[simulated] Suspicious kernel module listed: {mod}")
                context.kernel_findings.append(f"module:{mod}")
            if raw.get("kernel_patch_indicator"):
                findings.append("[simulated] Kernel patch/tamper heuristic (demo telemetry only)")
        if not findings:
            findings.append("No kernel anomalies in provided simulated telemetry")
        context.kernel_findings.extend(findings)
        return self._success(
            summary=f"Kernel analysis: {len(findings)} finding(s)",
            findings=findings,
            confidence=0.7 if findings else 0.5,
        )
