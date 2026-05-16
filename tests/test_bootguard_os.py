"""BootGuardAI OS shell and kernel tests."""

import pytest

from bootguardai.os.filesystem.vfs import VirtualFilesystem
from bootguardai.os.kernel.kernel import Kernel
from bootguardai.os.shell.commands import CommandContext


@pytest.fixture
def kernel(tmp_path, monkeypatch):
    from bootguardai.config import get_settings

    monkeypatch.setenv("BOOTGUARD_VFS_ROOT", str(tmp_path / "bgfs"))
    get_settings.cache_clear()
    k = Kernel()
    k.boot()
    return k


def test_kernel_boot(kernel):
    assert kernel.booted
    assert len(kernel.registry.list_services()) >= 12


def test_kernel_status(kernel):
    st = kernel.status()
    assert st["booted"] is True
    assert st["agents"] >= 12


def test_vfs_ls_cat(kernel):
    vfs = kernel.vfs
    vfs.write_report("test-001", "# report\nsimulated")
    assert "test-001.md" in vfs.ls("var/reports")
    assert "simulated" in vfs.cat("var/reports/test-001.md")


@pytest.mark.asyncio
async def test_shell_help(kernel):
    ctx = CommandContext(kernel)
    assert await ctx.run("help") is True


@pytest.mark.asyncio
async def test_shell_agents(kernel):
    ctx = CommandContext(kernel)
    assert await ctx.run("agents") is True


@pytest.mark.asyncio
async def test_shell_status(kernel):
    ctx = CommandContext(kernel)
    assert await ctx.run("status") is True


@pytest.mark.asyncio
async def test_shell_windows_analysis(kernel):
    ctx = CommandContext(kernel)
    assert await ctx.run("windows") is True


@pytest.mark.asyncio
async def test_shell_linux_analysis(kernel):
    ctx = CommandContext(kernel)
    assert await ctx.run("linux") is True


@pytest.mark.asyncio
async def test_shell_persistence(kernel):
    ctx = CommandContext(kernel)
    assert await ctx.run("persistence") is True


@pytest.mark.asyncio
async def test_shell_fs(kernel):
    ctx = CommandContext(kernel)
    assert await ctx.run("fs ls") is True


@pytest.mark.asyncio
async def test_shell_shutdown(kernel):
    ctx = CommandContext(kernel)
    assert await ctx.run("shutdown") is False


def test_boot_banner():
    from bootguardai.os.kernel.boot import BOOT_BANNER

    assert "BootGuardAI" in BOOT_BANNER or "Boot" in BOOT_BANNER
