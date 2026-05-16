"""Embedded boot flow knowledge (reference data, not live telemetry)."""

WINDOWS_UEFI_BOOT_CHAIN: list[str] = [
    "Power ON",
    "UEFI firmware",
    "POST",
    "ESP (EFI System Partition)",
    "bootmgfw.efi",
    "BCD (Boot Configuration Data)",
    "winload.efi",
    "ntoskrnl.exe",
    "HAL + driver load chain",
    "smss.exe",
    "winlogon.exe",
    "explorer.exe",
]

LINUX_UEFI_BOOT_CHAIN: list[str] = [
    "Power ON",
    "UEFI firmware",
    "POST",
    "EFI partition",
    "GRUB2",
    "Linux kernel",
    "initramfs",
    "systemd",
    "target units / services",
    "login",
]

BOOT_STAGES = {
    "windows": WINDOWS_UEFI_BOOT_CHAIN,
    "linux": LINUX_UEFI_BOOT_CHAIN,
}
