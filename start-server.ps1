# Start Advanced Memory MCP Server
# This script starts the ADN MCP server for the webapp

Write-Host "Starting Advanced Memory MCP Server..." -ForegroundColor Green
Write-Host "Working directory: $PSScriptRoot" -ForegroundColor Gray

# Change to the script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add it to your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the server
Write-Host "Starting server on http://localhost:8000..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

try {
    python -m advanced_memory.mcp.server
} catch {
    Write-Host "Error starting server: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure you're in the correct directory and all dependencies are installed" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
