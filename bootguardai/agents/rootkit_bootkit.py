"""Rootkit/Bootkit Detection Agent — heuristic indicators only."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.workflow import BootAnalysisContext

# Heuristic keywords from *provided* alert data only — no fabricated IOCs
BOOTKIT_SIGNALS = ("bootkit", "rootkit", "mbr", "vbr", "esp_tamper", "bootmgfw_replace")


class RootkitBootkitAgent(BaseAgent):
    name = "rootkit_bootkit"
    description = "Behavioral bootkit/rootkit heuristics (no fake detections)"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        findings: list[str] = []
        for alert in context.alerts:
            text = f"{alert.title} {alert.description}".lower()
            tags = " ".join(alert.tags).lower()
            combined = f"{text} {tags}"
            matched = [s for s in BOOTKIT_SIGNALS if s in combined]
            for signal in matched:
                findings.append(f"Heuristic match from alert text: {signal}")
            if alert.raw_data.get("bootkit_indicator"):
                findings.append(
                    f"[simulated] Analyst-provided bootkit_indicator: "
                    f"{alert.raw_data['bootkit_indicator']}"
                )
                context.detected_risks.append("bootkit_indicator")
        if not findings:
            findings.append("No bootkit/rootkit heuristics triggered from supplied data")
        return self._success(
            summary="Rootkit/bootkit heuristic scan complete",
            findings=findings,
            confidence=0.85 if context.detected_risks else 0.5,
        )
