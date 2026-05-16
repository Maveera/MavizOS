"""Reporting Agent — 12-section boot analysis report."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.boot_report import BootAnalysisReport
from bootguardai.models.workflow import BootAnalysisContext


class ReportingAgent(BaseAgent):
    name = "reporting"
    description = "Generate 12-section boot forensic reports"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        confidences = [r.confidence for r in context.agent_results.values() if r.confidence > 0]
        avg = sum(confidences) / len(confidences) if confidences else 0.5
        risk_count = len(context.detected_risks)

        report = BootAnalysisReport(
            analysis_id=context.analysis_id,
            os_type=context.os_type,
            simulated=True,
            executive_summary=self._executive(context, risk_count),
            boot_process_stage=context.boot_stages,
            technical_findings=context.technical_findings[:25],
            loaded_components=context.loaded_components,
            detected_risks=context.detected_risks,
            persistence_indicators=context.persistence_indicators[:20],
            kernel_analysis=context.kernel_findings[:20],
            bootloader_analysis=context.bootloader_findings[:20],
            security_assessment=self._security_assessment(risk_count, context),
            recommended_actions=context.recommended_actions,
            detection_opportunities=context.detection_opportunities,
            soc_notes=context.soc_notes,
        )
        context.report = report
        return self._success(
            summary="12-section boot analysis report generated",
            findings=[f"Risks: {risk_count}", f"Avg confidence: {avg:.2f}"],
            artifacts={"report": report.model_dump(mode="json")},
            confidence=avg,
        )

    def _executive(self, context: BootAnalysisContext, risks: int) -> str:
        return (
            f"BootGuardAI analysis {context.analysis_id[:8]} for {context.os_type.value} "
            f"({context.boot_mode.value}). {risks} risk indicator(s). "
            "All telemetry labeled simulated unless live collectors enabled. "
            "Destructive remediation requires analyst approval."
        )

    def _security_assessment(self, risks: int, context: BootAnalysisContext) -> str:
        if risks >= 3:
            return "HIGH — multiple boot integrity concerns"
        if risks >= 1:
            return "ELEVATED — boot-level anomalies require validation"
        return "LOW — no critical boot threats in supplied simulated data"
