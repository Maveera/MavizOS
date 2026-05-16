"""BootGuardAI shell entry."""

import asyncio

from bootguardai.os.kernel.boot import BOOT_BANNER
from bootguardai.os.kernel.kernel import Kernel
from bootguardai.os.shell.repl import BootGuardShell


def boot_and_shell() -> None:
    print(BOOT_BANNER)
    kernel = Kernel()
    kernel.boot()
    print(f"[OK] {len(kernel.registry.list_services())} agent services online.\n")
    shell = BootGuardShell(kernel)
    asyncio.run(shell.run_interactive())


def cli_entry() -> None:
    boot_and_shell()


if __name__ == "__main__":
    cli_entry()
