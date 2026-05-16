"""Mock telemetry integrations — all data labeled simulated."""

from typing import Any

from bootguardai.integrations.base import TelemetryAdapter


class MockWindowsEventLog(TelemetryAdapter):
    async def fetch_boot_events(self, host: str, limit: int = 50) -> list[dict[str, Any]]:
        return [
            {
                "event_id": 12,
                "source": "Microsoft-Windows-Kernel-Boot",
                "message": "Boot start",
                "host": host,
                "simulated": True,
            },
            {
                "event_id": 153,
                "source": "Microsoft-Windows-Kernel-Boot",
                "message": "Secure Boot policy",
                "host": host,
                "simulated": True,
            },
        ][:limit]


class MockJournalctl(TelemetryAdapter):
    async def fetch_boot_events(self, host: str, limit: int = 50) -> list[dict[str, Any]]:
        return [
            {"unit": "systemd", "message": "Reached target Basic System", "simulated": True},
            {"unit": "grub", "message": "GRUB configuration loaded", "simulated": True},
        ][:limit]


class MockEDRStub:
    async def boot_telemetry(self, host: str) -> dict[str, Any]:
        return {"host": host, "boot_integrity": "unknown", "simulated": True}


class MockSIEMStub:
    async def query(self, query: str) -> list[dict[str, Any]]:
        return [{"query": query, "hits": 0, "simulated": True}]
