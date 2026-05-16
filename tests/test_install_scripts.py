"""Static checks for MavizOS installation packaging (no installer execution)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_ROOT = REPO_ROOT / "install"

REQUIRED_FILES = [
    INSTALL_ROOT / "windows" / "install.ps1",
    INSTALL_ROOT / "windows" / "uninstall.ps1",
    INSTALL_ROOT / "windows" / "configure-appliance.ps1",
    INSTALL_ROOT / "windows" / "mavizos-shell.cmd",
    INSTALL_ROOT / "linux" / "install.sh",
    INSTALL_ROOT / "linux" / "uninstall.sh",
    INSTALL_ROOT / "linux" / "mavizos.service",
    INSTALL_ROOT / "linux" / "mavizos-getty.service",
    INSTALL_ROOT / "iso" / "build-iso.sh",
    INSTALL_ROOT / "iso" / "build-iso.ps1",
    INSTALL_ROOT / "iso" / "Dockerfile.builder",
    INSTALL_ROOT / "iso" / "README-ISO.md",
    INSTALL_ROOT / "iso" / "chroot-hooks" / "99-mavizos.sh",
    REPO_ROOT / "INSTALL.md",
    REPO_ROOT / "VERSION",
]

DESTRUCTIVE_PATTERNS = [
    r"remove-item\s+.*system32",
    r"rm\s+-rf\s+/(?:\s|$|\*)",
    r"format\s+[cC]:",
    r"remove-item\s+.*\\windows\\",
    r"diskpart\s+/",
]


@pytest.mark.parametrize("path", REQUIRED_FILES, ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_install_file_exists(path: Path) -> None:
    assert path.is_file(), f"missing: {path}"


def test_version_file_matches_pyproject() -> None:
    version_file = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    assert match, "version not found in pyproject.toml"
    assert version_file == match.group(1)


def test_windows_installer_key_strings() -> None:
    content = (INSTALL_ROOT / "windows" / "install.ps1").read_text(encoding="utf-8")
    assert r"C:\MavizOS" in content
    assert "pip install -e" in content
    assert "ScheduledTask" in content or "Register-ScheduledTask" in content
    assert "RunAsAdministrator" in content
    assert "does NOT" in content or "does not" in content.lower()


def test_windows_uninstall_safe() -> None:
    content = (INSTALL_ROOT / "windows" / "uninstall.ps1").read_text(encoding="utf-8")
    assert "MavizOS-Shell-Autostart" in content
    _assert_not_destructive(content, "windows/uninstall.ps1")


def test_linux_installer_key_strings() -> None:
    content = (INSTALL_ROOT / "linux" / "install.sh").read_text(encoding="utf-8")
    assert "/opt/mavizos" in content
    assert "MavizOS" in content
    assert "systemctl" in content
    assert "python3 -m venv" in content or "python3 -m venv" in content


def test_linux_systemd_unit() -> None:
    content = (INSTALL_ROOT / "linux" / "mavizos.service").read_text(encoding="utf-8")
    assert "mavizos serve" in content
    assert "User=mavizos" in content
    assert "/opt/mavizos" in content


def test_iso_build_outputs_dist() -> None:
    content = (INSTALL_ROOT / "iso" / "build-iso.sh").read_text(encoding="utf-8")
    assert "mavizos-os-" in content
    assert "dist/" in content
    assert "live-build" in content or "lb build" in content or "lb config" in content


def test_iso_chroot_installs_MavizOS() -> None:
    content = (INSTALL_ROOT / "iso" / "chroot-hooks" / "99-mavizos.sh").read_text(encoding="utf-8")
    assert "/opt/mavizos" in content
    assert "pip" in content


def test_install_md_covers_platforms() -> None:
    content = (REPO_ROOT / "INSTALL.md").read_text(encoding="utf-8")
    for token in ("Windows", "Linux", "ISO", "mermaid", "uninstall", "Safety"):
        assert token in content, f"INSTALL.md missing: {token}"


def test_readme_links_install_md() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "INSTALL.md" in readme
    assert "Production Installation" in readme


def test_no_destructive_wipe_commands() -> None:
    scripts = list((INSTALL_ROOT / "windows").glob("*.ps1"))
    scripts += list((INSTALL_ROOT / "linux").glob("*.sh"))
    scripts.append(INSTALL_ROOT / "iso" / "build-iso.sh")
    for path in scripts:
        text = path.read_text(encoding="utf-8", errors="replace")
        _assert_not_destructive(text, path.relative_to(REPO_ROOT).as_posix())


def _assert_not_destructive(text: str, label: str) -> None:
    lowered = text.lower()
    for pattern in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, lowered):
            pytest.fail(f"{label} matches destructive pattern: {pattern}")
