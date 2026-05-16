"""Shell entry point and CLI dispatcher."""

from __future__ import annotations

import argparse
import asyncio
import sys


def boot_and_shell(*, verbose_boot: bool = True, script: list[str] | None = None) -> None:
    """Boot kernel and start shell."""
    from mavizos.os.kernel.kernel import get_kernel
    from mavizos.os.shell.repl import MavizShell

    kernel = get_kernel()
    kernel.boot(verbose=verbose_boot)
    shell = MavizShell(kernel)
    if script:
        asyncio.run(shell.run_script(script))
    else:
        asyncio.run(shell.run_interactive())


def cli_entry() -> None:
    """Console script entry: MavizOS [boot|serve|shell|...]."""
    parser = argparse.ArgumentParser(
        prog="mavizos",
        description="MavizOS — Autonomous Agentic AI SOC Operating System",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="boot",
        choices=["boot", "shell", "serve", "help"],
        help="Command (default: boot into shell)",
    )
    parser.add_argument(
        "--quiet-boot",
        action="store_true",
        help="Suppress boot animation",
    )
    args = parser.parse_args()

    if args.command == "serve":
        from mavizos.main import run

        run()
    elif args.command == "help":
        print("mavizos        Boot and open interactive shell")
        print("mavizos boot   Same as default")
        print("mavizos shell  Interactive shell (skip banner if --quiet-boot)")
        print("mavizos serve  Start FastAPI server")
        print("python -m mavizos.boot   Boot sequence")
        print("python -m mavizos.main   API server")
    else:
        boot_and_shell(verbose_boot=not args.quiet_boot)


def main() -> None:
    """Module main for python -m mavizos.os.shell."""
    cli_entry()


if __name__ == "__main__":
    main()
