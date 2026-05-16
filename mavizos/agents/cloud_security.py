"""Cloud Security Agent — AWS/Azure/GCP log analysis."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult, AgentStatus
from mavizos.models.alert import AlertSource
from mavizos.models.workflow import InvestigationContext


class CloudSecurityAgent(BaseAgent):
    """Analyze cloud security alerts: IAM abuse, misconfigurations."""

    name = "cloud_security"
    description = "Cloud log analysis, IAM abuse, misconfiguration detection"

    async def process(self, context: InvestigationContext) -> AgentResult:
        cloud_alerts = [a for a in context.alerts if a.source == AlertSource.CLOUD]
        cloud_alerts.extend(
            a for a in context.alerts
            if a.raw_data.get("cloud_provider") or a.raw_data.get("aws_event")
        )

        if not cloud_alerts:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SKIPPED,
                summary="No cloud-related alerts in context",
            )

        findings: list[str] = []
        for alert in cloud_alerts:
            provider = alert.raw_data.get("cloud_provider", "unknown")
            event = alert.raw_data.get("event_name", alert.rule_name or "unknown")
            if "AssumeRole" in str(event) or "CreateAccessKey" in str(event):
                findings.append(f"[{provider}] Potential IAM abuse: {event}")
                context.recommended_actions.append(
                    f"Review IAM activity for {alert.user or 'unknown principal'}"
                )
            if alert.raw_data.get("public_bucket"):
                findings.append(f"[{provider}] S3/public storage misconfiguration detected")
                context.mitre_techniques.append("T1530")  # Data from Cloud Storage

        return self._success(
            summary=f"Cloud security: analyzed {len(cloud_alerts)} cloud alert(s)",
            findings=findings or ["No critical cloud misconfigurations identified"],
            confidence=0.6 if findings else 0.4,
        )
