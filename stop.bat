@echo off
REM Stop advanced-memory-mcp fleet ports
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0webapp\stop.ps1"
if errorlevel 1 pause

