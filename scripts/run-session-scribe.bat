@echo off
rem Session scribe wrapper for the hourly scheduled task (2026-07-17).
rem Digests new Claude session transcripts into vault inbox + aiwatcher inbox.
set PATH=C:\Users\sandr\.local\bin;%PATH%
rem venv lives at the repo root, not under scripts\.  %~dp0 is this batch's dir.
"%~dp0..\.venv\Scripts\python.exe" "%~dp0session_scribe.py" >> C:\temp\session-scribe.log 2>&1
