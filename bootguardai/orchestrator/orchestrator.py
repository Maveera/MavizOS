"""Central BootGuardAI orchestrator."""

import logging
from typing import Any
from uuid import uuid4

from bootguardai.agents import AGENT_REGISTRY
from bootguardai.agents.base import BaseAgent
from bootguardai.agents.memory_knowledge import MemoryKnowledgeAgent
from bootguardai.agents.remediation import RemediationAgent
from bootguardai.memory.store import MemoryStore
from bootguardai.models.agent_result import AgentResult, AgentStatus
from bootguardai.models.boot_alert import BootAlert, OSType
from bootguardai.models.workflow import BootAnalysisContext
from bootguardai.security.approval import ApprovalGate
from bootguardai.security.audit import AuditLogger
from bootguardai.workflows.boot_analysis import BootAnalysisWorkflow

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self) -> None:
        self.approval_gate = ApprovalGate()
        self.audit_logger = AuditLogger()
        self.memory_store = MemoryStore()
        self._agents: dict[str, BaseAgent] = {}
        self._analyses: dict[str, dict[str, Any]] = {}
        self._register_agents()

    def _register_agents(self) -> None:
        for name, cls in AGENT_REGISTRY.items():
            if name == "remediation":
                self._agents[name] = RemediationAgent(
                    approval_gate=self.approval_gate,
                    audit_logger=self.audit_logger,
                )
            elif name == "memory_knowledge":
                self._agents[name] = MemoryKnowledgeAgent(memory_store=self.memory_store)
            else:
                self._agents[name] = cls()
        logger.info("Registered %d BootGuardAI agents", len(self._agents))

    def list_agents(self) -> list[dict[str, str]]:
        return [{"name": a.name, "description": a.description} for a in self._agents.values()]

    async def run_agent(self, agent_name: str, context: BootAnalysisContext) -> AgentResult:
        agent = self._agents.get(agent_name)
        if not agent:
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                summary=f"Unknown agent: {agent_name}",
                errors=[f"Agent '{agent_name}' not registered"],
                simulated=True,
            )
        self.audit_logger.log(
            "orchestrator", "agent_start", agent_name, "started", context.analysis_id
        )
        try:
            result = await agent.process(context)
            context.agent_results[agent_name] = result
            self.audit_logger.log(
                "orchestrator",
                "agent_complete",
                agent_name,
                result.status.value,
                context.analysis_id,
            )
            return result
        except Exception as exc:
            logger.exception("Agent %s failed", agent_name)
            result = AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                summary=str(exc),
                errors=[str(exc)],
                simulated=True,
            )
            context.agent_results[agent_name] = result
            return result

    async def analyze(self, alerts: list[BootAlert], os_type: OSType | None = None) -> dict[str, Any]:
        analysis_id = str(uuid4())
        context = BootAnalysisContext(analysis_id=analysis_id, alerts=alerts, simulated=True)
        if os_type:
            context.os_type = os_type
        workflow = BootAnalysisWorkflow(self)
        await workflow.execute(context)
        report_dict = context.report.model_dump(mode="json") if context.report else {}
        result = {
            "analysis_id": analysis_id,
            "report": report_dict,
            "agent_results": {k: v.model_dump() for k, v in context.agent_results.items()},
            "pending_approvals": [r.model_dump() for r in self.approval_gate.list_pending()],
            "simulated": True,
        }
        self._analyses[analysis_id] = result
        return result

    async def analyze_windows(self, alerts: list[BootAlert]) -> dict[str, Any]:
        return await self.analyze(alerts, os_type=OSType.WINDOWS)

    async def analyze_linux(self, alerts: list[BootAlert]) -> dict[str, Any]:
        return await self.analyze(alerts, os_type=OSType.LINUX)

    async def persistence_hunt(self, alerts: list[BootAlert]) -> dict[str, Any]:
        analysis_id = str(uuid4())
        context = BootAnalysisContext(analysis_id=analysis_id, alerts=alerts, simulated=True)
        if alerts:
            context.os_type = alerts[0].os_type
        await self.run_agent("persistence_hunt", context)
        await self.run_agent("mitre_persistence", context)
        return {
            "analysis_id": analysis_id,
            "persistence_indicators": context.persistence_indicators,
            "mitre_techniques": context.mitre_techniques,
            "simulated": True,
        }

    def get_report(self, analysis_id: str) -> dict[str, Any] | None:
        return self._analyses.get(analysis_id)
