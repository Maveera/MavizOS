#!/usr/bin/env python3
"""MavizOS end-to-end demo script."""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mavizos.models.alert import Alert, AlertSeverity, AlertSource
from mavizos.orchestrator.orchestrator import Orchestrator


SAMPLE_ALERT = Alert(
    title="Suspicious encoded PowerShell execution",
    description="Encoded PowerShell with network connection to external IP",
    severity=AlertSeverity.HIGH,
    source=AlertSource.EDR,
    source_system="crowdstrike",
    host="WORKSTATION-42",
    user="jsmith",
    ip_address="203.0.113.50",
    process="powershell.exe",
    file_hash="a1b2c3d4e5f6789012345678abcdef01",
    raw_data={"command_line": "powershell.exe -enc SGVsbG8="},
    tags=["execution", "powershell", "c2"],
)


async def main() -> None:
    print("=" * 60)
    print("mavizos — Autonomous Agentic AI SOC Demo")
    print("=" * 60)

    orch = Orchestrator()
    print(f"\nRegistered agents: {len(orch.list_agents())}")

    print("\n--- Alert Triage ---")
    triage = await orch.triage_alert(SAMPLE_ALERT)
    print(json.dumps(triage, indent=2, default=str))

    print("\n--- Full Investigation (10-step pipeline) ---")
    result = await orch.investigate([SAMPLE_ALERT])
    print(f"Incident ID: {result['incident_id']}")
    print(f"Status: {result['status']}")
    print(f"Agents executed: {len(result['agent_results'])}")

    if result.get("report"):
        report = result["report"]
        print("\n--- Investigation Report (14 sections) ---")
        print(f"Executive Summary: {report['executive_summary'][:200]}...")
        print(f"Severity: {report['severity']}")
        print(f"Confidence: {report['confidence']}")
        print(f"MITRE Techniques: {report['mitre_mapping']}")
        print(f"IOCs: {len(report['iocs'])} (all simulated in demo)")
        print(f"Timeline Events: {len(report['timeline'])}")
        print(f"Recommended Actions: {report['recommended_actions']}")

    pending = result.get("pending_approvals", [])
    if pending:
        print(f"\n--- Pending Approvals ({len(pending)}) ---")
        for req in pending:
            print(f"  [{req['action_type']}] {req['description']} (id={req['id'][:8]})")

    print("\n--- Threat Hunt ---")
    hunt = await orch.hunt("Hunt for lateral movement from WORKSTATION-42")
    print(json.dumps(hunt, indent=2, default=str))

    print("\nDemo complete. Start API: python -m mavizos.main")


if __name__ == "__main__":
    asyncio.run(main())
