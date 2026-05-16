"""Threat Intelligence Agent — IOC enrichment and correlation."""

from mavizos.agents.base import BaseAgent
from mavizos.integrations.mock import MockThreatIntelAdapter
from mavizos.models.agent_result import AgentResult
from mavizos.models.ioc import IOC, IOCType
from mavizos.models.workflow import InvestigationContext


class ThreatIntelAgent(BaseAgent):
    """Enrich IOCs via threat intel feeds (mock in demo mode)."""

    name = "threat_intel"
    description = "IOC enrichment, reputation, threat actor mapping"

    def __init__(self) -> None:
        self._ti = MockThreatIntelAdapter()

    async def process(self, context: InvestigationContext) -> AgentResult:
        await self._ti.connect()
        findings: list[str] = []
        enriched: list[IOC] = []

        for alert in context.alerts:
            if alert.ip_address:
                result = await self._ti.enrich_ip(alert.ip_address)
                ioc = IOC(
                    value=alert.ip_address,
                    ioc_type=IOCType.IP,
                    reputation=result.data.get("reputation"),
                    confidence=result.data.get("confidence", 0.0),
                    enrichment=result.data,
                    simulated=result.simulated,
                )
                enriched.append(ioc)
                findings.append(
                    f"IP {alert.ip_address}: {ioc.reputation} "
                    f"(confidence={ioc.confidence:.2f}, simulated={ioc.simulated})"
                )

            if alert.file_hash:
                result = await self._ti.enrich_hash(alert.file_hash)
                ioc = IOC(
                    value=alert.file_hash,
                    ioc_type=IOCType.FILE_HASH,
                    reputation=result.data.get("reputation"),
                    confidence=result.data.get("confidence", 0.0),
                    enrichment=result.data,
                    simulated=result.simulated,
                )
                enriched.append(ioc)
                family = result.data.get("malware_family")
                findings.append(
                    f"Hash {alert.file_hash[:12]}...: {ioc.reputation}"
                    + (f", family={family}" if family else "")
                    + f" (simulated={ioc.simulated})"
                )

        context.iocs.extend(enriched)
        return self._success(
            summary=f"Enriched {len(enriched)} IOC(s) via threat intel (demo/simulated)",
            findings=findings,
            artifacts={"iocs": [i.model_dump() for i in enriched]},
            confidence=0.7 if enriched else 0.3,
        )
