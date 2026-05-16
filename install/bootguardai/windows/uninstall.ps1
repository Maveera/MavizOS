#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Uninstall BootGuardAI from C:\BootGuardAI (safe — does not touch System32).
#>
param([string]$InstallRoot = "C:\BootGuardAI")

$ErrorActionPreference = "Stop"
$taskName = "BootGuardAI-Shell-Autostart"
Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
Write-Host "[OK] Removed scheduled task: $taskName"

if (Test-Path $InstallRoot) {
    Write-Host "[*] Removing $InstallRoot (BootGuardAI only)..."
    Remove-Item -Recurse -Force $InstallRoot
    Write-Host "[OK] BootGuardAI uninstalled."
} else {
    Write-Host "[*] Install path not found: $InstallRoot"
}
