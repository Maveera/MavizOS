"""Timeline event models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """Chronological event in an investigation timeline."""

    timestamp: datetime
    source: str
    event_type: str
    description: str
    actor: str | None = None
    target: str | None = None
    severity: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
