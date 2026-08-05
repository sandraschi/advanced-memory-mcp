@echo off
rem Session scribe wrapper for the hourly scheduled task (2026-07-17).
rem Digests new Claude session transcripts into vault inbox + aiwatcher inbox.
set PATH=C:\Users\sandr\.local\bin;%PATH%
"%~dp0.venv\Scripts\python.exe" scripts\session_scribe.py >> C:\temp\session-scribe.log 2>&1
