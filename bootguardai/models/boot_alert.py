"""Boot analysis alert / sample input."""

from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class OSType(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    UNKNOWN = "unknown"


class BootMode(str, Enum):
    UEFI = "uefi"
    BIOS = "bios"
    UNKNOWN = "unknown"


class BootAlert(BaseModel):
    """Incoming boot security event or analyst-provided context."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    os_type: OSType = OSType.UNKNOWN
    boot_mode: BootMode = BootMode.UNKNOWN
    host: str | None = None
    secure_boot: bool | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    risk_score: int = 0
    classification: str = "requires_analysis"
