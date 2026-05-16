"""BootGuardAI interactive shell."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bootguardai.os.shell.commands import CommandContext

if TYPE_CHECKING:
    from bootguardai.os.kernel.kernel import Kernel


class BootGuardShell:
    def __init__(self, kernel: Kernel) -> None:
        self.kernel = kernel
        self.ctx = CommandContext(kernel)
        self.prompt = kernel.config.shell_prompt

    async def run_interactive(self) -> None:
        print("BootGuardAI shell. Type 'help' for commands.\n")
        while True:
            try:
                line = input(self.prompt + " ")
            except (EOFError, KeyboardInterrupt):
                print("\nUse 'shutdown' to exit.")
                continue
            try:
                cont = await self.ctx.run(line)
            except Exception as exc:
                print(f"Error: {exc}")
                cont = True
            if not cont:
                break
