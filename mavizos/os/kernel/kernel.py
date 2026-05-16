"""MavizOS kernel — wraps orchestrator and OS subsystems."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from mavizos import __version__
from mavizos.models.alert import Alert
from mavizos.orchestrator.orchestrator import Orchestrator
from mavizos.os.config.loader import OSConfig, load_os_config
from mavizos.os.filesystem.vfs import VirtualFilesystem
from mavizos.os.kernel.event_bus import EventBus
from mavizos.os.kernel.registry import ServiceRegistry
from mavizos.os.kernel.scheduler import Scheduler
from mavizos.os.processes.manager import ProcessManager
from mavizos.os.services.manager import ServiceManager

logger = logging.getLogger(__name__)

_kernel: Kernel | None = None


class Kernel:
    """
    MavizOS kernel.

    Wraps the existing orchestrator with OS metaphors: services, VFS,
    process table, scheduler, and event bus.
    """

    def __init__(self, config: OSConfig | None = None) -> None:
        self.config = config or load_os_config()
        self.version = __version__
        self.orchestrator = Orchestrator()
        self.event_bus = EventBus()
        self.services_registry = ServiceRegistry()
        self.process_manager = ProcessManager()
        self.scheduler = Scheduler(self.process_manager)
        self.vfs = VirtualFilesystem(self.config.vfs_root)
        self.service_manager = ServiceManager(self.services_registry)
        self._booted = False

    @property
    def booted(self) -> bool:
        return self._booted

    def boot(self, *, verbose: bool = True) -> None:
        """Run full boot sequence."""
        from mavizos.os.kernel.boot import run_boot_sequence

        if self._booted:
            return
        run_boot_sequence(self, verbose=verbose)

    async def triage_alert(self, alert: Alert) -> dict[str, Any]:
        """Triage with VFS persistence."""
        self.event_bus.publish("alert.triage", {"alert_id": alert.id})
        result = await self.orchestrator.triage_alert(alert)
        self.vfs.write_json(f"var/logs/triage_{alert.id[:8]}.json", result)
        if result.get("iocs"):
            self.vfs.persist_iocs(alert.id, result["iocs"])
        self.vfs.append_log(f"Triage complete: {alert.title}", source="alert_triage")
        return result

    async def investigate(self, alerts: list[Alert]) -> dict[str, Any]:
        """Investigation with VFS + process tracking."""
        proc = self.process_manager.create("investigate", metadata={"alerts": len(alerts)})
        self.process_manager.set_running(proc.pid)
        self.event_bus.publish("investigation.start", {"pid": proc.pid})

        try:
            result = await self.orchestrator.investigate(alerts)
            incident_id = result["incident_id"]
            proc.incident_id = incident_id
            self.process_manager.set_completed(proc.pid, result)

            incident = self.orchestrator.get_incident(incident_id)
            if incident:
                self.vfs.persist_incident(incident_id, incident.model_dump(mode="json"))
            if result.get("report"):
                self.vfs.persist_report(incident_id, result["report"])
                iocs = result["report"].get("iocs", [])
                if iocs:
                    self.vfs.persist_iocs(incident_id, iocs)
            self.vfs.append_log(f"Investigation {incident_id} completed", source="workflow")
            self.event_bus.publish("investigation.complete", {"incident_id": incident_id, "pid": proc.pid})
            return result
        except Exception as exc:
            self.process_manager.set_failed(proc.pid, str(exc))
            raise

    async def hunt(self, hypothesis: str, context_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Threat hunt with process tracking."""
        proc = self.process_manager.create("hunt", metadata={"hypothesis": hypothesis})
        self.process_manager.set_running(proc.pid)
        result = await self.orchestrator.hunt(hypothesis, context_data)
        self.process_manager.set_completed(proc.pid, result)
        self.vfs.write_json(f"var/logs/hunt_{proc.pid}.json", result)
        self.vfs.append_log(f"Hunt: {hypothesis[:60]}", source="threat_hunting")
        self.event_bus.publish("hunt.complete", {"pid": proc.pid})
        return result

    def shutdown(self) -> None:
        """Graceful kernel shutdown."""
        self.event_bus.publish("system.shutdown", {})
        self.vfs.append_log("System shutdown", source="kernel")
        self._booted = False
        logger.info("MavizOS kernel shutdown")


@lru_cache
def get_kernel() -> Kernel:
    """Return singleton kernel instance."""
    global _kernel
    if _kernel is None:
        _kernel = Kernel()
    return _kernel


def reset_kernel() -> None:
    """Reset kernel singleton (testing)."""
    global _kernel
    get_kernel.cache_clear()
    load_os_config.cache_clear()
    _kernel = None
