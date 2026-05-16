"""Pytest configuration."""

import pytest


@pytest.fixture
def sample_alert_data() -> dict:
    """Sample suspicious PowerShell alert."""
    return {
        "title": "Suspicious encoded PowerShell execution",
        "description": "Encoded PowerShell command detected on endpoint",
        "severity": "high",
        "source": "edr",
        "source_system": "crowdstrike",
        "host": "WORKSTATION-42",
        "user": "jsmith",
        "ip_address": "203.0.113.50",
        "process": "powershell.exe",
        "file_hash": "a1b2c3d4e5f6789012345678abcdef01",
        "raw_data": {"command_line": "powershell.exe -enc SGVsbG8="},
        "tags": ["execution", "powershell"],
    }
