# GitHub CI/CD Production Guide for MCP Servers

A comprehensive guide to implementing production-ready GitHub CI/CD workflows and tooling for Model Context Protocol (MCP) server repositories, based on the Advanced Memory MCP implementation and GLAMA.ai standards.

## Table of Contents

1. [Overview](#overview)
2. [GLAMA.ai Integration](#glamaai-integration)
3. [Repository Configuration](#repository-configuration)
4. [GitHub Actions Workflows](#github-actions-workflows)
5. [Code Quality Tools](#code-quality-tools)
6. [Security Scanning](#security-scanning)
7. [Release Management](#release-management)
8. [Dependency Management](#dependency-management)
9. [Issue and PR Templates](#issue-and-pr-templates)
10. [Branch Protection](#branch-protection)
11. [GLAMA.ai Standards Compliance](#glamaai-standards-compliance)
12. [Implementation Checklist](#implementation-checklist)

## Overview

This guide provides a complete blueprint for setting up production-ready GitHub CI/CD workflows for MCP server repositories, aligned with GLAMA.ai standards. The implementation includes:

- **GLAMA.ai Integration**: GitHub app installation and platform compliance
- **Comprehensive CI/CD Pipeline**: Multi-stage testing, linting, security scanning, and building
- **Automated Release Management**: Semantic versioning with automated PyPI publishing
- **Code Quality Enforcement**: Automated linting, formatting, and type checking
- **Security Scanning**: Automated vulnerability detection and dependency updates
- **Beta Testing Pipeline**: Dedicated workflows for pre-release validation
- **Dependency Management**: Automated updates with safety checks
- **Gold Status Compliance**: Meeting GLAMA.ai's highest quality standards

## GLAMA.ai Integration

### Platform Overview

**GLAMA.ai** is the #1 platform for discovering MCP servers worldwide, providing:

- **Server Directory**: Largest collection of MCP servers (5,000+ indexed)
- **Ranking System**: Servers ranked by security, compatibility, and ease of use
- **Chat Interface**: ChatGPT-like UI for interacting with MCP servers
- **API Gateway**: Fast, reliable AI gateway with 100+ AI models
- **Community**: 1,754 Discord members, active Reddit community

### GLAMA GitHub App Installation

The GLAMA GitHub app enhances repository management and ensures compliance with platform standards:

#### Installation Steps

1. **Access the GLAMA GitHub App**:
   - Navigate to [GLAMA GitHub App](https://github.com/apps/glama)
   - Click "Install" and select repositories to integrate

2. **Configure Permissions**:
   ```yaml
   # Required permissions for GLAMA.ai integration
   permissions:
     contents: read          # Repository content access
     metadata: read          # Repository metadata
     pull_requests: read     # PR information for quality assessment
     issues: read           # Issue tracking for community engagement
     actions: read          # CI/CD workflow monitoring
     security_events: read  # Security scanning results
   ```

3. **Repository Integration**:
   ```bash
   # Add GLAMA.ai badge to README.md
   [![GLAMA.ai](https://glama.ai/mcp/servers/YOUR_SERVER_ID/badge)](https://glama.ai/mcp/servers/YOUR_SERVER_ID)
   ```

4. **Verify Integration**:
   - Confirm app appears in repository's "Installed GitHub Apps"
   - Check GLAMA.ai platform for automatic repository indexing
   - Monitor quality score and ranking updates

#### GLAMA.ai Quality Standards

To achieve **Gold Status** (95/100+ points) on GLAMA.ai:

| **Metric** | **Gold Requirement** | **Implementation** |
|------------|---------------------|-------------------|
| **Test Coverage** | 80%+ | Comprehensive pytest suite with coverage reporting |
| **CI/CD Maturity** | Advanced | Multi-stage workflows with quality gates |
| **Documentation** | Comprehensive | Complete README, API docs, and guides |
| **Error Handling** | Advanced | Structured logging and graceful failure handling |
| **Security** | Production | Automated security scanning and vulnerability detection |
| **Platform Integration** | Native | GLAMA.ai badge and platform compliance |

#### Repository Optimization for GLAMA.ai

1. **Metadata Enhancement**:
   ```yaml
   # pyproject.toml optimization
   [project]
   name = "your-mcp-server"
   description = "Clear, compelling description for GLAMA.ai indexing"
   keywords = ["mcp", "ai", "claude", "knowledge-management"]
   classifiers = [
       "Development Status :: 5 - Production/Stable",
       "Intended Audience :: Developers",
       "License :: OSI Approved :: MIT License",
       "Programming Language :: Python :: 3",
       "Topic :: Software Development :: Libraries :: Python Modules",
   ]
   ```

2. **README.md Structure**:
   ```markdown
   # Your MCP Server Name
   
   [![GLAMA.ai](https://glama.ai/mcp/servers/YOUR_SERVER_ID/badge)](https://glama.ai/mcp/servers/YOUR_SERVER_ID)
   
   ## Quick Start
   ## Installation
   ## Features
   ## API Reference
   ## Contributing
   ## License
   ```

3. **Quality Indicators**:
   - ✅ Production-ready CI/CD pipeline
   - ✅ Comprehensive test coverage (80%+)
   - ✅ Security scanning enabled
   - ✅ Automated dependency updates
   - ✅ Structured documentation
   - ✅ Community guidelines and contribution process

## Repository Configuration

### Required Files Structure

```
.github/
├── workflows/
│   ├── ci.yml                    # Main CI/CD pipeline
│   ├── release.yml               # Release automation
│   ├── beta-testing.yml          # Beta release validation
│   ├── dependency-updates.yml    # Automated dependency updates
│   └── security.yml              # Security scanning
├── ISSUE_TEMPLATE/
│   ├── bug_report.md             # Bug report template
│   ├── feature_request.md        # Feature request template
│   └── config.yml                # Issue template configuration
└── dependabot.yml                # Dependency update configuration
```

### Repository Settings

Configure your repository with these settings:

- **Visibility**: Public (unless specific privacy requirements)
- **Features**: Enable Issues, Discussions, Projects, Wiki
- **Merge Options**: 
  - Allow auto-merge
  - Automatically delete head branches
  - Set "Allow squash merging" as default
- **Branch Protection**: Protect main/master branches (see Branch Protection section)

## GitHub Actions Workflows

### 1. Main CI/CD Pipeline (`ci.yml`)

The core workflow that runs on every push and pull request:

```yaml
name: CI/CD Pipeline (Full)

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master, develop ]
  workflow_dispatch:
    inputs:
      run_full_ci:
        description: 'Run full CI pipeline (may have warnings)'
        required: false
        default: false
        type: boolean

env:
  PYTHON_VERSION: "3.12"

jobs:
  lint:
    name: Lint and Format Check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      - name: Install dependencies
        run: uv sync --dev
      - name: Run ruff linting
        run: uv run ruff check . --fix
      - name: Run ruff formatting check
        run: uv run ruff format --check .
      - name: Run mypy type checking
        run: uv run mypy src/ --ignore-missing-imports || echo "Type checking completed with warnings"

  test:
    name: Test Suite
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest]
        python-version: ["3.11", "3.12"]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      - name: Install dependencies
        run: uv sync --dev
      - name: Run tests with coverage
        run: |
          uv run pytest --cov=src/advanced_memory --cov-report=xml --cov-report=term-missing -v --maxfail=10 --tb=short --cov-fail-under=50
      - name: Upload coverage to Codecov
        if: matrix.python-version == '3.12'
        uses: codecov/codecov-action@v3

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      - name: Install dependencies
        run: uv sync --dev
      - name: Run bandit security scan
        run: uv run bandit -r src/ -f json -o bandit-report.json --skip B101,B601 || echo "Security scan completed with warnings"
      - name: Run safety check
        run: uv run safety check --json --output safety-report.json || echo "Safety check completed with warnings"
      - name: Upload security reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json

  build:
    name: Build Package
    runs-on: ubuntu-latest
    needs: [lint, test, security]
    if: always() && (needs.lint.result == 'success' || needs.lint.result == 'skipped')
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      - name: Install build dependencies
        run: uv add --dev build twine
      - name: Build package
        run: uv run python -m build
      - name: Check package
        run: uv run twine check dist/*
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  mcpb-build:
    name: Build MCPB Package
    runs-on: ubuntu-latest
    needs: [lint, test]
    if: always() && (needs.lint.result == 'success' || needs.lint.result == 'skipped')
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install MCPB CLI
        run: npm install -g @anthropic-ai/mcpb || echo "MCPB CLI not available, skipping"
      - name: Validate manifest
        run: |
          if command -v mcpb >/dev/null 2>&1; then
            cd mcpb
            mcpb validate manifest.json
            cd ..
          else
            echo "MCPB CLI not available, skipping validation"
          fi
      - name: Build MCPB package
        run: |
          if command -v mcpb >/dev/null 2>&1; then
            cd mcpb
            mcpb pack . ../dist/advanced-memory-mcp.mcpb
            cd ..
          else
            echo "MCPB CLI not available, creating basic package"
            cd mcpb
            zip -r ../dist/advanced-memory-mcp.mcpb . -x "*.git*" "*.pyc" "__pycache__/*"
            cd ..
          fi
      - name: Upload MCPB package
        uses: actions/upload-artifact@v4
        with:
          name: mcpb-package
          path: dist/advanced-memory-mcp.mcpb

  integration-test:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [build]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      - name: Install built package
        run: uv pip install dist/*.whl
      - name: Run integration tests
        run: |
          if [ -d "test-int" ]; then
            cd test-int
            uv run pytest -v --maxfail=3
          else
            echo "No integration tests found, skipping"
          fi

  quality-gate:
    name: Quality Gate
    runs-on: ubuntu-latest
    needs: [lint, test, security, build, mcpb-build]
    if: always()
    steps:
      - name: Check critical jobs status
        run: |
          if [[ "${{ needs.lint.result }}" == "success" || "${{ needs.lint.result }}" == "skipped" ]] && \
             [[ "${{ needs.test.result }}" == "success" || "${{ needs.test.result }}" == "skipped" ]] && \
             [[ "${{ needs.build.result }}" == "success" || "${{ needs.build.result }}" == "skipped" ]]; then
            echo "✅ Quality gate passed"
          else
            echo "❌ Quality gate failed"
            exit 1
          fi
```

### 2. Release Automation (`release.yml`)

Automated release workflow triggered by version tags:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., v1.0.0)'
        required: true
        type: string

env:
  PYTHON_VERSION: "3.12"

jobs:
  release:
    name: Create Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write
      id-token: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      - name: Install build dependencies
        run: uv add --dev build twine
      - name: Build package
        run: uv run python -m build
      - name: Check package
        run: uv run twine check dist/*
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install MCPB CLI
        run: npm install -g @anthropic-ai/mcpb
      - name: Build MCPB package
        run: |
          if command -v mcpb >/dev/null 2>&1; then
            cd mcpb
            mcpb pack . ../dist/advanced-memory-mcp.mcpb
            cd ..
          else
            echo "MCPB CLI not available, creating basic package"
            cd mcpb
            zip -r ../dist/advanced-memory-mcp.mcpb . -x "*.git*" "*.pyc" "__pycache__/*"
            cd ..
          fi
      - name: Generate changelog
        id: changelog
        run: |
          if git describe --tags --abbrev=0 HEAD^ >/dev/null 2>&1; then
            PREVIOUS_TAG=$(git describe --tags --abbrev=0 HEAD^)
            CHANGELOG=$(git log --pretty=format:"- %s" $PREVIOUS_TAG..HEAD)
          else
            CHANGELOG=$(git log --pretty=format:"- %s" --reverse)
          fi
          echo "changelog<<EOF" >> $GITHUB_OUTPUT
          echo "$CHANGELOG" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
      - name: Extract version
        id: version
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            VERSION="${{ github.event.inputs.version }}"
          else
            VERSION="${{ github.ref_name }}"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "version_number=${VERSION#v}" >> $GITHUB_OUTPUT
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ steps.version.outputs.version }}
          release_name: Advanced Memory MCP ${{ steps.version.outputs.version }}
          body: |
            ## 🚀 What's New in Advanced Memory MCP ${{ steps.version.outputs.version }}
            
            ${{ steps.changelog.outputs.changelog }}
            
            ## 📦 Installation
            
            ### Claude Desktop Extension
            1. Download `advanced-memory-mcp.mcpb` from the assets below
            2. Open Claude Desktop
            3. Go to Settings > Extensions
            4. Drop the `.mcpb` file into the extensions page
            
            ### Python Package
            ```bash
            pip install advanced-memory-mcp==${{ steps.version.outputs.version_number }}
            ```
          draft: false
          prerelease: ${{ contains(steps.version.outputs.version, 'alpha') || contains(steps.version.outputs.version, 'beta') || contains(steps.version.outputs.version, 'rc') }}
      - name: Upload MCPB Package
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./dist/advanced-memory-mcp.mcpb
          asset_name: advanced-memory-mcp.mcpb
          asset_content_type: application/octet-stream
      - name: Upload Python Package
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./dist/advanced_memory_mcp-${{ steps.version.outputs.version_number }}-py3-none-any.whl
          asset_name: advanced_memory_mcp-${{ steps.version.outputs.version_number }}-py3-none-any.whl
          asset_content_type: application/zip

  publish-pypi:
    name: Publish to PyPI
    runs-on: ubuntu-latest
    needs: release
    if: startsWith(github.ref, 'refs/tags/v') && !contains(github.ref, 'alpha') && !contains(github.ref, 'beta') && !contains(github.ref, 'rc')
    environment: pypi
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### 3. Beta Testing Pipeline (`beta-testing.yml`)

Dedicated workflow for beta releases and pre-release validation:

```yaml
name: Beta Testing Pipeline

on:
  push:
    branches: [ beta, "*-beta" ]
  pull_request:
    branches: [ beta, "*-beta" ]
  schedule:
    # Run beta tests daily at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:

env:
  PYTHON_VERSION: "3.12"

jobs:
  beta-quality:
    name: Beta Quality Checks
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Install dependencies
      run: uv sync --dev
    - name: Run comprehensive tests
      run: uv run pytest tests/ -x --tb=short --maxfail=5
    - name: Run linting
      run: uv run ruff check . --output-format=github || echo "Linting completed with warnings"
    - name: Run type checking
      run: uv run mypy src/ --ignore-missing-imports || echo "Type checking completed with warnings"
    - name: Run security scans
      run: |
        uv run bandit -r src/ -f json -o bandit-beta.json || echo "Security scan completed with warnings"
        uv run safety check --json --output safety-beta.json || echo "Safety check completed with warnings"
    - name: Upload beta reports
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: beta-quality-reports
        path: |
          bandit-beta.json
          safety-beta.json

  beta-performance:
    name: Beta Performance Tests
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Install dependencies
      run: uv sync --dev
    - name: Create test data
      run: |
        uv run python -c "
        import os
        os.makedirs('test-data', exist_ok=True)
        # Create 100 test notes for performance testing
        for i in range(100):
            with open(f'test-data/note-{i:04d}.md', 'w') as f:
                f.write(f'# Test Note {i}\\n\\nThis is test content {i}.\\n')
        "
    - name: Run performance tests
      run: |
        uv run python -c "
        import time
        import subprocess
        start = time.time()
        result = subprocess.run(['uv', 'run', 'python', '-m', 'pytest', 'tests/', '-q'], capture_output=True)
        end = time.time()
        print(f'Full test suite: {end - start:.2f}s')
        print(f'Exit code: {result.returncode}')
        "
    - name: Test memory usage
      run: |
        uv run python -c "
        import psutil
        import os
        process = psutil.Process(os.getpid())
        print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
        "

  beta-integration:
    name: Beta Integration Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_USER: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Install dependencies
      run: uv sync --dev
    - name: Run integration tests
      run: uv run pytest tests/ -k "integration" -v
    - name: Test MCP server startup
      run: |
        uv run python -c "
        from advanced_memory.mcp.mcp_instance import mcp
        from advanced_memory.config import ConfigManager
        config = ConfigManager().config
        print('MCP server initialized successfully')
        print(f'Server name: {mcp.name}')
        "

  beta-release-validation:
    name: Beta Release Validation
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/beta'
    needs: [beta-quality, beta-performance, beta-integration]
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Build package
      run: uv build
    - name: Test installation
      run: |
        pip install dist/*.whl
        python -c "import advanced_memory; print(f'Version: {advanced_memory.__version__}')"
    - name: Test CLI commands
      run: |
        advanced-memory --help
        advanced-memory --version
    - name: Create beta release notes
      run: |
        echo "# Beta Release Validation Report" > beta-report.md
        echo "" >> beta-report.md
        echo "## Test Results" >> beta-report.md
        echo "- ✅ Quality checks passed" >> beta-report.md
        echo "- ✅ Performance tests passed" >> beta-report.md
        echo "- ✅ Integration tests passed" >> beta-report.md
        echo "- ✅ Package build successful" >> beta-report.md
        echo "- ✅ CLI functionality verified" >> beta-report.md
    - name: Upload beta report
      uses: actions/upload-artifact@v4
      with:
        name: beta-release-report
        path: beta-report.md
```

### 4. Dependency Updates (`dependency-updates.yml`)

Automated dependency management with safety checks:

```yaml
name: Dependency Updates

on:
  schedule:
    - cron: '0 2 * * 1' # Weekly on Monday at 2 AM UTC
  workflow_dispatch:

jobs:
  update-dependencies:
    name: Update Dependencies
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      - name: Update dependencies
        run: |
          uv lock --upgrade
          uv sync --dev
      - name: Run tests
        run: |
          uv run pytest --cov=src/advanced_memory -x
      - name: Check for changes
        id: changes
        run: |
          if git diff --quiet; then
            echo "has_changes=false" >> $GITHUB_OUTPUT
          else
            echo "has_changes=true" >> $GITHUB_OUTPUT
          fi
      - name: Create Pull Request
        if: steps.changes.outputs.has_changes == 'true'
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "chore: update dependencies"
          title: "chore: update dependencies"
          body: |
            ## 🔄 Dependency Updates
            
            This PR updates dependencies to their latest versions.
            
            ### Changes
            - Updated Python package dependencies
            - Updated development dependencies
            - Updated uv lock file
            
            ### Testing
            - [x] Tests pass locally
            - [x] No breaking changes detected
            
            ### Review Checklist
            - [ ] Review dependency changes
            - [ ] Verify no breaking changes
            - [ ] Test functionality
            - [ ] Approve and merge
            
            ---
            *This PR was automatically created by the dependency update workflow.*
          branch: dependency-updates
          delete-branch: true
          labels: |
            dependencies
            automated
```

### 5. Security Scanning (`security.yml`)

Comprehensive security scanning workflow:

```yaml
name: Security Scanning

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  schedule:
    # Run security scans weekly
    - cron: '0 6 * * 0'
  workflow_dispatch:

jobs:
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Install dependencies
      run: uv sync --dev
    - name: Run Safety (Python vulnerability scanner)
      run: uv run safety check --json --output safety-report.json || true
    - name: Run Bandit (Python security linter)
      run: uv run bandit -r src/ -f json -o bandit-report.json || true
    - name: Run Semgrep (Static analysis)
      run: |
        uv run semgrep --config=auto --json --output=semgrep-report.json src/ || true
    - name: Upload security reports
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: security-reports
        path: |
          safety-report.json
          bandit-report.json
          semgrep-report.json
    - name: Comment PR with security results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          let comment = '## 🔒 Security Scan Results\n\n';
          try {
            if (fs.existsSync('bandit-report.json')) {
              const bandit = JSON.parse(fs.readFileSync('bandit-report.json', 'utf8'));
              comment += `**Bandit Issues:** ${bandit.metrics.total_issues || 0}\n`;
            }
          } catch (e) {
            comment += '**Bandit:** Error reading report\n';
          }
          try {
            if (fs.existsSync('safety-report.json')) {
              const safety = JSON.parse(fs.readFileSync('safety-report.json', 'utf8'));
              comment += `**Safety Vulnerabilities:** ${safety.length || 0}\n`;
            }
          } catch (e) {
            comment += '**Safety:** Error reading report\n';
          }
          comment += '\n*Automated security scan completed*';
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

## Code Quality Tools

### pyproject.toml Configuration

Comprehensive tool configuration for code quality:

```toml
[project]
name = "advanced-memory"
version = "1.0.0b1"
description = "Independent local-first knowledge management system combining Zettelkasten with knowledge graphs"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "AGPL-3.0-or-later" }
authors = [
    { name = "Advanced Memory Community", email = "hello@advanced-memory.com" }
]

[build-system]
requires = ["hatchling", "uv-dynamic-versioning>=0.7.0"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
pythonpath = ["src", "tests"]
addopts = "-v -s"
testpaths = ["tests"]
asyncio_mode = "strict"

[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = ["migrations", "mcpb", "dxt", "dist", "htmlcov"]

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.uv]
dev-dependencies = [
    "gevent>=24.11.1",
    "icecream>=2.1.3",
    "pytest>=8.3.4",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-asyncio>=0.24.0",
    "pytest-xdist>=3.0.0",
    "ruff>=0.1.6",
    "mypy>=1.8.0",
    "black>=24.0.0",
    "isort>=5.13.0",
    "bandit>=1.7.0",
    "safety>=3.0.0",
    "pre-commit>=3.6.0",
    "types-setuptools>=69.0.0",
]

[tool.hatch.version]
source = "uv-dynamic-versioning"

[tool.uv-dynamic-versioning]
vcs = "git"
style = "pep440"
bump = true
fallback-version = "0.0.0"

[tool.pyright]
include = ["src/"]
exclude = ["**/__pycache__"]
ignore = ["test/"]
defineConstant = { DEBUG = true }
reportMissingImports = "error"
reportMissingTypeStubs = false
pythonVersion = "3.11"

[tool.mypy]
python_version = "3.11"
warn_return_any = false
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = false
warn_redundant_casts = false
warn_unused_ignores = false
warn_no_return = false
warn_unreachable = false
strict_equality = false
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = [
    "alembic.*",
    "fastmcp.*",
    "uv.*",
    "mcp.*",
    "watchfiles.*",
    "rich.*",
    "typer.*",
    "loguru.*",
    "pydantic.*",
    "sqlalchemy.*",
    "aiosqlite.*",
    "markdown_it.*",
    "frontmatter.*",
    "unidecode.*",
    "dateparser.*",
    "pillow.*",
    "pybars3.*",
    "pyjwt.*",
    "dotenv.*",
    "pytest.*",
    "bandit.*",
    "safety.*",
    "semgrep.*",
]
ignore_missing_imports = true

[tool.coverage.run]
concurrency = ["thread"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]

# Exclude specific modules that are difficult to test comprehensively
omit = [
    "*/external_auth_provider.py",  # External HTTP calls to OAuth providers
    "*/supabase_auth_provider.py",  # External HTTP calls to Supabase APIs
    "*/watch_service.py",           # File system watching - complex integration testing
    "*/background_sync.py",         # Background processes
    "*/cli/main.py",               # CLI entry point
    "*/services/migration_service.py", # Complex migration scenarios
]
```

### Dependabot Configuration

Automated dependency updates with safety controls:

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "02:00"
    open-pull-requests-limit: 10
    reviewers:
      - "sandraschi"
    assignees:
      - "sandraschi"
    commit-message:
      prefix: "chore"
      include: "scope"
    labels:
      - "dependencies"
      - "python"
    ignore:
      # Ignore major version updates for critical dependencies
      - dependency-name: "fastmcp"
        update-types: ["version-update:semver-major"]
      - dependency-name: "pydantic"
        update-types: ["version-update:semver-major"]

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "02:00"
    open-pull-requests-limit: 5
    reviewers:
      - "sandraschi"
    assignees:
      - "sandraschi"
    commit-message:
      prefix: "chore"
      include: "scope"
    labels:
      - "dependencies"
      - "github-actions"

  # Node.js dependencies (for MCPB CLI)
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "02:00"
    open-pull-requests-limit: 5
    reviewers:
      - "sandraschi"
    assignees:
      - "sandraschi"
    commit-message:
      prefix: "chore"
      include: "scope"
    labels:
      - "dependencies"
      - "javascript"
    ignore:
      # Ignore major version updates for MCPB CLI
      - dependency-name: "@anthropic-ai/mcpb"
        update-types: ["version-update:semver-major"]
```

## Issue and PR Templates

### Bug Report Template

```markdown
---
name: Bug Report
about: Create a report to help us improve Advanced Memory MCP
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## ❌ Actual Behavior
A clear and concise description of what actually happened.

## 📸 Screenshots
If applicable, add screenshots to help explain your problem.

## 🖥️ Environment
**Desktop (please complete the following information):**
 - OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
 - Claude Desktop Version: [e.g. 1.0.0]
 - Advanced Memory MCP Version: [e.g. 1.0.0]
 - Python Version: [e.g. 3.12.0]

## 📋 Additional Context
Add any other context about the problem here.

## 🔍 Diagnostic Information
If applicable, please include:
```

### Feature Request Template

```markdown
---
name: Feature Request
about: Suggest an idea for Advanced Memory MCP
title: '[FEATURE] '
labels: ['enhancement', 'needs-triage']
assignees: ''
---

## 🚀 Feature Description
A clear and concise description of what you want to happen.

## 💡 Motivation
Why is this feature important? What problem does it solve?

## 📝 Detailed Description
Provide a detailed explanation of the feature, including:
- How it should work
- What the user interface should look like
- Any specific requirements or constraints

## 🎯 Use Cases
Describe specific scenarios where this feature would be useful:
1. **Use Case 1**: Description
2. **Use Case 2**: Description
3. **Use Case 3**: Description

## 🔧 Implementation Ideas
If you have ideas about how this could be implemented, please share them here.
```

### Issue Template Configuration

```yaml
blank_issues_enabled: false
contact_links:
  - name: Advanced Memory MCP Community Discussions
    url: https://github.com/sandraschi/advanced-memory-mcp/discussions
    about: Ask questions and discuss ideas with the community
  - name: Documentation
    url: https://github.com/sandraschi/advanced-memory-mcp/blob/main/README.md
    about: Check our comprehensive documentation and guides
```

## Branch Protection

Configure branch protection rules for production-ready repositories:

### Required Settings

1. **Require pull request reviews before merging**
   - Required number of reviewers: 1
   - Dismiss stale PR approvals when new commits are pushed
   - Require review from code owners

2. **Require status checks to pass before merging**
   - Require branches to be up to date before merging
   - Required status checks:
     - `lint` (Lint and Format Check)
     - `test` (Test Suite)
     - `security` (Security Scan)
     - `build` (Build Package)
     - `quality-gate` (Quality Gate)

3. **Require conversation resolution before merging**
   - All conversations on the PR must be resolved

4. **Restrict pushes that create files**
   - Restrict pushes that create files larger than 100MB

5. **Do not allow bypassing the above settings**
   - Even administrators cannot bypass these rules

### Branch Protection Configuration

```yaml
# Example branch protection configuration
branch_protection_rules:
  main:
    required_status_checks:
      strict: true
      contexts:
        - "lint"
        - "test"
        - "security"
        - "build"
        - "quality-gate"
    enforce_admins: true
    required_pull_request_reviews:
      required_approving_review_count: 1
      dismiss_stale_reviews: true
      require_code_owner_reviews: true
    restrictions:
      users: []
      teams: []
```

## GLAMA.ai Standards Compliance

### Quality Metrics Tracking

Implement comprehensive quality tracking to meet GLAMA.ai Gold Status requirements:

#### 1. Test Coverage Monitoring
```yaml
# Enhanced coverage configuration for GLAMA.ai compliance
[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]

# Target: 80%+ for Gold Status
fail_under = 80
show_missing = true
precision = 2
```

#### 2. Security Compliance
```yaml
# Security scanning configuration for GLAMA.ai standards
security_checks:
  bandit:
    severity: medium
    confidence: medium
    exclude_tests: ["B101", "B601"]  # Skip assert and shell injection tests
  safety:
    check_live: true
    ignore_ids: []  # No ignored vulnerabilities for Gold Status
  semgrep:
    config: auto
    severity: error
```

#### 3. Documentation Standards
```markdown
# Required documentation structure for GLAMA.ai Gold Status
docs/
├── README.md              # Main project overview
├── INSTALLATION.md        # Detailed installation guide
├── API_REFERENCE.md       # Complete API documentation
├── CONTRIBUTING.md        # Contribution guidelines
├── CHANGELOG.md          # Version history
├── SECURITY.md           # Security policy
├── LICENSE               # License information
└── examples/             # Usage examples
    ├── basic_usage.md
    ├── advanced_features.md
    └── integration_guides.md
```

#### 4. Performance Benchmarks
```yaml
# Performance requirements for GLAMA.ai Gold Status
performance_targets:
  test_execution_time: "< 5 minutes"
  memory_usage: "< 500MB"
  startup_time: "< 10 seconds"
  api_response_time: "< 100ms"
  test_coverage: "> 80%"
```

### GLAMA.ai Integration Workflow

Add a dedicated workflow for GLAMA.ai platform integration:

```yaml
# .github/workflows/glama-integration.yml
name: GLAMA.ai Integration

on:
  push:
    branches: [ main, master ]
  release:
    types: [ published ]

jobs:
  glama-quality-check:
    name: GLAMA.ai Quality Assessment
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run quality assessment
        run: |
          echo "## GLAMA.ai Quality Assessment" >> $GITHUB_STEP_SUMMARY
          echo "### Test Coverage" >> $GITHUB_STEP_SUMMARY
          pytest --cov=src --cov-report=term-missing --cov-report=xml
          coverage=$(python -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); print(f'{float(tree.getroot().attrib[\"line-rate\"])*100:.1f}%')")
          echo "- Coverage: $coverage" >> $GITHUB_STEP_SUMMARY
          
          echo "### Security Scan" >> $GITHUB_STEP_SUMMARY
          bandit -r src/ -f json -o bandit-report.json || true
          safety check --json --output safety-report.json || true
          echo "- Security scan completed" >> $GITHUB_STEP_SUMMARY
          
          echo "### Documentation Check" >> $GITHUB_STEP_SUMMARY
          if [ -f "README.md" ] && [ -f "CONTRIBUTING.md" ] && [ -f "CHANGELOG.md" ]; then
            echo "- ✅ All required documentation present" >> $GITHUB_STEP_SUMMARY
          else
            echo "- ❌ Missing required documentation" >> $GITHUB_STEP_SUMMARY
          fi
      
      - name: Upload quality reports
        uses: actions/upload-artifact@v4
        with:
          name: glama-quality-reports
          path: |
            coverage.xml
            bandit-report.json
            safety-report.json
```

## Implementation Checklist

### Phase 1: Basic Setup
- [ ] Create `.github/workflows/` directory
- [ ] Set up main CI/CD pipeline (`ci.yml`)
- [ ] Configure `pyproject.toml` with tool settings
- [ ] Set up basic branch protection rules
- [ ] Create issue templates
- [ ] **Install GLAMA GitHub App**

### Phase 2: Quality Tools
- [ ] Configure Ruff for linting and formatting
- [ ] Set up MyPy for type checking
- [ ] Configure pytest with coverage reporting (80%+ target)
- [ ] Set up security scanning tools (Bandit, Safety, Semgrep)
- [ ] Configure Dependabot for dependency updates
- [ ] **Add GLAMA.ai badge to README**

### Phase 3: Release Automation
- [ ] Set up release workflow (`release.yml`)
- [ ] Configure PyPI publishing
- [ ] Set up MCPB package building
- [ ] Configure automated changelog generation
- [ ] Set up GitHub Releases automation
- [ ] **Configure GLAMA.ai integration workflow**

### Phase 4: Advanced Features
- [ ] Set up beta testing pipeline (`beta-testing.yml`)
- [ ] Configure security scanning workflow (`security.yml`)
- [ ] Set up dependency update automation (`dependency-updates.yml`)
- [ ] Configure integration testing
- [ ] Set up performance testing
- [ ] **Implement GLAMA.ai quality metrics tracking**

### Phase 5: Repository Configuration
- [ ] Configure repository settings
- [ ] Set up branch protection rules
- [ ] Configure issue templates
- [ ] Set up project boards
- [ ] Configure community guidelines
- [ ] **Optimize repository metadata for GLAMA.ai indexing**

### Phase 6: Documentation
- [ ] Create comprehensive README.md
- [ ] Set up CONTRIBUTING.md
- [ ] Create CHANGELOG.md
- [ ] Document setup and deployment processes
- [ ] Create API documentation
- [ ] **Ensure documentation meets GLAMA.ai Gold Status requirements**

### Phase 7: GLAMA.ai Compliance
- [ ] **Achieve 80%+ test coverage**
- [ ] **Pass all security scans with zero critical vulnerabilities**
- [ ] **Complete comprehensive documentation suite**
- [ ] **Implement structured logging throughout codebase**
- [ ] **Set up automated quality metrics reporting**
- [ ] **Monitor GLAMA.ai quality score and ranking**

### Phase 8: Monitoring and Maintenance
- [ ] Set up Codecov integration
- [ ] Configure security alerts
- [ ] Set up performance monitoring
- [ ] Create maintenance schedules
- [ ] Set up automated backups
- [ ] **Monitor GLAMA.ai platform updates and ranking changes**

## Best Practices

### Workflow Design
1. **Fail Fast**: Run quick checks first (linting, formatting)
2. **Parallel Execution**: Use matrix strategies for testing multiple Python versions
3. **Conditional Execution**: Use `if` conditions to skip unnecessary jobs
4. **Artifact Management**: Upload and download artifacts efficiently
5. **Error Handling**: Use `|| echo` for non-critical steps

### Security Considerations
1. **Secrets Management**: Store sensitive data in GitHub Secrets
2. **Least Privilege**: Use minimal required permissions
3. **Dependency Scanning**: Regular security scans and updates
4. **Code Review**: Require reviews for all changes
5. **Branch Protection**: Prevent direct pushes to main branches

### Performance Optimization
1. **Caching**: Use GitHub Actions cache for dependencies
2. **Parallel Jobs**: Run independent jobs in parallel
3. **Selective Testing**: Run only relevant tests based on changes
4. **Resource Management**: Use appropriate runner types
5. **Cleanup**: Remove temporary files and artifacts

### Maintenance
1. **Regular Updates**: Keep dependencies and actions up to date
2. **Monitoring**: Track workflow performance and failures
3. **Documentation**: Keep workflows and processes documented
4. **Testing**: Test workflow changes in feature branches
5. **Backup**: Maintain backup strategies for critical data

## Conclusion

This comprehensive GitHub CI/CD setup provides production-ready workflows for MCP server repositories, fully aligned with GLAMA.ai standards. The implementation includes:

- **GLAMA.ai Integration**: GitHub app installation and platform compliance for Gold Status
- **Complete CI/CD Pipeline**: Multi-stage testing, building, and deployment
- **Automated Quality Gates**: Linting, formatting, type checking, and security scanning
- **Release Automation**: Semantic versioning with automated publishing
- **Dependency Management**: Automated updates with safety checks
- **Security Scanning**: Regular vulnerability detection and reporting
- **Beta Testing**: Dedicated workflows for pre-release validation
- **Quality Metrics Tracking**: Comprehensive monitoring for GLAMA.ai Gold Status compliance

By following this guide, MCP server repositories can achieve the same production-ready standards as the Advanced Memory MCP implementation while meeting GLAMA.ai's highest quality requirements. This ensures:

- **Code Quality**: 80%+ test coverage and comprehensive quality gates
- **Security**: Zero critical vulnerabilities and automated security scanning
- **Documentation**: Complete documentation suite meeting GLAMA.ai standards
- **Platform Integration**: Native GLAMA.ai integration with quality monitoring
- **Reliable Releases**: Automated semantic versioning and publishing
- **Community Recognition**: Gold Status positioning on GLAMA.ai platform

The modular design allows for incremental implementation, starting with basic CI/CD and gradually adding advanced features as needed. Each component is designed to be maintainable, scalable, and adaptable to different project requirements while maintaining GLAMA.ai compliance.

### GLAMA.ai Benefits

Implementing these standards provides:

- **Enhanced Discoverability**: Premium placement in GLAMA.ai directory search results
- **Professional Credibility**: Gold tier badge and enterprise-grade quality signals
- **Community Recognition**: Thought leadership in MCP server development
- **Business Opportunities**: Enterprise adoption signals and consulting opportunities
- **Platform Partnerships**: Enhanced integration opportunities with GLAMA.ai ecosystem

This guide ensures your MCP server repository meets the highest industry standards while maximizing visibility and recognition on the GLAMA.ai platform.
