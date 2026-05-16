"""Memory Agent — organizational knowledge and historical context."""

from mavizos.agents.base import BaseAgent
from mavizos.memory.store import MemoryStore
from mavizos.models.agent_result import AgentResult
from mavizos.models.workflow import InvestigationContext


class MemoryAgent(BaseAgent):
    """Store and retrieve organizational security knowledge."""

    name = "memory"
    description = "Historical incidents, analyst decisions, recurring threats"

    def __init__(self, memory_store: MemoryStore | None = None) -> None:
        self._memory = memory_store or MemoryStore()

    async def process(self, context: InvestigationContext) -> AgentResult:
        findings: list[str] = []

        # Store current investigation summary
        self._memory.store(
            record_id=f"incident:{context.incident_id}",
            record_type="incident",
            content={
                "incident_id": context.incident_id,
                "alert_count": len(context.alerts),
                "mitre_techniques": context.mitre_techniques,
                "affected_assets": context.affected_assets,
            },
            tags=["investigation"] + context.mitre_techniques,
        )
        findings.append(f"Stored incident {context.incident_id[:8]} in organizational memory")

        # Search for related historical incidents
        related = []
        for technique in context.mitre_techniques:
            hits = self._memory.search(record_type="incident", tags=[technique], limit=5)
            for hit in hits:
                if hit.id != f"incident:{context.incident_id}":
                    related.append(hit.id)

        if related:
            findings.append(f"Found {len(related)} related historical incident(s) by MITRE technique")
            context.analyst_notes.append(
                f"Historical context: {len(related)} prior incident(s) with similar techniques"
            )
        else:
            findings.append("No matching historical incidents in memory store")

        return self._success(
            summary="Memory sync complete",
            findings=findings,
            artifacts={"related_incidents": related},
            confidence=0.7,
        )
