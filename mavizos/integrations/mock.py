"""Mock integration adapters for demo and testing."""

from datetime import UTC, datetime, timedelta
from typing import Any

from mavizos.integrations.base import (
    IntegrationResult,
    SIEMAdapter,
    ThreatIntelAdapter,
)


class MockSIEMAdapter(SIEMAdapter):
    """Simulated Splunk/Sentinel-style SIEM adapter."""

    vendor = "mock_siem"

    async def connect(self) -> bool:
        return True

    async def health_check(self) -> IntegrationResult:
        return IntegrationResult(success=True, data={"status": "ok"}, simulated=True)

    async def search_events(
        self,
        query: str,
        time_range_hours: int = 24,
    ) -> IntegrationResult:
        now = datetime.now(UTC)
        events = [
            {
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "source": "mock_siem",
                "event_type": "process_create",
                "host": "WORKSTATION-42",
                "user": "jsmith",
                "process": "powershell.exe",
                "command_line": "-enc <base64>",
                "query_matched": query,
            },
            {
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "source": "mock_siem",
                "event_type": "network_connection",
                "host": "WORKSTATION-42",
                "dest_ip": "203.0.113.50",
                "dest_port": 443,
            },
        ]
        return IntegrationResult(
            success=True,
            data={"events": events, "count": len(events), "time_range_hours": time_range_hours},
            simulated=True,
        )

    async def get_alert(self, alert_id: str) -> IntegrationResult:
        return IntegrationResult(
            success=True,
            data={"alert_id": alert_id, "status": "open", "source": "mock_siem"},
            simulated=True,
        )


class MockThreatIntelAdapter(ThreatIntelAdapter):
    """Simulated VirusTotal/OTX-style TI adapter — all data marked simulated."""

    vendor = "mock_threat_intel"

    async def connect(self) -> bool:
        return True

    async def health_check(self) -> IntegrationResult:
        return IntegrationResult(success=True, simulated=True)

    async def enrich_ip(self, ip: str) -> IntegrationResult:
        return IntegrationResult(
            success=True,
            data=self._mock_ip_enrichment(ip),
            simulated=True,
        )

    async def enrich_hash(self, file_hash: str) -> IntegrationResult:
        return IntegrationResult(
            success=True,
            data=self._mock_hash_enrichment(file_hash),
            simulated=True,
        )

    async def enrich_domain(self, domain: str) -> IntegrationResult:
        return IntegrationResult(
            success=True,
            data={
                "domain": domain,
                "reputation": "suspicious",
                "category": "c2_candidate",
                "confidence": 0.65,
                "note": "SIMULATED enrichment — not live threat intel",
            },
            simulated=True,
        )

    def _mock_ip_enrichment(self, ip: str) -> dict[str, Any]:
        """Generate deterministic simulated IP enrichment."""
        suspicious = ip.startswith("203.") or ip.startswith("198.51.")
        return {
            "ip": ip,
            "reputation": "malicious" if suspicious else "unknown",
            "abuse_score": 85 if suspicious else 10,
            "country": "XX",
            "asn": "AS00000 (simulated)",
            "tags": ["simulated", "c2_candidate"] if suspicious else ["simulated"],
            "confidence": 0.75 if suspicious else 0.3,
            "note": "SIMULATED enrichment — not live threat intel",
        }

    def _mock_hash_enrichment(self, file_hash: str) -> dict[str, Any]:
        """Generate deterministic simulated hash enrichment."""
        known_malicious_prefix = "a1b2c3"
        is_malicious = file_hash.lower().startswith(known_malicious_prefix)
        return {
            "hash": file_hash,
            "detection_ratio": "45/70" if is_malicious else "0/70",
            "malware_family": "Simulated.Trojan.Generic" if is_malicious else None,
            "reputation": "malicious" if is_malicious else "unknown",
            "confidence": 0.8 if is_malicious else 0.2,
            "note": "SIMULATED enrichment — not live threat intel",
        }
