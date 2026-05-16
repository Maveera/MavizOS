#!/usr/bin/env python3
"""MavizOS OS demo — boot sequence and shell commands (non-interactive)."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mavizos.os.kernel.kernel import Kernel, reset_kernel
from mavizos.os.config.loader import OSConfig
from mavizos.os.shell.repl import MavizShell


async def main() -> None:
    reset_kernel()
    config = OSConfig(boot_banner=True, vfs_root="./mavizos_fs")
    kernel = Kernel(config=config)

    print("=== MavizOS OS Demo ===\n")
    kernel.boot(verbose=True)

    shell = MavizShell(kernel)
    commands = [
        "status",
        "agents",
        "ps",
        "investigate",
        "incidents",
        "approvals",
        "audit",
        "fs ls /var",
        "hunt Lateral movement from WORKSTATION-42",
        "ps --all",
    ]
    print("\n=== Shell Commands (scripted) ===\n")
    for cmd in commands:
        print(f"MavizOS> {cmd}")
        await shell.ctx.run(cmd)
        print()

    print("Demo complete.")
    print("Interactive shell:  python -m mavizos")
    print("API + desktop:      python -m mavizos.main  →  http://localhost:8000/desktop")


if __name__ == "__main__":
    asyncio.run(main())
