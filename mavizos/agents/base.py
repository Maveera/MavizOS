"""Base agent interface for all MavizOS agents."""

from abc import ABC, abstractmethod

from mavizos.models.agent_result import AgentResult
from mavizos.models.workflow import InvestigationContext


class BaseAgent(ABC):
    """Abstract base for specialized SOC agents."""

    name: str = "base_agent"
    description: str = ""

    @abstractmethod
    async def process(self, context: InvestigationContext) -> AgentResult:
        """Execute agent logic against investigation context."""

    def _success(
        self,
        summary: str,
        findings: list[str] | None = None,
        artifacts: dict | None = None,
        confidence: float = 0.7,
    ) -> AgentResult:
        """Build a successful AgentResult."""
        return AgentResult(
            agent_name=self.name,
            summary=summary,
            findings=findings or [],
            artifacts=artifacts or {},
            confidence=confidence,
        )
