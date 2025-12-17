# Run comprehensive HTML export tests

Write-Host "Running HTML Export Combined Tests..." -ForegroundColor Cyan
py -3.13 -m pytest tests\mcp\test_export_html_combined.py -v --tb=short --color=yes

Write-Host "`nRunning Basic HTML Export Tests..." -ForegroundColor Cyan
py -3.13 -m pytest tests\mcp\test_export_html.py -v --tb=short --color=yes

Write-Host "`nAll HTML export tests completed!" -ForegroundColor Green
