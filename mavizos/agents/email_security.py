"""Email Security Agent — phishing, spoofing, attachments."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult, AgentStatus
from mavizos.models.alert import AlertSource
from mavizos.models.workflow import InvestigationContext

PHISHING_INDICATORS = {"phish", "spoof", "credential", "urgent", "invoice", "wire transfer"}


class EmailSecurityAgent(BaseAgent):
    """Analyze email-related alerts for phishing and abuse."""

    name = "email_security"
    description = "Phishing, attachments, spoofing, URL analysis"

    async def process(self, context: InvestigationContext) -> AgentResult:
        email_alerts = [a for a in context.alerts if a.source == AlertSource.EMAIL]
        if not email_alerts:
            # Also check raw_data for email indicators
            email_alerts = [
                a for a in context.alerts
                if a.raw_data.get("email_subject") or a.raw_data.get("sender")
            ]

        if not email_alerts:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SKIPPED,
                summary="No email-related alerts in context",
            )

        findings: list[str] = []
        for alert in email_alerts:
            subject = str(alert.raw_data.get("email_subject", alert.title)).lower()
            sender = alert.raw_data.get("sender", "unknown")
            indicators = [kw for kw in PHISHING_INDICATORS if kw in subject]
            if indicators:
                findings.append(
                    f"Phishing indicators in email from {sender}: {', '.join(indicators)}"
                )
                context.recommended_actions.append(f"Quarantine emails from {sender} (requires approval)")
            if alert.raw_data.get("attachment_hash"):
                findings.append(
                    f"Suspicious attachment hash: {alert.raw_data['attachment_hash'][:16]}..."
                )

        return self._success(
            summary=f"Email security: analyzed {len(email_alerts)} email alert(s)",
            findings=findings or ["No definitive phishing indicators identified"],
            confidence=0.65 if findings else 0.4,
        )
