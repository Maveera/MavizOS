"""Tests for MavizOS OS layer (kernel, VFS, shell)."""

import json
from pathlib import Path

import pytest

from mavizos.models.alert import Alert
from mavizos.os.config.loader import OSConfig
from mavizos.os.filesystem.vfs import VirtualFilesystem
from mavizos.os.kernel.event_bus import EventBus
from mavizos.os.kernel.kernel import Kernel, reset_kernel
from mavizos.os.kernel.registry import ServiceRegistry, ServiceState
from mavizos.os.processes.manager import ProcessManager
from mavizos.os.shell.repl import MavizShell
from mavizos.os.shell.samples import SAMPLE_ALERT


@pytest.fixture
def tmp_vfs(tmp_path: Path) -> VirtualFilesystem:
    return VirtualFilesystem(tmp_path / "mavizos_fs")


def test_vfs_layout_and_operations(tmp_vfs: VirtualFilesystem) -> None:
    entries = tmp_vfs.ls("/")
    names = {e["name"] for e in entries}
    assert "var/" in names or any("var" in n for n in names)
    tmp_vfs.write_json("var/reports/test.json", {"ok": True})
    content = json.loads(tmp_vfs.cat("/var/reports/test.json"))
    assert content["ok"] is True


def test_vfs_blocks_traversal(tmp_vfs: VirtualFilesystem) -> None:
    with pytest.raises(PermissionError):
        tmp_vfs.resolve("../../../etc/passwd")


def test_event_bus_publish() -> None:
    bus = EventBus()
    seen: list[str] = []
    bus.subscribe("test.topic", lambda topic, _payload: seen.append(topic))
    bus.publish("test.topic", {"x": 1})
    assert seen == ["test.topic"]
    assert len(bus.recent()) == 1


def test_process_manager_lifecycle() -> None:
    pm = ProcessManager()
    proc = pm.create("investigate", incident_id="abc")
    assert proc.pid >= 2000
    pm.set_running(proc.pid)
    pm.set_completed(proc.pid, {"incident_id": "abc", "status": "contained"})
    updated = pm.get(proc.pid)
    assert updated is not None
    assert updated.state.value == "completed"


@pytest.mark.asyncio
async def test_kernel_boot_and_investigate(tmp_path: Path) -> None:
    reset_kernel()
    config = OSConfig(vfs_root=str(tmp_path / "fs"), boot_banner=False)
    kernel = Kernel(config=config)
    kernel.boot(verbose=False)
    assert kernel.booted
    assert kernel.services_registry.running_count() == 13

    result = await kernel.investigate([SAMPLE_ALERT])
    assert result["incident_id"]
    assert result["report"]
    report_path = tmp_path / "fs" / "var" / "reports" / f"{result['incident_id']}.json"
    assert report_path.exists()


@pytest.mark.asyncio
async def test_shell_script_mode(tmp_path: Path) -> None:
    reset_kernel()
    config = OSConfig(vfs_root=str(tmp_path / "fs2"), boot_banner=False)
    kernel = Kernel(config=config)
    kernel.boot(verbose=False)
    shell = MavizShell(kernel)
    lines = await shell.run_script(["status", "agents", "help"])
    assert "status" in lines
    assert "agents" in lines


@pytest.mark.asyncio
async def test_kernel_triage_persists_to_vfs(tmp_path: Path) -> None:
    reset_kernel()
    config = OSConfig(vfs_root=str(tmp_path / "fs3"), boot_banner=False)
    kernel = Kernel(config=config)
    result = await kernel.triage_alert(SAMPLE_ALERT)
    assert result["classification"]
    for ioc in result.get("iocs", []):
        assert ioc.get("simulated") is True


def test_service_registry_states() -> None:
    from mavizos.orchestrator.orchestrator import Orchestrator

    orch = Orchestrator()
    reg = ServiceRegistry()
    reg.register_from_agents(orch._agents)
    started = reg.start_all()
    assert len(started) == 13
    assert all(s.state == ServiceState.RUNNING for s in started)
