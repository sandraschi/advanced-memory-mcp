# Check if backups were created
$outputFile = "backup-check-results.txt"

Write-Host "Checking backup locations..." | Tee-Object -FilePath $outputFile -Append

$desktop = [Environment]::GetFolderPath("Desktop")
$backupPath1 = Join-Path (Join-Path $desktop "repo backup") "advanced-memory-mcp"

Write-Host "" | Tee-Object -FilePath $outputFile -Append
Write-Host "=== Location 1: Desktop ===" | Tee-Object -FilePath $outputFile -Append
Write-Host "Path: $backupPath1" | Tee-Object -FilePath $outputFile -Append

if (Test-Path $backupPath1) {
    $files = Get-ChildItem -Path $backupPath1 -Filter "*.zip" -File | Sort-Object LastWriteTime -Descending
    Write-Host "Status: EXISTS - $($files.Count) backup file(s) found" | Tee-Object -FilePath $outputFile -Append
    if ($files.Count -gt 0) {
        $latest = $files[0]
        Write-Host "Latest backup:" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Name: $($latest.Name)" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Size: $([math]::Round($latest.Length/1MB, 2)) MB" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Date: $($latest.LastWriteTime)" | Tee-Object -FilePath $outputFile -Append
    }
} else {
    Write-Host "Status: DIRECTORY NOT FOUND" | Tee-Object -FilePath $outputFile -Append
}

$nPath = "N:\backup\dev\repo-backups\advanced-memory-mcp"
Write-Host "" | Tee-Object -FilePath $outputFile -Append
Write-Host "=== Location 2: N: drive ===" | Tee-Object -FilePath $outputFile -Append
Write-Host "Path: $nPath" | Tee-Object -FilePath $outputFile -Append

if (Test-Path $nPath) {
    $files = Get-ChildItem -Path $nPath -Filter "*.zip" -File | Sort-Object LastWriteTime -Descending
    Write-Host "Status: EXISTS - $($files.Count) backup file(s) found" | Tee-Object -FilePath $outputFile -Append
    if ($files.Count -gt 0) {
        $latest = $files[0]
        Write-Host "Latest backup:" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Name: $($latest.Name)" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Size: $([math]::Round($latest.Length/1MB, 2)) MB" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Date: $($latest.LastWriteTime)" | Tee-Object -FilePath $outputFile -Append
    }
} else {
    Write-Host "Status: NOT FOUND or N: drive not accessible" | Tee-Object -FilePath $outputFile -Append
}

$oneDrivePath = Join-Path (Join-Path (Join-Path $env:OneDrive "Backup") "repo-backups") "advanced-memory-mcp"
Write-Host "" | Tee-Object -FilePath $outputFile -Append
Write-Host "=== Location 3: OneDrive ===" | Tee-Object -FilePath $outputFile -Append
Write-Host "Path: $oneDrivePath" | Tee-Object -FilePath $outputFile -Append

if (Test-Path $oneDrivePath) {
    $files = Get-ChildItem -Path $oneDrivePath -Filter "*.zip" -File | Sort-Object LastWriteTime -Descending
    Write-Host "Status: EXISTS - $($files.Count) backup file(s) found" | Tee-Object -FilePath $outputFile -Append
    if ($files.Count -gt 0) {
        $latest = $files[0]
        Write-Host "Latest backup:" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Name: $($latest.Name)" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Size: $([math]::Round($latest.Length/1MB, 2)) MB" | Tee-Object -FilePath $outputFile -Append
        Write-Host "  Date: $($latest.LastWriteTime)" | Tee-Object -FilePath $outputFile -Append
    }
} else {
    Write-Host "Status: NOT FOUND or OneDrive not accessible" | Tee-Object -FilePath $outputFile -Append
}

Write-Host "" | Tee-Object -FilePath $outputFile -Append
Write-Host "Results saved to: $outputFile" | Tee-Object -FilePath $outputFile -Append
