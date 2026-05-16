"""Central orchestrator — agent registry, task routing, workflow execution."""

import logging
from typing import Any
from uuid import uuid4

from mavizos.agents import AGENT_REGISTRY
from mavizos.agents.base import BaseAgent
from mavizos.agents.soar_automation import SOARAutomationAgent
from mavizos.memory.store import MemoryStore
from mavizos.models.agent_result import AgentResult, AgentStatus
from mavizos.models.alert import Alert
from mavizos.models.incident import Incident, IncidentStatus
from mavizos.models.workflow import InvestigationContext
from mavizos.security.approval import ApprovalGate
from mavizos.security.audit import AuditLogger
from mavizos.workflows.investigation import InvestigationWorkflow

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Central orchestrator for MavizOS multi-agent operations.

    Responsibilities: task delegation, context sharing, memory sync,
    priority handling, workflow execution, escalation.
    """

    def __init__(self) -> None:
        self.approval_gate = ApprovalGate()
        self.audit_logger = AuditLogger()
        self.memory_store = MemoryStore()
        self._agents: dict[str, BaseAgent] = {}
        self._incidents: dict[str, Incident] = {}
        self._register_agents()

    def _register_agents(self) -> None:
        """Instantiate all registered agents."""
        for name, cls in AGENT_REGISTRY.items():
            if name == "soar_automation":
                self._agents[name] = SOARAutomationAgent(
                    approval_gate=self.approval_gate,
                    audit_logger=self.audit_logger,
                )
            elif name == "memory":
                from mavizos.agents.memory_agent import MemoryAgent

                self._agents[name] = MemoryAgent(memory_store=self.memory_store)
            else:
                self._agents[name] = cls()
        logger.info("Registered %d agents", len(self._agents))

    def list_agents(self) -> list[dict[str, str]]:
        """Return registered agent metadata."""
        return [
            {"name": a.name, "description": a.description}
            for a in self._agents.values()
        ]

    async def run_agent(
        self,
        agent_name: str,
        context: InvestigationContext,
    ) -> AgentResult:
        """Execute a single agent by name."""
        agent = self._agents.get(agent_name)
        if not agent:
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                summary=f"Unknown agent: {agent_name}",
                errors=[f"Agent '{agent_name}' not registered"],
            )
        self.audit_logger.log(
            actor="orchestrator",
            action="agent_start",
            target=agent_name,
            outcome="started",
            incident_id=context.incident_id,
        )
        try:
            result = await agent.process(context)
            context.agent_results[agent_name] = result
            self.audit_logger.log(
                actor="orchestrator",
                action="agent_complete",
                target=agent_name,
                outcome=result.status.value,
                incident_id=context.incident_id,
            )
            return result
        except Exception as exc:
            logger.exception("Agent %s failed", agent_name)
            result = AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                summary=str(exc),
                errors=[str(exc)],
            )
            context.agent_results[agent_name] = result
            return result

    async def triage_alert(self, alert: Alert) -> dict[str, Any]:
        """Triage a single alert."""
        incident_id = str(uuid4())
        context = InvestigationContext(incident_id=incident_id, alerts=[alert])
        result = await self.run_agent("alert_triage", context)
        await self.run_agent("threat_intel", context)
        return {
            "alert_id": alert.id,
            "classification": alert.classification,
            "priority_score": alert.priority_score,
            "false_positive_score": alert.false_positive_score,
            "severity": alert.severity.value,
            "triage": result.model_dump(),
            "iocs": [i.model_dump() for i in context.iocs],
        }

    async def investigate(self, alerts: list[Alert]) -> dict[str, Any]:
        """Run full 10-step investigation workflow."""
        incident_id = str(uuid4())
        incident = Incident(
            id=incident_id,
            title=alerts[0].title if alerts else "Investigation",
            status=IncidentStatus.INVESTIGATING,
            alerts=alerts,
        )
        self._incidents[incident_id] = incident

        context = InvestigationContext(incident_id=incident_id, alerts=alerts, incident=incident)
        workflow = InvestigationWorkflow(self)
        context = await workflow.execute(context)

        if context.report:
            incident.report_id = context.report.incident_id
            incident.affected_assets = context.affected_assets
            incident.iocs = [i.value for i in context.iocs]
            incident.mitre_techniques = context.mitre_techniques
            incident.status = IncidentStatus.CONTAINED
            incident.metadata["confidence"] = context.report.confidence

        return {
            "incident_id": incident_id,
            "status": incident.status.value,
            "agent_results": {k: v.model_dump() for k, v in context.agent_results.items()},
            "report": context.report.model_dump(mode="json") if context.report else None,
            "pending_approvals": [
                r.model_dump() for r in self.approval_gate.list_pending()
            ],
        }

    async def hunt(self, hypothesis: str, context_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run threat hunting agent with custom hypothesis."""
        incident_id = str(uuid4())
        context = InvestigationContext(
            incident_id=incident_id,
            metadata={"hypothesis": hypothesis, **(context_data or {})},
        )
        result = await self.run_agent("threat_hunting", context)
        return {"hypothesis": hypothesis, "result": result.model_dump()}

    async def generate_detection(self, alert: Alert) -> dict[str, Any]:
        """Generate detection rules from alert context."""
        context = InvestigationContext(incident_id=str(uuid4()), alerts=[alert])
        await self.run_agent("alert_triage", context)
        result = await self.run_agent("detection_engineering", context)
        return {"rules": result.artifacts.get("rules", {}), "result": result.model_dump()}

    def get_incident(self, incident_id: str) -> Incident | None:
        """Retrieve incident by ID."""
        return self._incidents.get(incident_id)
