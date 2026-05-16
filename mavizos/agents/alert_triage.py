"""Alert Triage Agent — FP identification, prioritization, classification."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult, AgentStatus
from mavizos.models.alert import AlertSeverity
from mavizos.models.workflow import InvestigationContext

# Heuristic FP indicators (demo logic)
FP_KEYWORDS = {"test", "scan", "benign", "authorized", "pentest"}
HIGH_RISK_KEYWORDS = {"ransomware", "lateral", "credential", "exfil", "c2", "mimikatz"}


class AlertTriageAgent(BaseAgent):
    """Triage SIEM/EDR alerts: severity, classification, FP scoring."""

    name = "alert_triage"
    description = "SIEM alert triage, false positive identification, prioritization"

    async def process(self, context: InvestigationContext) -> AgentResult:
        findings: list[str] = []
        max_priority = 0
        classifications: list[str] = []

        for alert in context.alerts:
            text = f"{alert.title} {alert.description}".lower()
            fp_score = sum(1 for kw in FP_KEYWORDS if kw in text) * 0.25
            risk_score = sum(2 for kw in HIGH_RISK_KEYWORDS if kw in text)

            if alert.process and "powershell" in (alert.process or "").lower():
                risk_score += 3
            if alert.file_hash and alert.file_hash.lower().startswith("a1b2c3"):
                risk_score += 5

            alert.false_positive_score = min(fp_score, 1.0)
            priority = max(0, min(100, risk_score * 10 - int(fp_score * 30)))
            alert.priority_score = priority
            max_priority = max(max_priority, priority)

            if fp_score >= 0.5:
                alert.classification = "likely_false_positive"
                findings.append(f"Alert {alert.id[:8]}: likely FP (score={fp_score:.2f})")
            elif risk_score >= 3:
                alert.classification = "suspicious_activity"
                alert.severity = AlertSeverity.HIGH
                classifications.append("suspicious_activity")
                findings.append(f"Alert {alert.id[:8]}: elevated — {alert.title}")
            else:
                alert.classification = "requires_investigation"
                findings.append(f"Alert {alert.id[:8]}: requires investigation")

        if not context.alerts:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SKIPPED,
                summary="No alerts to triage",
            )

        overall = "likely_false_positive" if max_priority < 20 else "suspicious_activity"
        return self._success(
            summary=f"Triage complete: {len(context.alerts)} alert(s), priority={max_priority}",
            findings=findings,
            artifacts={"max_priority": max_priority, "classification": overall},
            confidence=0.75 if max_priority >= 20 else 0.5,
        )
