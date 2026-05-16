# BootGuardAI ISO build wrapper (Windows)
$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$Version = (Get-Content (Join-Path $Root "bootguardai\VERSION") -Raw).Trim()
$Out = Join-Path $Root "dist\bootguardai-os-$Version.iso"
New-Item -ItemType Directory -Force -Path (Join-Path $Root "dist") | Out-Null
Write-Host "[*] BootGuardAI ISO: use WSL or Docker:"
Write-Host "  wsl bash install/bootguardai/iso/build-iso.sh"
Write-Host "  Expected artifact: $Out"
