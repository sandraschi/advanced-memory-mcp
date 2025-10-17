# pytest-cov - Test Coverage Tool

**What**: Test coverage measurement tool for Python  
**Official**: https://pytest-cov.readthedocs.io/  
**Purpose**: Measure which lines of code are executed during tests  
**Output**: `htmlcov/` directory with visual coverage reports

---

## Table of Contents

1. [What is Test Coverage?](#what-is-test-coverage)
2. [What is pytest-cov?](#what-is-pytest-cov)
3. [What is htmlcov/?](#what-is-htmlcov)
4. [How We Use It](#how-we-use-it)
5. [Understanding Coverage Reports](#understanding-coverage-reports)
6. [Advanced Memory Coverage](#advanced-memory-coverage)
7. [Improving Coverage](#improving-coverage)

---

## What is Test Coverage?

### Simple Explanation

**Test coverage** = What percentage of your code is executed when tests run

**Example**:
```python
def divide(a, b):
    if b == 0:              # Line 2
        return "Error"      # Line 3
    return a / b            # Line 4
```

**Test 1** (only happy path):
```python
def test_divide():
    assert divide(10, 2) == 5  # Executes lines 2, 4
```

**Coverage**: 2 out of 3 lines = **66.7%** (line 3 not tested!)

**Test 2** (both paths):
```python
def test_divide():
    assert divide(10, 2) == 5
    assert divide(10, 0) == "Error"  # Now executes line 3!
```

**Coverage**: 3 out of 3 lines = **100%**

---

### Why It Matters

**Higher coverage** = More confident code

| Coverage | Risk Level | Recommendation |
|----------|------------|----------------|
| 90-100% | Very Low | Excellent! |
| 80-89% | Low | Industry standard (good) |
| 70-79% | Medium | Acceptable |
| 50-69% | High | Needs improvement |
| <50% | Very High | Write tests! |

**Advanced Memory MCP**: ~85% overall (good!)

---

## What is pytest-cov?

### Technical Details

**pytest-cov** is a pytest plugin that:
- Integrates `coverage.py` with pytest
- Measures code execution during test runs
- Generates coverage reports in multiple formats

**Installation**:
```bash
uv add --dev pytest-cov
```

**Basic usage**:
```bash
pytest --cov=src
```

**Advanced Memory uses it in**:
- `just test` command
- GitHub Actions CI
- Local development

---

### Coverage Report Formats

pytest-cov can generate reports in multiple formats:

| Format | Output | Use Case |
|--------|--------|----------|
| **Terminal** | Text in console | Quick check during dev |
| **HTML** | `htmlcov/` directory | Detailed visual analysis |
| **XML** | `coverage.xml` | CI systems (Codecov, etc.) |
| **JSON** | `coverage.json` | Programmatic analysis |
| **LCOV** | `coverage.lcov` | Editor integrations |

**We use**: Terminal + HTML + XML

---

## What is htmlcov/?

### Directory Structure

```
htmlcov/
├── index.html                    # Main dashboard
├── class_index.html              # Coverage by class
├── function_index.html           # Coverage by function
├── z_*.html                      # Individual file reports
├── style*.css                    # Styling
├── coverage_html*.js             # Interactive features
└── status.json                   # Coverage data
```

**Size**: ~11 MB (for 1,190 tests covering 173 files)

**Created by**: `pytest --cov=src --cov-report=html`

---

### How to View

**Option 1: Open directly**
```bash
# Windows
explorer.exe htmlcov\index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

**Option 2: Python HTTP server**
```bash
cd htmlcov
python -m http.server 8000
# Visit: http://localhost:8000
```

---

### What You See

**Main Dashboard** (`index.html`):
- Overall coverage percentage
- List of all Python files
- Coverage % per file
- Number of missing lines
- Sortable columns

**File Details** (click any file):
- Complete source code
- Line-by-line coverage highlighting:
  - 🟢 Green = tested (executed)
  - 🔴 Red = not tested (never executed)
  - ⚪ Gray = non-executable (comments, blanks)
- Execution counts (how many times each line ran)
- Branch coverage (if enabled)

---

## How We Use It

### Advanced Memory MCP Configuration

**In `pyproject.toml`**:
```toml
[tool.pytest.ini_options]
addopts = "-v -s"
testpaths = ["tests"]

[tool.coverage.run]
source = ["src/advanced_memory"]
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

# Files excluded from coverage requirements
omit = [
    "*/external_auth_provider.py",
    "*/supabase_auth_provider.py",
    "*/watch_service.py",
    "*/background_sync.py",
    "*/cli/main.py",
    "*/services/migration_service.py",
]

fail_under = 80  # Require 80% minimum coverage
show_missing = true
precision = 2
```

---

### Commands That Generate Coverage

**Local development**:
```bash
# Run tests with coverage
just test
# Or
pytest --cov=src --cov-report=html

# Quick coverage check (terminal only)
pytest --cov=src --cov-report=term-missing
```

**GitHub Actions CI**:
```yaml
- name: Run tests with coverage
  run: |
    uv run pytest --cov=src --cov-report=xml --cov-report=html
    
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

---

## Understanding Coverage Reports

### Terminal Report

```
---------- coverage: platform linux, python 3.12 -----------
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
src/advanced_memory/__init__.py        10      0   100%
src/advanced_memory/config.py          45      5    89%   123-127
src/advanced_memory/mcp/tools/...     120     12    90%   45, 67-73
-----------------------------------------------------------------
TOTAL                               15234   2286    85%
```

**Columns**:
- **Stmts**: Total statements (lines of code)
- **Miss**: Statements not executed
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

---

### HTML Report (htmlcov/)

**Dashboard view**:
```
Module                              statements  missing  excluded  coverage
advanced_memory/config.py           45          5        0         89%
advanced_memory/mcp/tools/...       120         12       0         90%
```

**Click on file → Detailed view**:
```python
1  | import os                          # Gray (non-executable)
2  | from pathlib import Path           # Gray
3  |                                    # Gray
4  | def get_config():                  # Green (tested)
5  |     path = Path("config.toml")     # Green (tested)
6  |     if path.exists():               # Green (tested)
7  |         return load_config(path)    # Green (tested)
8  |     else:                           # Yellow (branch)
9  |         return default_config()     # Red (NOT TESTED!)
10 |                                    # Gray
```

**Hovering** over lines shows execution count: `"run 15 times"`

---

### Branch Coverage

**What is it**: Testing both `if` and `else` branches

**Example**:
```python
def check_value(x):
    if x > 10:        # Line 2
        return "big"  # Line 3
    else:             # Line 4
        return "small"  # Line 5
```

**Line coverage** (2 tests needed):
- Test with `x=15`: Covers lines 2, 3
- Test with `x=5`: Covers lines 2, 4, 5
- Result: 100% line coverage

**Branch coverage** (also 2 tests needed):
- Same tests cover both branches (if/else)
- Result: 100% branch coverage

**Advanced Memory**: Uses line coverage (simpler, faster)

---

## Advanced Memory Coverage

### Current Statistics

**Overall**: ~85% coverage (1,190 tests)

**By category**:

| Category | Files | Coverage | Notes |
|----------|-------|----------|-------|
| **MCP Tools** | 25 | 90-95% | Excellent! |
| **Repositories** | 8 | 90-95% | Well tested |
| **Services** | 15 | 80-90% | Good |
| **API Endpoints** | 14 | 85-90% | Good |
| **CLI Commands** | 26 | 75-85% | Acceptable |
| **Markdown Parser** | 6 | 90-95% | Excellent |
| **Utilities** | 20 | 80-90% | Good |

**Excluded files** (intentionally):
- `external_auth_provider.py` - External HTTP (hard to test)
- `supabase_auth_provider.py` - External API (hard to test)
- `watch_service.py` - File system watcher (integration test complexity)
- `background_sync.py` - Background processes (complex)
- `cli/main.py` - CLI entry point (tested via CLI tests)
- `migration_service.py` - Complex migration scenarios

---

### Coverage Trends

**Over time** (estimated):

| Date | Coverage | Change | Reason |
|------|----------|--------|--------|
| Sep 2024 | ~70% | Baseline | Initial fork |
| Oct 2024 | ~75% | +5% | Added MCP tool tests |
| Nov 2024 | ~80% | +5% | Added integration tests |
| Jan 2025 | ~85% | +5% | Added zettelmaker tests |

**Target**: Maintain 85%+ (current level)

---

## Improving Coverage

### Step 1: Find Untested Code

```bash
# Generate coverage report
just test

# Open in browser
explorer.exe htmlcov\index.html

# Sort by coverage (click "Cover" column)
# Files at bottom = lowest coverage
```

---

### Step 2: Identify Missing Lines

**Click on a low-coverage file** → See red lines (not tested)

**Example**: If you see:
```python
45  | def handle_error(e):           # Red
46  |     logger.error(f"Error: {e}")  # Red
47  |     return {"error": str(e)}     # Red
```

**Means**: This error handling code is never executed in tests!

---

### Step 3: Write Tests

```python
def test_handle_error():
    # Test the error handling path
    result = handle_error(ValueError("test"))
    assert result == {"error": "test"}
```

---

### Step 4: Verify Improvement

```bash
# Run tests again
just test

# Check htmlcov/
# Lines should now be green!
```

---

### Coverage Best Practices

**What to test**:
- ✅ Core business logic (high value)
- ✅ Public APIs (user-facing)
- ✅ Error handling (edge cases)
- ✅ Data transformations (complex logic)

**What NOT to obsess over**:
- ❌ `__repr__` methods (low value)
- ❌ Debug-only code (`if DEBUG:`)
- ❌ External API calls (use mocks instead)
- ❌ Abstract methods (tested via implementations)

**Sweet spot**: 80-85% coverage
- Below 80%: Too many gaps
- Above 95%: Diminishing returns (testing getters/setters)

---

## Configuration Reference

### pytest-cov Command Line

```bash
# Basic coverage
pytest --cov=src

# With HTML report
pytest --cov=src --cov-report=html

# With terminal report
pytest --cov=src --cov-report=term-missing

# Multiple formats
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term

# Fail if below threshold
pytest --cov=src --cov-fail-under=80

# Branch coverage (stricter)
pytest --cov=src --cov-branch
```

---

### Advanced Memory Commands

```bash
# Run tests with coverage (creates htmlcov/)
just test

# Run tests without coverage (faster)
uv run pytest -v

# Coverage only (no test execution)
coverage report

# Erase coverage data
coverage erase
```

---

## htmlcov/ Management

### When It's Created

**Every time you run**:
```bash
just test
pytest --cov=src --cov-report=html
```

**Not created by**:
```bash
pytest  # Without --cov flag
uv run pytest  # Without --cov flag
```

---

### Should You Commit It?

**NO!** ❌

**Why**:
- 11 MB of generated HTML
- Changes on every test run
- Not source code
- Regenerated easily

**Already in `.gitignore`**:
```gitignore
htmlcov/
.coverage
coverage.xml
*.cover
```

---

### Should You Backup It?

**NO!** ❌

**Why**:
- Regenerated on every test run
- Takes 11 MB
- Not valuable for restoration

**Our backup script excludes it**:
```powershell
$exclusions = @(
    "htmlcov",  # Coverage reports (11 MB)
    # ...
)
```

---

### When to Delete It

**Delete when**:
- Cleaning up disk space
- Before archiving project
- Before creating backups

**How to delete**:
```bash
# Manual
Remove-Item -Recurse -Force htmlcov

# Or use our clean command
just clean
```

**Recreate anytime**:
```bash
just test  # Regenerates htmlcov/
```

---

## Understanding Coverage Reports

### Coverage Metrics

**Statement coverage** (what we use):
```python
statements = total_lines - (comments + blank_lines)
coverage = (executed_statements / total_statements) * 100
```

**Branch coverage** (stricter):
```python
branches = if/else, try/except, loops
branch_coverage = (executed_branches / total_branches) * 100
```

**Advanced Memory**: Uses statement coverage (standard approach)

---

### Color Coding

**In htmlcov/ HTML files**:

| Color | Meaning | Action |
|-------|---------|--------|
| 🟢 Green | Line executed | Good! |
| 🔴 Red | Line never executed | Write test! |
| ⚪ Gray | Non-executable | Ignore |
| 🟡 Yellow highlight | Partial branch coverage | Test other branch |

---

### Execution Counts

**Hover over green lines** → See execution count

```
"run 1 time" = Executed once (minimal)
"run 15 times" = Executed 15 times (good)
"run 1190 times" = Executed in every test (very high)
```

**High counts** might indicate:
- Test fixtures that run for every test
- Utility functions called everywhere
- Initialization code

---

## Advanced Memory Coverage

### Coverage Requirements

**In `pyproject.toml`**:
```toml
[tool.coverage.report]
fail_under = 80  # Minimum 80% required
show_missing = true
precision = 2
```

**CI enforcement**:
```yaml
# GitHub Actions fails if coverage < 80%
- run: pytest --cov=src --cov-fail-under=80
```

---

### Excluded Files

**Why exclude files**:
- External integrations (hard to test)
- Background processes (complex setup)
- CLI entry points (tested via integration)
- Migration services (one-time operations)

**Advanced Memory exclusions**:
```toml
omit = [
    "*/external_auth_provider.py",   # OAuth providers
    "*/supabase_auth_provider.py",   # Supabase API
    "*/watch_service.py",             # File watcher
    "*/background_sync.py",           # Background service
    "*/cli/main.py",                  # CLI entry
    "*/services/migration_service.py", # Migrations
]
```

**Result**: These don't count toward coverage % (excluded from denominator)

---

### Excluded Lines

**Pragma comments** tell coverage to ignore specific lines:

```python
def debug_function():  # pragma: no cover
    # This function is never covered
    # (debug only, not tested)
    print("Debug info")
```

**Advanced Memory exclusions**:
```toml
exclude_lines = [
    "pragma: no cover",
    "def __repr__",           # String representations
    "if self.debug:",         # Debug code
    "if settings.DEBUG",      # Debug mode
    "raise AssertionError",   # Should never happen
    "raise NotImplementedError",  # Abstract methods
    "if 0:",                  # Dead code
    "if __name__ == .__main__.:",  # Entry points
    "class .*\\bProtocol\\):",  # Protocol classes
    "@(abc\\.)?abstractmethod",  # Abstract methods
]
```

---

## Improving Coverage

### Finding Gaps

**Step 1**: Open `htmlcov/index.html`

**Step 2**: Sort by coverage (click "Cover" column)

**Step 3**: Click files with <80% coverage

**Step 4**: Identify red lines (untested code)

**Step 5**: Write tests for those lines

---

### Example: Improving a File

**Before** (70% coverage):
```python
def process_data(data):
    if not data:                    # Green (tested)
        return None                 # Green (tested)
    
    processed = transform(data)     # Green (tested)
    
    if validate(processed):         # Green (tested)
        return processed            # Green (tested)
    else:                           
        logger.error("Invalid")     # Red (NOT TESTED!)
        return None                 # Red (NOT TESTED!)
```

**Add test**:
```python
def test_process_data_invalid():
    # Test the error path
    result = process_data(invalid_data)
    assert result is None
```

**After** (100% coverage):
- All lines green!
- Coverage increased from 70% → 100%

---

### Coverage vs. Test Quality

⚠️ **WARNING**: High coverage ≠ good tests!

**Bad test** (100% coverage, useless):
```python
def test_divide():
    divide(10, 2)  # Executes code, doesn't verify result!
```

**Good test** (100% coverage, useful):
```python
def test_divide():
    assert divide(10, 2) == 5  # Verifies correctness
    assert divide(10, 0) == "Error"  # Tests edge case
```

**Lesson**: Aim for high coverage AND meaningful assertions

---

## Troubleshooting

### Issue 1: htmlcov/ Not Generated

**Problem**: Ran pytest but no htmlcov/

**Cause**: Missing `--cov-report=html` flag

**Solution**:
```bash
pytest --cov=src --cov-report=html
```

---

### Issue 2: Coverage Shows 0%

**Problem**: Coverage shows 0% for all files

**Cause**: Wrong `--cov` path

**Solution**:
```bash
# Wrong
pytest --cov=advanced_memory  # No such top-level package

# Right
pytest --cov=src/advanced_memory  # Correct path
```

---

### Issue 3: Some Files Not in Report

**Problem**: Files missing from coverage report

**Cause**: Files in `omit` list (pyproject.toml)

**Solution**: Check `[tool.coverage.report]` section

---

### Issue 4: htmlcov/ Out of Date

**Problem**: Changed code but htmlcov shows old results

**Solution**:
```bash
# Delete old coverage data
coverage erase

# Run tests again
just test
```

---

## Quick Reference

### Commands

```bash
# Generate coverage
just test                                    # Full suite + htmlcov/
pytest --cov=src --cov-report=html          # Explicit

# View coverage
explorer.exe htmlcov\index.html             # Windows
open htmlcov/index.html                     # macOS

# Terminal report only (fast)
pytest --cov=src --cov-report=term-missing

# Delete coverage
just clean                                   # Removes htmlcov/
coverage erase                              # Removes .coverage database
```

---

### File Locations

```
htmlcov/              # HTML reports (11 MB, git-ignored)
.coverage             # Coverage database (binary)
coverage.xml          # XML report (for CI)
```

**All regenerated** by: `pytest --cov`

**All excluded** from: Git, backups

**All cleaned** by: `just clean`

---

## Summary

### What is htmlcov/?

**Technical**: HTML coverage report directory generated by pytest-cov

**Practical**: Visual dashboard showing which code is tested

**Size**: ~11 MB (for our project)

**Created by**: `pytest --cov=src --cov-report=html` or `just test`

**View**: Open `htmlcov/index.html` in browser

---

### Key Points

- ✅ Shows tested (green) vs. untested (red) code
- ✅ Helps identify gaps in test coverage
- ✅ Regenerated on every test run
- ❌ Don't commit to git
- ❌ Don't include in backups
- ✅ Safe to delete anytime
- 🔄 Recreated with `just test`

---

### Advanced Memory Stats

- **Overall coverage**: ~85%
- **Test count**: 1,190 tests
- **Files covered**: 173 Python files
- **Goal**: Maintain 80%+ (industry standard)
- **htmlcov/ size**: 11 MB

---

## See Also

- **pytest-cov docs**: https://pytest-cov.readthedocs.io/
- **coverage.py docs**: https://coverage.readthedocs.io/
- **Our testing guide**: [docs/testing/RUNNING_TESTS_GUIDE.md](../../testing/RUNNING_TESTS_GUIDE.md)
- **Our justfile**: [docs/tools/dev-tools/just.md](./just.md)

---

**Created**: October 17, 2025  
**Purpose**: Explain htmlcov/ and test coverage for Advanced Memory MCP  
**Status**: Complete reference guide

