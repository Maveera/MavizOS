"""Integration adapters for external security platforms."""

from mavizos.integrations.base import IntegrationAdapter
from mavizos.integrations.mock import MockSIEMAdapter, MockThreatIntelAdapter

__all__ = ["IntegrationAdapter", "MockSIEMAdapter", "MockThreatIntelAdapter"]
