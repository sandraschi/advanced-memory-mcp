#!/usr/bin/env pwsh
# CI Workflow Monitor for Advanced Memory MCP
# Monitors GitHub Actions after push, detects failures, and optionally auto-fixes
# Usage: .\scripts\monitor-ci.ps1 [-AutoFix] [-Continuous] [-WaitSeconds 120]

param(
    [int]$WaitSeconds = 120,     # Wait 2 minutes before checking
    [switch]$AutoFix,            # Automatically fix and repush
    [switch]$Continuous,         # Keep monitoring until success
    [int]$MaxAttempts = 3,       # Max auto-fix attempts
    [string]$Branch = "master"   # Branch to monitor
)

function Get-LatestWorkflowRun {
    # Get latest workflow run status from GitHub API
    $repo = "sandraschi/advanced-memory-mcp"
    $apiUrl = "https://api.github.com/repos/$repo/actions/runs?branch=$Branch&per_page=1"
    
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Headers @{
            "Accept" = "application/vnd.github+json"
        }
        return $response.workflow_runs[0]
    } catch {
        Write-Host "❌ Failed to fetch workflow status: $_" -ForegroundColor Red
        return $null
    }
}

function Get-WorkflowDetails {
    param($RunId)
    
    $repo = "sandraschi/advanced-memory-mcp"
    $apiUrl = "https://api.github.com/repos/$repo/actions/runs/$RunId/jobs"
    
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Headers @{
            "Accept" = "application/vnd.github+json"
        }
        return $response.jobs
    } catch {
        Write-Host "❌ Failed to fetch job details: $_" -ForegroundColor Red
        return $null
    }
}

function Analyze-Failures {
    param($Jobs)
    
    $failures = @{
        lint = $false
        format = $false
        tests = $false
        build = $false
        security = $false
        details = @()
    }
    
    foreach ($job in $Jobs) {
        if ($job.conclusion -eq "failure") {
            $jobName = $job.name.ToLower()
            
            $failures.details += @{
                name = $job.name
                url = $job.html_url
                conclusion = $job.conclusion
            }
            
            if ($jobName -match "lint") { $failures.lint = $true }
            if ($jobName -match "format") { $failures.format = $true }
            if ($jobName -match "test") { $failures.tests = $true }
            if ($jobName -match "build") { $failures.build = $true }
            if ($jobName -match "security") { $failures.security = $true }
        }
    }
    
    return $failures
}

function Auto-Fix-Issues {
    param($Failures)
    
    $fixed = $false
    $commitMessage = "fix: auto-fix CI failures"
    $changes = @()
    
    Write-Host "`n🔧 AUTO-FIXING DETECTED ISSUES...`n" -ForegroundColor Yellow
    
    # Fix format issues
    if ($Failures.format) {
        Write-Host "Fixing format issues..." -ForegroundColor Cyan
        ruff format . | Out-Null
        $changes += "format"
        $fixed = $true
    }
    
    # Fix lint issues
    if ($Failures.lint) {
        Write-Host "Fixing lint issues..." -ForegroundColor Cyan
        ruff check . --fix | Out-Null
        $changes += "lint"
        $fixed = $true
    }
    
    # Tests can't be auto-fixed
    if ($Failures.tests) {
        Write-Host "`n⚠️  Test failures detected - cannot auto-fix" -ForegroundColor Yellow
        Write-Host "Running tests locally to see failure...`n" -ForegroundColor Cyan
        uv run pytest --maxfail=1 -x --tb=short 2>&1 | Select-Object -Last 30
        return $false
    }
    
    # Build issues need manual intervention
    if ($Failures.build -and -not $Failures.format -and -not $Failures.lint) {
        Write-Host "`n⚠️  Build failures detected - cannot auto-fix" -ForegroundColor Yellow
        Write-Host "This requires manual intervention`n" -ForegroundColor Cyan
        return $false
    }
    
    if ($fixed) {
        $commitMessage += " (" + ($changes -join ", ") + ")"
        Write-Host "`n✅ Applied fixes: $($changes -join ', ')" -ForegroundColor Green
    }
    
    return $fixed
}

# Main monitoring loop
Write-Host "`n🔍 GITHUB ACTIONS MONITOR`n" -ForegroundColor Yellow
Write-Host "Repository: sandraschi/advanced-memory-mcp" -ForegroundColor White
Write-Host "Branch: $Branch" -ForegroundColor White
Write-Host "Auto-fix: $(if ($AutoFix) { 'ENABLED ✅' } else { 'DISABLED ❌' })" -ForegroundColor White
Write-Host "Continuous: $(if ($Continuous) { 'ENABLED ✅' } else { 'DISABLED ❌' })" -ForegroundColor White
Write-Host "Wait time: $WaitSeconds seconds`n" -ForegroundColor White

