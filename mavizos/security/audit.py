"""Immutable audit log for automated actions."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from mavizos.config import get_settings


class AuditEntry(BaseModel):
    """Single audit log entry."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: str
    action: str
    target: str
    outcome: str
    incident_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class AuditLogger:
    """Append-only audit logger with optional file persistence."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []
        settings = get_settings()
        self._log_path = Path(settings.audit_log_path)
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        actor: str,
        action: str,
        target: str,
        outcome: str,
        incident_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Record an audit entry."""
        entry = AuditEntry(
            actor=actor,
            action=action,
            target=target,
            outcome=outcome,
            incident_id=incident_id,
            details=details or {},
        )
        self._entries.append(entry)
        self._persist(entry)
        return entry

    def _persist(self, entry: AuditEntry) -> None:
        """Append entry to audit log file."""
        line = json.dumps(entry.model_dump(mode="json"), default=str)
        with self._log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def get_entries(
        self,
        incident_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Retrieve recent audit entries, optionally filtered."""
        entries = self._entries
        if incident_id:
            entries = [e for e in entries if e.incident_id == incident_id]
        return entries[-limit:]
