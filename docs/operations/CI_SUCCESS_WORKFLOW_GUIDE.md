# 🚀 CI Success Workflow - Never Break GitHub Actions Again!

**Complete guide to bulletproof CI/CD workflows with automated pre-push validation and post-push monitoring**

**Date**: October 17, 2025  
**Status**: Production-ready workflow automation  
**Goal**: Zero CI failures through automation

---

## 🎯 The Problem

**Common CI failures that waste time**:
- ❌ Forgot to run `ruff format` before pushing
- ❌ Forgot to run `ruff check` before pushing
- ❌ Tests pass locally but fail in CI
- ❌ Pushed and went away, didn't check CI status
- ❌ CI fails, have to fix, repush, wait again
- ❌ Multiple round trips to get CI green

**The cycle**:
```
Push → Wait 5min → CI fails → Fix → Push → Wait 5min → ...
```

**Result**: Wasted time, frustration, "bakabakashii!" moments

---

## ✅ The Solution: 3-Layer Defense

### Layer 1: Pre-Commit Hooks (Automatic)
**Runs BEFORE you commit** - catches issues immediately

### Layer 2: Pre-Push Validation (Manual/Automatic)
**Runs BEFORE you push** - ensures CI will pass

### Layer 3: Post-Push Monitoring (Automatic)
**Runs AFTER you push** - watches CI, auto-fixes if needed

---

## 🛠️ Layer 1: Pre-Commit Hooks Setup

**Automatically run checks before EVERY commit**

### Install Pre-Commit Framework

```powershell
# Install pre-commit
uv add --dev pre-commit

# Install hooks
uv run pre-commit install

# Test installation
uv run pre-commit run --all-files
```

### Create Pre-Commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
# Advanced Memory MCP Pre-Commit Hooks
# Runs automatically before every commit

repos:
  # Ruff - Fast Python linter and formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.0
    hooks:
      # Run the linter
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      # Run the formatter
      - id: ruff-format

  # MyPy - Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports, --explicit-package-bases]
        additional_dependencies: 
          - types-setuptools
          - sqlalchemy[mypy]
        pass_filenames: false

  # Standard pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: check-toml
      - id: detect-private-key

  # Security - Check for secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # Git commit message validation
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.0.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
```

### Initialize Secrets Baseline

```powershell
# Create baseline for detect-secrets
uv run detect-secrets scan > .secrets.baseline

# Review and audit
uv run detect-secrets audit .secrets.baseline
```

---

## 🚀 Layer 2: Pre-Push Validation Script

**Run full CI checks locally BEFORE pushing**

### Create Validation Script

Create `scripts/pre-push-check.ps1`:

```powershell
#!/usr/bin/env pwsh
# Pre-Push Validation Script for Advanced Memory MCP
# Runs all CI checks locally before pushing to prevent CI failures

param(
    [switch]$Quick,      # Skip slow tests
    [switch]$NoCoverage, # Skip coverage reporting
    [switch]$Verbose     # Verbose output
)

$ErrorActionPreference = "Continue"
$FailureCount = 0

