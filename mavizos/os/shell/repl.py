"""Interactive REPL for mavizos shell."""

from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING

from mavizos.os.shell.commands import CommandContext

if TYPE_CHECKING:
    from mavizos.os.kernel.kernel import Kernel

try:
    import readline  # noqa: F401 — enables history on Unix

    _READLINE = True
except ImportError:
    _READLINE = False


class MavizShell:
    """Read-eval-print loop with OS-style prompt."""

    def __init__(self, kernel: Kernel) -> None:
        self.kernel = kernel
        self.ctx = CommandContext(kernel)
        self.prompt = kernel.config.shell_prompt
        self._history: list[str] = []

    def _complete_hook(self) -> None:
        """Basic tab completion for commands."""
        if not _READLINE:
            return
        commands = [
            "help",
            "status",
            "agents",
            "ps",
            "triage",
            "investigate",
            "hunt",
            "incidents",
            "incident",
            "approvals",
            "approve",
            "audit",
            "fs",
            "clear",
            "shutdown",
            "boot",
            "serve",
        ]

        def completer(text: str, state: int) -> str | None:
            options = [c + " " for c in commands if c.startswith(text)]
            if state < len(options):
                return options[state]
            return None

        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    async def run_interactive(self) -> None:
        """Main REPL loop."""
        self._complete_hook()
        print(f"Welcome to mavizos. Type 'help' for commands.\n")
        while True:
            try:
                line = input(self.prompt + " ")
            except (EOFError, KeyboardInterrupt):
                print("\nUse 'shutdown' to exit.")
                continue
            self._history.append(line)
            try:
                cont = await self.ctx.run(line)
            except FileNotFoundError as exc:
                print(f"Error: {exc}")
                cont = True
            except Exception as exc:
                print(f"Error: {exc}")
                cont = True
            if not cont:
                break

    async def run_script(self, lines: list[str]) -> list[str]:
        """Execute commands non-interactively (for tests/demo)."""
        output: list[str] = []
        for line in lines:
            if line.strip().startswith("#"):
                continue
            cont = await self.ctx.run(line)
            output.append(line)
            if not cont:
                break
        return output
