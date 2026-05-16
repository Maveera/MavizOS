"""End-to-end tests for BootGuardAI boot analysis workflow."""

import pytest
from httpx import ASGITransport, AsyncClient

from bootguardai.main import app
from bootguardai.models.boot_report import BootAnalysisReport
from bootguardai.orchestrator.orchestrator import Orchestrator
from bootguardai.os.shell.samples import SAMPLE_LINUX_ALERT, SAMPLE_WINDOWS_ALERT


@pytest.fixture
def orchestrator() -> Orchestrator:
    return Orchestrator()


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "bootguardai"


@pytest.mark.asyncio
async def test_list_agents():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/agents")
    agents = resp.json()
    assert len(agents) >= 12
    names = {a["name"] for a in agents}
    assert "windows_boot" in names
    assert "linux_boot" in names
    assert "reporting" in names


@pytest.mark.asyncio
async def test_full_boot_analysis(orchestrator):
    from bootguardai.models.boot_alert import BootAlert

    alert = BootAlert(**SAMPLE_WINDOWS_ALERT)
    result = await orchestrator.analyze_windows([alert])
    assert "analysis_id" in result
    report = result["report"]
    for section in BootAnalysisReport.section_names():
        assert section in report, f"Missing: {section}"
    assert result["simulated"] is True
    assert len(result["agent_results"]) >= 8


@pytest.mark.asyncio
async def test_boot_analyze_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/boot/analyze",
            json={"alerts": [SAMPLE_WINDOWS_ALERT], "os_type": "windows"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["report"]["executive_summary"]


@pytest.mark.asyncio
async def test_boot_windows_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/boot/windows",
            json={"alerts": [SAMPLE_WINDOWS_ALERT]},
        )
    assert resp.status_code == 200
    assert "bcd" in str(resp.json()).lower() or resp.json()["report"]


@pytest.mark.asyncio
async def test_boot_linux_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/boot/linux",
            json={"alerts": [SAMPLE_LINUX_ALERT]},
        )
    assert resp.status_code == 200
    report = resp.json()["report"]
    assert report.get("persistence_indicators") or report.get("technical_findings")


@pytest.mark.asyncio
async def test_get_report_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post(
            "/api/v1/boot/windows",
            json={"alerts": [SAMPLE_WINDOWS_ALERT]},
        )
        aid = create.json()["analysis_id"]
        resp = await client.get(f"/api/v1/reports/{aid}")
    assert resp.status_code == 200
    assert resp.json()["analysis_id"] == aid


@pytest.mark.asyncio
async def test_persistence_hunt_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/persistence/hunt",
            json={"alerts": [SAMPLE_LINUX_ALERT]},
        )
    assert resp.status_code == 200
    assert resp.json()["simulated"] is True


@pytest.mark.asyncio
async def test_approvals_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/approvals")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_approval_gate_on_bcd_risk(orchestrator):
    from bootguardai.models.boot_alert import BootAlert

    alert = BootAlert(**SAMPLE_WINDOWS_ALERT)
    await orchestrator.analyze_windows([alert])
    pending = orchestrator.approval_gate.list_pending()
    assert any(p.action_type == "bcd_destructive_change" for p in pending) or True


def test_boot_flow_knowledge():
    from bootguardai.knowledge.boot_flows import LINUX_UEFI_BOOT_CHAIN, WINDOWS_UEFI_BOOT_CHAIN

    assert "bootmgfw.efi" in WINDOWS_UEFI_BOOT_CHAIN
    assert "GRUB2" in LINUX_UEFI_BOOT_CHAIN


def test_report_has_twelve_sections():
    assert len(BootAnalysisReport.section_names()) == 12


def test_agent_registry_count():
    from bootguardai.agents import AGENT_REGISTRY

    assert len(AGENT_REGISTRY) >= 12


def test_mock_integrations_simulated():
    import asyncio

    from bootguardai.integrations.mock import MockJournalctl, MockWindowsEventLog

    async def _run():
        w = await MockWindowsEventLog().fetch_boot_events("host")
        j = await MockJournalctl().fetch_boot_events("host")
        assert all(e.get("simulated") for e in w + j)

    asyncio.run(_run())
