# MavizOS ISO build helper for Windows (delegates to WSL2/Linux).
#Requires -Version 5.1
<#
.SYNOPSIS
  Launch ISO build inside WSL2 (recommended) or print manual instructions.
#>
[CmdletBinding()]
param(
    [switch]$NoDocker,
    [string]$WslDistro = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$BuildScript = "/mnt/" + ($RepoRoot -replace ':', '' -replace '\\', '/').ToLower() + "/install/iso/build-iso.sh"

Write-Host "MavizOS ISO Build (Windows helper)"
Write-Host "======================================"
Write-Host ""
Write-Host "A bootable ISO cannot be built natively on Windows."
Write-Host "This script invokes WSL2 to run build-iso.sh."
Write-Host ""

$wsl = Get-Command wsl -ErrorAction SilentlyContinue
if (-not $wsl) {
    Write-Host @"
WSL2 not found. Options:
  1. Install WSL2:  wsl --install
  2. Use a Linux VM and clone the repo
  3. Run Docker on Linux:  bash install/iso/build-iso.sh

See install/iso/README-ISO.md for full instructions.
"@
    exit 1
}

$useDocker = if ($NoDocker) { "0" } else { "auto" }
$distroArg = if ($WslDistro) { "-d $WslDistro" } else { "" }

$cmd = "cd '$($RepoRoot -replace '\\', '/')' 2>/dev/null || cd $(wslpath -a $RepoRoot); export USE_DOCKER=$useDocker; bash install/iso/build-iso.sh"
Write-Host "[*] Running in WSL: bash install/iso/build-iso.sh"
Write-Host ""

if ($WslDistro) {
    wsl -d $WslDistro bash -lc $cmd
} else {
    wsl bash -lc "cd '$(wsl -e wslpath -a $RepoRoot)' && export USE_DOCKER=$useDocker && bash install/iso/build-iso.sh"
}

if ($LASTEXITCODE -eq 0) {
    $iso = Get-ChildItem -Path (Join-Path $RepoRoot "dist") -Filter "mavizos-os-*.iso" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($iso) {
        Write-Host ""
        Write-Host "[OK] ISO: $($iso.FullName)"
    }
}
