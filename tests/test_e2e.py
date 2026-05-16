"""End-to-end tests for MavizOS investigation workflow."""

import pytest
from httpx import ASGITransport, AsyncClient

from mavizos.main import app
from mavizos.models.alert import Alert, AlertSeverity, AlertSource
from mavizos.orchestrator.orchestrator import Orchestrator


@pytest.fixture
def orchestrator() -> Orchestrator:
    return Orchestrator()


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_agents():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/agents")
    assert resp.status_code == 200
    agents = resp.json()
    assert len(agents) >= 13
    names = {a["name"] for a in agents}
    assert "alert_triage" in names
    assert "threat_intel" in names
    assert "reporting" in names


@pytest.mark.asyncio
async def test_triage_alert(sample_alert_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/alerts/triage", json=sample_alert_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["classification"] in ("suspicious_activity", "requires_investigation", "likely_false_positive")
    assert data["priority_score"] is not None


@pytest.mark.asyncio
async def test_full_investigation(orchestrator, sample_alert_data):
    alert = Alert(**sample_alert_data)
    result = await orchestrator.investigate([alert])

    assert "incident_id" in result
    assert result["report"] is not None
    report = result["report"]

    # Verify 14-section report structure
    required_sections = [
        "executive_summary",
        "severity",
        "confidence",
        "technical_findings",
        "timeline",
        "affected_assets",
        "iocs",
        "mitre_mapping",
        "root_cause_analysis",
        "recommended_actions",
        "automated_actions_taken",
        "detection_opportunities",
        "analyst_notes",
        "references",
    ]
    for section in required_sections:
        assert section in report, f"Missing report section: {section}"

    assert report["confidence"] > 0
    assert len(result["agent_results"]) >= 10


@pytest.mark.asyncio
async def test_investigation_api(sample_alert_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/investigate",
            json={"alerts": [sample_alert_data]},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["report"]["executive_summary"]
    assert "incident_id" in data


@pytest.mark.asyncio
async def test_approval_gate_for_destructive_actions(orchestrator, sample_alert_data):
    alert = Alert(**sample_alert_data)
    result = await orchestrator.investigate([alert])
    pending = result.get("pending_approvals", [])
    assert len(pending) >= 1
    assert pending[0]["action_type"] in ("firewall_block", "host_isolation")


@pytest.mark.asyncio
async def test_detection_generation(sample_alert_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/detections/generate", json=sample_alert_data)
    assert resp.status_code == 200
    data = resp.json()
    assert "rules" in data
    assert "sigma" in data["rules"]


@pytest.mark.asyncio
async def test_threat_intel_simulated(sample_alert_data):
    alert = Alert(**sample_alert_data)
    orch = Orchestrator()
    triage = await orch.triage_alert(alert)
    assert triage["iocs"]
    for ioc in triage["iocs"]:
        assert ioc.get("simulated") is True