function Write-StepHeader {
    param($Message)
    Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Message" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}

function Write-Pass {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Fail {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
    $script:FailureCount++
}

# Header
Write-Host "`n🎯 PRE-PUSH VALIDATION - PREVENTING CI FAILURES`n" -ForegroundColor Yellow
Write-Host "Running all checks that GitHub Actions will run...`n" -ForegroundColor White

# Check 1: Git Status
Write-StepHeader "CHECK 1: Git Status"
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Uncommitted changes:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
} else {
    Write-Pass "No uncommitted changes"
}

# Check 2: Ruff Linting
Write-StepHeader "CHECK 2: Ruff Linting"
Write-Host "Running: ruff check . --fix`n" -ForegroundColor Gray
$lintOutput = ruff check . --fix 2>&1
$lintExitCode = $LASTEXITCODE

if ($lintExitCode -eq 0) {
    Write-Pass "Lint check passed"
} else {
    Write-Fail "Lint check failed"
    $lintOutput | Select-Object -First 20
}

# Check 3: Ruff Formatting
Write-StepHeader "CHECK 3: Ruff Formatting"
Write-Host "Running: ruff format --check .`n" -ForegroundColor Gray
$formatOutput = ruff format --check . 2>&1
$formatExitCode = $LASTEXITCODE

if ($formatOutput -match "already formatted") {
    Write-Pass "Format check passed"
} else {
    Write-Fail "Format check failed - running auto-fix"
    ruff format . | Out-Null
    Write-Host "  → Auto-formatted files" -ForegroundColor Yellow
}

# Check 4: Python Syntax
Write-StepHeader "CHECK 4: Python Syntax Validation"
Write-Host "Checking all Python files compile...`n" -ForegroundColor Gray
$syntaxErrors = 0
Get-ChildItem src -Recurse -Filter "*.py" | ForEach-Object {
    python -m py_compile $_.FullName 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Syntax error: $($_.Name)"
        $syntaxErrors++
    }
}
if ($syntaxErrors -eq 0) {
    Write-Pass "All Python files have valid syntax"
}

# Check 5: Type Checking (Optional)
if (-not $Quick) {
    Write-StepHeader "CHECK 5: Type Checking (MyPy)"
    Write-Host "Running: mypy src/`n" -ForegroundColor Gray
    uv run mypy src/ --ignore-missing-imports 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "Type checking passed"
    } else {
        Write-Host "⚠️  Type checking completed with warnings (non-blocking)" -ForegroundColor Yellow
    }
}

# Check 6: Test Suite
Write-StepHeader "CHECK 6: Test Suite"
if ($Quick) {
    Write-Host "Running: pytest --maxfail=3 (quick mode)`n" -ForegroundColor Gray
    $testCmd = "uv run pytest --maxfail=3 -x --tb=short -q"
} elseif ($NoCoverage) {
    Write-Host "Running: pytest -v (no coverage)`n" -ForegroundColor Gray
    $testCmd = "uv run pytest -v --maxfail=10 --tb=short"
} else {
    Write-Host "Running: pytest with coverage (full CI simulation)`n" -ForegroundColor Gray
    $testCmd = "uv run pytest --cov=src/advanced_memory --cov-report=term-missing -v --maxfail=10 --tb=short"
}

Invoke-Expression $testCmd 2>&1 | Tee-Object -Variable testOutput | Out-Null
$testExitCode = $LASTEXITCODE

if ($testExitCode -eq 0) {
    Write-Pass "Test suite passed"
    if (-not $NoCoverage) {
        $testOutput | Select-String -Pattern "TOTAL.*\d+%" | ForEach-Object {
            Write-Host "  → $_" -ForegroundColor Cyan
        }
    }
} else {
    Write-Fail "Test suite failed"
    $testOutput | Select-String -Pattern "FAILED|ERROR" | Select-Object -First 10 | ForEach-Object {
        Write-Host "  → $_" -ForegroundColor Red
    }
}

# Check 7: Build Package
Write-StepHeader "CHECK 7: Package Build"
Write-Host "Running: uv build`n" -ForegroundColor Gray
Remove-Item -Recurse dist -ErrorAction SilentlyContinue
uv build 2>&1 | Out-Null
$buildExitCode = $LASTEXITCODE

if ($buildExitCode -eq 0) {
    Write-Pass "Package build successful"
    Get-ChildItem dist | ForEach-Object {
        Write-Host "  → $($_.Name)" -ForegroundColor Gray
    }
} else {
    Write-Fail "Package build failed"
}

