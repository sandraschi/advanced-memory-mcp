set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# --- Dashboard ---
# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Quality ---

# Execute repo-wide quality checks (Ruff + Biome)
# Note: one shell per line (just + windows-shell); chain with `;` so cwd persists.
lint:
    Set-Location '{{justfile_directory()}}'; uv run ruff check .
    Set-Location '{{justfile_directory()}}/webapp/frontend'; npx biome check src

# Execute repo-wide auto-fixes and formatting (Ruff + Biome)
fix:
    Set-Location '{{justfile_directory()}}'; uv run ruff check . --fix --unsafe-fixes; uv run ruff format .
    Set-Location '{{justfile_directory()}}/webapp/frontend'; npx biome check --write src

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'; uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'; uv run safety check

# --- Advanced Memory CLI ---

stats:
    Set-Location '{{justfile_directory()}}'; uv run python tools/repo_stats.py

# Install project + dev dependency group (uv)
install:
    Set-Location '{{justfile_directory()}}'; uv sync --group dev

bootstrap: install
    uv run pre-commit install
    Set-Location '{{justfile_directory()}}/webapp/frontend'; npm ci; if ($LASTEXITCODE -ne 0) { npm install }
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green

# --- RAG  LanceDB vector index ---

rag-gpu:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-gpu.ps1

rag-gpu-install:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-gpu-install.ps1

rag-cpu-install:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-cpu-install.ps1

# Sync status: files vs database (Rich output best in a real terminal)
status:
    Set-Location '{{justfile_directory()}}'; uv run advanced-memory status

# Run unit tests in parallel (excludes integration + megatest harness)
test-unit:
    Set-Location '{{justfile_directory()}}'; uv run pytest -p pytest_mock -v -n auto tests --ignore=tests/integration --ignore=tests/megatest

# Run integration tests in parallel
test-int:
    Set-Location '{{justfile_directory()}}'; uv run pytest -p pytest_mock -v --no-cov -n auto tests/integration

# Run MCP tool tests (sequential; avoids port / browser contention)
test-mcp:
    Set-Location '{{justfile_directory()}}'; uv run pytest -p pytest_mock -v tests/mcp

# Run all tests (unit + integration)
test: test-unit test-int

# --- Webapp (Playwright browser e2e) ---
# One-time: install npm deps + Chromium for Playwright (large download)
e2e-webapp-install:
    Set-Location '{{justfile_directory()}}/webapp/frontend'; npm install; npx playwright install chromium

# Run Playwright smoke tests (spawns FastAPI + Vite on CI; locally reuses 10704/10705 if already up)
e2e-webapp:
    Set-Location '{{justfile_directory()}}/webapp/frontend'; npm run test:e2e

# Playwright UI mode (step through tests in the browser)
e2e-webapp-ui:
    Set-Location '{{justfile_directory()}}/webapp/frontend'; npm run test:e2e:ui

# Playwright headed (visible Chromium)
e2e-webapp-headed:
    Set-Location '{{justfile_directory()}}/webapp/frontend'; npm run test:e2e:headed

# Type check (pyright)
type-check:
    Set-Location '{{justfile_directory()}}'; uv run pyright

# Clean build artifacts and cache files
@clean:
    Set-Location '{{justfile_directory()}}'; Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue; if (Test-Path "installer/build") { Remove-Item -Recurse -Force "installer/build" }; if (Test-Path "installer/dist") { Remove-Item -Recurse -Force "installer/dist" }; if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }; if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }; Get-ChildItem -Filter "rw.*.dmg" | Remove-Item -Force -ErrorAction SilentlyContinue

# Format code with ruff and Biome
format:
    Set-Location '{{justfile_directory()}}'; uv run ruff format .
    Set-Location '{{justfile_directory()}}/webapp/frontend'; npx biome check --write src

# Run MCP inspector tool
run-inspector:
    Set-Location '{{justfile_directory()}}'; npx @modelcontextprotocol/inspector

# Build MCPB bundle (requires Node.js + npx). Output: dist/advanced-memory-mcp.mcpb
pack:
    Set-Location '{{justfile_directory()}}'; if (-not (Test-Path "dist")) { New-Item -ItemType Directory -Path "dist" | Out-Null }; npx --yes @anthropic-ai/mcpb@latest validate manifest.json; npx --yes @anthropic-ai/mcpb@latest pack . "dist/advanced-memory-mcp.mcpb"

# Build macOS installer
installer-mac:
    cd installer && chmod +x make_icons.sh && ./make_icons.sh
    cd installer && uv run python setup.py bdist_mac

# Build Windows installer
installer-win:
    Set-Location '{{justfile_directory()}}/installer'; uv run python setup.py bdist_win32

# Update all dependencies to latest versions
update-deps:
    Set-Location '{{justfile_directory()}}'; uv sync --upgrade

# Run all code quality checks and tests
check: lint format type-check test

# Generate Alembic migration with descriptive message
migration message:
    Set-Location '{{justfile_directory()}}'; uv run alembic -c src/advanced_memory/alembic/alembic.ini revision --autogenerate -m "{{message}}"

