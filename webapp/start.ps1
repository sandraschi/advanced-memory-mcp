# Webapp Start - Standardized SOTA
$WebPort = 10835
$BackendPort = $WebPort + 1
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }

# 3. Start the Python backend in a new window
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$env:PYTHONPATH = "$ProjectRoot;$(Join-Path $ProjectRoot 'src')"
$backendCmd = "Set-Location '$ProjectRoot'; uv run uvicorn advanced_memory.api.app:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# Give backend a moment to bind
Start-Sleep -Seconds 2

# 4. Run server (Vite dev)
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Cyan
npm run dev -- --port $WebPort --host
