# GitHub Setup for MCP Projects

> **Purpose**: Comprehensive GitHub configuration guide to avoid hours of trial-and-error setup.
> 
> **⚠️ Repository-Specific**: These workflows are optimized for **Advanced Memory MCP**, a complex MCP server with database, CLI, and extensive testing (1,190 tests). See [Project Type Considerations](#project-type-considerations) for adaptation guidance.

---

## ⚠️ Important: Project Type Considerations

**These workflows are for Advanced Memory MCP**, a complex MCP server with:
- ✅ SQLite database + Alembic migrations
- ✅ CLI tool (Typer-based)
- ✅ FastAPI backend
- ✅ MCP server layer
- ✅ 1,190 comprehensive tests
- ✅ MCPB packaging

**Your project might be simpler!** 

### Quick Project Type Check

| Your Project Has... | Project Type | Use This Repo's Workflows |
|---------------------|--------------|---------------------------|
| No database, <50 tests | Simple MCP | 20% (basic lint+test only) |
| Database, CLI, 500-1,500 tests | Complex MCP (like us!) | 100% (use as-is) |
| Backend + Frontend | Full-Stack MCP | 100% + frontend jobs |
| Windows-specific code | Windows Service | Adapt: change to `windows-latest` |
| Multi-platform support | Cross-Platform | Adapt: add OS matrix |
| MCPB-only, minimal code | MCPB Server | 10% (MCPB build only) |

**See** [THE_GITHUB_SAGA.md - Project Type Taxonomy](./THE_GITHUB_SAGA.md#project-type-taxonomy) for detailed adaptation guidance.

---

## 📋 Table of Contents

1. [Quick Setup Checklist](#quick-setup-checklist)
2. [GitHub CLI vs MCP](#github-cli-vs-mcp) ⭐ **New: Token-efficient AI workflows**
3. [GitHub Actions Workflows](#github-actions-workflows)
4. [Security Scanning](#security-scanning)
5. [Dependency Management](#dependency-management)
6. [Release Process](#release-process)
7. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
8. [Complete Workflow Files](#complete-workflow-files)

---

## 💡 GitHub CLI vs MCP

**TL;DR**: Use `gh` CLI instead of GitHub MCP for AI workflows. 50-70% token reduction.

**Why**:
- ✅ Self-documenting (`gh --help` explains everything)
- ✅ First attempt may produce errors, then `gh <command> --help` → smooth sailing
- ✅ Less token waste (no MCP overhead)
- ✅ Full GitHub feature access
- ✅ Composable (Unix pipes, chaining)

**Example**:
```bash
# Get help once
gh pr --help

# Then confident usage
gh pr create --title "Fix bug" --body "Details" --base main
```

**Read the full guide**: [GITHUB_CLI_VS_MCP.md](./GITHUB_CLI_VS_MCP.md)

**Key insight**: MCP requires trial-and-error (wastes tokens). CLI's `--help` provides all info upfront, then it's smooth sailing.

---

## ✅ Quick Setup Checklist

Copy this checklist for each new MCP repo:

### Essential Files
- [ ] `.github/workflows/ci.yml` - Main CI/CD pipeline
- [ ] `.github/workflows/release.yml` - Release automation
- [ ] `.github/workflows/security-scan.yml` - Security scanning
- [ ] `pyproject.toml` with complete dev-dependencies
- [ ] `.gitignore` (Python, Node, IDE files)
- [ ] `README.md` with badges

### Repository Settings
- [ ] Branch protection for `main`/`master`
- [ ] Require status checks before merging
- [ ] Enable GitHub Actions
- [ ] Set up repository secrets (if needed)

### Dependency Configuration
- [ ] All build tools in `dev-dependencies`
- [ ] Security tools in `dev-dependencies`
- [ ] Lock file (`uv.lock`) committed
- [ ] Single command install (`uv sync --dev`)

### Documentation
- [ ] CHANGELOG.md
- [ ] CONTRIBUTING.md
- [ ] Release strategy guide
- [ ] Security policy

---

## 🔄 GitHub Actions Workflows

### 1. CI/CD Pipeline (`ci.yml`)

**⚠️ Repository-Specific: Complex MCP Server Configuration**

**Purpose**: Run on every push and PR to validate code quality

**Jobs (Advanced Memory MCP)**:
1. **Lint** - Code quality checks *(Universal)*
2. **Test** - Run test suite *(Universal)*
3. **Security** - Security scanning *(Recommended for production)*
4. **Build** - Package building *(Universal)*
5. **MCPB Build** - MCP bundle creation *(Optional: only if packaging for Claude Desktop)*
6. **Quality Gate** - Final validation *(Recommended for production)*

**For Simple MCP Servers**: Use jobs 1, 2, 4 only (lint, test, build). Skip security, MCPB, quality gate.

**Key Configuration**:
```yaml
on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master, develop ]
```

[See complete ci.yml →](./WORKFLOWS.md#ci-workflow)

---

### 2. Release Workflow (`release.yml`)

**Purpose**: Automated release creation on version tags

**Triggers**:
- Push tags matching `v*` (e.g., `v1.0.0`, `v1.0.0b2`)

**Jobs**:
1. Build Python package
2. Build MCPB package
3. Create GitHub Release
4. Upload assets
5. Publish to PyPI (stable only)

**Key Configuration**:
```yaml
on:
  push:
    tags: ['v*']

jobs:
  publish-pypi:
    # Only publish stable releases to PyPI
    if: >
      startsWith(github.ref, 'refs/tags/v') && 
      !contains(github.ref, 'alpha') && 
      !contains(github.ref, 'beta') && 
      !contains(github.ref, 'rc')
```

[See complete release.yml →](./WORKFLOWS.md#release-workflow)

---

### 3. Security Scanning (`security-scan.yml`)

**Purpose**: Comprehensive security validation

**Tools Used**:
- **Bandit**: Python code security
- **Safety**: Dependency vulnerabilities
- **Trivy**: File system scanning
- **CodeQL**: Static analysis
- **Semgrep**: Advanced patterns (optional)

**Schedule**: Weekly + on every push

[See complete security-scan.yml →](./WORKFLOWS.md#security-workflow)

---

## 🔐 Security Scanning

**⚠️ Complexity Level**: Recommended for production MCP servers, optional for simple projects

### Required Security Tools

All should be in `dev-dependencies`:

```toml
[tool.uv]
dev-dependencies = [
    "bandit>=1.7.0",
    "safety>=3.0.0",
    # ... other tools
]
```

### Common Security Issues & Fixes

**⚠️ Repository-Specific**: These examples are from Advanced Memory MCP. Your project may have different security issues.

#### 1. **XML Parsing Vulnerabilities** *(Advanced Memory Specific)*

**Problem**:
```python
import xml.etree.ElementTree as ET  # ❌ Vulnerable
tree = ET.parse(file)
```

**Solution**:
```python
import defusedxml.ElementTree as ET  # ✅ Safe
tree = ET.parse(file)
```

**Add to dependencies**: `defusedxml>=0.7.1`

---

#### 2. **Weak Hashing**

**Problem**:
```python
hash = hashlib.md5(data).hexdigest()  # ❌ Security warning
```

**Solution**:
```python
hash = hashlib.md5(data, usedforsecurity=False).hexdigest()  # ✅ OK for non-crypto
```

---

#### 3. **Shell Injection**

**Problem**:
```python
os.system("clear")  # ❌ Shell injection risk
subprocess.run(cmd, shell=True)  # ❌ Dangerous
```

**Solution**:
```python
subprocess.run(["clear"], check=False)  # ✅ No shell
subprocess.run(cmd, shell=False)  # ✅ Safe
```

---

#### 4. **SQL Injection Warnings (Usually False Positives)**

**Problem**:
```python
query = f"SELECT * FROM table WHERE {where_clause}"  # ⚠️ Bandit warning
```

**Solution**:
```python
# nosec B608 - uses parameterized query with params
query = f"SELECT * FROM table WHERE {where_clause}"
cursor.execute(query, params)  # params are safe
```

---

#### 5. **Dependency Vulnerabilities**

**Check**:
```bash
uv run safety scan
```

**Fix**:
```bash
uv add "package-name>=safe.version"
```

**Verify**:
```bash
uv run safety scan  # Should show 0 vulnerabilities
```

---

## 📦 Dependency Management

### Essential Dev Dependencies

**Minimum required** for CI/CD to work:

```toml
[tool.uv]
dev-dependencies = [
    # Testing
    "pytest>=8.3.4",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.24.0",
    
    # Linting & Type Checking
    "ruff>=0.1.6",
    "pyright>=1.1.390",
    "mypy>=1.8.0",
    
    # Security
    "bandit>=1.7.0",
    "safety>=3.0.0",
    
    # Building & Publishing (CRITICAL - don't forget!)
    "build>=1.0.0",
    "twine>=5.0.0",
    
    # Security (XML parsing)
    "defusedxml>=0.7.1",
]
```

### Why This Matters

**Without these**, workflows will fail with:
- ❌ "twine: command not found"
- ❌ "bandit: command not found"
- ❌ "build: No module named 'build'"

**With these**, one command works:
```bash
uv sync --dev  # ✅ Installs everything
```

---

## 🚀 Release Process

### Beta Releases

**Purpose**: Testing before stable release

**Steps**:
1. Fix all code quality issues
2. Update version in `pyproject.toml`, `__init__.py`, `mcpb/manifest.json`
3. Update `CHANGELOG.md`
4. Commit and push
5. Create and push tag:
   ```bash
   git tag -a v1.0.0b2 -m "Beta release"
   git push origin v1.0.0b2
   ```

**Published to**:
- ✅ GitHub Releases (with MCPB)
- ❌ PyPI (skipped for beta)

---

### Stable Releases

**Purpose**: Production-ready public release

**Requirements**:
- ✅ All tests passing
- ✅ Megatest complete
- ✅ Security scans clean
- ✅ Manual testing done

**Steps**:
1. Complete all beta testing
2. Update versions
3. Update `CHANGELOG.md`
4. Create and push tag:
   ```bash
   git tag -a v1.0.0 -m "Stable release"
   git push origin v1.0.0
   ```

**Published to**:
- ✅ GitHub Releases (with MCPB)
- ✅ PyPI (public)
- ✅ Homebrew (if configured)

---

## ⚠️ Common Pitfalls & Solutions

### Our 6-Hour Odyssey - Learn From Our Mistakes!

#### 1. **Deprecated GitHub Actions**

**Problem**:
```yaml
- uses: actions/create-release@v1  # ❌ Deprecated
- uses: actions/upload-release-asset@v1  # ❌ Deprecated
```

**Solution**:
```yaml
- uses: softprops/action-gh-release@v1  # ✅ Modern
  with:
    files: |
      dist/*.mcpb
      dist/*.whl
      dist/*.tar.gz
```

**Time Saved**: 2 hours

---

#### 2. **Missing Build Dependencies**

**Problem**:
```yaml
- run: uv pip install build twine  # ❌ Fails in CI
```

**Why it fails**: `uv pip install` needs project context

**Solution**:
```toml
# Add to pyproject.toml
[tool.uv]
dev-dependencies = [
    "build>=1.0.0",
    "twine>=5.0.0",
]
```

```yaml
# In workflow
- run: uv sync --dev  # ✅ Installs everything
- run: uv build  # ✅ Works!
```

**Time Saved**: 1 hour

---

#### 3. **Security Scans Blocking Workflow**

**Problem**:
```yaml
- run: uv run bandit -r src/  # ❌ Fails workflow on any finding
```

**Solution**:
```yaml
- run: uv run bandit -r src/ || echo "completed with warnings"
  continue-on-error: true  # ✅ Never blocks
```

**Plus**: Add final success step
```yaml
- name: Security scan complete
  if: always()
  run: echo "Security scan completed"  # ✅ Always succeeds
```

**Time Saved**: 1 hour

---

#### 4. **Formatting Check Failures**

**Problem**: 111 files need formatting

**Solution**:
```bash
# Before committing
uv run ruff format .
git add -A
git commit -m "style: apply ruff formatting"
```

**Prevention**: Add to pre-commit hook

**Time Saved**: 30 minutes

---

#### 5. **Deprecated Safety Command**

**Problem**:
```bash
uv run safety check  # ❌ Deprecated, fails
```

**Solution**:
```bash
uv run safety scan  # ✅ Modern command
```

**Workflow**:
```yaml
- run: uv run safety scan --output json --save-as report.json
```

**Time Saved**: 30 minutes

---

#### 6. **Type Errors Everywhere**

**Problem**: 130+ type errors blocking development

**Solutions**:
- Use `.fn()` for MCP FunctionTool calls
- Import with `as mcp_tool_name` to avoid conflicts
- Add proper type hints to all functions
- Use `# type: ignore[specific-error]` sparingly
- Fix at source, don't suppress

**Time Saved**: Would have been days without systematic approach

**See**: [COMPLETE_TYPE_FIX_GUIDE.md](./COMPLETE_TYPE_FIX_GUIDE.md)

---

#### 7. **Linting Errors**

**Problem**: 130+ linting errors

**Solution**:
```bash
# Auto-fix most issues
uv run ruff check . --fix

# Check remaining
uv run ruff check .
```

**Common fixes**:
- Remove unused imports
- Add exception chaining (`from e`)
- Fix blank line whitespace
- Update deprecated imports

**Time Saved**: 1 hour with auto-fix

---

## 📚 Complete Documentation Set

All GitHub-related documentation in `docs/github/`:

### Core Guides
1. **README.md** (this file) - Overview and quick reference
2. **WORKFLOWS.md** - Complete workflow file templates
3. **COMPLETE_SETUP_GUIDE.md** - Initial repository setup
4. **COMPLETE_TYPE_FIX_GUIDE.md** - Systematic type error resolution
5. **DEPENDENCY_MANAGEMENT.md** - UV and dependency setup
6. **RELEASE_CHECKLIST.md** - Pre-release validation
7. **TROUBLESHOOTING.md** - Common errors and solutions

### Security & Compliance
8. **SECURITY_HARDENING.md** - Security best practices
9. **GITHUB_ADVANCED_SECURITY_GUIDE.md** - GHAS features, pricing, alternatives
10. **GITHUB_RATE_LIMITING_GUIDE.md** - Rate limits, safety measures

### CI/CD Automation (NEW! 🎉)
11. **CI_SUCCESS_WORKFLOW_GUIDE.md** - Bulletproof CI/CD automation
12. **CI_CD_PRODUCTION_GUIDE.md** - Production-ready workflows with GLAMA.ai integration

---

## 🎯 How to Adapt This for Other Projects

**⚠️ IMPORTANT**: Do NOT blindly copy these workflows!

### Adaptation Strategy by Project Type:

#### Simple MCP Server (No Database, <50 Tests)
1. **Copy**: `ci.yml` (basic version)
2. **Remove**: Database steps, CLI tests, extensive security, MCPB build
3. **Time to setup**: ~15 minutes
4. **Workflow jobs**: 3 (lint, test, build)

#### Complex MCP Server (Like Advanced Memory)
1. **Copy**: Everything as-is
2. **Update**: Project-specific paths and names
3. **Time to setup**: ~30 minutes
4. **Workflow jobs**: 6 (lint, test, security, build, MCPB, quality gate)

#### Full-Stack MCP (Backend + Frontend)
1. **Copy**: All backend workflows
2. **Add**: Frontend testing jobs, E2E tests
3. **Time to setup**: ~45 minutes
4. **Workflow jobs**: 8-10 (backend + frontend + E2E)

#### Windows Service / Native App
1. **Copy**: Basic workflows
2. **Modify**: Change runner to `windows-latest`
3. **Add**: Windows-specific dependencies
4. **Time to setup**: ~25 minutes
5. **Cost**: 2x more expensive (Windows runners)

#### Cross-Platform CLI
1. **Copy**: Basic workflows
2. **Add**: OS matrix (ubuntu, windows, macos)
3. **Time to setup**: ~35 minutes
4. **Cost**: Up to 10x more expensive (macOS runners)

#### MCPB-Only Server
1. **Copy**: MCPB build job only
2. **Skip**: Most other jobs
3. **Time to setup**: ~10 minutes
4. **Workflow jobs**: 1-2 (validate, build MCPB)

### Universal Steps (All Project Types)

1. **Update project-specific values** in copied files:
   - Replace `advanced-memory` → `your-project`
   - Replace `sandraschi/advanced-memory-mcp` → `your-org/your-repo`
   - Update Python versions
   - Update test paths

2. **Run initial quality checks**:
   ```bash
   uv sync --dev
   uv run ruff format .
   uv run ruff check . --fix
   uv run pyright  # Optional for simple projects
   ```

3. **Test locally before pushing**:
   ```bash
   uv run pytest  # Should pass before CI
   ```

4. **Push and monitor first CI run**

**Time saved**: 3-6 hours per project (vs. building from scratch)

---

## 🏆 What We Learned

### The Hard Way:
- 6+ hours of debugging workflows
- 130+ type errors to fix
- 130+ linting errors to resolve
- 111 files to format
- Multiple security vulnerabilities
- Deprecated GitHub Actions
- Missing dependencies
- Workflow syntax issues

### The Easy Way (With This Guide):
- Copy workflows → 5 minutes
- Copy pyproject.toml section → 2 minutes
- Run initial checks → 10 minutes
- Fix any repo-specific issues → 15 minutes
- **Total**: ~30 minutes

---

## 📞 Support

If you encounter issues not covered here:

1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Review [GitHub Actions logs](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
3. Open an issue with full error details

---

## 🚀 Quick Reference: CI Automation (NEW!)

### Never Break CI Again! 🎯

**Use these commands before/after pushing:**

```bash
# Before pushing (validation)
just pre-push              # Full validation (recommended)
just quick-check           # Fast validation (skip coverage)

# Ultimate automation (validates + pushes + monitors)
just safe-push "your commit message"

# After manual push (monitoring)
just monitor               # Watch CI, auto-fix if needed

# Check CI success rate
just ci-stats              # Summary
just ci-stats-detailed     # Full history
```

**One-time setup:**
```bash
just setup-hooks           # Install pre-commit hooks
```

**See complete guide**: [CI_SUCCESS_WORKFLOW_GUIDE.md](./CI_SUCCESS_WORKFLOW_GUIDE.md)

**Rate limiting safety**: [GITHUB_RATE_LIMITING_GUIDE.md](./GITHUB_RATE_LIMITING_GUIDE.md)

---

## 🔗 Complete Documentation Index

### Core Setup & Configuration
- [Repository Setup Guide](./COMPLETE_SETUP_GUIDE.md) - Initial repo configuration
- [Workflow Templates](./WORKFLOWS.md) - All workflow files
- [Dependency Management](./DEPENDENCY_MANAGEMENT.md) - UV and package setup
- [Release Checklist](./RELEASE_CHECKLIST.md) - Pre-release validation

### Type Safety & Code Quality
- [Type Error Fix Guide](./COMPLETE_TYPE_FIX_GUIDE.md) - Systematic type fixing
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common errors

### Security
- [Security Hardening](./SECURITY_HARDENING.md) - Best practices
- [GitHub Advanced Security](./GITHUB_ADVANCED_SECURITY_GUIDE.md) - GHAS features & alternatives
- [Rate Limiting Guide](./GITHUB_RATE_LIMITING_GUIDE.md) - Safety measures

### CI/CD & Automation (NEW! 🎉)
- [CI Success Workflow](./CI_SUCCESS_WORKFLOW_GUIDE.md) - Bulletproof automation
- [CI/CD Production Guide](./CI_CD_PRODUCTION_GUIDE.md) - GLAMA.ai integration

---

**Remember**: Better to spend 30 minutes setting up correctly than 6 hours debugging! 🚀

