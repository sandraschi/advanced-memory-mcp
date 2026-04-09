# SOTA v12.0 start.ps1 for Advanced Memory MCP
$ErrorActionPreference = "Stop"

# Authoritative Port Registry: 10850
$PORT = 10850

Write-Host "--- Advanced Memory MCP Launcher ---" -ForegroundColor Cyan

# Clear port squatters (zombie processes)
$portProcess = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
if ($portProcess) {
    Write-Host "Killing process $portProcess squatting on port $PORT..." -ForegroundColor Yellow
    Stop-Process -Id $portProcess -Force -ErrorAction SilentlyContinue
}

# Clear stale lock if it exists (Antigravity/stdio mode)
$lockPath = Join-Path $HOME ".advanced-memory\mcp-stdio.lock"
if (Test-Path $lockPath) {
    Write-Host "Clearing stale lock file at $lockPath..." -ForegroundColor Yellow
    Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
}

# Kill orphaned am mcp or advanced-memory processes
$orphans = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*advanced-memory*" -or $_.CommandLine -like "*am mcp*" } | Where-Object { $_.ProcessId -ne $PID }
foreach ($p in $orphans) {
    Write-Host "Killing orphaned process $($p.ProcessId): $($p.CommandLine)" -ForegroundColor Yellow
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}

# Verify uv installation
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Error: 'uv' is not installed. Please install it from https://astral.sh/uv" -ForegroundColor Red
    exit 1
}

# Run the server in SSE mode (web/remote compatible)
Write-Host "Starting Advanced Memory MCP on port $PORT..." -ForegroundColor Green
$env:PYTHONPATH = "src"
uv run am mcp --transport sse --port $PORT
