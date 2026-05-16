"""Boot sequence — ASCII banner and service startup."""

from __future__ import annotations

import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mavizos.os.kernel.kernel import Kernel

BANNER = r"""
 ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗      ██████╗ ███████╗
 ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     ██╔═══██╗██╔════╝
 ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     ██║   ██║███████╗
 ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     ██║   ██║╚════██║
 ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗╚██████╔╝███████║
 ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝
                    Autonomous Agentic AI SOC Operating System
"""


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    if not _supports_color():
        return text
    return f"\033[{code}m{text}\033[0m"


def run_boot_sequence(kernel: Kernel, *, verbose: bool = True) -> None:
    """Execute boot: banner, mount VFS, start services, health check."""
    if verbose and kernel.config.boot_banner:
        print(_c(BANNER, "36"))
        print(_c(f"  MavizOS v{kernel.version}  |  DEMO MODE (simulated TI)", "33"))
        print()

    steps = [
        ("Initializing kernel", lambda: None),
        ("Mounting virtual filesystem", lambda: kernel.vfs._ensure_layout()),
        ("Loading service registry", lambda: kernel.services_registry.register_from_agents(kernel.orchestrator._agents)),
        ("Starting agent services", lambda: kernel.services_registry.start_all()),
        ("Running health checks", lambda: kernel.services_registry.health_check()),
        ("Starting event bus", lambda: kernel.event_bus.publish("system.boot", {"hostname": kernel.config.hostname})),
    ]

    for label, action in steps:
        if verbose:
            print(f"  [{_c('OK', '32')}] {label}...", end="", flush=True)
        action()
        if verbose:
            time.sleep(0.08)
            print(" done")

    services = kernel.services_registry.list_all()
    if verbose:
        print()
        print(_c(f"  {len(services)} agent services online", "32"))
        print(_c(f"  VFS mounted at {kernel.vfs.root.resolve()}", "90"))
        print()
        kernel.vfs.append_log("System boot complete", source="boot")
    kernel._booted = True
