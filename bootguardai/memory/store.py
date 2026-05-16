"""Organizational memory for boot analysis findings."""

import json
from pathlib import Path
from typing import Any

from bootguardai.config import get_settings


class MemoryStore:
    def __init__(self) -> None:
        self._path = Path(get_settings().memory_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return {"findings": [], "feedback": []}

    def save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def add_finding(self, analysis_id: str, summary: str, os_type: str) -> None:
        self._data.setdefault("findings", []).append(
            {"analysis_id": analysis_id, "summary": summary, "os_type": os_type}
        )
        self.save()

    def add_feedback(self, analysis_id: str, note: str) -> None:
        self._data.setdefault("feedback", []).append({"analysis_id": analysis_id, "note": note})
        self.save()

    def recent_findings(self, limit: int = 10) -> list[dict[str, Any]]:
        return list(self._data.get("findings", []))[-limit:]
