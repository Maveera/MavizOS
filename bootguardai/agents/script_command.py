"""Script/Command Agent — bcdedit, bootrec, journalctl, dmesg guidance."""

from bootguardai.agents.base import BaseAgent
from bootguardai.models.boot_alert import OSType
from bootguardai.models.workflow import BootAnalysisContext

WINDOWS_COMMANDS = [
    "bcdedit /enum all",
    "bootrec /scanos",
    "bootrec /rebuildbcd  # destructive — requires approval",
]
LINUX_COMMANDS = [
    "journalctl -b -1",
    "dmesg | grep -i firmware",
    "grub-install --version",
    "systemd-analyze blame",
]


class ScriptCommandAgent(BaseAgent):
    name = "script_command"
    description = "Analyst command guidance for boot forensics"

    async def process(self, context: BootAnalysisContext) -> AgentResult:
        if context.os_type == OSType.WINDOWS:
            cmds = WINDOWS_COMMANDS
        elif context.os_type == OSType.LINUX:
            cmds = LINUX_COMMANDS
        else:
            cmds = WINDOWS_COMMANDS + LINUX_COMMANDS
        findings = [f"Suggested: {c}" for c in cmds]
        context.soc_notes.extend(findings)
        return self._success(
            summary="Command guidance generated for analyst",
            findings=findings,
            artifacts={"commands": cmds},
            confidence=0.9,
        )
