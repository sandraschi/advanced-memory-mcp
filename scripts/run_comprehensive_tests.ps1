# Comprehensive CRUD and Search Test Runner
# Runs the comprehensive test suite and displays the report

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Comprehensive CRUD and Search Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the tests
Write-Host "Running tests..." -ForegroundColor Yellow
$testFile = "tests/mcp/test_comprehensive_crud_and_search.py"
$result = uv run python -m pytest $testFile -v --tb=short

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Report" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Display the report if it exists
$reportPath = "test_report_crud_search.md"
if (Test-Path $reportPath) {
    Write-Host "Report saved to: $reportPath" -ForegroundColor Green
    Write-Host ""
    Get-Content $reportPath | Write-Host
} else {
    Write-Host "Report not found at: $reportPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { "Green" } else { "Red" })
