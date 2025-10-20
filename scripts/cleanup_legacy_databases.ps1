# Cleanup Legacy Per-Project Advanced Memory Databases
# 
# This script removes .advanced-memory folders from project directories.
# These are legacy/redundant - the global database at ~\.advanced-memory\memory.db is used.
#
# SAFE: Only deletes database folders, NEVER deletes .md files or actual content!

param(
    [string]$ScanPath = "$env:USERPROFILE\Documents",
    [switch]$WhatIf = $false
)

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Advanced Memory - Legacy Database Cleanup" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

Write-Host "Scanning: $ScanPath" -ForegroundColor Yellow
Write-Host "Global DB: $env:USERPROFILE\.advanced-memory\memory.db (NOT deleted)" -ForegroundColor Green
Write-Host ""

# Find all .advanced-memory folders
$found = Get-ChildItem -Path $ScanPath -Directory -Recurse -Filter ".advanced-memory" -ErrorAction SilentlyContinue

if ($found.Count -eq 0) {
    Write-Host "No per-project .advanced-memory folders found!" -ForegroundColor Green
    Write-Host "System is already clean." -ForegroundColor Green
    exit 0
}

Write-Host "Found $($found.Count) per-project database folder(s):" -ForegroundColor Yellow
Write-Host ""

$totalSize = 0
foreach ($folder in $found) {
    # Skip the global .advanced-memory folder
    if ($folder.Parent.FullName -eq $env:USERPROFILE) {
        Write-Host "  SKIP: $($folder.FullName) (global config)" -ForegroundColor Cyan
        continue
    }
    
    # Calculate size
    $size = (Get-ChildItem -Path $folder.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $totalSize += $size
    $sizeMB = [math]::Round($size / 1MB, 2)
    
    Write-Host "  $($folder.Parent.Name)\" -ForegroundColor White -NoNewline
    Write-Host ".advanced-memory" -ForegroundColor Red -NoNewline
    Write-Host " ($sizeMB MB)" -ForegroundColor Gray
    Write-Host "    Path: $($folder.FullName)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Total space to reclaim: " -NoNewline
Write-Host "$([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Yellow
Write-Host ""

if ($WhatIf) {
    Write-Host "DRY RUN - No files will be deleted" -ForegroundColor Cyan
    Write-Host "Remove -WhatIf to actually delete" -ForegroundColor Cyan
    exit 0
}

# Confirm deletion
Write-Host "WARNING: This will DELETE the above folders!" -ForegroundColor Red
Write-Host "Your .md files and other content will NOT be touched." -ForegroundColor Green
Write-Host ""
$confirm = Read-Host "Continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Deleting..." -ForegroundColor Yellow

$deleted = 0
$failed = 0

foreach ($folder in $found) {
    # Skip global
    if ($folder.Parent.FullName -eq $env:USERPROFILE) {
        continue
    }
    
    try {
        Remove-Item -Path $folder.FullName -Recurse -Force -ErrorAction Stop
        Write-Host "  Deleted: $($folder.FullName)" -ForegroundColor Green
        $deleted++
    }
    catch {
        Write-Host "  FAILED: $($folder.FullName)" -ForegroundColor Red
        Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor DarkRed
        $failed++
    }
}

Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "COMPLETE" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "Deleted: $deleted" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })

if ($failed -gt 0) {
    Write-Host ""
    Write-Host "Some files were locked (probably by Claude Desktop)." -ForegroundColor Yellow
    Write-Host "Close Claude Desktop and run this script again." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Your markdown files and content are safe!" -ForegroundColor Green
Write-Host "Databases can be rebuilt anytime with sync." -ForegroundColor Cyan




