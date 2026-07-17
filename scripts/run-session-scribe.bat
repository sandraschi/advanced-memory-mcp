@echo off
rem Session scribe wrapper for the hourly scheduled task (2026-07-17).
rem Digests new Claude session transcripts into vault inbox + aiwatcher inbox.
set PATH=C:\Users\sandr\.local\bin;%PATH%
C:\Users\sandr\.local\bin\uv.exe run --directory D:\Dev\repos\advanced-memory-mcp python scripts\session_scribe.py >> C:\temp\session-scribe.log 2>&1
