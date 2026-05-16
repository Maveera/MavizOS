"""Sample boot alerts for demo and shell."""

SAMPLE_WINDOWS_ALERT = {
    "title": "Suspicious BCD modification detected",
    "description": "Boot Configuration Data store changed outside patch window",
    "os_type": "windows",
    "boot_mode": "uefi",
    "host": "WIN-UEFI-01",
    "secure_boot": True,
    "raw_data": {
        "bcd_modified": True,
        "boot_events": [
            "T+0s UEFI POST complete",
            "T+2s bootmgfw.efi loaded",
            "T+5s BCD read — hash mismatch [simulated]",
        ],
        "loaded_drivers": ["disk.sys", "partmgr.sys"],
    },
    "tags": ["boot", "bcd", "uefi"],
}

SAMPLE_LINUX_ALERT = {
    "title": "GRUB persistence indicator",
    "description": "Unexpected change to grub.cfg with initramfs anomaly",
    "os_type": "linux",
    "boot_mode": "uefi",
    "host": "lin-prod-03",
    "secure_boot": False,
    "raw_data": {
        "grub_cfg_modified": True,
        "initramfs_anomaly": True,
        "persistence_hits": ["systemd unit: suspicious-update.service"],
        "boot_events": ["T+0s GRUB menu", "T+3s kernel v6.8 boot"],
    },
    "tags": ["grub", "persistence", "linux"],
}
