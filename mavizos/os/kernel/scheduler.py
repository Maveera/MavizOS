"""Async task scheduler — wraps orchestrator jobs as OS processes."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable

from mavizos.os.processes.manager import ProcessManager, ProcessRecord

logger = logging.getLogger(__name__)


class Scheduler:
    """Schedules background work and tracks PIDs via ProcessManager."""

    def __init__(self, process_manager: ProcessManager) -> None:
        self._processes = process_manager
        self._tasks: dict[int, asyncio.Task[Any]] = {}

    def spawn(
        self,
        name: str,
        coro_factory: Callable[[], Awaitable[Any]],
        *,
        incident_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProcessRecord:
        """Start async job and return process record."""
        proc = self._processes.create(name, incident_id=incident_id, metadata=metadata)

        async def _wrapper() -> Any:
            self._processes.set_running(proc.pid)
            try:
                result = await coro_factory()
                self._processes.set_completed(proc.pid, result)
                return result
            except Exception as exc:
                logger.exception("Process %s failed", proc.pid)
                self._processes.set_failed(proc.pid, str(exc))
                raise

        task = asyncio.create_task(_wrapper())
        self._tasks[proc.pid] = task
        return proc

    async def wait(self, pid: int, timeout: float | None = None) -> Any:
        """Await process completion."""
        task = self._tasks.get(pid)
        if not task:
            raise KeyError(f"No task for PID {pid}")
        if timeout:
            return await asyncio.wait_for(task, timeout=timeout)
        return await task

    def cancel(self, pid: int) -> bool:
        """Cancel running process."""
        task = self._tasks.pop(pid, None)
        if task and not task.done():
            task.cancel()
            self._processes.set_failed(pid, "cancelled")
            return True
        return False
