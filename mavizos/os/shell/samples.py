"""Sample alerts for shell demo operations."""

from mavizos.models.alert import Alert, AlertSeverity, AlertSource

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
