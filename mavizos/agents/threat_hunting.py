"""Threat Hunting Agent — proactive anomaly detection."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult
from mavizos.models.workflow import InvestigationContext


class ThreatHuntingAgent(BaseAgent):
    """Proactive hunting for anomalies, persistence, lateral movement."""

    name = "threat_hunting"
    description = "Proactive threat hunting, anomaly detection"

    async def process(self, context: InvestigationContext) -> AgentResult:
        findings: list[str] = []
        hunt_queries: list[str] = []

        hosts = {a.host for a in context.alerts if a.host}
        users = {a.user for a in context.alerts if a.user}

        for host in hosts:
            hunt_queries.append(
                f'HUNT: Rare parent-child process chains on {host} (last 7d)'
            )
            hunt_queries.append(
                f'HUNT: Unusual outbound connections from {host} to non-corporate IPs'
            )

        for user in users:
            hunt_queries.append(
                f'HUNT: Impossible travel / concurrent sessions for {user}'
            )

        if context.mitre_techniques:
            if "T1021" in context.mitre_techniques:
                findings.append("Hunt hypothesis: active lateral movement — expand to adjacent hosts")
            if "T1071" in context.mitre_techniques:
                findings.append("Hunt hypothesis: C2 beaconing — analyze periodic network patterns")

        if len(context.timeline) > 3:
            findings.append(
                f"Anomaly: {len(context.timeline)} correlated events — review for attack progression"
            )

        context.detection_opportunities.extend(hunt_queries[:3])
        return self._success(
            summary=f"Threat hunting: {len(hunt_queries)} hunt query(ies) proposed",
            findings=findings or ["No active hunt hypotheses — baseline monitoring recommended"],
            artifacts={"hunt_queries": hunt_queries},
            confidence=0.55,
        )
