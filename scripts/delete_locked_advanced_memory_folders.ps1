# Delete locked .advanced-memory folders from project directories
# Run this AFTER closing Claude Desktop

$ErrorActionPreference = "Stop"

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Delete Per-Project .advanced-memory Folders" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

$folders = @(
    "C:\Users\sandr\Documents\claude-depot\.advanced-memory"
)

Write-Host "Will delete these folders:" -ForegroundColor Yellow
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        $size = (Get-ChildItem -Path $folder -Recurse -File | Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "  $folder ($sizeMB MB)" -ForegroundColor Red
    } else {
        Write-Host "  $folder (already deleted)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "These are PER-PROJECT databases (legacy/unused)." -ForegroundColor Yellow
Write-Host "The global database at C:\Users\sandr\.advanced-memory\memory.db will be used instead." -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
$success = 0
$failed = 0

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        Write-Host "Already deleted: $folder" -ForegroundColor Gray
        continue
    }
    
    try {
        Remove-Item -Path $folder -Recurse -Force -ErrorAction Stop
        Write-Host "Deleted: $folder" -ForegroundColor Green
        $success++
    }
    catch {
        Write-Host "FAILED: $folder" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor DarkRed
        Write-Host "  (Probably still locked by Claude Desktop)" -ForegroundColor Yellow
        $failed++
    }
}

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Deleted: $success | Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Yellow" } else { "Green" })
Write-Host ("=" * 70) -ForegroundColor Cyan

if ($failed -gt 0) {
    Write-Host ""
    Write-Host "CLOSE CLAUDE DESKTOP and run this script again." -ForegroundColor Red
}




