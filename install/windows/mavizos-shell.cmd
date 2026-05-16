@echo off
REM MavizOS interactive shell launcher (appliance mode)
setlocal
set "MavizOS_ROOT=C:\MavizOS"
set "VENV_PY=%MavizOS_ROOT%\.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [MavizOS] Installation not found at %MavizOS_ROOT%
    echo Run install\windows\install.ps1 as Administrator first.
    exit /b 1
)

cd /d "%MavizOS_ROOT%"
"%VENV_PY%" -m MavizOS %*
