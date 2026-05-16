"""Indicator of Compromise models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IOCType(str, Enum):
    """IOC indicator type."""

    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    USER = "user"
    HOST = "host"
    PROCESS = "process"
    REGISTRY = "registry"
    OTHER = "other"


class IOC(BaseModel):
    """Indicator of Compromise with enrichment metadata."""

    value: str
    ioc_type: IOCType
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    reputation: str | None = None
    confidence: float = 0.0
    sources: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    enrichment: dict[str, Any] = Field(default_factory=dict)
    simulated: bool = False
