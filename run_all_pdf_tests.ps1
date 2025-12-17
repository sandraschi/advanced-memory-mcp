# Run all PDF export tests

Write-Host "Running PDF Export Tests..." -ForegroundColor Cyan

cd d:\Dev\repos\advanced-memory-mcp

# Run all PDF export tests
py -3.13 -m pytest tests\mcp\test_export_pdf_native.py -v --tb=short

Write-Host "`nTests completed!" -ForegroundColor Green
