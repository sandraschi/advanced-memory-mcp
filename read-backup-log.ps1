# Read backup log file and output to repo directory
$logDir = Join-Path $env:APPDATA "backup-logs"
$today = Get-Date -Format 'yyyy-MM-dd'
$logFile = Join-Path $logDir "backup-$today.log"

Write-Host "Looking for log file: $logFile"

if (Test-Path $logFile) {
    Write-Host "Found log file!"
    $content = Get-Content $logFile
    $outputFile = Join-Path (Get-Location) "backup-log-$today.txt"
    $content | Out-File -FilePath $outputFile -Encoding utf8
    Write-Host "Log file copied to: $outputFile"
    Write-Host "`n=== LOG FILE CONTENT (last 100 lines) ==="
    $content | Select-Object -Last 100
} else {
    Write-Host "Log file not found. Checking for any log files:"
    if (Test-Path $logDir) {
        Get-ChildItem $logDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, LastWriteTime, @{Label="Size (KB)";Expression={[math]::Round($_.Length/1KB,2)}} -AutoSize
    } else {
        Write-Host "Log directory does not exist: $logDir"
    }
}
