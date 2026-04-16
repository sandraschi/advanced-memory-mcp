set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# â”€â”€ Dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Display the SOTA Industrial Dashboard
default:
    @$lines = Get-Content '{{justfile()}}'; \
    Write-Host ' [SOTA] Industrial Operations Dashboard v1.7.0' -ForegroundColor White -BackgroundColor Cyan; \
    Write-Host '' ; \
    $currentCategory = ''; \
    foreach ($line in $lines) { \
        if ($line -match '^# â”€â”€ ([^â”€]+) â”€') { \
            $currentCategory = $matches[1].Trim(); \
            Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
            Write-Host ('  ' + ('â”€' * 45)) -ForegroundColor Gray; \
        } elseif ($line -match '^# ([^â”€].+)') { \
            $desc = $matches[1].Trim(); \
            $idx = [array]::IndexOf($lines, $line); \
            if ($idx -lt $lines.Count - 1) { \
                $nextLine = $lines[$idx + 1]; \
                if ($nextLine -match '^([a-z0-9-]+):') { \
                    $recipe = $matches[1]; \
                    $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                    Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
                    Write-Host "$pad$desc" -ForegroundColor Gray; \
                } \
            } \
        } \
    } \
    Write-Host "`n  [System State: PROD/INDUSTRIALIZED]" -ForegroundColor DarkGray; \
    Write-Host ''

# â”€â”€ Quality â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Execute repo-wide quality checks (Ruff + Biome)
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .
    Set-Location '{{justfile_directory()}}/webapp/frontend'
    npx biome check src

# Execute repo-wide auto-fixes and formatting (Ruff + Biome)
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}/webapp/frontend'
    npx biome check --write src

# â”€â”€ Hardening â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# Advanced Memory - Modern Command Runner

stats:
    uv run python tools/repo_stats.py

# Install dependencies
install:
    pip install -e ".[dev]"
    uv sync
    @echo ""
    @echo "ðŸ’¡ Remember to activate the virtual environment by running: source .venv/bin/activate"

# Run unit tests in parallel
test-unit:
    uv run pytest -p pytest_mock -v -n auto

# Run integration tests in parallel
test-int:
    uv run pytest -p pytest_mock -v --no-cov -n auto test-int

# Run all tests
test: test-unit test-int

# Lint and fix code
# Type check code
type-check:
    uv run pyright

