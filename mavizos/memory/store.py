"""In-memory organizational knowledge store with JSON persistence."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from mavizos.config import get_settings


class MemoryRecord(BaseModel):
    """Stored organizational security knowledge."""

    id: str
    record_type: str
    content: dict[str, Any]
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MemoryStore:
    """In-memory store with optional JSON file persistence."""

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}
        settings = get_settings()
        self._persist_path = Path(settings.memory_persist_path)
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def store(
        self,
        record_id: str,
        record_type: str,
        content: dict[str, Any],
        tags: list[str] | None = None,
    ) -> MemoryRecord:
        """Store or update a memory record."""
        now = datetime.now(UTC)
        if record_id in self._records:
            rec = self._records[record_id]
            rec.content = content
            rec.tags = tags or rec.tags
            rec.updated_at = now
        else:
            rec = MemoryRecord(
                id=record_id,
                record_type=record_type,
                content=content,
                tags=tags or [],
            )
            self._records[record_id] = rec
        self._save()
        return rec

    def get(self, record_id: str) -> MemoryRecord | None:
        """Retrieve record by ID."""
        return self._records.get(record_id)

    def search(
        self,
        record_type: str | None = None,
        tags: list[str] | None = None,
        limit: int = 50,
    ) -> list[MemoryRecord]:
        """Search records by type and tags."""
        results = list(self._records.values())
        if record_type:
            results = [r for r in results if r.record_type == record_type]
        if tags:
            tag_set = set(tags)
            results = [r for r in results if tag_set.intersection(r.tags)]
        return results[:limit]

    def _save(self) -> None:
        """Persist all records to JSON file."""
        data = {k: v.model_dump(mode="json") for k, v in self._records.items()}
        with self._persist_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _load(self) -> None:
        """Load records from JSON file if present."""
        if not self._persist_path.exists():
            return
        try:
            with self._persist_path.open(encoding="utf-8") as f:
                data = json.load(f)
            for k, v in data.items():
                self._records[k] = MemoryRecord(**v)
        except (json.JSONDecodeError, OSError):
            pass
