"""Static checks for BootGuardAI installation packaging."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_ROOT = REPO_ROOT / "install" / "bootguardai"

REQUIRED_FILES = [
    INSTALL_ROOT / "windows" / "install.ps1",
    INSTALL_ROOT / "windows" / "uninstall.ps1",
    INSTALL_ROOT / "windows" / "configure-appliance.ps1",
    INSTALL_ROOT / "windows" / "bootguardai-shell.cmd",
    INSTALL_ROOT / "linux" / "install.sh",
    INSTALL_ROOT / "linux" / "uninstall.sh",
    INSTALL_ROOT / "linux" / "bootguardai.service",
    INSTALL_ROOT / "linux" / "bootguardai-getty.service",
    INSTALL_ROOT / "iso" / "build-iso.sh",
    INSTALL_ROOT / "iso" / "build-iso.ps1",
    INSTALL_ROOT / "iso" / "Dockerfile.builder",
    INSTALL_ROOT / "iso" / "README-ISO.md",
    INSTALL_ROOT / "iso" / "chroot-hooks" / "99-bootguardai.sh",
    REPO_ROOT / "INSTALL_BOOTGUARD.md",
    REPO_ROOT / "README_BOOTGUARD.md",
    REPO_ROOT / "bootguardai" / "VERSION",
]

DESTRUCTIVE_PATTERNS = [
    r"remove-item\s+.*system32",
    r"rm\s+-rf\s+/(?:\s|$|\*)",
    r"format\s+[cC]:",
]


@pytest.mark.parametrize("path", REQUIRED_FILES, ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_install_file_exists(path: Path) -> None:
    assert path.is_file(), f"missing: {path}"


def test_version_file():
    version = (REPO_ROOT / "bootguardai" / "VERSION").read_text(encoding="utf-8").strip()
    assert version == "0.1.0"


def test_windows_installer_paths():
    content = (INSTALL_ROOT / "windows" / "install.ps1").read_text(encoding="utf-8")
    assert r"C:\BootGuardAI" in content
    assert "pip install -e" in content
    assert "does NOT" in content or "does not" in content.lower()


def test_linux_installer_paths():
    content = (INSTALL_ROOT / "linux" / "install.sh").read_text(encoding="utf-8")
    assert "/opt/bootguardai" in content
    assert "bootguardai" in content


def test_linux_systemd_unit():
    content = (INSTALL_ROOT / "linux" / "bootguardai.service").read_text(encoding="utf-8")
    assert "/opt/bootguardai" in content
    assert "bootguardai.main" in content


def test_iso_build_naming():
    content = (INSTALL_ROOT / "iso" / "build-iso.sh").read_text(encoding="utf-8")
    assert "bootguardai-os-" in content


def test_no_destructive_commands():
    scripts = list((INSTALL_ROOT / "windows").glob("*.ps1"))
    scripts += list((INSTALL_ROOT / "linux").glob("*.sh"))
    scripts.append(INSTALL_ROOT / "iso" / "build-iso.sh")
    for path in scripts:
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for pattern in DESTRUCTIVE_PATTERNS:
            assert not re.search(pattern, text), f"{path} matches {pattern}"


def test_readme_bootguard_links_install():
    readme = (REPO_ROOT / "README_BOOTGUARD.md").read_text(encoding="utf-8")
    assert "INSTALL_BOOTGUARD.md" in readme
