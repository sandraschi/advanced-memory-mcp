@echo off
cd /d D:\Dev\repos\advanced-memory-mcp
set PATH=C:\Users\sandr\.local\bin;%PATH%
set MCP_PORT=10732
set MCP_HOST=127.0.0.1
set MCP_TRANSPORT=http
"%~dp0.venv\Scripts\python.exe" -m advanced_memory.cli.main mcp --transport streamable-http --host 127.0.0.1 --port 10732