# Clean build artifacts and cache files
clean:
    @Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    @Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    @If (Test-Path "installer/build") { Remove-Item -Recurse -Force "installer/build" }
    @If (Test-Path "installer/dist") { Remove-Item -Recurse -Force "installer/dist" }
    @If (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    @If (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    @Get-ChildItem -Filter "rw.*.dmg" | Remove-Item -Force -ErrorAction SilentlyContinue

# Format code with ruff and Biome
format:
    uv run ruff format .
    Set-Location '{{justfile_directory()}}/webapp/frontend'
    npx biome check --write src

# Run MCP inspector tool
run-inspector:
    npx @modelcontextprotocol/inspector

# Build MCPB bundle (requires Node.js + npx). Output: dist/advanced-memory-mcp.mcpb
pack:
    Set-Location '{{justfile_directory()}}'
    if (-not (Test-Path "dist")) { New-Item -ItemType Directory -Path "dist" | Out-Null }
    npx --yes @anthropic-ai/mcpb@latest validate manifest.json
    npx --yes @anthropic-ai/mcpb@latest pack . "dist/advanced-memory-mcp.mcpb"

# Build macOS installer
installer-mac:
    cd installer && chmod +x make_icons.sh && ./make_icons.sh
    cd installer && uv run python setup.py bdist_mac

# Build Windows installer
installer-win:
    cd installer && uv run python setup.py bdist_win32

# Update all dependencies to latest versions
update-deps:
    uv sync --upgrade

# Run all code quality checks and tests
check: lint format type-check test

# Generate Alembic migration with descriptive message
migration message:
    cd src/basic_memory/alembic && alembic revision --autogenerate -m "{{message}}"

# Create a stable release (e.g., just release v1.6.2)
release version:
    #!/usr/bin/env bash
    set -euo pipefail

    # Validate version format
    if [[ ! "{{version}}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "âŒ Invalid version format. Use: v1.6.2"
        exit 1
    fi

    # Extract version number without 'v' prefix
    VERSION_NUM=$(echo "{{version}}" | sed 's/^v//')

    echo "ðŸš€ Creating SOTA stable release {{version}}"

    # Pre-flight checks
    echo "ðŸ“‹ Running pre-flight checks..."
    if [[ -n $(git status --porcelain) ]]; then
        echo "âŒ Uncommitted changes found. Please commit or stash them first."
        exit 1
    fi

    if [[ $(git branch --show-current) != "main" ]]; then
        echo "âŒ Not on main branch. Switch to main first."
        exit 1
    fi

    # Check if tag already exists
    if git tag -l "{{version}}" | grep -q "{{version}}"; then
        echo "âŒ Tag {{version}} already exists"
        exit 1
    fi

    # Run quality checks
    echo "ðŸ” Running quality checks..."
    just check

    # Update version in __init__.py (if it exists)
    if [ -f src/advanced_memory/__init__.py ]; then
        echo "ðŸ“ Updating version in src/advanced_memory/__init__.py..."
        sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION_NUM\"/" src/advanced_memory/__init__.py
        rm -f src/advanced_memory/__init__.py.bak
        git add src/advanced_memory/__init__.py
        git commit -m "chore: update version to $VERSION_NUM for {{version}} release"
    fi

    # Create and push tag
    echo "ðŸ·ï¸  Creating tag {{version}}..."
    git tag "{{version}}"

    echo "ðŸ“¤ Pushing to GitHub..."
    git push origin main
    git push origin "{{version}}"

    echo "âœ… Release {{version}} created successfully!"
    echo "ðŸ“¦ Industrial Launch initiated (OIDC Handshake)."
    echo "ðŸ”— Monitor at: https://github.com/sandraschi/advanced-memory-mcp/actions"

# Create a beta release (e.g., just beta v0.13.2b1)
beta version:
    #!/usr/bin/env bash
    set -euo pipefail

    # Validate version format (allow beta/rc suffixes)
    if [[ ! "{{version}}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(b[0-9]+|rc[0-9]+)$ ]]; then
        echo "âŒ Invalid beta version format. Use: v0.13.2b1 or v0.13.2rc1"
        exit 1
    fi

    # Extract version number without 'v' prefix
    VERSION_NUM=$(echo "{{version}}" | sed 's/^v//')

    echo "ðŸ§ª Creating beta release {{version}}"

    # Pre-flight checks
    echo "ðŸ“‹ Running pre-flight checks..."
    if [[ -n $(git status --porcelain) ]]; then
        echo "âŒ Uncommitted changes found. Please commit or stash them first."
        exit 1
    fi

    if [[ $(git branch --show-current) != "main" ]]; then
        echo "âŒ Not on main branch. Switch to main first."
        exit 1
    fi

    # Check if tag already exists
    if git tag -l "{{version}}" | grep -q "{{version}}"; then
        echo "âŒ Tag {{version}} already exists"
        exit 1
    fi

    # Run quality checks
    echo "ðŸ” Running quality checks..."
    just check

    # Update version in __init__.py
    echo "ðŸ“ Updating version in __init__.py..."
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION_NUM\"/" src/basic_memory/__init__.py
    rm -f src/basic_memory/__init__.py.bak

    # Commit version update
    git add src/basic_memory/__init__.py
    git commit -m "chore: update version to $VERSION_NUM for {{version}} beta release"

    # Create and push tag
    echo "ðŸ·ï¸  Creating tag {{version}}..."
    git tag "{{version}}"

    echo "ðŸ“¤ Pushing to GitHub..."
    git push origin main
    git push origin "{{version}}"

    echo "âœ… Beta release {{version}} created successfully!"
    echo "ðŸ“¦ GitHub Actions will build and publish to PyPI as pre-release"
    echo "ðŸ”— Monitor at: https://github.com/advanced-memory/advanced-memory/actions"
    echo "ðŸ“¥ Install with: uv tool install advanced-memory --pre"

# List all available recipes
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CI/CD AUTOMATION - Never break GitHub Actions again!
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# Pre-push validation (run before every push!)
pre-push:
    @echo "ðŸ” Running pre-push validation..."
    @pwsh ./scripts/pre-push-check.ps1

# Quick validation (faster, skips coverage)
quick-check:
    @echo "âš¡ Quick validation..."
    @pwsh ./scripts/pre-push-check.ps1 -Quick

# Safe push with validation + monitoring
safe-push message:
    @echo "ðŸš€ Safe push with validation..."
    @pwsh ./scripts/safe-push.ps1 -Message "{{message}}"

# Monitor CI after manual push
monitor:
    @echo "ðŸ” Monitoring CI workflows..."
    @pwsh ./scripts/monitor-ci.ps1 -AutoFix -Continuous

# Check CI success metrics
ci-stats:
    @echo "ðŸ“Š CI success metrics..."
    @pwsh ./scripts/ci-metrics.ps1

# Detailed CI metrics with history
ci-stats-detailed:
    @echo "ðŸ“Š Detailed CI metrics..."
    @pwsh ./scripts/ci-metrics.ps1 -Detailed

# Install pre-commit hooks (one-time setup)
setup-hooks:
    @echo "ðŸ”§ Installing pre-commit hooks..."
    uv run pre-commit install
    @echo "âœ… Pre-commit hooks installed"
    @echo "ðŸ’¡ Hooks will run automatically before every commit"

# Run pre-commit on all files
pre-commit-all:
    @echo "ðŸ” Running pre-commit on all files..."
    uv run pre-commit run --all-files

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# REPOSITORY BACKUP - Automated backups excluding caches & venvs
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# Create repository backup (excludes .venv, caches, ~30-40 MB)
backup:
    @echo "ðŸ“¦ Creating repository backup..."
    @pwsh ./scripts/backup-repo.ps1

# Create backup including dist/ folder
backup-with-dist:
    @echo "ðŸ“¦ Creating repository backup (with dist/)..."
    @pwsh ./scripts/backup-repo.ps1 -IncludeDist

# Create backup to specific location
backup-to path:
    @echo "ðŸ“¦ Creating repository backup to {{path}}..."
    @pwsh ./scripts/backup-repo.ps1 -OutputPath "{{path}}"

# Create backup with WinRAR instead of 7-Zip
backup-winrar:
    @echo "ðŸ“¦ Creating repository backup (WinRAR)..."
    @pwsh ./scripts/backup-repo.ps1 -UseWinRAR
