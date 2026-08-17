#!/usr/bin/env pwsh
# Safe Push Script - Never break CI again!
# Combines pre-push validation + push + post-push monitoring
# Usage: .\scripts\safe-push.ps1 [-Message "commit message"] [-Quick] [-Force]

param(
    [switch]$Quick,
    [switch]$Force,
    [string]$Message,
    [string]$Branch = "master",
    [switch]$NoMonitor  # Skip post-push monitoring
)

Write-Host "`nâ•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•-" -ForegroundColor Cyan
Write-Host "â•‘  ðŸš€ SAFE PUSH - BULLETPROOF CI/CD WORKFLOW ðŸš€               â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•`n" -ForegroundColor Cyan

# Step 1: Pre-Push Validation
Write-Host "STEP 1: Pre-Push Validation`n" -ForegroundColor Yellow
Write-Host "Running all CI checks locally...`n" -ForegroundColor White

if ($Quick) {
    & "$PSScriptRoot\pre-push-check.ps1" -Quick
} else {
    & "$PSScriptRoot\pre-push-check.ps1"
}

$validationResult = $LASTEXITCODE

if ($validationResult -ne 0 -and -not $Force) {
    Write-Host "`nâŒ Pre-push checks failed! Not pushing.`n" -ForegroundColor Red
    Write-Host "Fix the issues or use -Force to push anyway (not recommended)`n" -ForegroundColor Yellow
    Write-Host "To see details:" -ForegroundColor Cyan
    Write-Host "  .\scripts\pre-push-check.ps1 -Verbose`n" -ForegroundColor White
    exit 1
}

if ($Force) {
    Write-Host "`nâš ï¸  FORCING PUSH despite validation failures!`n" -ForegroundColor Yellow
}

# Step 2: Commit Changes (if message provided)
if ($Message) {
    Write-Host "`nSTEP 2: Committing Changes`n" -ForegroundColor Yellow
    git add -A

    $commitOutput = git commit -m "$Message" 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "âœ… Changes committed`n" -ForegroundColor Green
    } elseif ($commitOutput -match "nothing to commit") {
        Write-Host "â„¹ï¸  No changes to commit`n" -ForegroundColor Cyan
    } else {
        Write-Host "âŒ Commit failed`n" -ForegroundColor Red
        $commitOutput
        exit 1
    }
}

# Step 3: Push
Write-Host "STEP 3: Pushing to GitHub`n" -ForegroundColor Yellow
Write-Host "Pushing to: origin/$Branch`n" -ForegroundColor White

git push origin $Branch

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nâŒ Push failed`n" -ForegroundColor Red
    exit 1
}

Write-Host "âœ… Pushed to $Branch`n" -ForegroundColor Green

# Step 4: Monitor CI (unless skipped)
if (-not $NoMonitor) {
    Write-Host "STEP 4: Monitoring GitHub Actions`n" -ForegroundColor Yellow
    Write-Host "Starting automated CI monitoring...`n" -ForegroundColor White

    & "$PSScriptRoot\monitor-ci.ps1" -AutoFix -Continuous -Branch $Branch

    exit $LASTEXITCODE
} else {
    Write-Host "STEP 4: Monitoring Skipped`n" -ForegroundColor Yellow
    Write-Host "Check manually: https://github.com/sandraschi/advanced-memory-mcp/actions`n" -ForegroundColor Cyan
    exit 0
}
