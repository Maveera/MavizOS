"""BootGuardAI shell command handlers."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

from bootguardai.models.boot_alert import BootAlert, BootMode, OSType
from bootguardai.os.shell.samples import SAMPLE_LINUX_ALERT, SAMPLE_WINDOWS_ALERT

if TYPE_CHECKING:
    from bootguardai.os.kernel.kernel import Kernel


class CommandContext:
    def __init__(self, kernel: Kernel) -> None:
        self.kernel = kernel

    async def run(self, line: str) -> bool:
        parts = line.strip().split()
        if not parts:
            return True
        cmd = parts[0].lower()
        args = parts[1:]

        handlers = {
            "help": self._help,
            "status": self._status,
            "agents": self._agents,
            "analyze": self._analyze,
            "windows": self._windows,
            "linux": self._linux,
            "persistence": self._persistence,
            "reports": self._reports,
            "approvals": self._approvals,
            "audit": self._audit,
            "fs": self._fs,
            "shutdown": self._shutdown,
        }
        handler = handlers.get(cmd)
        if not handler:
            print(f"Unknown command: {cmd}. Type 'help'.")
            return True
        return await handler(args)

    async def _help(self, _args: list[str]) -> bool:
        print(
            "Commands: help, status, agents, analyze, windows, linux, "
            "persistence, reports, fs ls|cat, approvals, audit, shutdown"
        )
        return True

    async def _status(self, _args: list[str]) -> bool:
        print(json.dumps(self.kernel.status(), indent=2))
        return True

    async def _agents(self, _args: list[str]) -> bool:
        for a in self.kernel.orchestrator.list_agents():
            print(f"  {a['name']}: {a['description']}")
        return True

    async def _analyze(self, _args: list[str]) -> bool:
        alert = BootAlert(**SAMPLE_WINDOWS_ALERT)
        result = await self.kernel.orchestrator.analyze([alert])
        self._print_result(result)
        return True

    async def _windows(self, _args: list[str]) -> bool:
        alert = BootAlert(**SAMPLE_WINDOWS_ALERT)
        result = await self.kernel.orchestrator.analyze_windows([alert])
        self._print_result(result)
        return True

    async def _linux(self, _args: list[str]) -> bool:
        alert = BootAlert(**SAMPLE_LINUX_ALERT)
        result = await self.kernel.orchestrator.analyze_linux([alert])
        self._print_result(result)
        return True

    async def _persistence(self, _args: list[str]) -> bool:
        alert = BootAlert(**SAMPLE_LINUX_ALERT)
        result = await self.kernel.orchestrator.persistence_hunt([alert])
        print(json.dumps(result, indent=2))
        return True

    async def _reports(self, args: list[str]) -> bool:
        if not args:
            print("Usage: reports <analysis_id>")
            return True
        report = self.kernel.orchestrator.get_report(args[0])
        print(json.dumps(report or {"error": "not found"}, indent=2))
        return True

    async def _approvals(self, _args: list[str]) -> bool:
        pending = self.kernel.orchestrator.approval_gate.list_pending()
        if not pending:
            print("No pending approvals.")
        for p in pending:
            print(f"  {p.id[:8]} [{p.action_type}] {p.description}")
        return True

    async def _audit(self, _args: list[str]) -> bool:
        for entry in self.kernel.orchestrator.audit_logger.recent(10):
            print(f"  {entry.get('timestamp')} {entry.get('action')} -> {entry.get('target')}")
        return True

    async def _fs(self, args: list[str]) -> bool:
        if not args:
            print("Usage: fs ls [path] | fs cat <path>")
            return True
        sub = args[0].lower()
        try:
            if sub == "ls":
                path = args[1] if len(args) > 1 else "."
                print("\n".join(self.kernel.vfs.ls(path)))
            elif sub == "cat":
                if len(args) < 2:
                    print("Usage: fs cat <path>")
                else:
                    print(self.kernel.vfs.cat(args[1]))
            else:
                print("Usage: fs ls|cat")
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
        return True

    async def _shutdown(self, _args: list[str]) -> bool:
        print("BootGuardAI shutting down.")
        return False

    def _print_result(self, result: dict) -> None:
        aid = result.get("analysis_id", "")[:8]
        report = result.get("report") or {}
        print(f"Analysis {aid} — {report.get('executive_summary', 'complete')[:120]}...")
        if report:
            self.kernel.vfs.write_report(
                result["analysis_id"],
                json.dumps(report, indent=2),
            )
