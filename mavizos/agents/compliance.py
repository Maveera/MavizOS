"""Compliance Agent — controls validation and framework mapping."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult
from mavizos.models.workflow import InvestigationContext

FRAMEWORK_MAP = {
    "T1003": ["NIST-AC-2", "CIS-6.8", "ISO-A.9.4"],
    "T1059.001": ["NIST-SI-4", "CIS-8.8", "PCI-10.6"],
    "T1071": ["NIST-SC-7", "CIS-13.3", "ISO-A.13.1"],
    "T1486": ["NIST-CP-9", "CIS-11.1", "HIPAA-164.308"],
}


class ComplianceAgent(BaseAgent):
    """Map findings to compliance frameworks and identify violations."""

    name = "compliance"
    description = "Compliance controls validation and audit evidence"

    async def process(self, context: InvestigationContext) -> AgentResult:
        findings: list[str] = []
        controls: list[str] = []
        violations: list[str] = []

        for technique in context.mitre_techniques:
            mapped = FRAMEWORK_MAP.get(technique, [])
            for ctrl in mapped:
                controls.append(ctrl)
                findings.append(f"{technique} maps to control {ctrl}")

        if any(a.classification == "suspicious_activity" for a in context.alerts):
            violations.append("Potential access control violation — unauthorized activity detected")
            findings.append("Policy violation: suspicious endpoint activity requires incident review")

        if not controls:
            findings.append("No specific compliance mappings — general incident response procedures apply")

        return self._success(
            summary=f"Compliance: {len(controls)} control(s), {len(violations)} violation(s)",
            findings=findings,
            artifacts={"controls": controls, "violations": violations},
            confidence=0.6,
        )
