# Remote graceful shutdown for ADN system
param(
    [string]$Reason = "Remote shutdown request",
    [switch]$Force
)

Write-Host "Shutting down ADN system gracefully..." -ForegroundColor Yellow
Write-Host "Reason: $Reason" -ForegroundColor Cyan
Write-Host "Force: $($Force.ToBool())" -ForegroundColor Cyan
Write-Host ""

try {
    $body = @{
        reason = $Reason
        force = $Force.ToBool()
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/system/graceful-exit" -Method POST -Body $body -ContentType "application/json"

    if ($response.success) {
        Write-Host "✅ Graceful shutdown initiated successfully" -ForegroundColor Green
        Write-Host "Response: $($response.message)" -ForegroundColor Green
        Write-Host "Timestamp: $($response.timestamp)" -ForegroundColor Gray
    } else {
        Write-Host "❌ Shutdown request failed" -ForegroundColor Red
        Write-Host "Error: $($response.error)" -ForegroundColor Red
    }

} catch {
    Write-Host "❌ Failed to connect to ADN bridge server" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure the ADN bridge server is running on port 8001" -ForegroundColor Yellow
    Write-Host "Start it with: .\run-webapp-clean.bat" -ForegroundColor Yellow
}

Write-Host ""
