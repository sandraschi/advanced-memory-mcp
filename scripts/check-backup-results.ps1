# Quick Backup Results Checker
# Run this after executing backup-repo.ps1 to verify results

$ErrorActionPreference = 'Continue'

Write-Host "=== BACKUP RESULTS CHECKER ===" -ForegroundColor Cyan
Write-Host ""

$repoName = "advanced-memory-mcp"
$desktop = [Environment]::GetFolderPath("Desktop")

$targets = @(
    @{ Name = "Desktop"; Path = Join-Path (Join-Path $desktop "repo backup") $repoName },
    @{ Name = "N: Drive"; Path = "N:\backup\dev\repo-backups\$repoName" },
    @{ Name = "OneDrive"; Path = Join-Path $env:OneDrive "repo backup\$repoName" }
)

$foundBackups = @()
$totalBackups = 0

foreach ($target in $targets) {
    Write-Host "Checking $($target.Name)..." -ForegroundColor Yellow
    Write-Host "  Path: $($target.Path)" -ForegroundColor Gray

    if ($target.Path -and (Test-Path (Split-Path $target.Path -Parent) -ErrorAction SilentlyContinue)) {
        if (Test-Path $target.Path -ErrorAction SilentlyContinue) {
            $zips = Get-ChildItem -Path $target.Path -Filter "*.zip" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

            if ($zips) {
                $latest = $zips | Select-Object -First 1
                $age = ((Get-Date) - $latest.LastWriteTime).TotalMinutes
                $totalBackups += $zips.Count

                Write-Host "  âœ" BACKUP FOUND!" -ForegroundColor Green
                Write-Host "    File: $($latest.Name)" -ForegroundColor Cyan
                Write-Host "    Size: $([math]::Round($latest.Length/1MB, 2)) MB" -ForegroundColor White
                Write-Host "    Created: $($latest.LastWriteTime)" -ForegroundColor White
                Write-Host "    Age: $([math]::Round($age, 1)) minutes" -ForegroundColor $(if ($age -lt 10) { "Green" } else { "Yellow" })
                Write-Host "    Total backups in directory: $($zips.Count)" -ForegroundColor Gray

                if ($age.TotalMinutes -lt 10) {
                    $foundBackups += @{
                        Location = $target.Name
                        File = $latest.Name
                        SizeMB = [math]::Round($latest.Length/1MB, 2)
                        AgeMinutes = [math]::Round($age, 1)
                        Recent = $true
                    }
                } else {
                    $foundBackups += @{
                        Location = $target.Name
                        File = $latest.Name
                        SizeMB = [math]::Round($latest.Length/1MB, 2)
                        AgeMinutes = [math]::Round($age, 1)
                        Recent = $false
                    }
                }
            } else {
                Write-Host "  âœ- No ZIP files found" -ForegroundColor Red
            }
        } else {
            Write-Host "  âœ- Directory does not exist" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  âœ- Target not accessible" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Summary
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
Write-Host ""

if ($foundBackups.Count -gt 0) {
    $recentBackups = $foundBackups | Where-Object { $_.Recent -eq $true }

    if ($recentBackups.Count -gt 0) {
        Write-Host "âœ" SUCCESS: Recent backups created!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Recent backups ($($recentBackups.Count) location(s)):" -ForegroundColor Green
        foreach ($backup in $recentBackups) {
            Write-Host "  - $($backup.Location): $($backup.File) ($($backup.SizeMB) MB, $($backup.AgeMinutes) min ago)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "âš  Backups found but may be old:" -ForegroundColor Yellow
        foreach ($backup in $foundBackups) {
            Write-Host "  - $($backup.Location): $($backup.File) ($($backup.AgeMinutes) min ago)" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "Total backup files found: $totalBackups" -ForegroundColor Cyan
} else {
    Write-Host "âœ- FAILED: No backup files found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check log files for errors:" -ForegroundColor Yellow
    Write-Host "  1. %APPDATA%\backup-logs\backup-*.log" -ForegroundColor Gray
    Write-Host "  2. .backup-output.txt in repo root" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Run backup script again with:" -ForegroundColor Yellow
    Write-Host "  .\scripts\backup-repo.ps1 -Verbose" -ForegroundColor Cyan
}

Write-Host ""
