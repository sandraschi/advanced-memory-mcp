# ADN Webapp - Unified Shutdown Script
# Kills all ADN webapp processes and frees ports
param(
    [string]$Reason = "Manual shutdown",
    [switch]$Force
)

$Ports = @(10704, 10705, 10733, 10735)
# Legacy ports from older configurations
$LegacyPorts = @(17770, 8001, 8002, 8003)
$AllPorts = $Ports + $LegacyPorts

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  ADN Webapp Shutdown" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Reason: $Reason" -ForegroundColor Gray
Write-Host ""

# Try graceful shutdown via bridge API first
$BridgePort = 10705
try {
    Write-Host "Attempting graceful shutdown via bridge API..." -ForegroundColor Cyan
    $body = @{ reason = $Reason; force = $Force.ToBool() } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:$BridgePort/api/v1/system/graceful-exit" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 5
    if ($response.success) {
        Write-Host "[OK] Graceful shutdown initiated" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
}
catch {
    Write-Host "[SKIP] Bridge not responding, killing processes directly" -ForegroundColor Gray
}

# Kill processes on all ports
foreach ($port in $AllPorts) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        if ($conn.OwningProcess -and $conn.OwningProcess -ne 0) {
            Write-Host "Killing PID $($conn.OwningProcess) on port $port" -ForegroundColor Yellow
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

# Kill ADN-titled processes
taskkill /FI "WINDOWTITLE eq ADN*" /F 2>$null | Out-Null

Start-Sleep -Seconds 1

Write-Host ""
Write-Host "[OK] All ADN webapp processes stopped." -ForegroundColor Green
Write-Host "Ports freed: $($AllPorts -join ', ')" -ForegroundColor Gray
