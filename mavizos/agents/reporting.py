"""Reporting Agent — executive summaries and structured reports."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult
from mavizos.models.alert import AlertSeverity
from mavizos.models.investigation_report import InvestigationReport
from mavizos.models.workflow import InvestigationContext


class ReportingAgent(BaseAgent):
    """Generate 14-section investigation reports."""

    name = "reporting"
    description = "Executive summaries, RCA, analyst reports"

    async def process(self, context: InvestigationContext) -> AgentResult:
        severity = AlertSeverity.MEDIUM
        for alert in context.alerts:
            if alert.severity in (AlertSeverity.CRITICAL, AlertSeverity.HIGH):
                severity = alert.severity
                break

        confidences = [
            r.confidence for r in context.agent_results.values() if r.confidence > 0
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        technical_findings: list[str] = []
        for result in context.agent_results.values():
            technical_findings.extend(result.findings[:5])

        mitre_mapping = []
        for tid in context.mitre_techniques:
            mitre_mapping.append({"technique_id": tid, "source": "investigation"})

        rca_parts = []
        if context.alerts:
            rca_parts.append(f"Triggered by: {context.alerts[0].title}")
        if context.mitre_techniques:
            rca_parts.append(f"Attack techniques: {', '.join(context.mitre_techniques)}")
        if context.iocs:
            rca_parts.append(f"Key IOCs: {len(context.iocs)} indicator(s) enriched (simulated)")

        report = InvestigationReport(
            incident_id=context.incident_id,
            executive_summary=self._executive_summary(context, severity),
            severity=severity,
            confidence=round(avg_confidence, 2),
            technical_findings=technical_findings[:20],
            timeline=context.timeline,
            affected_assets=context.affected_assets,
            iocs=context.iocs,
            mitre_mapping=mitre_mapping,
            root_cause_analysis=" | ".join(rca_parts) if rca_parts else "Insufficient data for RCA",
            recommended_actions=context.recommended_actions,
            automated_actions_taken=context.automated_actions,
            detection_opportunities=context.detection_opportunities,
            analyst_notes=context.analyst_notes,
            references=context.references,
        )
        context.report = report

        return self._success(
            summary="Investigation report generated (14 sections)",
            findings=[f"Report confidence: {avg_confidence:.2f}", f"Severity: {severity.value}"],
            artifacts={"report": report.model_dump(mode="json")},
            confidence=avg_confidence,
        )

    def _executive_summary(self, context: InvestigationContext, severity: AlertSeverity) -> str:
        alert_count = len(context.alerts)
        asset_count = len(context.affected_assets)
        technique_count = len(context.mitre_techniques)
        return (
            f"MavizOS investigated incident {context.incident_id[:8]} involving "
            f"{alert_count} alert(s) across {asset_count} asset(s). "
            f"Severity assessed as {severity.value}. "
            f"{technique_count} MITRE ATT&CK technique(s) identified. "
            "Threat intel enrichment performed in demo/simulated mode. "
            "Destructive remediation actions require analyst approval."
        )
