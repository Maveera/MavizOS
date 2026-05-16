@echo off
set ROOT=C:\BootGuardAI
if exist "%ROOT%\.venv\Scripts\python.exe" (
  "%ROOT%\.venv\Scripts\python.exe" -m bootguardai
) else (
  echo BootGuardAI not installed at %ROOT%
  exit /b 1
)
