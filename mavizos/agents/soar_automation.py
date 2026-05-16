"""SOAR Automation Agent — playbooks with approval gates."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult, AgentStatus
from mavizos.models.workflow import InvestigationContext
from mavizos.security.approval import ApprovalGate
from mavizos.security.audit import AuditLogger


class SOARAutomationAgent(BaseAgent):
    """Execute SOAR playbooks; destructive actions require approval."""

    name = "soar_automation"
    description = "SOAR playbook execution with approval gates"

    def __init__(
        self,
        approval_gate: ApprovalGate | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self._approval = approval_gate or ApprovalGate()
        self._audit = audit_logger or AuditLogger()

    async def process(self, context: InvestigationContext) -> AgentResult:
        findings: list[str] = []
        pending_approvals: list[str] = []

        # Autonomous actions (no approval)
        context.automated_actions.append("Created investigation ticket (simulated)")
        context.automated_actions.append("Sent Slack notification to #soc-alerts (simulated)")
        findings.append("Autonomous: ticket created, notification sent (simulated)")
        self._audit.log(
            actor=self.name,
            action="create_ticket",
            target=context.incident_id,
            outcome="success",
            incident_id=context.incident_id,
            details={"simulated": True},
        )

        # Destructive actions — require approval
        for alert in context.alerts:
            if alert.ip_address and alert.ip_address.startswith("203."):
                req = self._approval.request_approval(
                    action_type="firewall_block",
                    description=f"Block malicious IP {alert.ip_address}",
                    target=alert.ip_address,
                    requested_by=self.name,
                    incident_id=context.incident_id,
                )
                pending_approvals.append(req.id)
                findings.append(
                    f"PENDING APPROVAL: firewall block for {alert.ip_address} (req={req.id[:8]})"
                )
                context.recommended_actions.append(
                    f"Block IP {alert.ip_address} at perimeter firewall"
                )

            if alert.host and alert.classification == "suspicious_activity":
                req = self._approval.request_approval(
                    action_type="host_isolation",
                    description=f"Isolate host {alert.host}",
                    target=alert.host,
                    requested_by=self.name,
                    incident_id=context.incident_id,
                )
                pending_approvals.append(req.id)
                findings.append(
                    f"PENDING APPROVAL: host isolation for {alert.host} (req={req.id[:8]})"
                )

        status = AgentStatus.PENDING_APPROVAL if pending_approvals else AgentStatus.SUCCESS
        return AgentResult(
            agent_name=self.name,
            status=status,
            summary=f"SOAR: {len(context.automated_actions)} auto, {len(pending_approvals)} pending approval",
            findings=findings,
            artifacts={"pending_approvals": pending_approvals},
            confidence=0.8,
            requires_approval=bool(pending_approvals),
            approval_request_id=pending_approvals[0] if pending_approvals else None,
        )
