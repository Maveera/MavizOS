"""BootGuardAI — AI Operating System Boot Analysis and Security Intelligence Engine."""

from pathlib import Path

_VERSION_FILE = Path(__file__).resolve().parent / "VERSION"
__version__ = _VERSION_FILE.read_text(encoding="utf-8").strip() if _VERSION_FILE.exists() else "0.1.0"
