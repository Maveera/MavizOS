#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Install MavizOS as a dedicated Windows SOC appliance (non-destructive).

.DESCRIPTION
  Copies MavizOS to C:\MavizOS, creates a Python venv, installs the package,
  registers autostart (scheduled task), and optional desktop shortcut.
  Does NOT delete Windows system files or format drives.

.PARAMETER SourceRoot
  Path to the MavizOS repository (default: two levels above this script).

.PARAMETER InstallRoot
  Installation directory (default: C:\MavizOS).

.PARAMETER Autostart
  Register logon scheduled task to launch mavizos shell.

.PARAMETER SkipPythonInstall
  Do not attempt to install Python via winget/chocolatey.

.PARAMETER ConfigureAppliance
  Run configure-appliance.ps1 after install (startup hardening, optional kiosk hints).
#>
[CmdletBinding()]
param(
    [string]$SourceRoot = "",
    [string]$InstallRoot = "C:\MavizOS",
    [switch]$Autostart = $true,
    [switch]$SkipPythonInstall,
    [switch]$ConfigureAppliance
)

$ErrorActionPreference = "Stop"

function Get-SentinelVersion {
    param([string]$Root)
    $versionFile = Join-Path $Root "VERSION"
    if (Test-Path $versionFile) {
        return (Get-Content $versionFile -Raw).Trim()
    }
    $pyproject = Join-Path $Root "pyproject.toml"
    if (Test-Path $pyproject) {
        $content = Get-Content $pyproject -Raw
        if ($content -match 'version\s*=\s*"([^"]+)"') {
            return $Matches[1]
        }
    }
    return "0.0.0"
}

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Ensure-Python {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) {
        $ver = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        $parts = $ver.Split(".")
        if ([int]$parts[0] -ge 3 -and [int]$parts[1] -ge 11) {
            Write-Host "[OK] Python $ver found: $($py.Source)"
            return $py.Source
        }
        Write-Warning "Python found but $ver < 3.11 required."
    }

    if ($SkipPythonInstall) {
        throw "Python 3.11+ not found. Install from https://www.python.org/downloads/ or re-run without -SkipPythonInstall."
    }

    Write-Host "[*] Attempting Python 3.12 via winget..."
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        & winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")
        $py = Get-Command python -ErrorAction SilentlyContinue
        if ($py) { return $py.Source }
    }

    $choco = Get-Command choco -ErrorAction SilentlyContinue
    if ($choco) {
        Write-Host "[*] Attempting Python via Chocolatey..."
        & choco install python312 -y
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")
        $py = Get-Command python -ErrorAction SilentlyContinue
        if ($py) { return $py.Source }
    }

    throw @"
Python 3.11+ is required. Install manually, then re-run:
  winget install Python.Python.3.12
  choco install python312
"@
}

function Sync-Project {
    param(
        [string]$From,
        [string]$To
    )
    if (-not (Test-Path $From)) {
        throw "Source not found: $From"
    }
    New-Item -ItemType Directory -Force -Path $To | Out-Null

    $excludeDirs = @(".git", ".venv", "__pycache__", ".pytest_cache", "dist", "build", "node_modules")
    $excludeFiles = @("*.pyc", "*.pyo")

    Write-Host "[*] Syncing $From -> $To"
    $robolog = Join-Path $env:TEMP "MavizOS-robocopy.log"
    $xd = ($excludeDirs | ForEach-Object { "/XD", $_ }) -join " "
    $xf = ($excludeFiles | ForEach-Object { "/XF", $_ }) -join " "
    $cmd = "robocopy `"$From`" `"$To`" /MIR /NFL /NDL /NJH /NJS /NP $xd $xf"
    cmd /c $cmd | Out-Null
    $code = $LASTEXITCODE
    if ($code -ge 8) {
        throw "robocopy failed with exit code $code (see $robolog)"
    }
}

