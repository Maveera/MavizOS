"""10-step investigation workflow pipeline."""

import logging
from typing import TYPE_CHECKING

from mavizos.models.workflow import InvestigationContext, WorkflowStep

if TYPE_CHECKING:
    from mavizos.orchestrator.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

# 10-step investigation pipeline with agent mapping
INVESTIGATION_PIPELINE: list[tuple[str, str]] = [
    (WorkflowStep.INTAKE, "intake"),
    (WorkflowStep.TRIAGE, "alert_triage"),
    (WorkflowStep.ENRICHMENT, "threat_intel"),
    (WorkflowStep.TELEMETRY_CORRELATION, "investigation"),
    (WorkflowStep.MALWARE_ANALYSIS, "malware_analysis"),
    (WorkflowStep.ATTACK_MAPPING, "mitre_attack"),
    (WorkflowStep.THREAT_HUNTING, "threat_hunting"),
    (WorkflowStep.COMPLIANCE_CHECK, "compliance"),
    (WorkflowStep.REMEDIATION_PLANNING, "soar_automation"),
    (WorkflowStep.REPORTING, "reporting"),
    (WorkflowStep.MEMORY_SYNC, "memory"),
]

# Conditional agents run when relevant
CONDITIONAL_AGENTS = [
    ("email_security", lambda ctx: any(
        a.raw_data.get("email_subject") or a.raw_data.get("sender")
        for a in ctx.alerts
    )),
    ("cloud_security", lambda ctx: any(
        a.raw_data.get("cloud_provider") or a.raw_data.get("aws_event")
        for a in ctx.alerts
    )),
]


class InvestigationWorkflow:
    """Orchestrated 10-step investigation pipeline."""

    def __init__(self, orchestrator: "Orchestrator") -> None:
        self._orchestrator = orchestrator

    async def execute(self, context: InvestigationContext) -> InvestigationContext:
        """Execute full investigation workflow."""
        logger.info("Starting investigation %s", context.incident_id)

        for step_name, agent_name in INVESTIGATION_PIPELINE:
            if agent_name == "intake":
                self._intake(context)
                continue
            logger.info("Step %s: running agent %s", step_name, agent_name)
            await self._orchestrator.run_agent(agent_name, context)

        for agent_name, condition in CONDITIONAL_AGENTS:
            if condition(context):
                logger.info("Conditional agent: %s", agent_name)
                await self._orchestrator.run_agent(agent_name, context)

        return context

    def _intake(self, context: InvestigationContext) -> None:
        """Step 1: Intake — normalize alert data into context."""
        for alert in context.alerts:
            if alert.host and alert.host not in context.affected_assets:
                context.affected_assets.append(alert.host)
            if alert.user:
                context.analyst_notes.append(f"Primary user: {alert.user}")
        context.references.append("MavizOS Investigation Workflow v1.0")
        context.metadata["pipeline_steps"] = len(INVESTIGATION_PIPELINE)
