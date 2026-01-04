#!/usr/bin/env pwsh
# Pre-Push Validation Script for Advanced Memory MCP
# Runs all CI checks locally before pushing to prevent CI failures
# Usage: .\scripts\pre-push-check.ps1 [-Quick] [-NoCoverage] [-Verbose]

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
    $padding = " " * ([math]::Max(0, 61 - $Message.Length))
    Write-Host "║  $Message$padding║" -ForegroundColor Cyan
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
    if ($Verbose) {
        $lintOutput | Select-Object -First 20
    }
}

# Check 3: Ruff Formatting
Write-StepHeader "CHECK 3: Ruff Formatting"
Write-Host "Running: ruff format --check .`n" -ForegroundColor Gray
$formatOutput = ruff format --check . 2>&1
$formatExitCode = $LASTEXITCODE

if ($formatOutput -match "already formatted" -or $formatExitCode -eq 0) {
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
Get-ChildItem src -Recurse -Filter "*.py" -ErrorAction SilentlyContinue | ForEach-Object {
    python -m py_compile $_.FullName 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Syntax error: $($_.Name)"
        $syntaxErrors++
    }
}
if ($syntaxErrors -eq 0) {
    Write-Pass "All Python files have valid syntax"
}

# Check 5: Import Validation
Write-StepHeader "CHECK 5: Critical Import Validation"
Write-Host "Verifying key modules import correctly...`n" -ForegroundColor Gray
$importTests = @(
    "from advanced_memory import __version__",
    "from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker",
    "from advanced_memory.services.template_generator import TemplateGenerator"
)

$importErrors = 0
foreach ($import in $importTests) {
    python -c "$import" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Import failed: $import"
        $importErrors++
    }
}
if ($importErrors -eq 0) {
    Write-Pass "All critical imports successful"
}

# Check 6: Type Checking (Optional, non-blocking)
if (-not $Quick) {
    Write-StepHeader "CHECK 6: Type Checking (MyPy)"
    Write-Host "Running: mypy src/ --ignore-missing-imports`n" -ForegroundColor Gray
    uv run mypy src/ --ignore-missing-imports 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "Type checking passed"
    } else {
        Write-Host "⚠️  Type checking completed with warnings (non-blocking)" -ForegroundColor Yellow
    }
}

# Check 7: Test Suite
Write-StepHeader "CHECK 7: Test Suite"
if ($Quick) {
    Write-Host "Quick mode: Running fast subset (~30 seconds)`n" -ForegroundColor Gray
    $testCmd = "uv run pytest --maxfail=3 -x --tb=line -q"
} elseif ($NoCoverage) {
    Write-Host "Running: ALL tests in parallel (faster!)`n" -ForegroundColor Gray
    Write-Host "Expected time: ~1.5-2 minutes`n" -ForegroundColor Cyan
    $testCmd = "uv run pytest -n auto -v --maxfail=10 --tb=short"
} else {
    Write-Host "Running: FULL test suite with coverage (CI simulation)`n" -ForegroundColor Gray
    Write-Host "Expected time: ~4 minutes" -ForegroundColor Yellow
    Write-Host "⏰ PLEASE BE PATIENT - Tests will run to completion!`n" -ForegroundColor Red
    Write-Host "💡 This matches EXACTLY what CI will run" -ForegroundColor Cyan
    Write-Host "💡 Parallelized for speed (using -n auto)`n" -ForegroundColor Cyan
    $testCmd = "uv run pytest -n auto --cov=src/advanced_memory --cov-report=term-missing --tb=short --cov-fail-under=50"
}

$testOutput = Invoke-Expression $testCmd 2>&1
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
    if ($Verbose) {
        $testOutput | Select-String -Pattern "FAILED|ERROR" | Select-Object -First 10 | ForEach-Object {
            Write-Host "  → $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  Run with -Verbose to see details" -ForegroundColor Gray
    }
}

# Check 8: Build Package
Write-StepHeader "CHECK 8: Package Build"
Write-Host "Running: uv build`n" -ForegroundColor Gray
Remove-Item -Recurse dist -ErrorAction SilentlyContinue
uv build 2>&1 | Out-Null
$buildExitCode = $LASTEXITCODE

if ($buildExitCode -eq 0) {
    Write-Pass "Package build successful"
    if ($Verbose) {
        Get-ChildItem dist -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "  → $($_.Name)" -ForegroundColor Gray
        }
    }
} else {
    Write-Fail "Package build failed"
}

# Check 9: Package Validation
if ($buildExitCode -eq 0) {
    Write-StepHeader "CHECK 9: Package Validation"
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
    Write-Host "To see test details:" -ForegroundColor Cyan
    Write-Host "  .\scripts\pre-push-check.ps1 -Verbose`n" -ForegroundColor White
    exit 1
}
