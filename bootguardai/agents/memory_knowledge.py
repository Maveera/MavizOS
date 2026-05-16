"""Memory/Knowledge Agent — historical boot findings."""

from bootguardai.agents.base import BaseAgent
from bootguardai.memory.store import MemoryStore
from bootguardai.models.workflow import BootAnalysisContext


class MemoryKnowledgeAgent(BaseAgent):
    name = "memory_knowledge"
    description = "Historical boot findings and analyst feedback"

    def __init__(self, memory_store: MemoryStore | None = None) -> None:
        self._memory = memory_store or MemoryStore()

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        summary = (
            f"{context.os_type.value} boot analysis — "
            f"{len(context.detected_risks)} risk(s)"
        )
        self._memory.add_finding(context.analysis_id, summary, context.os_type.value)
        prior = self._memory.recent_findings(5)
        findings = [f"Stored finding for {context.analysis_id[:8]}"]
        if prior:
            findings.append(f"Prior analyses in memory: {len(prior)}")
        return self._success(
            summary="Memory updated with boot analysis summary",
            findings=findings,
            artifacts={"recent": prior},
            confidence=0.8,
        )
