# Start ADN Webapp with all required services (reservoir ports 10704, 10733 per WEBAPP_PORTS.md)
# Clears ports, then starts startup service and webapp

$WebPort = 10704
$StartupPort = 10733
try { Set-Location webapp; npx --yes kill-port $WebPort $StartupPort 2>$null; Set-Location $PSScriptRoot } catch { Set-Location $PSScriptRoot }

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

Write-Host "Starting ADN Startup Service (port 10733)..." -ForegroundColor Green
$startupService = Start-Process -FilePath "node" -ArgumentList "startup-service.js" -NoNewWindow -PassThru

# Wait a moment for startup service to start
Start-Sleep -Seconds 2

Write-Host "Starting ADN Webapp (port 10704)..." -ForegroundColor Green
$webappDir = Join-Path $PSScriptRoot "webapp"
$webappProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm run dev" -NoNewWindow -PassThru -WorkingDirectory $webappDir

Write-Host "" -ForegroundColor Green
Write-Host "ADN Webapp started successfully!" -ForegroundColor Green
Write-Host "Webapp: http://localhost:10704" -ForegroundColor Cyan
Write-Host "Startup Service: http://localhost:10733" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Gray
Write-Host "The webapp will automatically start the bridge server when needed." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Gray

# Wait for user to stop
try {
    if ($webappProcess -and $webappProcess.Id) {
        Wait-Process -Id $webappProcess.Id
    } else {
        Write-Host "Webapp process did not start. Press Enter to exit." -ForegroundColor Yellow
        Read-Host
    }
} finally {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    if ($webappProcess -and $webappProcess.Id) {
        Stop-Process -Id $webappProcess.Id -ErrorAction SilentlyContinue
    }
    if ($startupService -and $startupService.Id) {
        Stop-Process -Id $startupService.Id -ErrorAction SilentlyContinue
    }
    Write-Host "All services stopped." -ForegroundColor Green
}
