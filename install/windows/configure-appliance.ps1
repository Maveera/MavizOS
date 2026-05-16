#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Optional MavizOS appliance hardening (non-destructive).

.DESCRIPTION
  Disables common third-party startup entries (with backup), sets environment hints,
  and documents kiosk/shell-replacement options. Does NOT delete system32 or format drives.

.PARAMETER InstallRoot
  MavizOS installation path.

.PARAMETER DisableStartupApps
  Disable non-Microsoft Run/RunOnce entries for current user (backup created).

.PARAMETER SetSentinelFirst
  Add mavizos shell to HKCU Run (in addition to scheduled task).

.PARAMETER KioskHintsOnly
  Only print kiosk / Assigned Access guidance without registry changes.
#>
[CmdletBinding()]
param(
    [string]$InstallRoot = "C:\MavizOS",
    [switch]$DisableStartupApps,
    [switch]$SetSentinelFirst,
    [switch]$KioskHintsOnly
)

$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host " MavizOS Appliance Configuration"
Write-Host "========================================"
Write-Host ""
Write-Host "WARNING: Review each change. This script never deletes Windows system files."
Write-Host "The Windows kernel and desktop remain; MavizOS becomes the default SOC experience."
Write-Host ""

if ($KioskHintsOnly) {
    Write-Host @"
Kiosk / dedicated workstation options (manual):
  1. Windows Assigned Access: Settings -> Accounts -> Other users -> Set up assigned access
  2. Replace Explorer shell (advanced): backup HKLM\...\Winlogon Shell, set to mavizos-shell.cmd
  3. Full-screen browser to http://localhost:8000/desktop after 'mavizos serve'
  4. Group Policy: disable consumer features, USB storage if required by policy

Revert: restore Winlogon Shell = explorer.exe and remove Assigned Access.
"@
    exit 0
}

$launcher = Join-Path $InstallRoot "install\windows\mavizos-shell.cmd"
if (-not (Test-Path $launcher)) {
    $launcher = Join-Path $PSScriptRoot "mavizos-shell.cmd"
}

if ($SetSentinelFirst) {
    $runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    New-Item -Path $runKey -Force | Out-Null
    Set-ItemProperty -Path $runKey -Name "MavizOS" -Value "`"$launcher`""
    Write-Host "[OK] HKCU Run -> mavizos shell"
}

if ($DisableStartupApps) {
    $backupDir = Join-Path $InstallRoot "install\backups"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupFile = Join-Path $backupDir "startup-run-backup-$stamp.json"

    $runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    $props = Get-ItemProperty -Path $runKey -ErrorAction SilentlyContinue
    $backup = @{}
    if ($props) {
        $props.PSObject.Properties | Where-Object {
            $_.Name -notin @("PSPath", "PSParentPath", "PSChildName", "PSDrive", "PSProvider")
        } | ForEach-Object {
            $backup[$_.Name] = $_.Value
        }
    }
    $backup | ConvertTo-Json | Set-Content $backupFile -Encoding UTF8
    Write-Host "[OK] Startup backup: $backupFile"

    $skip = @("MavizOS", "SecurityHealth", "Windows Defender")
    foreach ($name in $backup.Keys) {
        if ($skip -contains $name) { continue }
        if ($name -match "^(OneDrive|Discord|Spotify|Steam|Epic)") {
            Remove-ItemProperty -Path $runKey -Name $name -ErrorAction SilentlyContinue
            Write-Host "[*] Disabled startup: $name"
        }
    }
    Write-Host "Only selected third-party Run entries were removed. Restore from backup JSON if needed."
}

$applianceMarker = Join-Path $InstallRoot "install\.appliance-configured"
@{
    configuredAt = (Get-Date).ToUniversalTime().ToString("o")
    installRoot  = $InstallRoot
} | ConvertTo-Json | Set-Content $applianceMarker -Encoding UTF8

Write-Host ""
Write-Host "Appliance configuration complete."
Write-Host "For stricter lockdown, re-run with -KioskHintsOnly and follow printed guidance."
