"""Abstract integration adapter interfaces."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class IntegrationResult(BaseModel):
    """Normalized integration response."""

    success: bool
    data: dict[str, Any] = {}
    errors: list[str] = []
    simulated: bool = False


class IntegrationAdapter(ABC):
    """Base class for all vendor integrations."""

    vendor: str = "unknown"

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to external system."""

    @abstractmethod
    async def health_check(self) -> IntegrationResult:
        """Verify integration connectivity."""


class SIEMAdapter(IntegrationAdapter):
    """SIEM platform adapter interface."""

    @abstractmethod
    async def search_events(
        self,
        query: str,
        time_range_hours: int = 24,
    ) -> IntegrationResult:
        """Execute SIEM search query."""

    @abstractmethod
    async def get_alert(self, alert_id: str) -> IntegrationResult:
        """Fetch alert by ID."""


class EDRAdapter(IntegrationAdapter):
    """EDR platform adapter interface."""

    @abstractmethod
    async def get_host_details(self, hostname: str) -> IntegrationResult:
        """Retrieve host telemetry."""

    @abstractmethod
    async def isolate_host(self, hostname: str) -> IntegrationResult:
        """Request host isolation (requires approval)."""


class ThreatIntelAdapter(IntegrationAdapter):
    """Threat intelligence feed adapter interface."""

    @abstractmethod
    async def enrich_ip(self, ip: str) -> IntegrationResult:
        """Enrich IP address."""

    @abstractmethod
    async def enrich_hash(self, file_hash: str) -> IntegrationResult:
        """Enrich file hash."""

    @abstractmethod
    async def enrich_domain(self, domain: str) -> IntegrationResult:
        """Enrich domain."""


class SOARAdapter(IntegrationAdapter):
    """SOAR platform adapter interface."""

    @abstractmethod
    async def execute_playbook(
        self,
        playbook_name: str,
        inputs: dict[str, Any],
    ) -> IntegrationResult:
        """Execute SOAR playbook."""


class TicketingAdapter(IntegrationAdapter):
    """Ticketing system adapter interface."""

    @abstractmethod
    async def create_ticket(
        self,
        title: str,
        description: str,
        priority: str,
    ) -> IntegrationResult:
        """Create incident ticket."""


class CommsAdapter(IntegrationAdapter):
    """Communications platform adapter interface."""

    @abstractmethod
    async def send_notification(
        self,
        channel: str,
        message: str,
    ) -> IntegrationResult:
        """Send notification to channel."""


class CloudAdapter(IntegrationAdapter):
    """Cloud platform adapter interface."""

    @abstractmethod
    async def query_logs(
        self,
        service: str,
        filter_expr: str,
        hours: int = 24,
    ) -> IntegrationResult:
        """Query cloud audit/activity logs."""
