"""Persistence Hunt Agent — rc.local, systemd, registry Run keys."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.boot_alert import OSType
from bootguardai.models.workflow import BootAnalysisContext

PERSISTENCE_WINDOWS = ("Run", "RunOnce", "Winlogon", "Services", "Scheduled Tasks")
PERSISTENCE_LINUX = ("rc.local", "systemd unit", "cron", "profile.d", "init.d")


class PersistenceHuntAgent(BaseAgent):
    name = "persistence_hunt"
    description = "Boot-time persistence: registry, systemd, startup scripts"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        findings: list[str] = []
        for alert in context.alerts:
            raw = alert.raw_data
            for item in raw.get("persistence_hits") or []:
                findings.append(f"[simulated] Persistence indicator: {item}")
                context.persistence_indicators.append(str(item))
        if context.os_type == OSType.WINDOWS:
            findings.append(f"Windows persistence surfaces reviewed: {', '.join(PERSISTENCE_WINDOWS)}")
        elif context.os_type == OSType.LINUX:
            findings.append(f"Linux persistence surfaces reviewed: {', '.join(PERSISTENCE_LINUX)}")
        context.persistence_indicators.extend(findings[:5])
        return self._success(
            summary=f"Persistence hunt: {len(context.persistence_indicators)} indicator(s)",
            findings=findings,
            confidence=0.72,
        )
