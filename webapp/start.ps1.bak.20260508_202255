Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Webapp: Python FastAPI backend + Vite frontend (single supported launcher)
$WebPort = 10704
$BackendPort = 10705
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup (frontend has package.json)
Set-Location $PSScriptRoot
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Set-Location $frontendPath
    npm install
    Set-Location $PSScriptRoot
}

# 3. Start the Python backend (Background). uv --project finds package; CWD stays webapp.
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$PSScriptRoot'; uv run --project '$ProjectRoot' uvicorn advanced_memory.server:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 3b. Wait and verify backend is listening
$maxAttempts = 6
$attempt = 0
$backendUp = $false
while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    $conn = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue
    if ($conn) { $backendUp = $true; break }
    $attempt++
}
if ($backendUp) {
    Write-Host "Backend (port $BackendPort) is up." -ForegroundColor Green
} else {
    Write-Host "Backend (port $BackendPort) not responding after $($maxAttempts * 2)s; check the backend window." -ForegroundColor Yellow
}

# 4. Run Vite dev from frontend
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
Set-Location $frontendPath

# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
npm run dev -- --port $WebPort --host




