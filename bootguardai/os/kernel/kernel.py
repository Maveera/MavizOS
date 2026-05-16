"""BootGuardAI kernel — agent registry, VFS, orchestrator bridge."""

from bootguardai.config import get_settings
from bootguardai.orchestrator.orchestrator import Orchestrator
from bootguardai.os.filesystem.vfs import VirtualFilesystem
from bootguardai.os.kernel.registry import AgentRegistry


class Kernel:
    def __init__(self) -> None:
        self.config = get_settings()
        self.vfs = VirtualFilesystem()
        self.orchestrator = Orchestrator()
        self.registry = AgentRegistry(self.orchestrator)
        self.booted = False

    def boot(self) -> None:
        self.registry.register_all()
        self.booted = True

    def status(self) -> dict[str, object]:
        return {
            "booted": self.booted,
            "agents": len(self.orchestrator.list_agents()),
            "vfs_root": str(self.vfs.root),
            "demo_mode": self.config.demo_mode,
        }
