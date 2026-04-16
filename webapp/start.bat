@echo off
setlocal
REM Launcher in starts/ — %~dp0 is starts\; webapp lives under advanced-memory-mcp\webapp.
set "WEBAPP=%~dp0..\..\advanced-memory-mcp\webapp"
cd /d "%WEBAPP%"
if not exist "start.ps1" (
  echo [ERROR] advanced-memory-mcp webapp not found. Expected: %CD%\start.ps1
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\start.ps1"
if errorlevel 1 pause
endlocal
