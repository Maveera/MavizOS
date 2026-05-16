#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Install BootGuardAI to C:\BootGuardAI (non-destructive).

.DESCRIPTION
  Copies BootGuardAI, creates venv, pip install -e, optional autostart.
  Does NOT delete System32, format drives, or wipe the OS.
#>
[CmdletBinding()]
param(
    [string]$SourceRoot = "",
    [string]$InstallRoot = "C:\BootGuardAI",
    [switch]$Autostart = $true,
    [switch]$SkipPythonInstall
)

$ErrorActionPreference = "Stop"

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-BootGuardVersion {
    param([string]$Root)
    $vf = Join-Path $Root "bootguardai\VERSION"
    if (Test-Path $vf) { return (Get-Content $vf -Raw).Trim() }
    return "0.1.0"
}

function Ensure-Python {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) {
        $ver = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        $p = $ver.Split(".")
        if ([int]$p[0] -ge 3 -and [int]$p[1] -ge 11) { return $py.Source }
    }
    if ($SkipPythonInstall) { throw "Python 3.11+ required." }
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        & winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")
    }
    return (Get-Command python).Source
}

function Sync-Project {
    param([string]$From, [string]$To)
    New-Item -ItemType Directory -Force -Path $To | Out-Null
    $excludeDirs = @(".git", ".venv", "__pycache__", ".pytest_cache", "dist", "build")
    $xd = ($excludeDirs | ForEach-Object { "/XD", $_ }) -join " "
    cmd /c "robocopy `"$From`" `"$To`" /MIR /NFL /NDL /NJH /NJS /NP $xd" | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed: $LASTEXITCODE" }
}

if (-not (Test-Admin)) { throw "Run as Administrator." }
if (-not $SourceRoot) {
    $SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
}
$version = Get-BootGuardVersion -Root $SourceRoot
Write-Host "[*] Installing BootGuardAI v$version to $InstallRoot"
Write-Host "[*] This installer does NOT modify Windows system directories."

$python = Ensure-Python
Sync-Project -From $SourceRoot -To $InstallRoot
$venvPy = Join-Path $InstallRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    & $python -m venv (Join-Path $InstallRoot ".venv")
}
& $venvPy -m pip install --upgrade pip wheel setuptools | Out-Null
& $venvPy -m pip install -e $InstallRoot
New-Item -ItemType Directory -Force -Path (Join-Path $InstallRoot "data") | Out-Null

if ($Autostart) {
    $launcher = Join-Path $PSScriptRoot "bootguardai-shell.cmd"
    $taskName = "BootGuardAI-Shell-Autostart"
    Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$launcher`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Description "BootGuardAI v$version" | Out-Null
    Write-Host "[OK] Autostart task: $taskName"
}

Write-Host "[OK] BootGuardAI installed to $InstallRoot"
Write-Host "  Shell:  $InstallRoot\.venv\Scripts\python.exe -m bootguardai"
Write-Host "  API:    $InstallRoot\.venv\Scripts\python.exe -m uvicorn bootguardai.main:app --port 8081"
