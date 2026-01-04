#!/usr/bin/env pwsh
# CI Success Metrics Tracker
# Track CI success rate over time to measure improvement
# Usage: .\scripts\ci-metrics.ps1 [-Count 50] [-Detailed]

param(
    [int]$Count = 50,      # Number of recent runs to analyze
    [switch]$Detailed      # Show detailed breakdown
)

$repo = "sandraschi/advanced-memory-mcp"
$apiUrl = "https://api.github.com/repos/$repo/actions/runs?per_page=$Count"

Write-Host "`n📊 CI SUCCESS METRICS`n" -ForegroundColor Yellow
Write-Host "Repository: $repo" -ForegroundColor White
Write-Host "Analyzing last $Count workflow runs...`n" -ForegroundColor White

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Headers @{
        "Accept" = "application/vnd.github+json"
    }
    $runs = $response.workflow_runs
} catch {
    Write-Host "❌ Failed to fetch workflow data: $_`n" -ForegroundColor Red
    exit 1
}

$total = $runs.Count
$success = ($runs | Where-Object { $_.conclusion -eq "success" }).Count
$failure = ($runs | Where-Object { $_.conclusion -eq "failure" }).Count
$cancelled = ($runs | Where-Object { $_.conclusion -eq "cancelled" }).Count
$inProgress = ($runs | Where-Object { $_.status -eq "in_progress" -or $_.status -eq "queued" }).Count

$successRate = if ($total -gt 0) { [math]::Round(($success / $total) * 100, 1) } else { 0 }
$failureRate = if ($total -gt 0) { [math]::Round(($failure / $total) * 100, 1) } else { 0 }

# Summary
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
Write-Host "📈 OVERALL STATISTICS`n" -ForegroundColor Yellow

Write-Host "Total runs: $total" -ForegroundColor White
Write-Host "Successful: $success (${successRate}%)" -ForegroundColor Green
Write-Host "Failed: $failure (${failureRate}%)" -ForegroundColor Red
Write-Host "Cancelled: $cancelled" -ForegroundColor Yellow
Write-Host "In Progress: $inProgress`n" -ForegroundColor Cyan

# Success rate assessment
Write-Host "Success Rate: ${successRate}%  " -NoNewline
if ($successRate -ge 95) {
    Write-Host "🏆 EXCELLENT!" -ForegroundColor Green
} elseif ($successRate -ge 80) {
    Write-Host "⭐ GOOD" -ForegroundColor Yellow
} elseif ($successRate -ge 60) {
    Write-Host "⚠️  NEEDS IMPROVEMENT" -ForegroundColor Yellow
} else {
    Write-Host "❌ CRITICAL - Use pre-push checks!" -ForegroundColor Red
}

Write-Host "`nTarget: 95%+ success rate" -ForegroundColor Cyan

# Detailed breakdown
if ($Detailed) {
    Write-Host "`n═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
    Write-Host "📋 RECENT WORKFLOW HISTORY`n" -ForegroundColor Yellow

    foreach ($run in $runs | Select-Object -First 10) {
        $emoji = switch ($run.conclusion) {
            "success" { "✅" }
            "failure" { "❌" }
            "cancelled" { "⚠️ " }
            default { "⏳" }
        }

        $date = [DateTime]::Parse($run.created_at).ToString("MM/dd HH:mm")
        $duration = if ($run.conclusion) {
            $start = [DateTime]::Parse($run.created_at)
            $end = [DateTime]::Parse($run.updated_at)
            $diff = $end - $start
            "$([math]::Floor($diff.TotalMinutes))m $($diff.Seconds)s"
        } else {
            "running"
        }

        Write-Host "$emoji [$date] $($run.name) - $duration" -ForegroundColor White
        if ($run.conclusion -eq "failure") {
            Write-Host "   $($run.html_url)" -ForegroundColor Gray
        }
    }
}

# Failure analysis
if ($failure -gt 0) {
    Write-Host "`n═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
    Write-Host "🔍 FAILURE ANALYSIS`n" -ForegroundColor Yellow

    $failedRuns = $runs | Where-Object { $_.conclusion -eq "failure" } | Select-Object -First 10

    $failureTypes = @{}
    foreach ($run in $failedRuns) {
        $name = $run.name
        if (-not $failureTypes.ContainsKey($name)) {
            $failureTypes[$name] = 0
        }
        $failureTypes[$name]++
    }

    Write-Host "Most common failing workflows:" -ForegroundColor White
    $failureTypes.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
        Write-Host "  $($_.Value)x - $($_.Key)" -ForegroundColor Red
    }
}

# Recommendations
Write-Host "`n═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
Write-Host "💡 RECOMMENDATIONS`n" -ForegroundColor Yellow

if ($successRate -lt 95) {
    Write-Host "To improve success rate:" -ForegroundColor White
    Write-Host "  1. Use .\scripts\pre-push-check.ps1 before every push" -ForegroundColor Cyan
    Write-Host "  2. Install pre-commit hooks: uv run pre-commit install" -ForegroundColor Cyan
    Write-Host "  3. Use .\scripts\safe-push.ps1 for automated workflow" -ForegroundColor Cyan
    Write-Host "  4. Enable auto-monitoring: .\scripts\monitor-ci.ps1 -AutoFix`n" -ForegroundColor Cyan
} else {
    Write-Host "  🎉 You're doing great! Keep it up!`n" -ForegroundColor Green
    Write-Host "  Continue using your current practices." -ForegroundColor White
}

Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

exit 0
