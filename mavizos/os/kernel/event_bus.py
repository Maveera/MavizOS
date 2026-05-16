"""In-kernel publish/subscribe event bus."""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger(__name__)

EventHandler = Callable[[str, dict[str, Any]], None]


@dataclass
class BusEvent:
    """Recorded kernel event."""

    topic: str
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    """Lightweight pub/sub for OS-level notifications."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: list[BusEvent] = []
        self._max_history = 500

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        """Register handler for topic (use '*' for all)."""
        self._handlers[topic].append(handler)

    def publish(self, topic: str, payload: dict[str, Any] | None = None) -> None:
        """Emit event to subscribers and audit history."""
        data = payload or {}
        event = BusEvent(topic=topic, payload=data)
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]
        logger.debug("event_bus: %s %s", topic, data)
        for handler in self._handlers.get(topic, []):
            handler(topic, data)
        for handler in self._handlers.get("*", []):
            handler(topic, data)

    def recent(self, limit: int = 20) -> list[BusEvent]:
        """Return recent events."""
        return self._history[-limit:]
