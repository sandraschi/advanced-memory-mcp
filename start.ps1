# SOTA v12.0 start.ps1 for Advanced Memory MCP
$ErrorActionPreference = "Stop"

# Authoritative Port Registry: 10850
$PORT = 10850

Write-Host "--- Advanced Memory MCP Launcher ---" -ForegroundColor Cyan

# Clear port squatters (zombie processes)
$portProcess = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
if ($portProcess) {
    Write-Host "Killing process $portProcess squatting on port $PORT..." -ForegroundColor Yellow
    Stop-Process -Id $portProcess -Force
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
