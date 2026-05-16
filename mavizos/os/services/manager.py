"""High-level service manager over kernel registry."""

from __future__ import annotations

from mavizos.os.kernel.registry import ServiceRecord, ServiceRegistry


class ServiceManager:
    """Facade for querying and controlling agent services."""

    def __init__(self, registry: ServiceRegistry) -> None:
        self._registry = registry

    def list_services(self) -> list[ServiceRecord]:
        return self._registry.list_all()

    def status_summary(self) -> dict[str, int | str]:
        services = self._registry.list_all()
        running = self._registry.running_count()
        return {
            "total": len(services),
            "running": running,
            "health": "healthy" if running == len(services) else "degraded",
        }
