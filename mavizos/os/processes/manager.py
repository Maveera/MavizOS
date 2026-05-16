"""PID tracking for running investigations and hunts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ProcessState(str, Enum):
    """OS process state."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessRecord:
    """A tracked MavizOS workload."""

    pid: int
    name: str
    state: ProcessState = ProcessState.PENDING
    incident_id: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None
    result_summary: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "name": self.name,
            "state": self.state.value,
            "incident_id": self.incident_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "result_summary": self.result_summary,
        }


class ProcessManager:
    """Maintains PID table for async SOC operations."""

    def __init__(self) -> None:
        self._next_pid = 2000
        self._processes: dict[int, ProcessRecord] = {}

    def create(
        self,
        name: str,
        *,
        incident_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProcessRecord:
        pid = self._next_pid
        self._next_pid += 1
        proc = ProcessRecord(
            pid=pid,
            name=name,
            incident_id=incident_id,
            metadata=metadata or {},
        )
        self._processes[pid] = proc
        return proc

    def get(self, pid: int) -> ProcessRecord | None:
        return self._processes.get(pid)

    def list_all(self, active_only: bool = False) -> list[ProcessRecord]:
        procs = list(self._processes.values())
        if active_only:
            procs = [p for p in procs if p.state in (ProcessState.PENDING, ProcessState.RUNNING)]
        return sorted(procs, key=lambda p: p.pid, reverse=True)

    def set_running(self, pid: int) -> None:
        if proc := self._processes.get(pid):
            proc.state = ProcessState.RUNNING

    def set_completed(self, pid: int, result: Any = None) -> None:
        if proc := self._processes.get(pid):
            proc.state = ProcessState.COMPLETED
            proc.ended_at = datetime.now(timezone.utc)
            if isinstance(result, dict):
                proc.incident_id = result.get("incident_id") or proc.incident_id
                proc.result_summary = f"status={result.get('status', 'done')}"
            else:
                proc.result_summary = "completed"

    def set_failed(self, pid: int, error: str) -> None:
        if proc := self._processes.get(pid):
            proc.state = ProcessState.FAILED
            proc.ended_at = datetime.now(timezone.utc)
            proc.result_summary = error[:200]
