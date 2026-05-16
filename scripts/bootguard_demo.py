#!/usr/bin/env python3
"""BootGuardAI demo — Windows BCD alert + Linux GRUB persistence sample."""

import asyncio
import json

from bootguardai.models.boot_alert import BootAlert
from bootguardai.orchestrator.orchestrator import Orchestrator
from bootguardai.os.shell.samples import SAMPLE_LINUX_ALERT, SAMPLE_WINDOWS_ALERT


async def main() -> None:
    orch = Orchestrator()
    print("=== BootGuardAI Demo (simulated telemetry) ===\n")

    print("--- Windows UEFI: suspicious BCD modification ---")
    win = BootAlert(**SAMPLE_WINDOWS_ALERT)
    win_result = await orch.analyze_windows([win])
    print(f"Analysis: {win_result['analysis_id']}")
    report = win_result.get("report", {})
    print(f"Executive: {report.get('executive_summary', '')[:200]}...")
    print(f"Risks: {report.get('detected_risks', [])}\n")

    print("--- Linux: GRUB persistence sample ---")
    lin = BootAlert(**SAMPLE_LINUX_ALERT)
    lin_result = await orch.analyze_linux([lin])
    print(f"Analysis: {lin_result['analysis_id']}")
    lin_report = lin_result.get("report", {})
    print(f"Persistence: {lin_report.get('persistence_indicators', [])[:3]}")
    print(f"MITRE (from agents): {lin_result.get('agent_results', {}).get('mitre_persistence', {})}\n")

    print("--- Full report sections ---")
    for section in report:
        if section not in ("generated_at", "analysis_id"):
            print(f"  - {section}")
    print("\nAll data labeled simulated: true")


if __name__ == "__main__":
    asyncio.run(main())
