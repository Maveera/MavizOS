#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Optional BootGuardAI appliance hardening hints (non-destructive).
#>
param([string]$InstallRoot = "C:\BootGuardAI")

Write-Host "[*] BootGuardAI appliance configuration (informational)"
Write-Host "  - Set BOOTGUARD_DEMO_MODE=false for production collectors"
Write-Host "  - Restrict API port 8081 via Windows Firewall if exposed"
Write-Host "  - Install root: $InstallRoot"
Write-Host "[OK] No system files were modified by this script."
