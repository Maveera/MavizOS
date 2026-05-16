"""Investigation Agent — telemetry correlation and timelines."""

from datetime import datetime, timedelta

from mavizos.agents.base import BaseAgent
from mavizos.integrations.mock import MockSIEMAdapter
from mavizos.models.agent_result import AgentResult
from mavizos.models.timeline import TimelineEvent
from mavizos.models.workflow import InvestigationContext


class InvestigationAgent(BaseAgent):
    """Correlate telemetry, build timelines, identify lateral movement."""

    name = "investigation"
    description = "Telemetry correlation, timelines, root cause analysis"

    def __init__(self) -> None:
        self._siem = MockSIEMAdapter()

    async def process(self, context: InvestigationContext) -> AgentResult:
        await self._siem.connect()
        findings: list[str] = []
        hosts = {a.host for a in context.alerts if a.host}

        query_parts = []
        for alert in context.alerts:
            if alert.host:
                query_parts.append(f'host="{alert.host}"')
            if alert.user:
                query_parts.append(f'user="{alert.user}"')

        query = " OR ".join(query_parts) if query_parts else "severity>=medium"
        result = await self._siem.search_events(query, time_range_hours=48)
        events = result.data.get("events", [])

        for evt in events:
            ts = datetime.fromisoformat(evt["timestamp"].replace("Z", ""))
            timeline_evt = TimelineEvent(
                timestamp=ts,
                source=evt.get("source", "siem"),
                event_type=evt.get("event_type", "unknown"),
                description=self._describe_event(evt),
                actor=evt.get("user"),
                target=evt.get("dest_ip") or evt.get("host"),
                raw_data=evt,
            )
            context.timeline.append(timeline_evt)
            if evt.get("host") and evt["host"] not in context.affected_assets:
                context.affected_assets.append(evt["host"])

        for host in hosts:
            if host and host not in context.affected_assets:
                context.affected_assets.append(host)

        if len(events) >= 2:
            findings.append(
                f"Correlated {len(events)} events across {len(context.affected_assets)} asset(s)"
            )
            if any(e.get("event_type") == "network_connection" for e in events):
                findings.append("Potential outbound C2 communication observed (simulated telemetry)")
        else:
            findings.append("Limited telemetry correlation — expand query scope")

        context.timeline.sort(key=lambda e: e.timestamp)
        return self._success(
            summary=f"Investigation: {len(context.timeline)} timeline events",
            findings=findings,
            artifacts={"event_count": len(events), "simulated": result.simulated},
            confidence=0.65 if events else 0.4,
        )

    def _describe_event(self, evt: dict) -> str:
        et = evt.get("event_type", "event")
        if et == "process_create":
            return f"Process created: {evt.get('process')} by {evt.get('user')} on {evt.get('host')}"
        if et == "network_connection":
            return f"Network connection to {evt.get('dest_ip')}:{evt.get('dest_port')}"
        return f"{et} on {evt.get('host', 'unknown')}"
