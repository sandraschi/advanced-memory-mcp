# ADN Webapp - Unified Start Script
# Starts backend (bridge-server + startup-service) and frontend (Vite dev server)
# Ports: 10704 (webapp), 10705 (bridge), 10733 (startup service)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot

$WebPort = 10704
$BridgePort = 10705
$StartupPort = 10733

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ADN Webapp Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
try {
    $nodeVersion = & node --version 2>$null
    Write-Host "[OK] Node.js $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Node.js not found. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Kill any existing processes on our ports
Write-Host "Clearing ports $WebPort, $BridgePort, $StartupPort..." -ForegroundColor Yellow
try { npx --yes kill-port $WebPort $BridgePort $StartupPort 2>$null } catch {}

# Install backend dependencies if needed
$backendDir = Join-Path $ScriptDir "backend"
if (!(Test-Path (Join-Path $backendDir "node_modules"))) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    Push-Location $backendDir
    & npm install
    Pop-Location
}

# Install frontend dependencies if needed
$frontendDir = Join-Path $ScriptDir "frontend"
if (!(Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location $frontendDir
    & npm install
    Pop-Location
}

# Start bridge server (the actual HTTP API on port 10705)
Write-Host ""
Write-Host "Starting bridge server (port $BridgePort)..." -ForegroundColor Green
$bridgeProcess = Start-Process -FilePath "node" -ArgumentList "bridge-server.js" -WorkingDirectory $backendDir -NoNewWindow -PassThru

Start-Sleep -Seconds 2

# Start startup service (management API on port 10733)
Write-Host "Starting startup service (port $StartupPort)..." -ForegroundColor Green
$startupProcess = Start-Process -FilePath "node" -ArgumentList "startup-service.js" -WorkingDirectory $backendDir -NoNewWindow -PassThru

Start-Sleep -Seconds 1

# Start frontend (Vite dev server)
Write-Host "Starting frontend (Vite on port $WebPort)..." -ForegroundColor Green
$webappProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm run dev" -WorkingDirectory $frontendDir -NoNewWindow -PassThru

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ADN Webapp Running" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Frontend:  http://localhost:$WebPort" -ForegroundColor Cyan
Write-Host "  Bridge:    http://localhost:$BridgePort" -ForegroundColor Cyan
Write-Host "  Startup:   http://localhost:$StartupPort" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Gray

# Wait and cleanup on exit
try {
    if ($webappProcess -and $webappProcess.Id) {
        Wait-Process -Id $webappProcess.Id
    }
    else {
        Write-Host "Frontend process did not start. Press Enter to exit." -ForegroundColor Yellow
        Read-Host
    }
}
finally {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    if ($webappProcess -and $webappProcess.Id) {
        Stop-Process -Id $webappProcess.Id -ErrorAction SilentlyContinue
    }
    if ($bridgeProcess -and $bridgeProcess.Id) {
        Stop-Process -Id $bridgeProcess.Id -ErrorAction SilentlyContinue
    }
    if ($startupProcess -and $startupProcess.Id) {
        Stop-Process -Id $startupProcess.Id -ErrorAction SilentlyContinue
    }
    Write-Host "All services stopped." -ForegroundColor Green
}
