"""BootGuardAI specialized boot security agents."""

from bootguardai.agents.bootloader_integrity import BootloaderIntegrityAgent
from bootguardai.agents.firmware_uefi import FirmwareUEFIAgent
from bootguardai.agents.forensics_timeline import ForensicsTimelineAgent
from bootguardai.agents.kernel_analysis import KernelAnalysisAgent
from bootguardai.agents.linux_boot import LinuxBootAgent
from bootguardai.agents.memory_knowledge import MemoryKnowledgeAgent
from bootguardai.agents.mitre_persistence import MitrePersistenceAgent
from bootguardai.agents.persistence_hunt import PersistenceHuntAgent
from bootguardai.agents.remediation import RemediationAgent
from bootguardai.agents.reporting import ReportingAgent
from bootguardai.agents.rootkit_bootkit import RootkitBootkitAgent
from bootguardai.agents.script_command import ScriptCommandAgent
from bootguardai.agents.windows_boot import WindowsBootAgent

AGENT_REGISTRY: dict[str, type] = {
    "windows_boot": WindowsBootAgent,
    "linux_boot": LinuxBootAgent,
    "bootloader_integrity": BootloaderIntegrityAgent,
    "kernel_analysis": KernelAnalysisAgent,
    "persistence_hunt": PersistenceHuntAgent,
    "firmware_uefi": FirmwareUEFIAgent,
    "rootkit_bootkit": RootkitBootkitAgent,
    "forensics_timeline": ForensicsTimelineAgent,
    "script_command": ScriptCommandAgent,
    "mitre_persistence": MitrePersistenceAgent,
    "reporting": ReportingAgent,
    "memory_knowledge": MemoryKnowledgeAgent,
    "remediation": RemediationAgent,
}

__all__ = ["AGENT_REGISTRY", "WindowsBootAgent", "LinuxBootAgent", "ReportingAgent"]
