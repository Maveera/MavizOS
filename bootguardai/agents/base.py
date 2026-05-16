"""Base agent interface."""

from abc import ABC, abstractmethod

from bootguardai.models.agent_result import AgentResult
from bootguardai.models.workflow import BootAnalysisContext


class BaseAgent(ABC):
    name: str = "base_agent"
    description: str = ""

    @abstractmethod
    async def process(self, context: BootAnalysisContext) -> AgentResult:
        ...

    def _success(
        self,
        summary: str,
        findings: list[str] | None = None,
        artifacts: dict | None = None,
        confidence: float = 0.7,
    ) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            summary=summary,
            findings=findings or [],
            artifacts=artifacts or {},
            confidence=confidence,
            simulated=True,
        )
