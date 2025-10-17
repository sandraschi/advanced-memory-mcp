# Advanced Memory - Modern Command Runner

# Install dependencies
install:
    pip install -e ".[dev]"
    uv sync
    @echo ""
    @echo "💡 Remember to activate the virtual environment by running: source .venv/bin/activate"

# Run unit tests in parallel
test-unit:
    uv run pytest -p pytest_mock -v -n auto

# Run integration tests in parallel
test-int:
    uv run pytest -p pytest_mock -v --no-cov -n auto test-int

# Run all tests
test: test-unit test-int

# Lint and fix code
lint:
    uv run ruff check . --fix

# Type check code
type-check:
    uv run pyright

# Clean build artifacts and cache files
clean:
    find . -type f -name '*.pyc' -delete
    find . -type d -name '__pycache__' -exec rm -r {} +
    rm -rf installer/build/ installer/dist/ dist/
    rm -f rw.*.dmg .coverage.*

# Format code with ruff
format:
    uv run ruff format .

# Run MCP inspector tool
run-inspector:
    npx @modelcontextprotocol/inspector

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

# Create a stable release (e.g., just release v0.13.2)
release version:
    #!/usr/bin/env bash
    set -euo pipefail
    
    # Validate version format
    if [[ ! "{{version}}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "❌ Invalid version format. Use: v0.13.2"
        exit 1
    fi
    
    # Extract version number without 'v' prefix
    VERSION_NUM=$(echo "{{version}}" | sed 's/^v//')
    
    echo "🚀 Creating stable release {{version}}"
    
    # Pre-flight checks
    echo "📋 Running pre-flight checks..."
    if [[ -n $(git status --porcelain) ]]; then
        echo "❌ Uncommitted changes found. Please commit or stash them first."
        exit 1
    fi
    
    if [[ $(git branch --show-current) != "main" ]]; then
        echo "❌ Not on main branch. Switch to main first."
        exit 1
    fi
    
    # Check if tag already exists
    if git tag -l "{{version}}" | grep -q "{{version}}"; then
        echo "❌ Tag {{version}} already exists"
        exit 1
    fi
    
    # Run quality checks
    echo "🔍 Running quality checks..."
    just check
    
    # Update version in __init__.py
    echo "📝 Updating version in __init__.py..."
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION_NUM\"/" src/basic_memory/__init__.py
    rm -f src/basic_memory/__init__.py.bak
    
    # Commit version update
    git add src/basic_memory/__init__.py
    git commit -m "chore: update version to $VERSION_NUM for {{version}} release"
    
    # Create and push tag
    echo "🏷️  Creating tag {{version}}..."
    git tag "{{version}}"
    
    echo "📤 Pushing to GitHub..."
    git push origin main
    git push origin "{{version}}"
    
    echo "✅ Release {{version}} created successfully!"
    echo "📦 GitHub Actions will build and publish to PyPI"
    echo "🔗 Monitor at: https://github.com/advanced-memory/advanced-memory/actions"

# Create a beta release (e.g., just beta v0.13.2b1)
beta version:
    #!/usr/bin/env bash
    set -euo pipefail
    
    # Validate version format (allow beta/rc suffixes)
    if [[ ! "{{version}}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(b[0-9]+|rc[0-9]+)$ ]]; then
        echo "❌ Invalid beta version format. Use: v0.13.2b1 or v0.13.2rc1"
        exit 1
    fi
    
    # Extract version number without 'v' prefix
    VERSION_NUM=$(echo "{{version}}" | sed 's/^v//')
    
    echo "🧪 Creating beta release {{version}}"
    
    # Pre-flight checks
    echo "📋 Running pre-flight checks..."
    if [[ -n $(git status --porcelain) ]]; then
        echo "❌ Uncommitted changes found. Please commit or stash them first."
        exit 1
    fi
    
    if [[ $(git branch --show-current) != "main" ]]; then
        echo "❌ Not on main branch. Switch to main first."
        exit 1
    fi
    
    # Check if tag already exists
    if git tag -l "{{version}}" | grep -q "{{version}}"; then
        echo "❌ Tag {{version}} already exists"
        exit 1
    fi
    
    # Run quality checks
    echo "🔍 Running quality checks..."
    just check
    
    # Update version in __init__.py
    echo "📝 Updating version in __init__.py..."
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION_NUM\"/" src/basic_memory/__init__.py
    rm -f src/basic_memory/__init__.py.bak
    
    # Commit version update
    git add src/basic_memory/__init__.py
    git commit -m "chore: update version to $VERSION_NUM for {{version}} beta release"
    
    # Create and push tag
    echo "🏷️  Creating tag {{version}}..."
    git tag "{{version}}"
    
    echo "📤 Pushing to GitHub..."
    git push origin main
    git push origin "{{version}}"
    
    echo "✅ Beta release {{version}} created successfully!"
    echo "📦 GitHub Actions will build and publish to PyPI as pre-release"
    echo "🔗 Monitor at: https://github.com/advanced-memory/advanced-memory/actions"
    echo "📥 Install with: uv tool install advanced-memory --pre"

# List all available recipes
default:
    @just --list

# ═══════════════════════════════════════════════════════════════
# CI/CD AUTOMATION - Never break GitHub Actions again!
# ═══════════════════════════════════════════════════════════════

# Pre-push validation (run before every push!)
pre-push:
    @echo "🔍 Running pre-push validation..."
    @pwsh ./scripts/pre-push-check.ps1

# Quick validation (faster, skips coverage)
quick-check:
    @echo "⚡ Quick validation..."
    @pwsh ./scripts/pre-push-check.ps1 -Quick

# Safe push with validation + monitoring
safe-push message:
    @echo "🚀 Safe push with validation..."
    @pwsh ./scripts/safe-push.ps1 -Message "{{message}}"

# Monitor CI after manual push
monitor:
    @echo "🔍 Monitoring CI workflows..."
    @pwsh ./scripts/monitor-ci.ps1 -AutoFix -Continuous

# Check CI success metrics
ci-stats:
    @echo "📊 CI success metrics..."
    @pwsh ./scripts/ci-metrics.ps1

# Detailed CI metrics with history
ci-stats-detailed:
    @echo "📊 Detailed CI metrics..."
    @pwsh ./scripts/ci-metrics.ps1 -Detailed

# Install pre-commit hooks (one-time setup)
setup-hooks:
    @echo "🔧 Installing pre-commit hooks..."
    uv run pre-commit install
    @echo "✅ Pre-commit hooks installed"
    @echo "💡 Hooks will run automatically before every commit"

# Run pre-commit on all files
pre-commit-all:
    @echo "🔍 Running pre-commit on all files..."
    uv run pre-commit run --all-files
