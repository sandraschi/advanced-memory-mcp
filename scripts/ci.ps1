$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "== advanced-memory-mcp CI ==" -ForegroundColor Cyan
uv sync --group dev
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv run ruff check src tests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv run ruff format --check src tests
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
uv run pytest -q --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "CI passed." -ForegroundColor Green