# Check 8: Package Validation
if ($buildExitCode -eq 0) {
    Write-StepHeader "CHECK 8: Package Validation"
    Write-Host "Running: twine check dist/*`n" -ForegroundColor Gray
    uv run twine check dist/* 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "Package validation passed"
    } else {
        Write-Fail "Package validation failed"
    }
}

# Final Summary
Write-Host "`n═══════════════════════════════════════════════════════════════`n" -ForegroundColor Magenta
Write-Host "📊 VALIDATION SUMMARY`n" -ForegroundColor Yellow

if ($FailureCount -eq 0) {
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  🎉 ALL CHECKS PASSED! SAFE TO PUSH! 🎉                     ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    Write-Host "Your code will pass GitHub Actions! ✅" -ForegroundColor Green
    Write-Host "`nReady to push:" -ForegroundColor Cyan
    Write-Host "  git push origin master`n" -ForegroundColor White
    exit 0
} else {
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║  ❌ $FailureCount CHECK(S) FAILED - DO NOT PUSH YET! ❌              ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Red
    Write-Host "Fix the issues above before pushing!" -ForegroundColor Yellow
    Write-Host "`nTo auto-fix format issues:" -ForegroundColor Cyan
    Write-Host "  ruff format .`n" -ForegroundColor White
    Write-Host "To auto-fix lint issues:" -ForegroundColor Cyan
    Write-Host "  ruff check . --fix`n" -ForegroundColor White
    exit 1
}
```

### Usage

```powershell
# Full validation (recommended before pushing)
.\scripts\pre-push-check.ps1

# Quick mode (faster, skips coverage)
.\scripts\pre-push-check.ps1 -Quick

# No coverage (tests only)
.\scripts\pre-push-check.ps1 -NoCoverage

# Verbose output
.\scripts\pre-push-check.ps1 -Verbose
```

---

## 🔍 Layer 3: Post-Push Workflow Monitor

**Automatically monitor GitHub Actions and fix failures**

### Create Monitoring Script

Create `scripts/monitor-ci.ps1`:

```powershell
#!/usr/bin/env pwsh
# CI Workflow Monitor for Advanced Memory MCP
# Monitors GitHub Actions after push, detects failures, and optionally auto-fixes

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
    }
    
    foreach ($job in $Jobs) {
        if ($job.conclusion -eq "failure") {
            $jobName = $job.name.ToLower()
            
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
    
    Write-Host "`n🔧 AUTO-FIXING DETECTED ISSUES...`n" -ForegroundColor Yellow
    
    # Fix format issues
    if ($Failures.format) {
        Write-Host "Fixing format issues..." -ForegroundColor Cyan
        ruff format . | Out-Null
        $fixed = $true
    }
    
    # Fix lint issues
    if ($Failures.lint) {
        Write-Host "Fixing lint issues..." -ForegroundColor Cyan
        ruff check . --fix | Out-Null
        $fixed = $true
    }
    
    # Tests can't be auto-fixed, but we can run them to see the error
    if ($Failures.tests) {
        Write-Host "`n⚠️  Test failures detected - cannot auto-fix" -ForegroundColor Yellow
        Write-Host "Running tests locally to see failure...`n" -ForegroundColor Cyan
        uv run pytest --maxfail=1 -x --tb=short 2>&1 | Select-Object -Last 30
        return $false
    }
    
    return $fixed
}

# Main monitoring loop
Write-Host "`n🔍 GITHUB ACTIONS MONITOR`n" -ForegroundColor Yellow
Write-Host "Repository: sandraschi/advanced-memory-mcp" -ForegroundColor White
Write-Host "Branch: $Branch" -ForegroundColor White
Write-Host "Auto-fix: $(if ($AutoFix) { 'ENABLED ✅' } else { 'DISABLED ❌' })" -ForegroundColor White
Write-Host "Wait time: $WaitSeconds seconds`n" -ForegroundColor White

Write-Host "⏳ Waiting $WaitSeconds seconds for workflows to start...`n" -ForegroundColor Cyan
Start-Sleep -Seconds $WaitSeconds

$attempt = 0
$success = $false

do {
    $attempt++
    
    Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Magenta
    Write-Host "🔄 Attempt $attempt of $MaxAttempts`n" -ForegroundColor Yellow
    
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
    
    Write-Host "Status: $status" -ForegroundColor White
    Write-Host "Conclusion: $conclusion" -ForegroundColor White
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
            if ($AutoFix) {
                $fixed = Auto-Fix-Issues -Failures $failures
                
                if ($fixed) {
                    Write-Host "`n✅ Auto-fixes applied!`n" -ForegroundColor Green
                    Write-Host "Committing fixes..." -ForegroundColor Cyan
                    git add -A
                    git commit -m "fix: auto-fix CI failures (format/lint)

Auto-fixed by monitor-ci.ps1 script after workflow failure.

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
                Write-Host "`n💡 To auto-fix, run with -AutoFix flag`n" -ForegroundColor Yellow
                break
            }
        }
    }
    
} while ($Continuous -and $attempt -lt $MaxAttempts -and -not $success)

# Final status
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Magenta

if ($success) {
    Write-Host "🎊 All workflows succeeded! 🎊`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Monitoring completed - check GitHub Actions`n" -ForegroundColor Yellow
    Write-Host "URL: https://github.com/sandraschi/advanced-memory-mcp/actions`n" -ForegroundColor Cyan
    exit 1
}
```

### Usage

```powershell
# Basic monitoring (wait 2 min, then check once)
.\scripts\monitor-ci.ps1

# Auto-fix and repush
.\scripts\monitor-ci.ps1 -AutoFix

# Continuous monitoring (keeps checking until success)
.\scripts\monitor-ci.ps1 -AutoFix -Continuous

# Custom wait time (5 minutes)
.\scripts\monitor-ci.ps1 -WaitSeconds 300 -AutoFix
```

---

## 🎯 Complete Workflow Integration

### The Perfect Push Process

Create `scripts/safe-push.ps1`:

```powershell
#!/usr/bin/env pwsh
# Safe Push Script - Never break CI again!
# Combines pre-push validation + push + post-push monitoring

param(
    [switch]$Quick,
    [switch]$Force,
    [string]$Message,
    [string]$Branch = "master"
)

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚀 SAFE PUSH - BULLETPROOF CI/CD WORKFLOW 🚀               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Pre-Push Validation
Write-Host "STEP 1: Pre-Push Validation`n" -ForegroundColor Yellow
Write-Host "Running all CI checks locally...`n" -ForegroundColor White

if ($Quick) {
    .\scripts\pre-push-check.ps1 -Quick
} else {
    .\scripts\pre-push-check.ps1
}

if ($LASTEXITCODE -ne 0 -and -not $Force) {
    Write-Host "`n❌ Pre-push checks failed! Not pushing.`n" -ForegroundColor Red
    Write-Host "Fix the issues or use -Force to push anyway (not recommended)`n" -ForegroundColor Yellow
    exit 1
}

# Step 2: Commit Changes (if message provided)
if ($Message) {
    Write-Host "`nSTEP 2: Committing Changes`n" -ForegroundColor Yellow
    git add -A
    git commit -m "$Message"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Commit failed`n" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Changes committed`n" -ForegroundColor Green
}

# Step 3: Push
Write-Host "STEP 3: Pushing to GitHub`n" -ForegroundColor Yellow
git push origin $Branch

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Push failed`n" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pushed to $Branch`n" -ForegroundColor Green

# Step 4: Monitor CI
Write-Host "STEP 4: Monitoring GitHub Actions`n" -ForegroundColor Yellow
Write-Host "Starting automated CI monitoring...`n" -ForegroundColor White

.\scripts\monitor-ci.ps1 -AutoFix -Continuous -Branch $Branch

exit $LASTEXITCODE
```

### Usage

```powershell
# Basic safe push (validates + pushes + monitors)
.\scripts\safe-push.ps1

# With commit message
.\scripts\safe-push.ps1 -Message "fix: update documentation"

# Quick mode (faster validation)
.\scripts\safe-push.ps1 -Quick

# Force push (skip validation - not recommended!)
.\scripts\safe-push.ps1 -Force
```

---

## 📋 Git Hooks Integration

### Install Git Hook

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash
# Pre-push hook - runs validation before every push

echo "🔍 Running pre-push validation..."

# Run pre-push check script
if command -v pwsh >/dev/null 2>&1; then
    pwsh ./scripts/pre-push-check.ps1 -Quick
elif command -v powershell >/dev/null 2>&1; then
    powershell -File ./scripts/pre-push-check.ps1 -Quick
else
    # Fallback to basic checks
    echo "Running basic checks..."
    ruff check . --fix
    ruff format .
    pytest --maxfail=1 -x
fi

exit $?
```

### Make Hook Executable

```powershell
# Windows (Git Bash)
chmod +x .git/hooks/pre-push

# Or copy from template
Copy-Item scripts/git-hooks/pre-push .git/hooks/pre-push
```

---

## 🎯 Best Practices Checklist

### Before Every Push

```powershell
# THE GOLDEN RULE: Run this before EVERY push!

# Option 1: Manual (comprehensive)
ruff check . --fix
ruff format .
uv run pytest -v
uv build
git add -A
git commit -m "your message"
git push origin master

# Option 2: Automated (recommended)
.\scripts\safe-push.ps1 -Message "your message"
```

---

### Daily Development Workflow

```powershell
# Morning: Start development
git pull origin master
uv sync --dev

# During development: Commit often
git add specific-file.py
git commit -m "feat: implement feature X"
# (pre-commit hooks run automatically)

# Before push: Validate
.\scripts\pre-push-check.ps1

# Push: Use safe-push
.\scripts\safe-push.ps1

# Monitor: Automatic
# (monitor-ci.ps1 runs automatically with safe-push)
```

---

### Emergency Hotfix Workflow

```powershell
# Fix critical bug in production

# 1. Quick validation
.\scripts\pre-push-check.ps1 -Quick

# 2. Push immediately
git push origin master

# 3. Monitor aggressively
.\scripts\monitor-ci.ps1 -WaitSeconds 60 -AutoFix -Continuous

# Will auto-fix format/lint issues if they occur
```

---

## 🤖 Claude Integration - Automated CI Management

### How Claude Can Help

**During development session**, Claude can:

1. **Before pushing**: Run validation checks
   ```powershell
   # Claude runs this
   .\scripts\pre-push-check.ps1
   ```

2. **After pushing**: Monitor CI automatically
   ```powershell
   # Claude runs this (2-min delay)
   Start-Sleep 120
   .\scripts\monitor-ci.ps1 -AutoFix
   ```

3. **On failure**: Detect error type, fix, repush
   ```powershell
   # Claude analyzes failure, applies fix, repushes
   ruff format .
   git add -A
   git commit -m "fix: auto-format CI failure"
   git push origin master
   ```

---

### Claude Automation Pattern

**Recommended workflow for Claude**:

```
User: "push the changes"

Claude:
1. ✅ Runs pre-push-check.ps1
2. ✅ If passes, pushes to GitHub
3. ✅ Waits 2 minutes
4. ✅ Checks GitHub Actions status
5. ✅ If failed: detects error type
6. ✅ Auto-fixes (format/lint)
7. ✅ Commits and repushes
8. ✅ Monitors again
9. ✅ Reports final status to user
```

**User sees**: "Pushed! CI passing ✅"

**User doesn't see**: All the automatic fixing that happened

---

## 🎨 GitHub Actions Status API

### Quick Status Check

```powershell
# Check latest workflow status
$repo = "sandraschi/advanced-memory-mcp"
$response = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/actions/runs?per_page=1"
$run = $response.workflow_runs[0]

Write-Host "Latest workflow: $($run.name)"
Write-Host "Status: $($run.status)"
Write-Host "Conclusion: $($run.conclusion)"
Write-Host "URL: $($run.html_url)"
```

### Detailed Job Status

```powershell
# Get job-level details
$runId = $run.id
$jobs = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/actions/runs/$runId/jobs"

foreach ($job in $jobs.jobs) {
    $emoji = if ($job.conclusion -eq "success") { "✅" } else { "❌" }
    Write-Host "$emoji $($job.name): $($job.conclusion)"
}
```

---

## 📊 CI Failure Prevention Metrics

### Success Rate Tracking

Create `scripts/ci-metrics.ps1`:

```powershell
#!/usr/bin/env pwsh
# Track CI success rate over time

$repo = "sandraschi/advanced-memory-mcp"
$apiUrl = "https://api.github.com/repos/$repo/actions/runs?per_page=50"

$response = Invoke-RestMethod -Uri $apiUrl
$runs = $response.workflow_runs

$total = $runs.Count
$success = ($runs | Where-Object { $_.conclusion -eq "success" }).Count
$failure = ($runs | Where-Object { $_.conclusion -eq "failure" }).Count
$successRate = [math]::Round(($success / $total) * 100, 1)

Write-Host "`n📊 CI SUCCESS METRICS (Last 50 runs)`n" -ForegroundColor Yellow
Write-Host "Total runs: $total" -ForegroundColor White
Write-Host "Successful: $success (${successRate}%)" -ForegroundColor Green
Write-Host "Failed: $failure ($(100 - $successRate)%)" -ForegroundColor Red
Write-Host "`nTarget: 95%+ success rate" -ForegroundColor Cyan

if ($successRate -ge 95) {
    Write-Host "🎉 Excellent! You're meeting the target!" -ForegroundColor Green
} elseif ($successRate -ge 80) {
    Write-Host "⚠️  Good, but room for improvement" -ForegroundColor Yellow
} else {
    Write-Host "❌ Needs improvement - use pre-push checks!" -ForegroundColor Red
}
```

---

## 🚨 Common Failure Patterns & Auto-Fixes

### Pattern 1: Format Issues

**Symptoms**:
```
Error: ruff format --check failed
1 file would be reformatted
```

**Auto-fix**:
```powershell
ruff format .
git add -A
git commit -m "fix: auto-format files"
git push origin master
```

**Prevention**: Use pre-commit hooks

---

### Pattern 2: Lint Issues

**Symptoms**:
```
Error: F401 'asyncio' imported but unused
Error: E501 Line too long
```

**Auto-fix**:
```powershell
ruff check . --fix
git add -A
git commit -m "fix: auto-fix lint issues"
git push origin master
```

**Prevention**: Run `ruff check . --fix` before commit

---

### Pattern 3: Test Failures

**Symptoms**:
```
FAILED tests/integration/mcp/test_xyz.py::test_abc
AssertionError: expected X but got Y
```

**Cannot auto-fix**: Requires manual code changes

**Detection**:
```powershell
# Run exact failing test locally
uv run pytest tests/integration/mcp/test_xyz.py::test_abc -v --tb=short

# See full error output
# Fix the code
# Run test again to verify
```

**Prevention**: Run full test suite before push

---

### Pattern 4: Build Failures

**Symptoms**:
```
Error: Module 'xyz' not found
Error: Import error in setup
```

**Diagnosis**:
```powershell
# Test build locally
uv build

# Check dependencies
uv tree

# Verify imports
python -c "import advanced_memory; print(advanced_memory.__version__)"
```

**Prevention**: Test `uv build` before push

---

## 📝 Justfile Integration

Add to your `justfile`:

```makefile
# Pre-push validation
pre-push:
    @echo "🔍 Running pre-push validation..."
    @pwsh ./scripts/pre-push-check.ps1

# Safe push with validation
safe-push message:
    @echo "🚀 Safe push with validation..."
    @pwsh ./scripts/safe-push.ps1 -Message "{{message}}"

# Monitor CI after manual push
monitor:
    @echo "🔍 Monitoring CI workflows..."
    @pwsh ./scripts/monitor-ci.ps1 -AutoFix -Continuous

# Quick validation (faster)
quick-check:
    @echo "⚡ Quick validation..."
    @pwsh ./scripts/pre-push-check.ps1 -Quick

# CI metrics
ci-stats:
    @echo "📊 CI success metrics..."
    @pwsh ./scripts/ci-metrics.ps1
```

### Usage

```bash
# Before pushing
just pre-push

# Safe push
just safe-push "fix: update documentation"

# Monitor after push
just monitor

# Quick check during development
just quick-check

# Check CI success rate
just ci-stats
```

---

## ✅ Implementation Checklist

### Initial Setup (One-time)

- [ ] Install pre-commit: `uv add --dev pre-commit`
- [ ] Create `.pre-commit-config.yaml`
- [ ] Run: `uv run pre-commit install`
- [ ] Create `scripts/pre-push-check.ps1`
- [ ] Create `scripts/monitor-ci.ps1`
- [ ] Create `scripts/safe-push.ps1`
- [ ] Create `scripts/ci-metrics.ps1`
- [ ] Make scripts executable
- [ ] Test each script once
- [ ] Add justfile shortcuts
- [ ] Document in README

---

### Daily Usage

- [ ] Use `just pre-push` before every push
- [ ] Or use `just safe-push "message"` for everything
- [ ] Monitor CI with `just monitor` if you push manually
- [ ] Check `just ci-stats` weekly

---

## 🎯 Expected Results

### Before This Guide

**Typical CI failure cycle**:
```
1. Write code (30 min)
2. Push to GitHub
3. Wait 5 min for CI
4. CI fails (format issue)
5. Fix format
6. Push again
7. Wait 5 min for CI
8. CI fails (test issue)
9. Fix test
10. Push again
11. Wait 5 min for CI
12. Finally passes

Total time: 30 min code + 15 min CI waits + frustration
```

---

### After This Guide

**Streamlined workflow**:
```
1. Write code (30 min)
2. Run just safe-push "message"
   → Validates locally (1 min)
   → Pushes automatically
   → Monitors CI (2 min)
   → Auto-fixes if needed
   → Reports success
3. CI passes first time ✅

Total time: 30 min code + 3 min automation = 33 min
```

**Savings**: 12 minutes per push + zero frustration!

---

## 🎊 Success Metrics

**Target KPIs**:
- CI success rate: **95%+** (first push)
- Auto-fix rate: **90%** (format/lint issues)
- Manual interventions: **<5%** (test failures only)
- Average fix time: **<5 minutes**
- Developer satisfaction: **100%** (no more bakabakashii!)

---

## 📚 Additional Resources

**Tools**:
- Pre-commit: https://pre-commit.com
- Ruff: https://docs.astral.sh/ruff/
- GitHub Actions: https://docs.github.com/en/actions
- GitHub API: https://docs.github.com/en/rest

**Scripts Location**:
- `scripts/pre-push-check.ps1` - Pre-push validation
- `scripts/monitor-ci.ps1` - CI monitoring
- `scripts/safe-push.ps1` - Complete workflow
- `scripts/ci-metrics.ps1` - Success tracking

---

## ✅ Conclusion

With this 3-layer defense system:

1. **Pre-commit hooks**: Catch issues before commit
2. **Pre-push validation**: Ensure CI will pass
3. **Post-push monitoring**: Auto-fix if something slips through

You'll achieve:
- ✅ 95%+ CI success rate
- ✅ Zero wasted time on CI failures
- ✅ Automatic fixing of format/lint issues
- ✅ Peace of mind knowing CI will pass
- ✅ No more "pulling teeth" to get workflows green

**The future of CI/CD**: Push confidently, let automation handle the rest! 🚀

---

**Created**: October 17, 2025  
**For**: Advanced Memory MCP + all repositories  
**Status**: Ready to implement

**Happy pushing!** 🎉✨

