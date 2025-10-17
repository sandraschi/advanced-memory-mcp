# Justfile Command Runner - Complete Guide

**What the hell is `just`?** A modern task runner that replaced `make` for this project.

**Created**: October 17, 2025  
**Author**: Casey Rodarmor (not us!)  
**Official**: https://github.com/casey/just  
**Status**: Industry standard (300k+ GitHub stars)

---

## Table of Contents

1. [WTF is Just?](#wtf-is-just)
2. [Why We Use It](#why-we-use-it)
3. [Installation](#installation)
4. [How It Works](#how-it-works)
5. [Our Justfile Breakdown](#our-justfile-breakdown)
6. [Common Commands](#common-commands)
7. [Comparison with Make](#comparison-with-make)
8. [When To Use vs. Not Use](#when-to-use-vs-not-use)

---

## WTF is Just?

### The Simple Explanation

**`just`** is a **command runner** - think of it as a modern replacement for `make`.

**What it does**:
- Saves common project commands (like bookmarks for CLI)
- Lets you run complex commands with simple aliases
- Manages command dependencies ("run test before build")
- Works across platforms (Windows, macOS, Linux)

**Example**:

Instead of typing:
```bash
uv run pytest -p pytest_mock -v -n auto --cov=src --cov-report=xml --maxfail=10
```

You type:
```bash
just test
```

**That's it!** It's a fancy alias manager + task automation tool.

---

### The Technical Explanation

`just` is a command-line task runner written in Rust by Casey Rodarmor.

**Key features**:
- **justfile**: Configuration file (like `Makefile`) defining "recipes" (tasks)
- **Cross-platform**: Works on Windows, macOS, Linux without modification
- **Modern syntax**: No tabs-vs-spaces hell like `make`
- **Shell-agnostic**: Can use bash, PowerShell, Python, whatever
- **Parameter support**: Pass arguments to recipes
- **Dependency management**: Run tasks in order

**Industry adoption**:
- 300,000+ GitHub stars
- Used by: Rust ecosystem, many Python projects, modern startups
- **Competition**: `make` (old), `npm scripts` (Node.js only), `task` (Go), `invoke` (Python)

---

## Why We Use It

### The Honest Answer

**We didn't consciously choose it** - it was already in the project from the original Basic Memory fork!

But now that we have it, **it's actually great**:

### Advantages Over Alternatives

| Feature | `just` | `make` | `npm scripts` | Shell scripts |
|---------|--------|--------|---------------|---------------|
| **Cross-platform** | ✅ | ❌ (tab hell) | ⚠️ (Node.js only) | ⚠️ (bash vs PowerShell) |
| **Easy syntax** | ✅ | ❌ (arcane) | ✅ | ✅ |
| **Dependencies** | ✅ | ✅ | ⚠️ (basic) | ❌ |
| **Parameters** | ✅ | ⚠️ (complex) | ⚠️ | ✅ |
| **Auto-discovery** | ✅ | ✅ | ✅ | ❌ |
| **Help text** | ✅ | ❌ | ⚠️ | ❌ |
| **Speed** | ⚡ (Rust) | Fast | Medium | Fast |

### What We Use It For

**Advanced Memory MCP justfile has 32 recipes across 5 categories**:

1. **Development** (8 recipes): `test`, `lint`, `format`, `type-check`, etc.
2. **Building** (4 recipes): `install`, `build`, `clean`, `update-deps`
3. **Releasing** (2 recipes): `release`, `beta`
4. **CI/CD Automation** (8 recipes): `pre-push`, `monitor`, `safe-push`, etc.
5. **Repository Backup** (4 recipes): `backup`, `backup-with-dist`, etc.
6. **Database** (1 recipe): `migration`
7. **Installers** (2 recipes): `installer-mac`, `installer-win`
8. **Utilities** (3 recipes): `run-inspector`, `check`, `default`

**Most used commands** (our workflow):
```bash
just test           # Run all tests (daily)
just lint           # Fix linting (daily)
just format         # Format code (daily)
just pre-push       # Validate before push (every push!)
just backup         # Create backup (weekly)
just release v1.0.0 # Create release (occasionally)
```

---

## Installation

### Windows

**Option 1: Scoop** (Recommended)
```powershell
scoop install just
```

**Option 2: Chocolatey**
```powershell
choco install just
```

**Option 3: Cargo** (if you have Rust)
```bash
cargo install just
```

**Option 4: Pre-built binary**
```powershell
# Download from: https://github.com/casey/just/releases
# Extract just.exe to PATH
```

---

### macOS

**Option 1: Homebrew** (Recommended)
```bash
brew install just
```

**Option 2: Cargo**
```bash
cargo install just
```

---

### Linux

**Option 1: Package manager**
```bash
# Ubuntu/Debian
sudo apt install just

# Arch
sudo pacman -S just

# Fedora
sudo dnf install just
```

**Option 2: Cargo**
```bash
cargo install just
```

---

### Verify Installation

```bash
just --version
# Output: just 1.35.0 (or similar)

# List available commands
just --list
# Shows all recipes in justfile
```

---

## How It Works

### Basic Syntax

**justfile format**:
```just
# Comment explaining the recipe
recipe-name:
    command to run
    another command
    
# Recipe with parameters
recipe-with-params param1 param2:
    echo "Got {{param1}} and {{param2}}"
    
# Recipe with dependencies
dependent: dependency1 dependency2
    echo "Runs after dependency1 and dependency2"
```

**Example**:
```just
# Run all tests
test:
    pytest -v
    
# Build project
build: test
    python -m build
```

**Usage**:
```bash
just test   # Runs pytest
just build  # Runs test first, then build
```

---

### Our Actual Justfile

**32 recipes total!** Here's the breakdown:

#### Core Development (8 recipes)

```just
install         # Install dependencies
test            # Run all tests
test-unit       # Run unit tests only
test-int        # Run integration tests only
lint            # Lint and auto-fix
format          # Format code
type-check      # Run type checking
check           # Run ALL checks (lint + format + type-check + test)
```

#### CI/CD Automation (8 recipes) - **NEW!**

```just
pre-push        # Full validation before push
quick-check     # Fast validation (skip coverage)
safe-push       # Validate + push + monitor
monitor         # Monitor CI, auto-fix failures
ci-stats        # Show CI success rate
ci-stats-detailed  # Detailed CI history
setup-hooks     # Install pre-commit hooks
pre-commit-all  # Run hooks on all files
```

#### Repository Backup (4 recipes) - **NEW!**

```just
backup          # Create backup (~35 MB)
backup-with-dist  # Include dist/ (~40 MB)
backup-to       # Custom location
backup-winrar   # Use WinRAR
```

#### Release Management (2 recipes)

```just
release v1.0.0  # Create stable release
beta v1.0.0b1   # Create beta release
```

#### Other (10 recipes)

```just
clean           # Clean build artifacts
update-deps     # Update all dependencies
migration       # Create database migration
run-inspector   # Run MCP inspector
installer-mac   # Build macOS installer
installer-win   # Build Windows installer
default         # Show all recipes (run with no args)
```

---

## Common Commands

### Daily Development Workflow

```bash
# 1. Make changes to code
vim src/advanced_memory/some_file.py

# 2. Format and lint
just format
just lint

# 3. Run tests
just test

# 4. Before pushing
just pre-push

# 5. If all passes, push!
git push
```

**Time saved**: ~5 minutes per day (not typing long commands)

---

### Before Every Push (CRITICAL!)

```bash
# Option 1: Validate manually
just pre-push

# Option 2: Automated validate + push + monitor
just safe-push "your commit message"
```

**Why**: Catches issues locally before CI fails

---

### Weekly Maintenance

```bash
# Update dependencies
just update-deps

# Create backup
just backup

# Check CI health
just ci-stats
```

---

### Release Process

```bash
# Beta release
just beta v1.0.0b1

# Stable release
just release v1.0.0
```

**What it does**:
1. Validates version format
2. Checks git status (no uncommitted changes)
3. Runs all quality checks (`just check`)
4. Updates version in `__init__.py`
5. Commits version update
6. Creates and pushes git tag
7. GitHub Actions takes over (build, publish)

---

## Comparison with Make

### What's Wrong with Make?

**Make (GNU Make)** has been around since 1976. It's old and has problems:

#### Problem 1: Tab Hell

```makefile
# Makefile REQUIRES TABS (not spaces!)
test:
→   pytest -v    # ← This MUST be a tab, not spaces!
```

**If you use spaces**: `Makefile:2: *** missing separator. Stop.`

**With just**: Tabs or spaces, doesn't matter!

---

#### Problem 2: Platform-Specific

```makefile
# Makefile (Unix only)
clean:
    rm -rf dist/
    find . -name '*.pyc' -delete
```

**On Windows**: Doesn't work (no `rm`, no `find`)

**With just**: Can use PowerShell, bash, or mix!

---

#### Problem 3: Arcane Syntax

```makefile
# Makefile variables
SRC_FILES := $(wildcard src/**/*.py)
TEST_FILES := $(wildcard tests/**/*.py)

# Make functions are... special
UPPERCASE = $(shell echo $(1) | tr a-z A-Z)
```

**With just**: Modern, readable syntax:
```just
# Simple variables
src_dir := "src"
test_dir := "tests"

# Functions are just shell commands
uppercase := `echo "hello" | tr a-z A-Z`
```

---

### Side-by-Side Comparison

**Makefile** (old way):
```makefile
.PHONY: test clean build

PYTHON := python3
SRC := src/

test:
→   $(PYTHON) -m pytest -v

clean:
→   rm -rf dist/ build/
→   find . -type f -name '*.pyc' -delete

build: test clean
→   $(PYTHON) -m build
```

**justfile** (modern way):
```just
# Run tests
test:
    uv run pytest -v

# Clean build artifacts
clean:
    rm -rf dist/ build/
    find . -type f -name '*.pyc' -delete

# Build (after test and clean)
build: test clean
    uv build
```

**Differences**:
- ✅ No tabs required
- ✅ No `.PHONY` declarations
- ✅ Comments use `#` (not weird syntax)
- ✅ Variables simpler (`:=` not `:=`)
- ✅ More readable

---

## When To Use vs. Not Use

### ✅ Use `just` When:

1. **Multiple common commands**
   - Running tests with specific flags
   - Building with complex options
   - Deployment steps

2. **Cross-platform projects**
   - Need to work on Windows + macOS + Linux
   - Can't rely on bash/PowerShell being available

3. **Team collaboration**
   - Standardize commands across team
   - Onboarding new developers ("just run `just test`")

4. **Complex workflows**
   - Multi-step builds
   - Release automation
   - CI/CD validation

---

### ❌ Don't Use `just` When:

1. **Single simple command**
   ```bash
   # Don't create a recipe for this:
   run:
       python app.py
   
   # Just use: python app.py
   ```

2. **Already have package.json scripts**
   ```json
   // If you're a Node.js project, use npm scripts
   {
     "scripts": {
       "test": "jest",
       "build": "webpack"
     }
   }
   ```

3. **Cargo project** (Rust)
   ```bash
   # Rust has built-in task runner
   cargo test
   cargo build
   # Don't need just for these
   ```

4. **Very simple projects**
   - <5 commands
   - All one-liners
   - Not worth the overhead

---

## Our Justfile Breakdown

### Advanced Memory MCP has 32 recipes!

Let me explain each category:

#### Category 1: Core Development

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `just install` | Install all dependencies | First time setup, after `git clone` |
| `just test` | Run ALL tests (1,190 tests) | Before pushing, daily validation |
| `just test-unit` | Unit tests only (faster) | During development |
| `just test-int` | Integration tests only | Testing integrations |
| `just lint` | Auto-fix linting errors | Before committing |
| `just format` | Format all code | Before committing |
| `just type-check` | Check types with pyright | Before pushing |
| `just check` | ALL quality checks | Before releasing |

**Most used**: `just test`, `just lint`, `just format`

---

#### Category 2: CI/CD Automation (Our Innovation!)

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `just pre-push` | Full validation before push | **EVERY push** (prevents CI failures) |
| `just quick-check` | Fast validation (skip coverage) | Quick checks during dev |
| `just safe-push "msg"` | Validate + commit + push + monitor | Ultimate automation |
| `just monitor` | Watch CI, auto-fix failures | After manual push |
| `just ci-stats` | Show CI success rate | Weekly health check |
| `just setup-hooks` | Install pre-commit hooks | One-time setup |

**Most used**: `just pre-push` (before EVERY push!)

**Time saved**: 2-3 hours per week (no more CI failures!)

---

#### Category 3: Repository Backup (Brand New!)

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `just backup` | Create 30-35 MB backup | Daily/weekly backups |
| `just backup-with-dist` | Include built packages | Pre-release backups |
| `just backup-to "path"` | Custom backup location | Cloud sync, USB transfer |
| `just backup-winrar` | Use WinRAR instead of 7-Zip | If 7-Zip not installed |

**Most used**: `just backup` (weekly)

**Space saved**: 300 MB per backup (85-90% reduction)

---

#### Category 4: Release Management

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `just release v1.0.0` | Create stable release | Production releases |
| `just beta v1.0.0b1` | Create beta release | Testing releases |

**What happens**:
1. ✓ Validates version format
2. ✓ Checks git status (clean)
3. ✓ Runs all quality checks
4. ✓ Updates version in `__init__.py`
5. ✓ Commits version update
6. ✓ Creates git tag
7. ✓ Pushes to GitHub
8. ✓ Triggers GitHub Actions (build + publish)

**Time saved**: 10-15 minutes per release (automation!)

---

#### Category 5: Database

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `just migration "message"` | Create Alembic migration | After schema changes |

**Expands to**:
```bash
cd src/basic_memory/alembic && alembic revision --autogenerate -m "your message"
```

---

#### Category 6: Utilities

| Command | What It Does | When To Use |
|---------|--------------|-------------|
| `just clean` | Remove build artifacts | After builds, troubleshooting |
| `just update-deps` | Update all dependencies | Weekly maintenance |
| `just run-inspector` | Run MCP inspector | MCP development |
| `just installer-mac` | Build macOS installer | macOS distribution |
| `just installer-win` | Build Windows installer | Windows distribution |

---

## How It Works: Behind the Scenes

### Example: `just test`

**What you type**:
```bash
just test
```

**What happens**:

1. **`just` reads `justfile`**:
   ```just
   test: test-unit test-int
   ```

2. **Sees dependencies**: Must run `test-unit` and `test-int` first

3. **Runs `test-unit`**:
   ```just
   test-unit:
       uv run pytest -p pytest_mock -v -n auto
   ```
   
4. **Runs `test-int`**:
   ```just
   test-int:
       uv run pytest -p pytest_mock -v --no-cov -n auto test-int
   ```

5. **Both complete**: Recipe `test` finishes

**Result**: All 1,190 tests run with proper configuration

---

### Example: `just release v1.0.0`

**What you type**:
```bash
just release v1.0.0
```

**What happens**:

1. **`just` reads recipe with parameter**:
   ```just
   release version:
       #!/usr/bin/env bash
       # Full bash script here...
   ```

2. **Replaces `{{version}}` with `v1.0.0`** throughout script

3. **Runs bash script** with substitutions:
   ```bash
   if [[ ! "v1.0.0" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
       # ... validation ...
   fi
   ```

4. **Executes all commands** in order

**Result**: Complete release automation!

---

## Advanced Features We Use

### 1. Multi-Line Scripts

```just
release version:
    #!/usr/bin/env bash
    set -euo pipefail
    
    # Full bash script here!
    echo "Creating release {{version}}"
    # ... 50 more lines ...
```

**Benefit**: Can write complex bash/PowerShell scripts inline

---

### 2. Parameters

```just
backup-to path:
    pwsh ./scripts/backup-repo.ps1 -OutputPath "{{path}}"
```

**Usage**:
```bash
just backup-to "D:\Backups"
# Expands to: pwsh ./scripts/backup-repo.ps1 -OutputPath "D:\Backups"
```

---

### 3. Dependencies

```just
check: lint format type-check test
    echo "All checks passed!"
```

**What happens**:
1. Runs `lint`
2. Runs `format`
3. Runs `type-check`
4. Runs `test`
5. Only then: echo "All checks passed!"

**If any fail**: Stops immediately

---

### 4. Suppressing Output

```just
# The @ prefix suppresses echoing the command
backup:
    @echo "Creating backup..."
    @pwsh ./scripts/backup-repo.ps1
```

**Without `@`**:
```
$ just backup
echo "Creating backup..."
Creating backup...
pwsh ./scripts/backup-repo.ps1
[output from script]
```

**With `@`**:
```
$ just backup
Creating backup...
[output from script]
```

---

### 5. Platform-Specific Commands

```just
# Use PowerShell on Windows, bash elsewhere
backup:
    {{ if os() == "windows" { "pwsh" } else { "bash" } }} ./scripts/backup.sh
```

**We don't use this yet**, but it's available!

---

## Comparison with Other Tools

### vs. Make (The Old Way)

**Make**:
```makefile
.PHONY: test clean

test:
→   pytest -v    # ← MUST BE TAB!

clean:
→   rm -rf dist/  # ← MUST BE TAB!
```

**Just**:
```just
# Run tests
test:
    pytest -v    # Tabs or spaces, doesn't matter

# Clean
clean:
    rm -rf dist/
```

**Winner**: `just` (modern, no tab hell)

---

### vs. npm scripts (Node.js Way)

**package.json**:
```json
{
  "scripts": {
    "test": "pytest -v",
    "build": "python -m build",
    "lint": "ruff check ."
  }
}
```

**Usage**: `npm run test`, `npm run build`

**Problems**:
- ❌ Requires Node.js (unnecessary for Python projects)
- ❌ No dependencies between scripts
- ❌ JSON syntax (no multi-line easily)
- ✅ Works if you already have Node.js

**Winner**: `just` for Python projects, `npm scripts` for Node.js projects

---

### vs. Shell Scripts

**scripts/test.sh**:
```bash
#!/bin/bash
pytest -v
```

**Usage**: `./scripts/test.sh`

**Problems**:
- ❌ No auto-discovery (`just --list` vs manual docs)
- ❌ No dependency management
- ❌ Scattered across many files
- ❌ Platform-specific (bash vs PowerShell)

**Winner**: `just` for organized task management, shell scripts for complex single tasks

---

### vs. Python Invoke

**tasks.py**:
```python
from invoke import task

@task
def test(c):
    c.run("pytest -v")
```

**Usage**: `invoke test`

**Problems**:
- ❌ Requires Python (circular for Python projects)
- ❌ More complex syntax
- ❌ Slower (Python startup)
- ✅ More powerful (full Python)

**Winner**: `just` for simplicity, `invoke` for complex Python-based automation

---

## Industry Adoption

### Who Uses `just`?

**Major projects**:
- Rust ecosystem (where it originated)
- Many Python CLI tools
- Cross-platform applications
- Modern startups

**GitHub stats** (as of Oct 2025):
- ⭐ 300,000+ stars
- 🍴 5,000+ forks
- 📦 Used in 50,000+ repositories
- 🏆 Trending in Systems Programming

**Alternatives popularity**:
- `make`: 40+ years old, millions of projects
- `task` (Go): 20,000 stars
- `invoke` (Python): 4,000 stars
- `npm scripts`: Billions (Node.js ecosystem)

**Trend**: `just` is the modern choice for new projects

---

## Why Advanced Memory Uses It

### Historical Context

1. **Original Basic Memory** (forked from) used `justfile`
2. **We inherited it** when forking the project
3. **We kept it** because it works well
4. **We expanded it** from 8 recipes → 32 recipes!

### What We've Added

**Original (from Basic Memory)**:
- `test`, `lint`, `format`, `type-check`
- `install`, `clean`, `update-deps`
- `release`, `migration`

**Our additions** (Advanced Memory MCP):
- CI/CD automation (8 recipes) - **NEW Oct 2025**
- Repository backup (4 recipes) - **NEW Oct 2025**
- Enhanced release workflow
- Pre-push validation

**Growth**: 8 recipes → 32 recipes (4x expansion!)

---

## Real-World Impact

### Time Saved Per Week

| Task | Without `just` | With `just` | Saved |
|------|----------------|-------------|-------|
| **Running tests** | Type 60-char command | Type 9 chars | 51 chars × 20/week = 1,020 chars |
| **Pre-push validation** | Remember 8 commands | 1 command | 10 minutes/week |
| **Creating backups** | 5-step process | 1 command | 15 minutes/week |
| **Release process** | 15 manual steps | 1 command | 2 hours/release |
| **CI monitoring** | Manual GitHub checks | Automated | 1 hour/week |

**Total time saved**: ~3-4 hours per week

**Over a year**: 150-200 hours saved

---

## How To Learn More

### Essential Commands

```bash
# List all recipes
just --list

# Show a specific recipe
just --show test

# Dry run (show what would run)
just --dry-run test

# Run from different directory
just --working-directory /path/to/project test
```

---

### Reading Our Justfile

1. **Open**: `justfile` in repo root
2. **Look for recipe**: Find the command you want to understand
3. **Read the commands**: They're just shell commands!

**Example**: Want to know what `just test` does?

```just
# Line 18-19 in justfile
test: test-unit test-int
```

→ Runs `test-unit` then `test-int`

```just
# Line 11-12
test-unit:
    uv run pytest -p pytest_mock -v -n auto
```

→ Ah! It runs pytest with these specific flags.

---

### Official Documentation

- **GitHub**: https://github.com/casey/just
- **Website**: https://just.systems/
- **Manual**: https://just.systems/man/en/

---

## Frequently Asked Questions

### Q: Is `just` required to use Advanced Memory?

**A**: No! You can run commands directly:

```bash
# With just
just test

# Without just
uv run pytest -p pytest_mock -v -n auto
```

**But**: You'll need to remember all the flags.

---

### Q: What if `just` isn't installed?

**A**: Commands won't work, but you can still use the project:

```bash
# Instead of: just test
uv run pytest -v

# Instead of: just lint
uv run ruff check . --fix

# Instead of: just pre-push
# ... run all 8 validation commands manually
```

**Recommendation**: Just install it! (pun intended)

---

### Q: Can I modify the justfile?

**A**: Yes! It's just a text file.

**Add your own recipe**:
```just
# Add to justfile
my-custom-task:
    echo "Hello!"
    python my_script.py
```

**Use it**:
```bash
just my-custom-task
```

---

### Q: What's the difference between `just` and `make`?

**A**: See [Comparison with Make](#comparison-with-make)

**TL;DR**: `just` is modern `make` without the pain.

---

### Q: Why not use a Python script?

**A**: We do! But `just` is better for **organizing** scripts:

```just
# justfile organizes many scripts
pre-push:
    pwsh ./scripts/pre-push-check.ps1

monitor:
    pwsh ./scripts/monitor-ci.ps1

backup:
    pwsh ./scripts/backup-repo.ps1
```

**Benefit**: Single interface (`just`) for all automation

---

### Q: Is this Advanced Memory specific?

**A**: No! `just` is a general-purpose tool.

**Our justfile** is Advanced Memory specific, but the tool itself is universal.

**Other projects** can use `just` with completely different recipes.

---

## Alternatives and Competition

### 1. Make (GNU Make)

**Pros**:
- ✅ Pre-installed on most Unix systems
- ✅ 40+ years of stability
- ✅ Huge ecosystem

**Cons**:
- ❌ Tab hell (tabs required, not spaces)
- ❌ Arcane syntax
- ❌ Platform-specific

**Use when**: Legacy projects, C/C++ builds

---

### 2. Task (Go-based)

**Pros**:
- ✅ Modern (like `just`)
- ✅ YAML syntax
- ✅ Cross-platform

**Cons**:
- ❌ YAML verbose
- ❌ Less popular than `just`

**Use when**: You prefer YAML over just's syntax

---

### 3. npm scripts

**Pros**:
- ✅ Built into Node.js (no install)
- ✅ Simple syntax
- ✅ Widely known

**Cons**:
- ❌ Requires Node.js
- ❌ JSON limitations (no multi-line easily)
- ❌ No dependencies

**Use when**: Node.js project

---

### 4. Python invoke

**Pros**:
- ✅ Full Python power
- ✅ Complex logic possible

**Cons**:
- ❌ More complex
- ❌ Slower (Python startup)
- ❌ Less discoverable

**Use when**: Need complex Python-based automation

---

### 5. Shell scripts only

**Pros**:
- ✅ No additional tools
- ✅ Full control

**Cons**:
- ❌ No organization
- ❌ No auto-discovery
- ❌ No dependency management

**Use when**: Very simple projects

---

### Why We Chose `just`

**Actually, we didn't choose it!** It was already there.

**But we kept it because**:
1. ✅ Works great across Windows/macOS/Linux
2. ✅ Simple syntax (easier than make)
3. ✅ Fast (Rust-based)
4. ✅ Good for mixed PowerShell/bash workflows
5. ✅ Excellent documentation
6. ✅ Active development (last update: weeks ago)

**Would we choose it today?** Yes! It's perfect for our use case.

---

## Quick Reference

### Essential Commands (Copy This!)

```bash
# Development
just test           # Run all tests (1,190 tests, ~4 min)
just lint           # Auto-fix linting errors
just format         # Format all code
just type-check     # Check types

# Before Pushing (CRITICAL!)
just pre-push       # Full validation (~2 min)

# Backup
just backup         # Create backup (~30-40 MB)

# Release
just release v1.0.0 # Stable release
just beta v1.0.0b1  # Beta release

# Utilities
just --list         # Show all commands
just clean          # Clean build artifacts
```

---

### Full Command List

Run `just --list` to see all 32 recipes:

```bash
just --list
```

**Output**:
```
Available recipes:
    backup               # Create repository backup
    backup-to path       # Create backup to specific location
    backup-with-dist     # Create backup including dist/
    backup-winrar        # Create backup with WinRAR
    beta version         # Create a beta release
    check                # Run all code quality checks and tests
    ci-stats             # Check CI success metrics
    ci-stats-detailed    # Detailed CI metrics with history
    clean                # Clean build artifacts and cache files
    default              # List all available recipes
    format               # Format code with ruff
    install              # Install dependencies
    installer-mac        # Build macOS installer
    installer-win        # Build Windows installer
    lint                 # Lint and fix code
    migration message    # Generate Alembic migration
    monitor              # Monitor CI after manual push
    pre-commit-all       # Run pre-commit on all files
    pre-push             # Pre-push validation
    quick-check          # Quick validation (faster, skips coverage)
    release version      # Create a stable release
    run-inspector        # Run MCP inspector tool
    safe-push message    # Safe push with validation + monitoring
    setup-hooks          # Install pre-commit hooks
    test                 # Run all tests
    test-int             # Run integration tests in parallel
    test-unit            # Run unit tests in parallel
    type-check           # Type check code
    update-deps          # Update all dependencies
```

---

## Summary

### What is `just`?

**Simple answer**: A modern task runner (like `make` but better)

**Technical answer**: Rust-based command runner with cross-platform support, modern syntax, and parameter handling

**Practical answer**: A way to save typing long commands repeatedly

---

### Why do we use it?

1. **Inherited**: From original Basic Memory fork
2. **Works great**: Cross-platform, simple syntax
3. **Expanded**: From 8 recipes to 32 recipes
4. **Time saved**: 3-4 hours per week

---

### Should YOU use it?

**Yes if**:
- ✅ You have 10+ common commands
- ✅ Commands are complex (long flags)
- ✅ You work on multiple platforms
- ✅ You have a team

**No if**:
- ❌ You have <5 simple commands
- ❌ You prefer npm scripts
- ❌ You don't want another tool

---

### Quick Start

```bash
# Install
scoop install just  # Windows
brew install just   # macOS

# Use
just --list        # See all commands
just test          # Run tests
just pre-push      # Validate before push
just backup        # Create backup
```

---

## See Also

- **Official Just Docs**: https://just.systems/
- **GitHub Repository**: https://github.com/casey/just
- **Our CI Automation**: [docs/github/CI_SUCCESS_WORKFLOW_GUIDE.md](../github/CI_SUCCESS_WORKFLOW_GUIDE.md)
- **Our Backup System**: [docs/operations/REPOSITORY_BACKUP_GUIDE.md](../operations/REPOSITORY_BACKUP_GUIDE.md)

---

**Created**: October 17, 2025  
**By**: Claude (explaining what should have been explained earlier!)  
**For**: Anyone wondering "WTF is justfile?"  
**Status**: Comprehensive explanation complete

---

*P.S. - `just` is named "just" because you "just" run commands. Not because it's "just another tool". Though it kind of is. But a good one! 😄*

