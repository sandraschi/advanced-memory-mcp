@echo off
REM Webapp: same as start.ps1 (Python FastAPI + Vite). Use this if you prefer double-click / cmd.
cd /d "%~dp0"
powershell -NoLogo -ExecutionPolicy Bypass -File "%~dp0start.ps1"
if errorlevel 1 pause
