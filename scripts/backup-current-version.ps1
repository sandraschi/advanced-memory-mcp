# Backup Current Version of backup-repo.ps1
# Creates a timestamped backup before reverting

$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot "backup-repo.ps1"
$backupDir = Join-Path $PSScriptRoot "backup-versions"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = Join-Path $backupDir "backup-repo.ps1.backup-$timestamp.ps1"

Write-Host "Backing up current version..." -ForegroundColor Cyan
Write-Host "  Source: $scriptPath"
Write-Host "  Backup: $backupPath"

Copy-Item -Path $scriptPath -Destination $backupPath -Force

Write-Host "Backup created successfully!" -ForegroundColor Green
Write-Host "  File: $backupPath"
Write-Host "  Size: $([math]::Round((Get-Item $backupPath).Length / 1KB, 2)) KB"
