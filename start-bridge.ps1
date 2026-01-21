# Start ADN MCP Bridge Server
# This starts the bridge server that connects to ADN MCP via stdio

Write-Host "Starting ADN MCP Bridge Server..." -ForegroundColor Green
Write-Host "Working directory: $PSScriptRoot" -ForegroundColor Gray

# Change to the script directory
Set-Location $PSScriptRoot

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>$null
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js and add it to your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required packages are installed
if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the bridge server
Write-Host "Starting bridge server on http://localhost:8001..." -ForegroundColor Cyan
Write-Host "This server connects to ADN MCP via stdio transport" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the bridge server" -ForegroundColor Yellow
Write-Host ""

try {
    node bridge-server.js
} catch {
    Write-Host "Error starting bridge server: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure all dependencies are installed" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
