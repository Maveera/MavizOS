"""Virtual SOC filesystem rooted at ./mavizos_fs/."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class VirtualFilesystem:
    """
    POSIX-like virtual filesystem for MavizOS artifacts.

    Layout:
        mavizos_fs/
          etc/
          var/incidents/
          var/reports/
          var/logs/
          var/iocs/
    """

    DEFAULT_ROOT = Path("./mavizos_fs")

    def __init__(self, root: Path | str | None = None) -> None:
        self.root = Path(root) if root else self.DEFAULT_ROOT
        self._ensure_layout()

    def _ensure_layout(self) -> None:
        for sub in (
            "etc",
            "var/incidents",
            "var/reports",
            "var/logs",
            "var/iocs",
            "var/audit",
            "home",
        ):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

    def resolve(self, path: str) -> Path:
        """Resolve user path against VFS root (blocks traversal)."""
        clean = path.strip().replace("\\", "/")
        if clean in ("", "/", "."):
            return self.root
        if clean.startswith("/"):
            clean = clean.lstrip("/")
        target = (self.root / clean).resolve()
        root_resolved = self.root.resolve()
        if not str(target).startswith(str(root_resolved)):
            raise PermissionError("Path traversal denied")
        return target

    def ls(self, path: str = "/") -> list[dict[str, str]]:
        """List directory entries."""
        target = self.resolve(path)
        if not target.exists():
            raise FileNotFoundError(f"No such path: {path}")
        if not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
        entries: list[dict[str, str]] = []
        for child in sorted(target.iterdir()):
            rel = child.relative_to(self.root.resolve())
            entries.append(
                {
                    "name": child.name + ("/" if child.is_dir() else ""),
                    "path": "/" + str(rel).replace("\\", "/"),
                    "type": "dir" if child.is_dir() else "file",
                    "size": str(child.stat().st_size) if child.is_file() else "-",
                }
            )
        return entries

    def cat(self, path: str) -> str:
        """Read file contents."""
        target = self.resolve(path)
        if not target.exists():
            raise FileNotFoundError(f"No such file: {path}")
        if target.is_dir():
            raise IsADirectoryError(f"Is a directory: {path}")
        return target.read_text(encoding="utf-8")

    def write_json(self, rel_path: str, data: Any) -> Path:
        """Write JSON artifact under VFS."""
        target = self.resolve(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return target

    def persist_incident(self, incident_id: str, payload: dict[str, Any]) -> None:
        """Store incident snapshot."""
        self.write_json(f"var/incidents/{incident_id}.json", payload)

    def persist_report(self, incident_id: str, report: dict[str, Any]) -> None:
        """Store investigation report."""
        self.write_json(f"var/reports/{incident_id}.json", report)

    def persist_iocs(self, incident_id: str, iocs: list[dict[str, Any]]) -> None:
        """Store IOC bundle."""
        self.write_json(f"var/iocs/{incident_id}.json", {"incident_id": incident_id, "iocs": iocs})

    def append_log(self, message: str, *, source: str = "kernel") -> None:
        """Append line to system log."""
        log_dir = self.root / "var/logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "system.log"
        ts = datetime.now(timezone.utc).isoformat()
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(f"[{ts}] [{source}] {message}\n")

    def tree(self, path: str = "/", max_depth: int = 3) -> str:
        """ASCII tree of VFS."""
        base = self.resolve(path)
        lines: list[str] = [str(base.relative_to(self.root.resolve()) or ".")]

        def _walk(directory: Path, prefix: str, depth: int) -> None:
            if depth > max_depth:
                return
            children = sorted(directory.iterdir())
            for i, child in enumerate(children):
                connector = "└── " if i == len(children) - 1 else "├── "
                lines.append(f"{prefix}{connector}{child.name}")
                if child.is_dir():
                    extension = "    " if i == len(children) - 1 else "│   "
                    _walk(child, prefix + extension, depth + 1)

        if base.is_dir():
            _walk(base, "", 0)
        return "\n".join(lines)

    def reset(self) -> None:
        """Wipe VFS (testing only)."""
        if self.root.exists():
            shutil.rmtree(self.root)
        self._ensure_layout()
