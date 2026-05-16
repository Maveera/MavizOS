"""Shell command handlers."""

from __future__ import annotations

import asyncio
import json
import shlex
from pathlib import Path
from typing import TYPE_CHECKING, Any

from mavizos.models.alert import Alert
from mavizos.os.shell.samples import SAMPLE_ALERT

if TYPE_CHECKING:
    from mavizos.os.kernel.kernel import Kernel

try:
    from rich.console import Console
    from rich.table import Table

    _RICH = True
except ImportError:
    _RICH = False


def _console() -> Any:
    if _RICH:
        return Console()
    return None


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
    con = _console()
    if con and _RICH:
        table = Table(show_header=True, header_style="bold cyan")
        for h in headers:
            table.add_column(h)
        for row in rows:
            table.add_row(*[str(c) for c in row])
        con.print(table)
    else:
        print("  ".join(headers))
        print("-" * 60)
        for row in rows:
            print("  ".join(str(c) for c in row))


class CommandContext:
    """Execution context for shell commands."""

    def __init__(self, kernel: Kernel) -> None:
        self.kernel = kernel

    async def run(self, line: str) -> bool:
        """
        Execute one shell line.

        Returns False when shell should exit (shutdown).
        """
        line = line.strip()
        if not line:
            return True
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            print(f"Parse error: {exc}")
            return True
        cmd = parts[0].lower()
        args = parts[1:]

        handlers: dict[str, Any] = {
            "help": self.cmd_help,
            "?": self.cmd_help,
            "status": self.cmd_status,
            "agents": self.cmd_agents,
            "ps": self.cmd_ps,
            "triage": self.cmd_triage,
            "investigate": self.cmd_investigate,
            "hunt": self.cmd_hunt,
            "incidents": self.cmd_incidents,
            "incident": self.cmd_incident,
            "approvals": self.cmd_approvals,
            "approve": self.cmd_approve,
            "audit": self.cmd_audit,
            "fs": self.cmd_fs,
            "clear": self.cmd_clear,
            "cls": self.cmd_clear,
            "shutdown": self.cmd_shutdown,
            "exit": self.cmd_shutdown,
            "quit": self.cmd_shutdown,
            "boot": self.cmd_boot,
            "serve": self.cmd_serve_hint,
        }

        handler = handlers.get(cmd)
        if not handler:
            print(f"Unknown command: {cmd}. Type 'help' for commands.")
            return True
        if cmd in ("clear", "cls", "shutdown", "exit", "quit", "help", "?", "boot", "serve"):
            result = handler(args)
            if asyncio.iscoroutine(result):
                return await result
            return result if result is not None else True
        return await handler(args)

    def cmd_help(self, _args: list[str]) -> bool:
        print(
            """
MavizOS Shell Commands
─────────────────────────
  help              Show this help
  status            System and service health
  agents            List registered agent services
  ps                Running investigations / processes
  triage <file|->   Triage alert from JSON file or stdin (-)
  investigate       Run full investigation (sample alert)
  hunt [hypothesis] Threat hunt with hypothesis
  incidents         List incidents (orchestrator + VFS)
  incident <id>     Show incident details and report summary
  approvals         Pending approval queue
  approve <id>      Approve destructive action (demo)
  audit             Recent audit log entries
  fs ls [path]      List virtual filesystem
  fs cat <path>     Read file from VFS
  fs tree [path]    Directory tree
  clear             Clear screen
  shutdown          Graceful exit

  boot              Re-run boot sequence
  serve             Hint: start API server (mavizos serve)

Type commands at the mavizos> prompt. Tab completion where supported.
"""
        )
        return True

    async def cmd_status(self, _args: list[str]) -> bool:
        summary = self.kernel.service_manager.status_summary()
        con = _console()
        if con and _RICH:
            con.print(f"[bold green]MavizOS[/] v{self.kernel.version}")
            con.print(f"Hostname: {self.kernel.config.hostname}")
            con.print(f"Booted: {self.kernel.booted} | Demo: {self.kernel.config.demo_mode}")
            con.print(
                f"Services: {summary['running']}/{summary['total']} running — {summary['health']}"
            )
            con.print(f"VFS: {self.kernel.vfs.root.resolve()}")
            procs = self.kernel.process_manager.list_all(active_only=True)
            con.print(f"Active processes: {len(procs)}")
        else:
            print(f"MavizOS v{self.kernel.version} | booted={self.kernel.booted}")
            print(f"Services: {summary}")
        return True

    async def cmd_agents(self, _args: list[str]) -> bool:
        services = self.kernel.service_manager.list_services()
        rows = [[s.name, s.state.value, s.description[:50]] for s in services]
        _print_table(["Service", "State", "Description"], rows)
        return True

    async def cmd_ps(self, args: list[str]) -> bool:
        active_only = "--all" not in args
        procs = self.kernel.process_manager.list_all(active_only=active_only)
        if not procs:
            print("No processes.")
            return True
        rows = [
            [p.pid, p.name, p.state.value, p.incident_id or "-", p.result_summary or "-"]
            for p in procs
        ]
        _print_table(["PID", "Name", "State", "Incident", "Summary"], rows)
        return True

    async def cmd_triage(self, args: list[str]) -> bool:
        if not args:
            print("Usage: triage <alert.json|->")
            return True
        alert = self._load_alert(args[0])
        print("Running triage (simulated TI enrichment)...")
        result = await self.kernel.triage_alert(alert)
        print(json.dumps(result, indent=2, default=str))
        return True

    async def cmd_investigate(self, _args: list[str]) -> bool:
        print("Starting 10-step investigation pipeline (sample alert)...")
        result = await self.kernel.investigate([SAMPLE_ALERT])
        print(f"Incident ID: {result['incident_id']}")
        print(f"Status: {result['status']}")
        if result.get("report"):
            report = result["report"]
            print(f"\nExecutive Summary:\n{report['executive_summary'][:400]}...")
            print(f"Severity: {report['severity']} | Confidence: {report['confidence']}")
            print(f"VFS report: /var/reports/{result['incident_id']}.json")
        pending = result.get("pending_approvals", [])
        if pending:
            print(f"\nPending approvals: {len(pending)}")
        return True

    async def cmd_hunt(self, args: list[str]) -> bool:
        hypothesis = " ".join(args) if args else "Hunt for lateral movement from compromised endpoints"
        print(f"Hunting: {hypothesis}")
        result = await self.kernel.hunt(hypothesis)
        print(json.dumps(result, indent=2, default=str))
        return True

    async def cmd_incidents(self, _args: list[str]) -> bool:
        orch = self.kernel.orchestrator
        incidents = list(orch._incidents.values())
        vfs_dir = self.kernel.vfs.root / "var/incidents"
        vfs_ids = {p.stem for p in vfs_dir.glob("*.json")} if vfs_dir.exists() else set()
        all_ids = {i.id for i in incidents} | vfs_ids
        if not all_ids:
            print("No incidents recorded.")
            return True
        rows: list[list[str]] = []
        for iid in sorted(all_ids):
            inc = orch.get_incident(iid)
            if inc:
                rows.append([iid[:12] + "…", inc.status.value, inc.title[:40]])
            else:
                rows.append([iid[:12] + "…", "archived", "(vfs only)"])
        _print_table(["ID", "Status", "Title"], rows)
        return True

    async def cmd_incident(self, args: list[str]) -> bool:
        if not args:
            print("Usage: incident <id>")
            return True
        iid = args[0]
        orch = self.kernel.orchestrator
        inc = orch.get_incident(iid)
        if not inc:
            for full_id in orch._incidents:
                if full_id.startswith(iid):
                    iid = full_id
                    inc = orch.get_incident(iid)
                    break
        if inc:
            print(json.dumps(inc.model_dump(mode="json"), indent=2, default=str))
        else:
            print(f"Incident {iid} not in memory; checking VFS...")
        report_path = f"/var/reports/{iid}.json"
        try:
            report_text = self.kernel.vfs.cat(report_path)
            report = json.loads(report_text)
            print("\n--- Report Summary ---")
            print(report.get("executive_summary", "")[:500])
        except (FileNotFoundError, json.JSONDecodeError):
            if not inc:
                print("Incident not found.")
        return True

    async def cmd_approvals(self, _args: list[str]) -> bool:
        pending = self.kernel.orchestrator.approval_gate.list_pending()
        if not pending:
            print("No pending approvals.")
            return True
        rows = [[r.id[:8], r.action_type, r.description[:45]] for r in pending]
        _print_table(["ID", "Action", "Description"], rows)
        return True

    async def cmd_approve(self, args: list[str]) -> bool:
        if not args:
            print("Usage: approve <request_id>")
            return True
        prefix = args[0]
        gate = self.kernel.orchestrator.approval_gate
        match = None
        for req in gate.list_pending():
            if req.id.startswith(prefix):
                match = req.id
                break
        if not match:
            print("Approval request not found.")
            return True
        req = gate.approve(match, "shell_operator")
        if req:
            self.kernel.orchestrator.audit_logger.log(
                actor="shell_operator",
                action="approval_granted",
                target=match,
                outcome="approved",
                incident_id=req.incident_id,
            )
            print(f"Approved: {req.action_type} ({match[:8]})")
        return True

    async def cmd_audit(self, args: list[str]) -> bool:
        limit = 20
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                pass
        entries = self.kernel.orchestrator.audit_logger.get_entries(limit=limit)
        rows = [
            [e.timestamp.isoformat()[:19], e.actor, e.action, e.outcome] for e in entries
        ]
        _print_table(["Time", "Actor", "Action", "Outcome"], rows)
        return True

    async def cmd_fs(self, args: list[str]) -> bool:
        if not args:
            print("Usage: fs ls [path] | fs cat <path> | fs tree [path]")
            return True
        sub = args[0].lower()
        rest = args[1:]
        try:
            if sub == "ls":
                path = rest[0] if rest else "/"
                entries = self.kernel.vfs.ls(path)
                rows = [[e["type"], e["path"], e["size"]] for e in entries]
                _print_table(["Type", "Path", "Size"], rows)
            elif sub == "cat":
                if not rest:
                    print("Usage: fs cat <path>")
                    return True
                print(self.kernel.vfs.cat(rest[0]))
            elif sub == "tree":
                path = rest[0] if rest else "/"
                print(self.kernel.vfs.tree(path))
            else:
                print(f"Unknown fs subcommand: {sub}")
        except (FileNotFoundError, PermissionError, IsADirectoryError, NotADirectoryError) as exc:
            print(f"fs error: {exc}")
        return True

    def cmd_clear(self, _args: list[str]) -> bool:
        import os
        import sys

        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")
        return True

    def cmd_shutdown(self, _args: list[str]) -> bool:
        print("Shutting down mavizos...")
        self.kernel.shutdown()
        return False

    def cmd_boot(self, _args: list[str]) -> bool:
        self.kernel._booted = False
        self.kernel.boot(verbose=True)
        return True

    def cmd_serve_hint(self, _args: list[str]) -> bool:
        print("Start API server:  python -m mavizos.main")
        print("Or:                mavizos serve")
        print("Web desktop:       http://localhost:8000/desktop")
        return True

    def _load_alert(self, source: str) -> Alert:
        if source == "-":
            data = json.loads(input())
        else:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(source)
            data = json.loads(path.read_text(encoding="utf-8"))
        return Alert(**data)
