"""Load /etc/mavizos/ style configuration."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from mavizos.config import get_settings


class OSConfig(BaseModel):
    """MavizOS kernel configuration."""

    hostname: str = "mavizos-soc-01"
    vfs_root: str = "./mavizos_fs"
    shell_prompt: str = "mavizos>"
    boot_banner: bool = True
    demo_mode: bool = True
    max_process_history: int = 100
    services_autostart: bool = True
    extra: dict[str, Any] = Field(default_factory=dict)


def _find_config_paths() -> list[Path]:
    candidates = [
        Path("etc/mavizos/config.json"),
        Path("/etc/mavizos/config.json"),
        Path.home() / ".MavizOS" / "config.json",
    ]
    return [p for p in candidates if p.is_file()]


@lru_cache
def load_os_config() -> OSConfig:
    """Merge defaults, file config, and environment settings."""
    settings = get_settings()
    data: dict[str, Any] = {
        "demo_mode": settings.demo_mode,
        "vfs_root": "./mavizos_fs",
    }
    for path in _find_config_paths():
        try:
            file_data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(file_data, dict):
                data.update(file_data)
        except (json.JSONDecodeError, OSError):
            continue
    return OSConfig(**data)
