# 🪝 Pre-Commit Hooks - Complete Guide

**Comprehensive guide to pre-commit hooks: what they are, how they work, and which ones to use**

**Date**: October 17, 2025
**For**: Advanced Memory MCP + all Python projects
**Status**: Production configuration included

---

## 🎯 What Are Pre-Commit Hooks?

### The Simple Explanation

**Pre-commit hooks** are **automated checks that run BEFORE you commit code**.

**Think of them as**:
- A bouncer at the door of your Git commits
- Quality control that happens automatically
- Your personal code reviewer before commit
- A safety net that catches mistakes early

**The workflow**:
```
You type: git commit -m "fix: update code"
           ↓
Pre-commit hooks run automatically
           ↓
Checks: format, lint, syntax, security, etc.
           ↓
✅ All pass? → Commit proceeds
❌ Any fail? → Commit blocked, must fix
```

---

### The Technical Explanation

**Pre-commit hooks** are scripts that Git runs before creating a commit. They:

1. **Live in**: `.git/hooks/pre-commit` (created by pre-commit framework)
2. **Run automatically**: Every time you run `git commit`
3. **Can modify files**: Fix formatting, remove whitespace, etc.
4. **Can block commits**: If checks fail, commit is rejected
5. **Are local**: Each developer has their own hooks

