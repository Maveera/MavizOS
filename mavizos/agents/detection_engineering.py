"""Detection Engineering Agent — Sigma, YARA, KQL, SPL generation."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult
from mavizos.models.workflow import InvestigationContext


class DetectionEngineeringAgent(BaseAgent):
    """Generate detection rules from investigation findings."""

    name = "detection_engineering"
    description = "Sigma, YARA, KQL, SPL detection rule generation"

    async def process(self, context: InvestigationContext) -> AgentResult:
        rules: dict[str, str] = {}
        findings: list[str] = []

        for alert in context.alerts:
            if alert.process and "powershell" in alert.process.lower():
                rules["sigma"] = self._sigma_powershell(alert)
                rules["kql"] = self._kql_powershell(alert)
                rules["spl"] = self._spl_powershell(alert)
                findings.append("Generated Sigma/KQL/SPL rules for encoded PowerShell")
                context.detection_opportunities.append(
                    "Deploy Sigma rule: suspicious encoded PowerShell execution"
                )

            if alert.file_hash:
                rules["yara"] = self._yara_hash(alert.file_hash)
                findings.append(f"Generated YARA rule for hash prefix {alert.file_hash[:8]}")

        if not rules:
            rules["sigma"] = (
                "title: MavizOS Generic Suspicious Activity\n"
                "status: experimental\n"
                "logsource:\n  product: windows\n"
                "detection:\n  condition: selection\n  selection:\n    EventID: 4688\n"
            )
            findings.append("Generated generic Sigma template — tune with investigation context")

        return self._success(
            summary=f"Detection engineering: {len(rules)} rule format(s) generated",
            findings=findings,
            artifacts={"rules": rules},
            confidence=0.7,
        )

    def _sigma_powershell(self, alert) -> str:
        return (
            "title: Suspicious Encoded PowerShell\n"
            "status: experimental\n"
            "logsource:\n  product: windows\n  service: powershell\n"
            "detection:\n  selection:\n"
            "    Image|endswith: '\\powershell.exe'\n"
            "    CommandLine|contains: '-enc'\n"
            "  condition: selection\n"
            f"# Generated from alert: {alert.id[:8]}\n"
        )

    def _kql_powershell(self, alert) -> str:
        host = alert.host or "*"
        return (
            "DeviceProcessEvents\n"
            f"| where DeviceName == '{host}'\n"
            "| where FileName =~ 'powershell.exe'\n"
            "| where ProcessCommandLine contains '-enc'\n"
        )

    def _spl_powershell(self, alert) -> str:
        host = alert.host or "*"
        return (
            f'index=winevent host="{host}" '
            'Image="*\\\\powershell.exe" CommandLine="*-enc*" '
            "| stats count by host, user, CommandLine"
        )

    def _yara_hash(self, file_hash: str) -> str:
        return (
            "rule MavizOS_Simulated_Malware {\n"
            "  meta:\n    description = 'Generated from investigation — tune before production'\n"
            "  strings:\n"
            f'    $hash = "{file_hash}"\n'
            "  condition:\n    $hash\n}\n"
        )
