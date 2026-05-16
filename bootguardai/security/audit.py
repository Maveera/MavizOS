"""Audit logging for BootGuardAI actions."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bootguardai.config import get_settings


class AuditLogger:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._path = Path(self._settings.audit_log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        actor: str,
        action: str,
        target: str,
        outcome: str,
        analysis_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "actor": actor,
            "action": action,
            "target": target,
            "outcome": outcome,
            "analysis_id": analysis_id,
            "metadata": metadata or {},
            "simulated": self._settings.demo_mode,
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        lines = self._path.read_text(encoding="utf-8").strip().splitlines()
        entries = [json.loads(line) for line in lines[-limit:] if line.strip()]
        return entries
