"""Agent service registry."""

from bootguardai.orchestrator.orchestrator import Orchestrator


class AgentRegistry:
    def __init__(self, orchestrator: Orchestrator) -> None:
        self._orchestrator = orchestrator
        self._services: list[str] = []

    def register_all(self) -> None:
        self._services = [a["name"] for a in self._orchestrator.list_agents()]

    def list_services(self) -> list[str]:
        return list(self._services)
