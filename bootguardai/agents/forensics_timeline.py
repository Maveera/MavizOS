"""Forensics Timeline Agent — boot event timeline reconstruction."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.workflow import BootAnalysisContext


class ForensicsTimelineAgent(BaseAgent):
    name = "forensics_timeline"
    description = "Boot event timeline from simulated event logs"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        events: list[str] = []
        for alert in context.alerts:
            for ev in alert.raw_data.get("boot_events") or []:
                events.append(f"[simulated] {ev}")
        if not events and context.boot_stages:
            for i, stage in enumerate(context.boot_stages[:6]):
                events.append(f"T+{i}s reference stage: {stage}")
        context.metadata["boot_timeline"] = events
        return self._success(
            summary=f"Timeline: {len(events)} event(s)",
            findings=events[:15],
            artifacts={"timeline": events},
            confidence=0.7,
        )
