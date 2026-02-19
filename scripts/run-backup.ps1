# Launcher: runs backup-repo.ps1 with PowerShell 7 (required for script parsing).
# Use this from any terminal (cmd, PowerShell 5.1, or pwsh) to ensure backup runs in pwsh.
$scriptDir = $PSScriptRoot
$backupScript = Join-Path $scriptDir "backup-repo.ps1"
if (-not (Test-Path $backupScript)) {
    Write-Host "[ERROR] backup-repo.ps1 not found: $backupScript" -ForegroundColor Red
    exit 1
}
& pwsh -NoProfile -ExecutionPolicy Bypass -File $backupScript @args
exit $LASTEXITCODE
