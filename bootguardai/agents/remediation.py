"""Remediation planning with approval gates for destructive boot fixes."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.workflow import BootAnalysisContext
from bootguardai.security.approval import ApprovalGate
from bootguardai.security.audit import AuditLogger


class RemediationAgent(BaseAgent):
    name = "remediation"
    description = "Remediation recommendations with approval gates"

    def __init__(
        self,
        approval_gate: ApprovalGate | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self._approval = approval_gate or ApprovalGate()
        self._audit = audit_logger or AuditLogger()

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        findings: list[str] = []
        destructive = []
        if "bcd_tampering_indicator" in context.detected_risks:
            destructive.append(
                ("bcd_destructive_change", "Restore BCD from trusted backup", "BCD store")
            )
        if "grub_tampering" in context.detected_risks:
            destructive.append(
                ("grub_cfg_overwrite", "Restore grub.cfg from signed image", "/boot/grub/grub.cfg")
            )
        if "bootkit_indicator" in context.detected_risks:
            destructive.append(
                ("bootloader_rewrite", "Reflash bootmgfw from install media", "ESP")
            )

        for action_type, desc, target in destructive:
            if self._approval.requires_approval(action_type):
                req = self._approval.request_approval(
                    action_type=action_type,
                    description=desc,
                    target=target,
                    requested_by="remediation_agent",
                    analysis_id=context.analysis_id,
                )
                findings.append(f"Approval required [{req.id[:8]}]: {desc}")
                self._audit.log(
                    "remediation_agent",
                    "approval_requested",
                    action_type,
                    "pending",
                    context.analysis_id,
                )
            context.recommended_actions.append(f"[GATED] {desc} — {target}")

        context.recommended_actions.extend(
            [
                "Validate boot chain with offline media",
                "Compare boot components against golden image",
                "Enable Secure Boot if policy allows",
            ]
        )
        context.detection_opportunities.extend(
            [
                "Alert on BCD/grub.cfg modification",
                "Monitor EFI partition writes",
                "Correlate Secure Boot state changes",
            ]
        )
        return self._success(
            summary=f"Remediation plan: {len(destructive)} gated action(s)",
            findings=findings,
            confidence=0.7,
        )