Write-Host "⏳ Waiting $WaitSeconds seconds for workflows to start...`n" -ForegroundColor Cyan
Start-Sleep -Seconds $WaitSeconds

$attempt = 0
$success = $false

do {
    $attempt++
    
    Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Magenta
    Write-Host "🔄 Check Attempt $attempt of $MaxAttempts`n" -ForegroundColor Yellow
    
    # Get latest workflow run
    Write-Host "Fetching latest workflow status..." -ForegroundColor Cyan
    $workflow = Get-LatestWorkflowRun
    
    if (-not $workflow) {
        Write-Host "❌ Could not fetch workflow status`n" -ForegroundColor Red
        exit 1
    }
    
    $status = $workflow.status
    $conclusion = $workflow.conclusion
    $runUrl = $workflow.html_url
    $workflowName = $workflow.name
    
    Write-Host "Workflow: $workflowName" -ForegroundColor White
    Write-Host "Status: $status" -ForegroundColor White
    if ($conclusion) {
        Write-Host "Conclusion: $conclusion" -ForegroundColor White
    }
    Write-Host "URL: $runUrl`n" -ForegroundColor Cyan
    
    # Wait if still running
    if ($status -eq "in_progress" -or $status -eq "queued") {
        Write-Host "⏳ Workflow still running... waiting 30 seconds`n" -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        continue
    }
    
    # Check conclusion
    if ($conclusion -eq "success") {
        Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║  🎉 WORKFLOW SUCCEEDED! 🎉                                   ║" -ForegroundColor Green
        Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
        $success = $true
        break
    }
    
    if ($conclusion -eq "failure") {
        Write-Host "❌ WORKFLOW FAILED`n" -ForegroundColor Red
        
        # Get job details
        Write-Host "Fetching failure details..." -ForegroundColor Cyan
        $jobs = Get-WorkflowDetails -RunId $workflow.id
        
        if ($jobs) {
            Write-Host "`nFailed jobs:" -ForegroundColor Yellow
            foreach ($job in $jobs) {
                if ($job.conclusion -eq "failure") {
                    Write-Host "  ❌ $($job.name)" -ForegroundColor Red
                    Write-Host "     URL: $($job.html_url)" -ForegroundColor Gray
                }
            }
            
            # Analyze failures
            $failures = Analyze-Failures -Jobs $jobs
            
            # Auto-fix if enabled
            if ($AutoFix -and ($failures.lint -or $failures.format)) {
                $fixed = Auto-Fix-Issues -Failures $failures
                
                if ($fixed) {
                    Write-Host "`n✅ Auto-fixes applied!`n" -ForegroundColor Green
                    Write-Host "Committing fixes..." -ForegroundColor Cyan
                    git add -A
                    git commit -m "fix: auto-fix CI failures (format/lint)

Auto-fixed by monitor-ci.ps1 script after workflow failure.
Detected and fixed: format and/or lint issues.

Signed-off-by: CI Monitor <ci@advanced-memory.com>"
                    
                    Write-Host "Pushing fixes..." -ForegroundColor Cyan
                    git push origin $Branch
                    
                    Write-Host "`n⏳ Waiting 120 seconds for new workflow...`n" -ForegroundColor Yellow
                    Start-Sleep -Seconds 120
                } else {
                    Write-Host "`n❌ Could not auto-fix failures`n" -ForegroundColor Red
                    Write-Host "Manual intervention required!" -ForegroundColor Yellow
                    Write-Host "Check: $runUrl`n" -ForegroundColor Cyan
                    break
                }
            } else {
                if (-not $AutoFix) {
                    Write-Host "`n💡 To auto-fix format/lint issues, run with -AutoFix flag`n" -ForegroundColor Yellow
                }
                Write-Host "Check details at: $runUrl`n" -ForegroundColor Cyan
                break
            }
        }
    }
    
    if ($conclusion -eq "cancelled") {
        Write-Host "⚠️  Workflow was cancelled`n" -ForegroundColor Yellow
        break
    }
    
} while ($Continuous -and $attempt -lt $MaxAttempts -and -not $success)

# Final status
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Magenta

if ($success) {
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  🎊 ALL WORKFLOWS SUCCEEDED! 🎊                              ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    exit 0
} elseif ($attempt -ge $MaxAttempts) {
    Write-Host "⚠️  Max attempts reached ($MaxAttempts)`n" -ForegroundColor Yellow
    Write-Host "Manual intervention required`n" -ForegroundColor Red
    Write-Host "Check: https://github.com/sandraschi/advanced-memory-mcp/actions`n" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "⏹️  Monitoring stopped`n" -ForegroundColor Yellow
    Write-Host "Check status: https://github.com/sandraschi/advanced-memory-mcp/actions`n" -ForegroundColor Cyan
    exit 1
}

