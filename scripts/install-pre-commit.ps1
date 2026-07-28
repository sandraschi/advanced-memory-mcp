$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
uv sync --group dev
uv run pre-commit install
uv run pre-commit run --all-files
exit $LASTEXITCODE
