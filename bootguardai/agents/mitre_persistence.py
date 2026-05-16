"""MITRE/Persistence Mapping Agent — ATT&CK persistence techniques."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.workflow import BootAnalysisContext

TECHNIQUE_MAP = {
    "bcd_tampering_indicator": ("T1542.003", "Bootkit"),
    "grub_tampering": ("T1542.003", "Bootkit"),
    "secure_boot_off": ("T1542.003", "Bootkit"),
    "bootkit_indicator": ("T1542.003", "Bootkit"),
    "persistence": ("T1547", "Boot or Logon Autostart Execution"),
}


class MitrePersistenceAgent(BaseAgent):
    name = "mitre_persistence"
    description = "Map boot findings to MITRE ATT&CK persistence techniques"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        findings: list[str] = []
        for risk in context.detected_risks:
            if risk in TECHNIQUE_MAP:
                tid, name = TECHNIQUE_MAP[risk]
                context.mitre_techniques.append(tid)
                findings.append(f"{tid} — {name} (from {risk})")
        for ind in context.persistence_indicators:
            if "T1547" not in context.mitre_techniques:
                context.mitre_techniques.append("T1547")
            findings.append(f"T1547 relevance: persistence indicator '{ind[:40]}'")
        if not findings:
            findings.append("No MITRE mappings from current simulated findings")
        return self._success(
            summary=f"MITRE mapping: {len(context.mitre_techniques)} technique(s)",
            findings=findings,
            artifacts={"techniques": context.mitre_techniques},
            confidence=0.75,
        )
