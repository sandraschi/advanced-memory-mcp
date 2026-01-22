# Restart Watch Service - PowerShell Script for MCP Server Stability
# This script can be run to restart the file watcher if it becomes unstable

param(
    [switch]$Force,
    [switch]$Verbose
)

Write-Host "Advanced Memory MCP - Watch Service Restart Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Configuration
$AdvancedMemoryHome = $env:ADVANCED_MEMORY_HOME
if (-not $AdvancedMemoryHome) {
    $AdvancedMemoryHome = "$env:USERPROFILE"
}

$WatchStatusFile = Join-Path $AdvancedMemoryHome ".advanced-memory\watch-status.json"
$LogFile = Join-Path $AdvancedMemoryHome ".advanced-memory\restart-watch-service.log"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "$Timestamp - $Message"
    Write-Host $LogMessage -ForegroundColor Yellow
    Add-Content -Path $LogFile -Value $LogMessage
}

# Check if watch service is running
function Get-WatchServiceStatus {
    if (Test-Path $WatchStatusFile) {
        try {
            $status = Get-Content $WatchStatusFile -Raw | ConvertFrom-Json
            return $status
        } catch {
            Write-Log "Error reading watch status file: $($_.Exception.Message)"
            return $null
        }
    } else {
        Write-Log "Watch status file not found: $WatchStatusFile"
        return $null
    }
}

# Kill existing watch service processes
function Stop-WatchService {
    Write-Log "Stopping existing watch service processes..."

    # Find and kill python processes related to watch service
    $watchProcesses = Get-Process | Where-Object {
        $_.ProcessName -eq "python" -and
        ($_.CommandLine -like "*watch*" -or $_.CommandLine -like "*sync*")
    }

    foreach ($proc in $watchProcesses) {
        try {
            Write-Log "Terminating process: $($proc.Id) - $($proc.CommandLine)"
            Stop-Process -Id $proc.Id -Force
        } catch {
            Write-Log "Failed to terminate process $($proc.Id): $($_.Exception.Message)"
        }
    }
}

# Restart the MCP server (which will restart the watch service)
function Restart-MCPServer {
    Write-Log "Restarting MCP server to reinitialize watch service..."

    # The watch service is started by the MCP server lifespan
    # So we need to restart the MCP server process
    Write-Log "Note: MCP server should automatically restart watch service on next tool call"
    Write-Log "If issues persist, restart Cursor IDE completely"
}

# Main logic
$status = Get-WatchServiceStatus

if ($status) {
    Write-Host "Current Watch Service Status:" -ForegroundColor Green
    Write-Host "  Running: $($status.running)"
    Write-Host "  Process ID: $($status.pid)"
    Write-Host "  Error Count: $($status.error_count)"
    Write-Host "  Start Time: $($status.start_time)"
    Write-Host "  Recent Events: $($status.recent_events.Count)"

    if ($status.error_count -gt 5) {
        Write-Host "⚠️  High error count detected!" -ForegroundColor Red
    }

    if (-not $status.running) {
        Write-Host "⚠️  Watch service is not running!" -ForegroundColor Red
        $Force = $true
    }
} else {
    Write-Host "Unable to read watch service status" -ForegroundColor Red
    $Force = $true
}

if ($Force) {
    Write-Host "`nRestarting watch service..." -ForegroundColor Yellow
    Stop-WatchService
    Restart-MCPServer

    Write-Host "`nRestart complete. Monitor the status with:" -ForegroundColor Green
    Write-Host "  status('diagnostic')" -ForegroundColor Cyan
    Write-Host "  Or run this script again to check status" -ForegroundColor Cyan
} else {
    Write-Host "`nWatch service appears healthy. Use -Force to restart anyway." -ForegroundColor Green
}

Write-Host "`nLog file: $LogFile" -ForegroundColor Gray
