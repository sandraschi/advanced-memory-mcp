# Start ADN Startup Service
# This service allows the webapp to start/stop the bridge server

Write-Host "Starting ADN Startup Service..." -ForegroundColor Green

# Check if Node.js is available
try {
    $nodeVersion = & node --version 2>$null
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Gray
} catch {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if dependencies are installed
if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Start the startup service
Write-Host "Starting startup service on port 8002..." -ForegroundColor Green
Write-Host "POST /start-bridge to start the bridge server" -ForegroundColor Gray
Write-Host "POST /stop-bridge to stop the bridge server" -ForegroundColor Gray

& node startup-service.js
