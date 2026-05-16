"""Systemd-like service registry for SOC agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mavizos.agents.base import BaseAgent


class ServiceState(str, Enum):
    """Agent service lifecycle state."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class ServiceRecord:
    """Registered agent service."""

    name: str
    description: str
    state: ServiceState = ServiceState.STOPPED
    pid: int | None = None
    started_at: datetime | None = None
    last_health_check: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "description": self.description,
            "state": self.state.value,
            "pid": str(self.pid) if self.pid else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


class ServiceRegistry:
    """Maps agent names to OS services with health state."""

    def __init__(self) -> None:
        self._services: dict[str, ServiceRecord] = {}

    def register_from_agents(self, agents: dict[str, BaseAgent]) -> None:
        """Build service table from orchestrator agents."""
        for name, agent in agents.items():
            self._services[name] = ServiceRecord(
                name=name,
                description=agent.description,
                state=ServiceState.STOPPED,
            )

    def start_all(self) -> list[ServiceRecord]:
        """Mark all services as running (boot sequence)."""
        now = datetime.now(timezone.utc)
        started: list[ServiceRecord] = []
        for idx, svc in enumerate(self._services.values(), start=100):
            svc.state = ServiceState.RUNNING
            svc.pid = idx
            svc.started_at = now
            svc.last_health_check = now
            started.append(svc)
        return started

    def health_check(self) -> list[ServiceRecord]:
        """Refresh health timestamps; all registered agents are healthy in demo."""
        now = datetime.now(timezone.utc)
        for svc in self._services.values():
            if svc.state == ServiceState.RUNNING:
                svc.last_health_check = now
            elif svc.state == ServiceState.STOPPED:
                svc.state = ServiceState.DEGRADED
        return list(self._services.values())

    def get(self, name: str) -> ServiceRecord | None:
        return self._services.get(name)

    def list_all(self) -> list[ServiceRecord]:
        return sorted(self._services.values(), key=lambda s: s.name)

    def running_count(self) -> int:
        return sum(1 for s in self._services.values() if s.state == ServiceState.RUNNING)
