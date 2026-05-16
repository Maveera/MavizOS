"""MITRE ATT&CK Agent — technique mapping and attack chains."""

from mavizos.agents.base import BaseAgent
from mavizos.models.agent_result import AgentResult
from mavizos.models.workflow import InvestigationContext

# Simplified technique mapping heuristics
TECHNIQUE_MAP: dict[str, dict[str, str]] = {
    "powershell": {
        "technique_id": "T1059.001",
        "technique": "PowerShell",
        "tactic": "Execution",
    },
    "lateral": {
        "technique_id": "T1021",
        "technique": "Remote Services",
        "tactic": "Lateral Movement",
    },
    "credential": {
        "technique_id": "T1003",
        "technique": "OS Credential Dumping",
        "tactic": "Credential Access",
    },
    "exfil": {
        "technique_id": "T1041",
        "technique": "Exfiltration Over C2 Channel",
        "tactic": "Exfiltration",
    },
    "ransomware": {
        "technique_id": "T1486",
        "technique": "Data Encrypted for Impact",
        "tactic": "Impact",
    },
    "phishing": {
        "technique_id": "T1566",
        "technique": "Phishing",
        "tactic": "Initial Access",
    },
    "c2": {
        "technique_id": "T1071",
        "technique": "Application Layer Protocol",
        "tactic": "Command and Control",
    },
}


class MitreAttackAgent(BaseAgent):
    """Map observed activity to MITRE ATT&CK techniques and tactics."""

    name = "mitre_attack"
    description = "MITRE ATT&CK technique mapping and attack chain analysis"

    async def process(self, context: InvestigationContext) -> AgentResult:
        findings: list[str] = []
        mappings: list[dict[str, str]] = []
        seen: set[str] = set()

        for alert in context.alerts:
            text = f"{alert.title} {alert.description} {alert.process or ''}".lower()
            for keyword, mapping in TECHNIQUE_MAP.items():
                if keyword in text and mapping["technique_id"] not in seen:
                    seen.add(mapping["technique_id"])
                    mappings.append(mapping)
                    context.mitre_techniques.append(mapping["technique_id"])
                    findings.append(
                        f"{mapping['technique_id']}: {mapping['technique']} ({mapping['tactic']})"
                    )

        if alert := (context.alerts[0] if context.alerts else None):
            if alert.process and "powershell" in alert.process.lower():
                m = TECHNIQUE_MAP["powershell"]
                if m["technique_id"] not in seen:
                    mappings.append(m)
                    context.mitre_techniques.append(m["technique_id"])
                    findings.append(f"{m['technique_id']}: {m['technique']} ({m['tactic']})")

        if context.timeline:
            for evt in context.timeline:
                if evt.event_type == "network_connection":
                    m = TECHNIQUE_MAP["c2"]
                    if m["technique_id"] not in seen:
                        seen.add(m["technique_id"])
                        mappings.append(m)
                        context.mitre_techniques.append(m["technique_id"])
                        findings.append(
                            f"{m['technique_id']}: {m['technique']} — network C2 indicator"
                        )

        return self._success(
            summary=f"MITRE mapping: {len(mappings)} technique(s) identified",
            findings=findings or ["No MITRE techniques mapped — insufficient context"],
            artifacts={"mappings": mappings},
            confidence=0.6 if mappings else 0.3,
        )
