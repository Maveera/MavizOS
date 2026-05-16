#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Roll back MavizOS Windows appliance installation.

.DESCRIPTION
  Removes scheduled task, desktop shortcut, and optionally the C:\MavizOS tree.
  Does NOT modify Windows system directories or uninstall Python.
#>
[CmdletBinding()]
param(
    [string]$InstallRoot = "C:\MavizOS",
    [switch]$RemoveInstallDir,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$taskName = "MavizOS-Shell-Autostart"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "[OK] Removed scheduled task: $taskName"
}

$desktop = [Environment]::GetFolderPath("Desktop")
$lnk = Join-Path $desktop "mavizos.lnk"
if (Test-Path $lnk) {
    Remove-Item $lnk -Force
    Write-Host "[OK] Removed desktop shortcut"
}

$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
if (Get-ItemProperty -Path $runKey -Name "MavizOS" -ErrorAction SilentlyContinue) {
    Remove-ItemProperty -Path $runKey -Name "MavizOS" -ErrorAction SilentlyContinue
    Write-Host "[OK] Removed Run key autostart entry"
}

$marker = Join-Path $InstallRoot "install\.installed-windows.json"
if (Test-Path $marker) {
    Remove-Item $marker -Force
}

if ($RemoveInstallDir) {
    if (-not $Force) {
        Write-Warning "This will delete $InstallRoot and all MavizOS data under it."
        $confirm = Read-Host "Type YES to confirm"
        if ($confirm -ne "YES") {
            Write-Host "Aborted. Install directory kept."
            exit 0
        }
    }
    if (Test-Path $InstallRoot) {
        Remove-Item -LiteralPath $InstallRoot -Recurse -Force
        Write-Host "[OK] Removed $InstallRoot"
    }
} else {
    Write-Host "Install directory preserved: $InstallRoot"
    Write-Host "Re-run with -RemoveInstallDir to delete the installation tree."
}

Write-Host "MavizOS Windows uninstall finished."
