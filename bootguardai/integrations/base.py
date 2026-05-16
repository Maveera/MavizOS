"""Integration adapter interfaces."""

from abc import ABC, abstractmethod
from typing import Any


class TelemetryAdapter(ABC):
    @abstractmethod
    async def fetch_boot_events(self, host: str, limit: int = 50) -> list[dict[str, Any]]:
        ...