# Create a stable release (e.g., just release v1.6.2)
release version:
    #!/usr/bin/env bash
    set -euo pipefail

    # Validate version format
    if [[ ! "{{version}}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "ERROR: Invalid version format. Use: v1.6.2"
        exit 1
    fi

    # Extract version number without 'v' prefix
    VERSION_NUM=$(echo "{{version}}" | sed 's/^v//')

    echo "Creating stable release {{version}}"

    # Pre-flight checks
    echo "Running pre-flight checks..."
    if [[ -n $(git status --porcelain) ]]; then
        echo "ERROR: Uncommitted changes found. Please commit or stash them first."
        exit 1
    fi

    if [[ $(git branch --show-current) != "main" ]]; then
        echo "ERROR: Not on main branch. Switch to main first."
        exit 1
    fi

    # Check if tag already exists
    if git tag -l "{{version}}" | grep -q "{{version}}"; then
        echo "ERROR: Tag {{version}} already exists"
        exit 1
    fi

    # Run quality checks
    echo "Running quality checks..."
    just check

    # Update version in __init__.py (if it exists)
    if [ -f src/advanced_memory/__init__.py ]; then
        echo "Updating version in src/advanced_memory/__init__.py..."
        sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION_NUM\"/" src/advanced_memory/__init__.py
        rm -f src/advanced_memory/__init__.py.bak
        git add src/advanced_memory/__init__.py
        git commit -m "chore: update version to $VERSION_NUM for {{version}} release"
    fi

    # Create and push tag
    echo "Creating tag {{version}}..."
    git tag "{{version}}"

    echo "Pushing to GitHub..."
    git push origin main
    git push origin "{{version}}"

    echo "OK: Release {{version}} created successfully."
    echo "Monitor: https://github.com/sandraschi/advanced-memory-mcp/actions"

# Create a beta release (e.g., just beta v0.13.2b1)
beta version:
    #!/usr/bin/env bash
    set -euo pipefail

    # Validate version format (allow beta/rc suffixes)
    if [[ ! "{{version}}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(b[0-9]+|rc[0-9]+)$ ]]; then
        echo "ERROR: Invalid beta version format. Use: v0.13.2b1 or v0.13.2rc1"
        exit 1
    fi

    # Extract version number without 'v' prefix
    VERSION_NUM=$(echo "{{version}}" | sed 's/^v//')

    echo "Creating beta release {{version}}"

    # Pre-flight checks
    echo "Running pre-flight checks..."
    if [[ -n $(git status --porcelain) ]]; then
        echo "ERROR: Uncommitted changes found. Please commit or stash them first."
        exit 1
    fi

    if [[ $(git branch --show-current) != "main" ]]; then
        echo "ERROR: Not on main branch. Switch to main first."
        exit 1
    fi

    # Check if tag already exists
    if git tag -l "{{version}}" | grep -q "{{version}}"; then
        echo "ERROR: Tag {{version}} already exists"
        exit 1
    fi

    # Run quality checks
    echo "Running quality checks..."
    just check

    # Update version in __init__.py
    echo "Updating version in __init__.py..."
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION_NUM\"/" src/advanced_memory/__init__.py
    rm -f src/advanced_memory/__init__.py.bak

    # Commit version update
    git add src/advanced_memory/__init__.py
    git commit -m "chore: update version to $VERSION_NUM for {{version}} beta release"

    # Create and push tag
    echo "Creating tag {{version}}..."
    git tag "{{version}}"

    echo "Pushing to GitHub..."
    git push origin main
    git push origin "{{version}}"

    echo "OK: Beta release {{version}} created successfully."
    echo "GitHub Actions can build and publish to PyPI as pre-release."
    echo "Monitor: https://github.com/sandraschi/advanced-memory-mcp/actions"
    echo "Install pre-release: uv tool install advanced-memory --pre"

# --- CI / automation ---
# Pre-push validation (run before every push)
pre-push:
    @echo "Running pre-push validation..."
    @pwsh ./scripts/pre-push-check.ps1

# Quick validation (faster, skips coverage)
quick-check:
    @echo "Quick validation..."
    @pwsh ./scripts/pre-push-check.ps1 -Quick

# Safe push with validation + monitoring
safe-push message:
    @echo "Safe push with validation..."
    @pwsh ./scripts/safe-push.ps1 -Message "{{message}}"

# Monitor CI after manual push
monitor:
    @echo "Monitoring CI workflows..."
    @pwsh ./scripts/monitor-ci.ps1 -AutoFix -Continuous

# Check CI success metrics
ci-stats:
    @echo "CI success metrics..."
    @pwsh ./scripts/ci-metrics.ps1

# Detailed CI metrics with history
ci-stats-detailed:
    @echo "Detailed CI metrics..."
    @pwsh ./scripts/ci-metrics.ps1 -Detailed

# Install pre-commit hooks (one-time setup)
setup-hooks:
    @echo "Installing pre-commit hooks..."
    uv run pre-commit install
    @echo "Pre-commit hooks installed."
    @echo "Hooks run automatically before each commit."

# Run pre-commit on all files
pre-commit-all:
    @echo "Running pre-commit on all files..."
    uv run pre-commit run --all-files

# --- Backup ---
# Create repository backup (excludes .venv, caches, ~30-40 MB)
backup:
    @echo "Creating repository backup..."
    @pwsh ./scripts/backup-repo.ps1

# Create backup including dist/ folder
backup-with-dist:
    @echo "Creating repository backup (with dist/)..."
    @pwsh ./scripts/backup-repo.ps1 -IncludeDist

# Create backup to specific location
backup-to path:
    @echo "Creating repository backup to {{path}}..."
    @pwsh ./scripts/backup-repo.ps1 -OutputPath "{{path}}"

# Create backup with WinRAR instead of 7-Zip
backup-winrar:
	@echo "Creating repository backup (WinRAR)..."
	@pwsh ./scripts/backup-repo.ps1 -UseWinRAR

# --- Native  Tauri ---

# Build the Tauri NSIS desktop installer (full pipeline: frontend -> Rust -> NSIS)
build-native:
	$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
	Set-Location '{{justfile_directory()}}\native'
	npx @tauri-apps/cli build --bundles nsis

# Bootstrap: install dev deps + pre-commit hook
