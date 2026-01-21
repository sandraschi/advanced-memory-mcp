# Start ADN Webapp with all required services
# This script starts the startup service and then the webapp

Write-Host "Starting ADN Webapp..." -ForegroundColor Green
Write-Host "This will start all required services automatically" -ForegroundColor Gray

# Check if Node.js is available
try {
    $nodeVersion = & node --version 2>$null
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Gray
} catch {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if webapp dependencies are installed
Push-Location webapp
if (!(Test-Path "node_modules")) {
    Write-Host "Installing webapp dependencies..." -ForegroundColor Yellow
    & npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install webapp dependencies" -ForegroundColor Red
        Pop-Location
        exit 1
    }
}
Pop-Location

# Check if root dependencies are installed (for startup service and bridge)
if (!(Test-Path "node_modules")) {
    Write-Host "Installing root dependencies..." -ForegroundColor Yellow
    & npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install root dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Starting ADN Startup Service (port 8002)..." -ForegroundColor Green
$startupService = Start-Process -FilePath "node" -ArgumentList "startup-service.js" -NoNewWindow -PassThru

# Wait a moment for startup service to start
Start-Sleep -Seconds 2

Write-Host "Starting ADN Webapp (port 17770)..." -ForegroundColor Green
Push-Location webapp
$webappProcess = Start-Process -FilePath "npm" -ArgumentList "run dev" -NoNewWindow -PassThru
Pop-Location

Write-Host "" -ForegroundColor Green
Write-Host "ADN Webapp started successfully!" -ForegroundColor Green
Write-Host "Webapp: http://localhost:17770" -ForegroundColor Cyan
Write-Host "Startup Service: http://localhost:8002" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Gray
Write-Host "The webapp will automatically start the bridge server when needed." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Gray

# Wait for user to stop
try {
    Wait-Process -Id $webappProcess.Id
} finally {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Stop-Process -Id $webappProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $startupService.Id -ErrorAction SilentlyContinue
    Write-Host "All services stopped." -ForegroundColor Green
}