function Install-Venv {
    param(
        [string]$PythonExe,
        [string]$Root
    )
    $venv = Join-Path $Root ".venv"
    if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) {
        Write-Host "[*] Creating virtual environment..."
        & $PythonExe -m venv $venv
    }
    $venvPy = Join-Path $venv "Scripts\python.exe"
    Write-Host "[*] Installing MavizOS package (editable)..."
    & $venvPy -m pip install --upgrade pip wheel setuptools | Out-Null
    & $venvPy -m pip install -e $Root
    return $venvPy
}

function Set-EnvFile {
    param([string]$Root)
    $example = Join-Path $Root ".env.example"
    $envFile = Join-Path $Root ".env"
    if ((Test-Path $example) -and -not (Test-Path $envFile)) {
        Copy-Item $example $envFile
        Write-Host "[*] Created .env from .env.example"
    }
    $data = Join-Path $Root "data"
    New-Item -ItemType Directory -Force -Path $data | Out-Null
}

function Register-Autostart {
    param(
        [string]$Root,
        [string]$Version
    )
    $launcher = Join-Path $Root "install\windows\mavizos-shell.cmd"
    if (-not (Test-Path $launcher)) {
        $launcher = Join-Path $PSScriptRoot "mavizos-shell.cmd"
    }
    $taskName = "MavizOS-Shell-Autostart"
    $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$launcher`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "MavizOS v$Version shell autostart" | Out-Null
    Write-Host "[OK] Scheduled task registered: $taskName"
}

function New-DesktopShortcut {
    param([string]$Launcher, [string]$Version)
    $wsh = New-Object -ComObject WScript.Shell
    $desktop = [Environment]::GetFolderPath("Desktop")
    $lnk = Join-Path $desktop "mavizos.lnk"
    $sc = $wsh.CreateShortcut($lnk)
    $sc.TargetPath = $Launcher
    $sc.WorkingDirectory = "C:\MavizOS"
    $sc.Description = "MavizOS AI SOC Shell v$Version"
    $sc.Save()
    Write-Host "[OK] Desktop shortcut: $lnk"
}

# --- Main ---
if (-not (Test-Admin)) {
    throw "Run this script as Administrator (right-click PowerShell -> Run as administrator)."
}

if (-not $SourceRoot) {
    $SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

$version = Get-SentinelVersion -Root $SourceRoot
Write-Host "========================================"
Write-Host " MavizOS Windows Installer v$version"
Write-Host "========================================"
Write-Host ""
Write-Host "SAFETY: This installer does NOT wipe Windows or delete system files."
Write-Host "Windows remains the host OS; MavizOS runs as the primary SOC experience."
Write-Host ""

$python = Ensure-Python
Sync-Project -From $SourceRoot -To $InstallRoot
$venvPy = Install-Venv -PythonExe $python -Root $InstallRoot
Set-EnvFile -Root $InstallRoot

$launcher = Join-Path $InstallRoot "install\windows\mavizos-shell.cmd"
if (-not (Test-Path $launcher)) {
    Copy-Item (Join-Path $PSScriptRoot "mavizos-shell.cmd") $launcher -Force
}

if ($Autostart) {
    Register-Autostart -Root $InstallRoot -Version $version
}

New-DesktopShortcut -Launcher $launcher -Version $version

$marker = Join-Path $InstallRoot "install\.installed-windows.json"
@{
    version     = $version
    installedAt = (Get-Date).ToUniversalTime().ToString("o")
    installRoot = $InstallRoot
    autostart   = [bool]$Autostart
} | ConvertTo-Json | Set-Content $marker -Encoding UTF8

if ($ConfigureAppliance) {
    $cfg = Join-Path $PSScriptRoot "configure-appliance.ps1"
    if (Test-Path $cfg) {
        Write-Host "[*] Running appliance configuration..."
        & $cfg -InstallRoot $InstallRoot
    }
}

Write-Host ""
Write-Host "Installation complete."
Write-Host "  Root:     $InstallRoot"
Write-Host "  Shell:    $launcher"
Write-Host "  API:      $InstallRoot\.venv\Scripts\mavizos.exe serve"
Write-Host "  Desktop:  http://localhost:8000/desktop"
Write-Host ""
Write-Host "Launch now:  & '$launcher'"
Write-Host "Uninstall:   install\windows\uninstall.ps1"
