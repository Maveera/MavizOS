"""Vendor-specific adapter stubs — implement connect() for production."""

from typing import Any

from mavizos.integrations.base import (
    CloudAdapter,
    CommsAdapter,
    EDRAdapter,
    IntegrationResult,
    SIEMAdapter,
    SOARAdapter,
    ThreatIntelAdapter,
    TicketingAdapter,
)


class _StubAdapter:
    """Shared stub behavior for unimplemented integrations."""

    async def connect(self) -> bool:
        return False

    async def health_check(self) -> IntegrationResult:
        return IntegrationResult(
            success=False,
            errors=[f"{self.vendor} adapter not configured — stub only"],
            simulated=False,
        )


def _not_implemented(method: str, vendor: str) -> IntegrationResult:
    return IntegrationResult(
        success=False,
        errors=[f"{vendor}.{method} not implemented — configure credentials"],
    )


# SIEM stubs
class SplunkAdapter(SIEMAdapter, _StubAdapter):
    vendor = "splunk"

    async def search_events(self, query: str, time_range_hours: int = 24) -> IntegrationResult:
        return _not_implemented("search_events", self.vendor)

    async def get_alert(self, alert_id: str) -> IntegrationResult:
        return _not_implemented("get_alert", self.vendor)


class SentinelAdapter(SIEMAdapter, _StubAdapter):
    vendor = "microsoft_sentinel"

    async def search_events(self, query: str, time_range_hours: int = 24) -> IntegrationResult:
        return _not_implemented("search_events", self.vendor)

    async def get_alert(self, alert_id: str) -> IntegrationResult:
        return _not_implemented("get_alert", self.vendor)


# EDR stubs
class CrowdStrikeAdapter(EDRAdapter, _StubAdapter):
    vendor = "crowdstrike"

    async def get_host_details(self, hostname: str) -> IntegrationResult:
        return _not_implemented("get_host_details", self.vendor)

    async def isolate_host(self, hostname: str) -> IntegrationResult:
        return _not_implemented("isolate_host", self.vendor)


class DefenderAdapter(EDRAdapter, _StubAdapter):
    vendor = "microsoft_defender"

    async def get_host_details(self, hostname: str) -> IntegrationResult:
        return _not_implemented("get_host_details", self.vendor)

    async def isolate_host(self, hostname: str) -> IntegrationResult:
        return _not_implemented("isolate_host", self.vendor)


# SOAR stub
class XSOARAdapter(SOARAdapter, _StubAdapter):
    vendor = "xsoar"

    async def execute_playbook(
        self,
        playbook_name: str,
        inputs: dict[str, Any],
    ) -> IntegrationResult:
        return _not_implemented("execute_playbook", self.vendor)


# Ticketing stub
class JiraAdapter(TicketingAdapter, _StubAdapter):
    vendor = "jira"

    async def create_ticket(
        self,
        title: str,
        description: str,
        priority: str,
    ) -> IntegrationResult:
        return _not_implemented("create_ticket", self.vendor)


# Comms stub
class SlackAdapter(CommsAdapter, _StubAdapter):
    vendor = "slack"

    async def send_notification(self, channel: str, message: str) -> IntegrationResult:
        return _not_implemented("send_notification", self.vendor)


# Cloud stub
class AWSAdapter(CloudAdapter, _StubAdapter):
    vendor = "aws"

    async def query_logs(
        self,
        service: str,
        filter_expr: str,
        hours: int = 24,
    ) -> IntegrationResult:
        return _not_implemented("query_logs", self.vendor)
