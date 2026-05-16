"""MavizOS specialized SOC agents."""

from mavizos.agents.alert_triage import AlertTriageAgent
from mavizos.agents.cloud_security import CloudSecurityAgent
from mavizos.agents.compliance import ComplianceAgent
from mavizos.agents.detection_engineering import DetectionEngineeringAgent
from mavizos.agents.email_security import EmailSecurityAgent
from mavizos.agents.investigation import InvestigationAgent
from mavizos.agents.malware_analysis import MalwareAnalysisAgent
from mavizos.agents.memory_agent import MemoryAgent
from mavizos.agents.mitre_attack import MitreAttackAgent
from mavizos.agents.reporting import ReportingAgent
from mavizos.agents.soar_automation import SOARAutomationAgent
from mavizos.agents.threat_hunting import ThreatHuntingAgent
from mavizos.agents.threat_intel import ThreatIntelAgent

AGENT_REGISTRY: dict[str, type] = {
    "alert_triage": AlertTriageAgent,
    "threat_intel": ThreatIntelAgent,
    "investigation": InvestigationAgent,
    "malware_analysis": MalwareAnalysisAgent,
    "mitre_attack": MitreAttackAgent,
    "soar_automation": SOARAutomationAgent,
    "detection_engineering": DetectionEngineeringAgent,
    "threat_hunting": ThreatHuntingAgent,
    "compliance": ComplianceAgent,
    "reporting": ReportingAgent,
    "memory": MemoryAgent,
    "email_security": EmailSecurityAgent,
    "cloud_security": CloudSecurityAgent,
}

__all__ = [
    "AGENT_REGISTRY",
    "AlertTriageAgent",
    "ThreatIntelAgent",
    "InvestigationAgent",
    "MalwareAnalysisAgent",
    "MitreAttackAgent",
    "SOARAutomationAgent",
    "DetectionEngineeringAgent",
    "ThreatHuntingAgent",
    "ComplianceAgent",
    "ReportingAgent",
    "MemoryAgent",
    "EmailSecurityAgent",
    "CloudSecurityAgent",
]