**Framework**: We use the `pre-commit` Python package (https://pre-commit.com)
- Manages hooks from multiple sources
- Configures hooks in `.pre-commit-config.yaml`
- Updates hooks automatically
- Runs hooks in isolated environments

---

## 📋 What Hooks Do We Currently Have?

### Our Current Configuration (`.pre-commit-config.yaml`)

#### 1. **Ruff** - Fast Python Linter & Formatter

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.7.4
  hooks:
    - id: ruff
      args: [--fix, --exit-non-zero-on-fix]
    - id: ruff-format
```

**What it does**:
- `ruff`: Checks code quality (unused imports, syntax errors, style issues)
  - **Auto-fixes** most issues automatically
  - Blocks commit if can't fix automatically
- `ruff-format`: Formats code (indentation, line length, spacing)
  - **Auto-formats** all Python files
  - Ensures consistent code style

**Example**:
```python
# Before commit (you wrote):
import os
import sys   # ← Unused import
def   foo(  ):  # ← Extra whitespace
  return   "hello"   # ← Indentation issue

# After pre-commit hook runs automatically:
import os  # ← Removed unused import
def foo():  # ← Fixed whitespace
    return "hello"  # ← Fixed indentation
```

**Benefits**:
- ✅ Never commit unformatted code
- ✅ Never commit unused imports
- ✅ Consistent style across team
- ✅ CI format check always passes

---

#### 2. **Standard Pre-Commit Hooks** - File Quality

```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.6.0
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: check-yaml
    - id: check-json
    - id: check-toml
    - id: check-added-large-files
    - id: check-merge-conflict
    - id: detect-private-key
    - id: mixed-line-ending
```

**What each does**:

| Hook | What It Does | Example |
|------|--------------|---------|
| `trailing-whitespace` | Removes spaces at end of lines | `hello   ` → `hello` |
| `end-of-file-fixer` | Ensures files end with newline | Adds `\n` at end |
| `check-yaml` | Validates YAML syntax | Catches invalid `.github/workflows/*.yml` |
| `check-json` | Validates JSON syntax | Catches invalid `manifest.json` |
| `check-toml` | Validates TOML syntax | Catches invalid `pyproject.toml` |
| `check-added-large-files` | Blocks files >1MB | Prevents accidentally committing binaries |
| `check-merge-conflict` | Detects merge markers | Finds `<<<<<<< HEAD` in files |
| `detect-private-key` | Finds SSH/GPG keys | Prevents committing `id_rsa` |
| `mixed-line-ending` | Fixes CRLF/LF issues | Ensures consistent line endings |

**Benefits**:
- ✅ Never commit broken YAML/JSON/TOML
- ✅ Never commit large binaries accidentally
- ✅ Never commit merge conflict markers
- ✅ Never commit private keys
- ✅ Consistent file formatting

---

#### 3. **Detect-Secrets** - Secret Detection

```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
      exclude: ^(uv\.lock|\.secrets\.baseline)$
```

**What it does**:
- Scans all files for secrets (API keys, passwords, tokens)
- Compares against baseline (`.secrets.baseline`)
- Blocks commit if new secrets detected
- Supports 50+ secret types

**Detects**:
- AWS keys: `AKIA...`
- API tokens: `sk-...`, `ghp_...`
- Private keys: `-----BEGIN RSA PRIVATE KEY-----`
- Passwords in URLs: `https://user:password@example.com`
- And 50+ more patterns

**Example**:
```python
# This would be BLOCKED:
API_KEY = "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"  # 🚨 OpenAI API key detected!

# Commit fails with:
# ❌ Secret detected in config.py
# Type: OpenAI API Key
# Line: 42
```

**Benefits**:
- ✅ Never commit API keys
- ✅ Never commit passwords
- ✅ Never commit tokens
- ✅ Security by default

---

## 🎯 Which Hooks Should We Add?

### Recommended Additions

#### 1. **MyPy** - Type Checking (Recommended!)

```yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.13.0
  hooks:
    - id: mypy
      args: [--ignore-missing-imports, --explicit-package-bases]
      additional_dependencies:
        - types-setuptools
        - sqlalchemy[mypy]
        - types-requests
      pass_filenames: false
```

**Why add it**:
- ✅ Catches type errors before commit
- ✅ Prevents CI type check failures
- ✅ Better IDE integration
- ⚠️  Can be slow (5-10 seconds per commit)

**Recommendation**: **Add it** if you want stricter type safety

---

#### 2. **Pytest** - Run Tests on Changed Files

```yaml
- repo: local
  hooks:
    - id: pytest-check
      name: pytest-check
      entry: uv run pytest
      language: system
      pass_filenames: false
      always_run: false
      args: [--maxfail=1, -x, --tb=short, -q]
```

**Why add it**:
- ✅ Catches test failures before commit
- ✅ Fast feedback loop
- ⚠️  Can be VERY slow if many tests
- ⚠️  May not work in all environments

**Recommendation**: **Don't add** - too slow for every commit. Use `just pre-push` instead.

---

#### 3. **Bandit** - Security Linting

```yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.10
  hooks:
    - id: bandit
      args: [-r, src/, -ll]  # Low severity only
      exclude: ^tests/
```

**Why add it**:
- ✅ Catches security issues early
- ✅ SQL injection, shell injection, etc.
- ⚠️  Many false positives
- ⚠️  Slower than ruff

**Recommendation**: **Maybe** - useful but can be annoying. We already run in CI.

---

#### 4. **Conventional Commits** - Commit Message Format

```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.6.0
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
```

**Why add it**:
- ✅ Enforces commit message format
- ✅ Ensures: `feat:`, `fix:`, `docs:`, etc.
- ✅ Better changelogs
- ⚠️  Can be strict/annoying

**Example**:
```bash
# BLOCKED:
git commit -m "updated stuff"
# ❌ Commit message doesn't follow Conventional Commits

# ALLOWED:
git commit -m "feat: add new feature"
# ✅ Follows format: type: description
```

**Recommendation**: **Add it** - improves commit history quality

---

#### 5. **Markdown Linting** - Documentation Quality

```yaml
- repo: https://github.com/markdownlint/markdownlint
  rev: v0.12.0
  hooks:
    - id: markdownlint
      args: [--config, .markdownlint.yaml]
```

**Why add it**:
- ✅ Consistent markdown formatting
- ✅ Catches broken links
- ✅ Ensures documentation quality
- ⚠️  Can be picky about formatting

**Recommendation**: **Maybe** - useful if documentation is critical

---

#### 6. **Check Added Large Files** - Already have! ✅

```yaml
- id: check-added-large-files
  args: ['--maxkb=1000']
```

**Current**: 1MB limit
**Could increase**: `--maxkb=5000` (5MB)
**Could decrease**: `--maxkb=500` (500KB for stricter control)

**Recommendation**: **Keep as-is** (1MB is good)

---

#### 7. **Requirements.txt Update** - Not needed for us

```yaml
- repo: https://github.com/python-poetry/poetry
  rev: 1.8.0
  hooks:
    - id: poetry-check
    - id: poetry-lock
```

**Why NOT needed**:
- We use `uv` (not Poetry)
- `uv.lock` updates automatically
- No need for this hook

**Recommendation**: **Don't add**

---

#### 8. **Docstring Coverage** - Code Documentation

```yaml
- repo: https://github.com/econchick/interrogate
  rev: 1.7.0
  hooks:
    - id: interrogate
      args: [--fail-under=80, src/]
```

**Why add it**:
- ✅ Ensures functions have docstrings
- ✅ Enforces documentation standards
- ✅ Better code maintainability
- ⚠️  Can be annoying for simple functions

**Recommendation**: **Maybe** - useful for public APIs

---

#### 9. **Notebook Quality** - Jupyter Notebooks

```yaml
- repo: https://github.com/nbQA-dev/nbQA
  rev: 1.8.7
  hooks:
    - id: nbqa-ruff
    - id: nbqa-mypy
```

**Why NOT needed**:
- We don't use Jupyter notebooks in this project

**Recommendation**: **Don't add**

---

#### 10. **Import Sorting** - Not needed (Ruff does it)

```yaml
- repo: https://github.com/pycqa/isort
  rev: 5.13.0
  hooks:
    - id: isort
```

**Why NOT needed**:
- Ruff already sorts imports
- Would conflict with Ruff
- Redundant

**Recommendation**: **Don't add** - Ruff handles it

---

## ✅ Recommended Configuration

### Current (What We Have)

```yaml
repos:
  # 1. Ruff (linting + formatting)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff (auto-fixes most issues)
      - id: ruff-format (auto-formats code)

  # 2. Standard hooks (9 file quality checks)
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
      - id: mixed-line-ending

  # 3. Detect-secrets (security)
  - repo: https://github.com/Yelp/detect-secrets
    hooks:
      - id: detect-secrets
```

**Total**: 12 hooks across 3 repositories

---

### Enhanced (What We Should Add)

```yaml
repos:
  # Ruff (existing)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Standard hooks (existing)
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: mixed-line-ending
      # NEW: Add these for better file handling
      - id: check-case-conflict        # Prevents case-sensitive filename issues
      - id: check-executables-have-shebangs
      - id: check-shebang-scripts-are-executable
      - id: fix-byte-order-marker      # Removes UTF-8 BOM

  # Detect-secrets (existing)
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: ^(uv\.lock|\.secrets\.baseline)$

  # NEW: Conventional Commits (commit message format)
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.6.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]

  # NEW: MyPy (type checking) - Optional, can be slow
  # Uncomment if you want type checking before every commit
  # - repo: https://github.com/pre-commit/mirrors-mypy
  #   rev: v1.13.0
  #   hooks:
  #     - id: mypy
  #       args: [--ignore-missing-imports]
  #       additional_dependencies:
  #         - types-setuptools
  #         - sqlalchemy[mypy]
  #       pass_filenames: false
```

**Total Enhanced**: 17 hooks (5 new)

---

## 🚀 How Pre-Commit Hooks Work

### The Lifecycle

#### 1. Installation (One-time)

```powershell
# Install pre-commit package
uv add --dev pre-commit

# Install hooks into .git/hooks/
uv run pre-commit install

# Also install commit-msg hook (for conventional commits)
uv run pre-commit install --hook-type commit-msg
```

**What this does**:
- Creates `.git/hooks/pre-commit` script
- Creates `.git/hooks/commit-msg` script
- These run automatically on every commit

---

#### 2. Every Commit

```bash
git add file.py
git commit -m "fix: update code"
```

**What happens**:
```
1. Git prepares commit
2. Runs .git/hooks/pre-commit
3. Pre-commit framework reads .pre-commit-config.yaml
4. Runs each hook in order:

   Running ruff...
   ✅ Passed (auto-fixed 2 issues)

   Running ruff-format...
   ✅ Passed (formatted 1 file)

   Running trailing-whitespace...
   ✅ Passed

   Running check-yaml...
   ✅ Passed

   Running detect-secrets...
   ✅ Passed (no secrets detected)

   ... (all 12 hooks run)

5. If ALL pass → Commit proceeds
6. If ANY fail → Commit blocked
```

**If hooks modify files**:
```
✅ Hooks modified files (auto-fixed)
❌ Commit blocked - files changed
💡 Stage the changes and commit again:
   git add .
   git commit -m "fix: update code"
```

---

#### 3. Manual Run (Optional)

```powershell
# Run hooks on all files (not just staged)
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff

# Run only on staged files
uv run pre-commit run

# Skip hooks for emergency commit (not recommended!)
git commit --no-verify -m "emergency fix"
```

---

#### 4. Update Hooks

```powershell
# Update hook versions
uv run pre-commit autoupdate

# Re-install after config changes
uv run pre-commit install
```

---

## 📊 Current vs Enhanced Comparison

| Feature | Current | Enhanced | Benefit |
|---------|---------|----------|---------|
| **Linting** | ✅ Ruff | ✅ Ruff | Same |
| **Formatting** | ✅ Ruff | ✅ Ruff | Same |
| **File quality** | ✅ 9 hooks | ✅ 13 hooks | +4 file checks |
| **Secret detection** | ✅ detect-secrets | ✅ detect-secrets | Same |
| **Commit messages** | ❌ No | ✅ Conventional commits | Better history |
| **Type checking** | ❌ No | ⚠️ Optional (slow) | Stricter types |
| **Total hooks** | 12 | 17 | +5 hooks |

---

## 🎯 Recommendation: What To Add

### ⭐ Definitely Add

#### 1. Conventional Commits (Commit Message Format)

**Add this**:
```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.6.0
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
```

**Why**:
- ✅ Enforces `feat:`, `fix:`, `docs:` format
- ✅ Better changelog generation
- ✅ Clear commit history
- ✅ Fast (no performance impact)
- ✅ Used by most open source projects

**Impact**: Minimal annoyance, big benefit

---

#### 2. Additional Standard Hooks (4 more)

**Add these to existing standard hooks**:
```yaml
- id: check-case-conflict        # Windows/Mac/Linux filename issues
- id: check-executables-have-shebangs
- id: check-shebang-scripts-are-executable
- id: fix-byte-order-marker      # UTF-8 BOM issues
```

**Why**:
- ✅ Prevents cross-platform issues
- ✅ Ensures scripts are executable
- ✅ Fixes encoding issues
- ✅ Fast (milliseconds)

**Impact**: Zero annoyance, prevents rare bugs

---

### 🤔 Maybe Add

#### 3. MyPy Type Checking

**Only if**:
- You want strict type safety
- You're willing to wait 5-10 seconds per commit
- You want to catch type errors immediately

**Trade-off**:
- ✅ Catches type errors before CI
- ❌ Slows down commits significantly
- ❌ Can be annoying for quick fixes

**Alternative**: Run `just pre-push` before pushing (includes MyPy but not on every commit)

---

### ❌ Don't Add

#### 4. Pytest (Tests)

**Why NOT**:
- ❌ Too slow (10-30 seconds per commit)
- ❌ Makes commits painful
- ❌ Discourages frequent commits

**Better**: Run tests with `just pre-push` before pushing

---

#### 5. Bandit (Security)

**Why NOT**:
- ❌ Ruff already catches many issues
- ❌ Many false positives
- ❌ Already runs in CI

**Better**: Keep in CI only

---

## 🔧 Updated Configuration (Recommended)

Create `.pre-commit-config.yaml` with these additions:

```yaml
# Advanced Memory MCP Pre-Commit Hooks (Enhanced)
# Install: uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

repos:
  # Ruff - Fast Python linter and formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Standard pre-commit hooks (ENHANCED - 13 hooks now)
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: mixed-line-ending
      # NEW: Additional file quality checks
      - id: check-case-conflict
      - id: check-executables-have-shebangs
      - id: check-shebang-scripts-are-executable
      - id: fix-byte-order-marker

  # Security - Check for secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: ^(uv\.lock|\.secrets\.baseline)$

  # NEW: Conventional Commits (commit message format)
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.6.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]

# Configuration
default_stages: [commit]
fail_fast: false
```

**Total**: 17 hooks (added 5 new ones)

---

## 📝 How to Update Your Configuration

### Step 1: Update Config File

Replace `.pre-commit-config.yaml` with enhanced version above.

---

### Step 2: Install Enhanced Hooks

```powershell
# Install both pre-commit and commit-msg hooks
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

# Update to latest versions
uv run pre-commit autoupdate

# Test on all files
uv run pre-commit run --all-files
```

---

### Step 3: Verify Installation

```powershell
# Check installed hooks
Get-Content .git/hooks/pre-commit | Select-Object -First 5
Get-Content .git/hooks/commit-msg | Select-Object -First 5

# Test with a commit
git add README.md
git commit -m "test: verify hooks work"
# Should see hooks running!
```

---

## 🎯 Hook Performance Impact

### Typical Commit Time

**Without hooks**:
```
git commit -m "message"
→ Instant (0.1 seconds)
```

**With current hooks (12 hooks)**:
```
git commit -m "message"
→ Ruff: 0.5 seconds
→ Ruff-format: 0.3 seconds
→ Standard hooks: 0.2 seconds
→ Detect-secrets: 0.5 seconds
Total: ~1.5 seconds
```

**With enhanced hooks (17 hooks)**:
```
git commit -m "message"
→ All checks: ~2 seconds
```

**With MyPy added**:
```
git commit -m "message"
→ All checks + MyPy: ~7-10 seconds (SLOW!)
```

---

## 💡 Best Practices

### 1. Keep Hooks Fast

**Good hooks** (run on every commit):
- ✅ Ruff (very fast)
- ✅ File quality checks (instant)
- ✅ Secret detection (fast)
- ✅ Conventional commits (instant)

**Slow hooks** (run before push, not commit):
- ⚠️ MyPy (5-10 seconds)
- ❌ Pytest (10-30 seconds)
- ❌ Bandit (3-5 seconds)

**Rule of thumb**: Keep commits under 3 seconds

---

### 2. Auto-Fix When Possible

```yaml
# GOOD: Auto-fixes issues
- id: ruff
  args: [--fix]

- id: ruff-format  # Formats automatically

- id: trailing-whitespace  # Removes automatically

# BAD: Just reports errors
- id: ruff
  args: []  # No auto-fix, you must fix manually
```

**Philosophy**: Hooks should **help** you, not **annoy** you!

---

### 3. Make Exceptions Easy

```yaml
# Allow skipping hooks for emergency commits
fail_fast: false

# Allow override with --no-verify
# git commit --no-verify -m "emergency!"
```

**Don't be too strict** - sometimes you need to commit quickly!

---

### 4. Update Regularly

```powershell
# Monthly: Update hook versions
uv run pre-commit autoupdate

# Commit the updates
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

---

## 🎨 Hook Categories Explained

### Category 1: Code Quality

**Purpose**: Ensure code is well-written

**Hooks**:
- Ruff linting (errors, unused imports, complexity)
- Ruff formatting (style, indentation, spacing)

**When they run**: Every commit

---

### Category 2: File Quality

**Purpose**: Ensure files are correctly formatted

**Hooks**:
- Trailing whitespace removal
- End-of-file fixing
- YAML/JSON/TOML validation
- Line ending normalization

**When they run**: Every commit

---

### Category 3: Security

**Purpose**: Prevent security issues

**Hooks**:
- Secret detection (API keys, passwords, tokens)
- Private key detection (SSH keys, GPG keys)

**When they run**: Every commit

---

### Category 4: Git Quality

**Purpose**: Ensure clean Git history

**Hooks**:
- Merge conflict detection
- Large file blocking
- Conventional commit messages

**When they run**: Every commit / commit-msg

---

### Category 5: Type Safety (Optional)

**Purpose**: Catch type errors early

**Hooks**:
- MyPy type checking

**When they run**: Every commit (if enabled)

**Trade-off**: Slower commits but better type safety

---

## 🎯 Final Recommendations

### For Advanced Memory MCP

#### Definitely Add (5 new hooks):
1. ✅ **Conventional commits** - Better commit history
2. ✅ **check-case-conflict** - Prevents cross-platform issues
3. ✅ **check-executables-have-shebangs** - Script quality
4. ✅ **check-shebang-scripts-are-executable** - Script permissions
5. ✅ **fix-byte-order-marker** - UTF-8 BOM issues

#### Maybe Add:
6. ⚠️ **MyPy** - Only if you want strict type checking before every commit

#### Don't Add:
- ❌ Pytest - Too slow for every commit (use `just pre-push` instead)
- ❌ Bandit - Already in CI
- ❌ isort - Ruff already does it
- ❌ black - Ruff already does it

---

## 📚 Hook Resources

**Official Documentation**:
- Pre-commit Framework: https://pre-commit.com
- Hook Repository: https://github.com/pre-commit/pre-commit-hooks
- Ruff Pre-commit: https://github.com/astral-sh/ruff-pre-commit

**Supported Hooks**:
- All available hooks: https://pre-commit.com/hooks.html
- Language-specific: https://github.com/pre-commit/pre-commit-hooks#hooks-available

**Best Practices**:
- Keep hooks fast (<3 seconds total)
- Auto-fix when possible
- Don't block for non-critical issues
- Update regularly

---

## ✅ Quick Reference

### Installation

```bash
# Install pre-commit package
uv add --dev pre-commit

# Install hooks
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

# Test
uv run pre-commit run --all-files
```

### Daily Usage

```bash
# Hooks run automatically
git commit -m "feat: new feature"
→ Hooks run automatically
→ Issues are auto-fixed
→ Commit proceeds if all pass

# Skip hooks (emergency only!)
git commit --no-verify -m "emergency fix"
```

### Maintenance

```bash
# Update hooks monthly
uv run pre-commit autoupdate

# Run manually
uv run pre-commit run --all-files

# Clean hook cache
uv run pre-commit clean
```

---

## 🎊 Conclusion

**Pre-commit hooks** are your first line of defense against bad commits!

**We currently have**:
- 12 hooks (Ruff, standard checks, secret detection)
- ~1.5 seconds per commit
- Good coverage

**We should add**:
- Conventional commits (better history)
- 4 additional file quality checks
- Total: 17 hooks, ~2 seconds per commit

**We should NOT add**:
- MyPy (too slow for every commit)
- Pytest (way too slow)
- Bandit (already in CI)

**Result**: Fast, helpful hooks that make commits better without being annoying! 🚀

---

**Created**: October 17, 2025
**For**: Advanced Memory MCP + all Python projects
**Status**: Enhanced configuration ready to apply

**Commit with confidence!** 🪝✨
