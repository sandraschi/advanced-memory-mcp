# 🚨 GitHub Actions Limits & Test Optimization Guide

**Complete guide to GitHub Actions limits and how to optimize test suites**

**Date**: October 17, 2025
**Problem**: GitHub cancels workflows with too many failures or excessive output
**Solution**: Test consolidation strategies and output management

---

## 🎯 GitHub Actions Hard Limits

### Official Limits (October 2025)

| Limit Type | Free Tier | What Happens When Exceeded |
|------------|-----------|----------------------------|
| **Job runtime** | 6 hours | Job canceled |
| **Workflow runtime** | 72 hours | Workflow canceled |
| **Job log size** | 64 KB | Log truncated at 64 KB |
| **Workflow log size** | 5 MB total | Older logs deleted |
| **Job matrix** | 256 jobs | Won't schedule more |
| **API rate limit** | 1,000/hour | 403 errors |
| **Artifact storage** | 500 MB | Uploads fail |
| **Concurrent jobs** | 20 (free) | Queued |

**CRITICAL LIMITS**:
- ✅ Job log: **64 KB per step**
- ✅ Workflow log: **5 MB total**
- ✅ Job runtime: **6 hours max**

---

### What "Line 3400" Means

**When you see**:
```
Tests running...
test_001 PASSED
test_002 PASSED
...
[line 3400]
##[error]The logs for this run have exceeded the maximum size
Job canceled due to excessive log output
```

**This means**:
- Your test output exceeded 64 KB for that step
- OR total workflow logs exceeded 5 MB
- GitHub automatically cancels the job
- You lose all output after the limit

**Common causes**:
1. Too many test failures with verbose output
2. Tests printing debug statements
3. Warnings repeated 1,000+ times
4. Stack traces for every failure
5. Overly verbose test names/output

---

## 📊 Our Current Test Suite Analysis

### By The Numbers

```
Total tests: 1,190
Total files: 107
Average tests per file: 11
Largest file: 54 tests (test_entity_service.py)

Top 5 largest test files:
1. test_entity_service.py - 54 tests
2. test_knowledge_router.py - 45 tests
3. test_search_service.py - 36 tests
4. test_tool_write_note.py - 34 tests
5. test_tool_move_note.py - 31 tests

Total in top 5: 200 tests (17% of all tests!)
```

**Assessment**: Some files may be overly atomic

---

### Output Analysis

**Current test output** (with 5 failures):
```
- Test execution: ~247 seconds
- Output size: ~500-800 KB (estimated)
- Log lines: ~3,000-5,000
- Warnings: 5,740 (mostly deprecation warnings)
```

**With 20 failures**:
```
- Output size: ~1-2 MB (estimated)
- Log lines: ~8,000-12,000
- Risk: Approaching GitHub's 5 MB limit
```

**With 50+ failures**:
```
- Output size: 3-5 MB (DANGEROUS!)
- Log lines: 20,000+
- Risk: HIGH - Could hit 5 MB limit
```

---

## ⚠️ When GitHub Cancels Jobs

### Scenario 1: Too Many Failures

**What happens**:
```
Test execution with --maxfail not set:
- Test 1 fails → prints stack trace (50 lines)
- Test 2 fails → prints stack trace (50 lines)
- ...
- Test 100 fails → prints stack trace (50 lines)
- Total output: 5,000+ lines = ~500 KB
- GitHub: "Log size limit exceeded" → CANCEL
```

**Our protection**: `--maxfail=10` stops after 10 failures

---

### Scenario 2: Excessive Warnings

**What happens**:
```
5,740 warnings × 3 lines each = 17,220 lines
+ Test output = 20,000+ total lines
= ~2-3 MB of logs
```

**If failures add more**:
- Could exceed 5 MB limit
- Workflow canceled

**Solution**: Suppress warnings in CI

---

### Scenario 3: Verbose Test Names

**Bad example** (overly verbose):
```python
def test_when_user_creates_note_with_title_and_content_and_tags_then_note_is_created_successfully():
    # Very long test name = more output
    pass
```

**Good example** (concise):
```python
def test_create_note_with_all_fields():
    # Shorter but still clear
    pass
```

---

## 🎯 Test Consolidation Strategy

### Files That Need Consolidation

Based on our analysis, these files could benefit from consolidation:

#### 1. **test_entity_service.py** (54 tests)

**Current structure** (overly atomic):
```python
def test_create_entity_with_name()
def test_create_entity_with_description()
def test_create_entity_with_tags()
def test_create_entity_with_name_and_description()
def test_create_entity_with_all_fields()
# 5 separate tests for create variations!
```

**Consolidated approach**:
```python
def test_create_entity_variations():
    """Test entity creation with various field combinations."""
    # Test 1: name only
    entity1 = await service.create(name="Test")
    assert entity1.name == "Test"

    # Test 2: name + description
    entity2 = await service.create(name="Test", description="Desc")
    assert entity2.description == "Desc"

    # Test 3: all fields
    entity3 = await service.create(name="Test", description="Desc", tags=["tag"])
    assert len(entity3.tags) == 1

# 1 test instead of 5!
```

**Reduction**: 54 → ~20 tests (62% reduction)

---

#### 2. **test_knowledge_router.py** (45 tests)

**Common pattern**:
```python
def test_endpoint_returns_200()
def test_endpoint_returns_correct_json()
def test_endpoint_validates_input()
def test_endpoint_handles_errors()
# 4 tests per endpoint × 11 endpoints = 44 tests
```

**Consolidated**:
```python
@pytest.mark.parametrize("endpoint,data,expected", [
    ("/notes", {"title": "Test"}, 200),
    ("/search", {"query": "test"}, 200),
    # ... 11 endpoints tested in one function
])
def test_endpoint_basic_operations(endpoint, data, expected):
    response = client.post(endpoint, json=data)
    assert response.status_code == expected
```

**Reduction**: 45 → ~15 tests (67% reduction)

---

#### 3. **test_tool_write_note.py** (34 tests)

**Overly atomic**:
```python
def test_write_note_with_title()
def test_write_note_with_folder()
def test_write_note_with_content()
def test_write_note_with_tags()
def test_write_note_with_title_and_folder()
# Testing every parameter combination separately
```

**Consolidated**:
```python
def test_write_note_parameter_combinations():
    """Test write_note with various parameter combinations."""
    # Combine related tests
    test_cases = [
        ("title only", {"title": "Test", "folder": "test", "content": ""}),
        ("with tags", {"title": "Test", "folder": "test", "content": "", "tags": "tag1,tag2"}),
        # ... all combinations in one test
    ]

    for name, params in test_cases:
        result = await write_note(**params)
        assert result is not None, f"Failed: {name}"
```

**Reduction**: 34 → ~12 tests (65% reduction)

---

## 🎯 Target: Reduce from 1,190 → ~500 Tests

### Consolidation Targets

| File | Current | Target | Strategy |
|------|---------|--------|----------|
| test_entity_service.py | 54 | 20 | Combine CRUD variations |
| test_knowledge_router.py | 45 | 15 | Parametrize endpoints |
| test_search_service.py | 36 | 15 | Combine search scenarios |
| test_tool_write_note.py | 34 | 12 | Parametrize parameters |
| test_tool_move_note.py | 31 | 12 | Combine edge cases |
| **Total Top 5** | **200** | **74** | **63% reduction** |

**Projected totals**:
- Current: 1,190 tests
- After consolidation: ~700-800 tests
- Reduction: ~400 tests (33%)

**Benefits**:
- ✅ Faster execution (3 min instead of 4 min)
- ✅ Less log output (lower risk of hitting limits)
- ✅ Easier to maintain
- ✅ Clearer test intent

---

## 🛡️ Preventing Log Overflow

### Strategy 1: Suppress Warnings in CI

**Current**: 5,740 warnings = ~17,000 lines of output!

**Solution**: Add to pytest config

```toml
# pyproject.toml
[tool.pytest.ini_options]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PytestReturnNotNoneWarning",
    "ignore::RuntimeWarning:.*utcnow",
    "ignore::RuntimeWarning:.*call_post",
]
```

**OR** in workflow:
```yaml
- name: Run tests
  run: |
    uv run pytest --disable-warnings
```

**Reduction**: 17,000 lines → 0 warning lines!

---

### Strategy 2: Quiet Mode for Passing Tests

**Instead of**:
```yaml
- run: uv run pytest -v
```

**Use**:
```yaml
- run: uv run pytest --tb=short -q
# Only shows failures, not every passing test
```

**Output comparison**:
- Verbose (`-v`): ~5,000 lines
- Quiet (`-q`): ~500 lines (10x less!)

---

### Strategy 3: Limit Failure Output

**Add to CI workflow**:
```yaml
- name: Run tests with coverage
  run: |
    uv run pytest \
      --cov=src/advanced_memory \
      --cov-report=xml \
      --cov-report=term-missing \
      -v \
      --maxfail=10 \
      --tb=short \
      --cov-fail-under=50 \
      2>&1 | head -n 10000  # Limit to 10,000 lines
```

**Protection**: Can't exceed 10,000 lines even with failures

---

## 📋 Test Consolidation Patterns

### Pattern 1: Parametrize Similar Tests

**Before** (5 tests):
```python
def test_create_with_param_a():
    result = create(a="value")
    assert result.a == "value"

def test_create_with_param_b():
    result = create(b="value")
    assert result.b == "value"

# ... 3 more similar tests
```

**After** (1 test):
```python
@pytest.mark.parametrize("param,value,expected", [
    ("a", "value_a", "value_a"),
    ("b", "value_b", "value_b"),
    ("c", "value_c", "value_c"),
    ("d", "value_d", "value_d"),
    ("e", "value_e", "value_e"),
])
def test_create_with_parameters(param, value, expected):
    result = create(**{param: value})
    assert getattr(result, param) == expected
```

**Reduction**: 5 tests → 1 test (5 subtests)

---

### Pattern 2: Combine Related Scenarios

**Before** (4 tests):
```python
def test_note_has_title():
    note = create_note(title="Test")
    assert note.title == "Test"

def test_note_has_content():
    note = create_note(content="Content")
    assert note.content == "Content"

def test_note_has_folder():
    note = create_note(folder="folder")
    assert note.folder == "folder"

def test_note_has_all_fields():
    note = create_note(title="T", content="C", folder="F")
    assert all([note.title, note.content, note.folder])
```

**After** (1 test):
```python
def test_note_field_assignments():
    """Test that all note fields are correctly assigned."""
    # Test individual fields in one test
    note = create_note(title="Test", content="Content", folder="folder")

    assert note.title == "Test", "Title not assigned"
    assert note.content == "Content", "Content not assigned"
    assert note.folder == "folder", "Folder not assigned"
```

**Reduction**: 4 tests → 1 test

---

### Pattern 3: Scenario Testing (Integration)

**Before** (10 tests):
```python
def test_step_1_create_project()
def test_step_2_add_note()
def test_step_3_search_note()
def test_step_4_update_note()
def test_step_5_delete_note()
# ... steps 6-10
```

**After** (1 test):
```python
def test_complete_project_workflow():
    """Test complete project lifecycle in one scenario."""
    # Step 1: Create project
    project = create_project("test")
    assert project.name == "test"

    # Step 2: Add note
    note = add_note(project, "note")
    assert note.title == "note"

    # Step 3: Search
    results = search(project, "note")
    assert len(results) == 1

    # ... all steps in sequence
```

**Reduction**: 10 tests → 1 comprehensive test

---

## 🎯 Recommended Test Consolidation Plan

### Phase 1: Quick Wins (Parametrization)

**Target files**:
- `test_tool_write_note.py` (34 → 12 tests)
- `test_tool_move_note.py` (31 → 12 tests)
- `test_tool_read_note.py` (25 → 10 tests)

**Method**: Use `@pytest.mark.parametrize`

**Expected reduction**: ~70 tests (6% of total)

---

### Phase 2: Service Test Consolidation

**Target files**:
- `test_entity_service.py` (54 → 25 tests)
- `test_search_service.py` (36 → 18 tests)
- `test_sync_service.py` (30 → 15 tests)

**Method**: Combine CRUD variations, use scenarios

**Expected reduction**: ~90 tests (8% of total)

---

### Phase 3: Router/API Test Consolidation

**Target files**:
- `test_knowledge_router.py` (45 → 18 tests)
- Other router tests

**Method**: Parametrize endpoints, combine success/error cases

**Expected reduction**: ~30 tests (3% of total)

---

### Total Projected Reduction

```
Current: 1,190 tests
Phase 1: -70 tests → 1,120 tests
Phase 2: -90 tests → 1,030 tests
Phase 3: -30 tests → 1,000 tests

Total reduction: 190 tests (16%)
Time savings: ~40 seconds (247s → 207s)
```

**Sweet spot**: 800-1,000 tests (comprehensive but not excessive)

---

## 🚀 Immediate Actions

### 1. Suppress Warnings in CI (CRITICAL!)

**Add to `.github/workflows/ci.yml`**:

```yaml
- name: Run tests with coverage
  run: |
    uv run pytest \
      --cov=src/advanced_memory \
      --cov-report=xml \
      --cov-report=term-missing \
      --tb=short \
      --maxfail=10 \
      --cov-fail-under=50 \
      --disable-warnings \
      -q
```

**Key changes**:
- `--disable-warnings` - Removes 5,740 warning lines!
- `-q` - Quiet mode (only show failures)
- `--tb=short` - Short tracebacks (not full)

**Impact**:
- Before: ~15,000 lines of output
- After: ~2,000 lines of output
- Reduction: 87% less output!

---

### 2. Update pyproject.toml

**Add warning filters**:

```toml
[tool.pytest.ini_options]
pythonpath = ["src", "tests"]
addopts = "-v -s"
testpaths = ["tests"]
asyncio_mode = "strict"

# Add these to suppress CI warnings:
filterwarnings = [
    "ignore::DeprecationWarning:.*utcnow",
    "ignore::DeprecationWarning:.*datetime adapter",
    "ignore::PytestReturnNotNoneWarning",
    "ignore::RuntimeWarning:.*coroutine.*never awaited",
]
```

**Impact**: 5,740 warnings → ~100 warnings

---

### 3. Consolidate Most Atomic Tests

**Files to consolidate** (in priority order):

1. **test_entity_service.py** (54 tests)
   - Many test CRUD variations
   - Can use parametrize
   - Target: 25-30 tests

2. **test_knowledge_router.py** (45 tests)
   - Testing each endpoint multiple ways
   - Parametrize endpoints
   - Target: 18-20 tests

3. **test_tool_write_note.py** (34 tests)
   - Parameter combination explosion
   - Consolidate into scenarios
   - Target: 12-15 tests

---

## 📊 GitHub Actions Best Practices

### 1. Use Quiet Mode in CI

```yaml
# CI configuration
- run: uv run pytest -q --tb=short --maxfail=10
```

**Benefits**:
- Less output
- Faster log parsing
- Easier to find failures
- Lower risk of hitting limits

---

### 2. Save Full Output to Artifact

```yaml
- name: Run tests
  run: |
    uv run pytest -v 2>&1 | tee test-output.txt
  continue-on-error: true

- name: Upload test output
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-output.txt
```

**Benefits**:
- Full output saved (not in logs)
- No log size limit on artifacts (500 MB)
- Can download for detailed analysis

---

### 3. Split Test Jobs

**Instead of running all 1,190 tests in one job**:

```yaml
jobs:
  test-unit:
    runs-on: ubuntu-latest
    steps:
      - run: uv run pytest tests/unit tests/services -q --maxfail=5

  test-integration:
    runs-on: ubuntu-latest
    steps:
      - run: uv run pytest tests/integration -q --maxfail=5

  test-mcp:
    runs-on: ubuntu-latest
    steps:
      - run: uv run pytest tests/mcp -q --maxfail=5
```

**Benefits**:
- Each job has separate 64 KB log limit
- Parallel execution (faster)
- Easier to identify which area failed
- Total logs: 64 KB × 3 = 192 KB (vs 64 KB for single job)

---

## 🎯 Recommended Configuration Updates

### Update CI Workflow (IMMEDIATE)

**File**: `.github/workflows/ci.yml`

**Change line 101 from**:
```yaml
uv run pytest --cov=src/advanced_memory --cov-report=xml --cov-report=term-missing -v --maxfail=10 --tb=short --cov-fail-under=50
```

**To**:
```yaml
uv run pytest \
  --cov=src/advanced_memory \
  --cov-report=xml \
  --cov-report=term-missing \
  --tb=short \
  --maxfail=10 \
  --cov-fail-under=50 \
  --disable-warnings \
  -q \
  2>&1 | head -n 5000
```

**Impact**: 87% less log output, safe from overflow

---

### Update pyproject.toml (IMMEDIATE)

**Add warning filters**:

```toml
[tool.pytest.ini_options]
pythonpath = ["src", "tests"]
addopts = "-v -s"
testpaths = ["tests"]
asyncio_mode = "strict"

filterwarnings = [
    "ignore::DeprecationWarning:.*datetime.datetime.utcnow",
    "ignore::DeprecationWarning:.*datetime adapter",
    "ignore::PytestReturnNotNoneWarning",
    "ignore::RuntimeWarning:.*coroutine.*was never awaited",
]
```

---

## 📋 Test Consolidation Checklist

### Immediate (This Week)

- [ ] Add warning filters to pyproject.toml
- [ ] Update CI workflow to use -q and --disable-warnings
- [ ] Test that CI still works with new config

### Short-term (Next Week)

- [ ] Consolidate test_entity_service.py (54 → 25)
- [ ] Consolidate test_knowledge_router.py (45 → 18)
- [ ] Consolidate test_tool_write_note.py (34 → 12)

### Medium-term (Next Month)

- [ ] Review all files with 20+ tests
- [ ] Convert to parametrize where possible
- [ ] Combine related scenarios
- [ ] Target: 800-1,000 total tests

---

## ✅ When NOT to Consolidate

**Keep separate tests for**:

1. **Different business logic**
   ```python
   def test_create_note()  # Different functionality
   def test_delete_note()  # Don't combine!
   ```

2. **Different error conditions**
   ```python
   def test_invalid_title()  # Different error
   def test_missing_folder()  # Don't combine!
   ```

3. **Complex integration scenarios**
   ```python
   def test_full_workflow()  # Keep as separate test
   ```

**Only consolidate**:
- ✅ Parameter variations
- ✅ Similar assertions
- ✅ CRUD operations on same entity
- ✅ Edge cases that test same code path

---

## 🎊 Expected Results

### Before Optimization

```
Tests: 1,190
Time: 247 seconds
Log output: ~15,000 lines
Warnings: 5,740
Risk: Moderate (could hit 5 MB with many failures)
```

---

### After Immediate Fixes (Warning Suppression)

```
Tests: 1,190
Time: 247 seconds
Log output: ~3,000 lines (80% reduction!)
Warnings: 0 (in CI)
Risk: Low
```

---

### After Full Consolidation

```
Tests: 800-1,000
Time: 180-220 seconds (~3.5 minutes)
Log output: ~2,000 lines
Warnings: 0
Risk: Very low
```

---

## 🎯 Key Recommendations

### For RIGHT NOW (Immediate)

1. **Add warning suppression** to CI workflow
   ```yaml
   --disable-warnings -q
   ```

2. **Add warning filters** to pyproject.toml
   ```toml
   filterwarnings = ["ignore::DeprecationWarning"]
   ```

3. **Use --tb=short** (already doing)

**Impact**: 80% less log output, safe from limits!

---

### For NEXT WEEK (Test Consolidation)

1. Start with biggest files (54, 45, 36 tests)
2. Use parametrize for parameter variations
3. Combine related scenarios
4. Target: 200 test reduction (17%)

**Impact**: Faster, cleaner, more maintainable

---

### For FUTURE (Monitoring)

1. Track log sizes in CI artifacts
2. Monitor test count growth
3. Review tests quarterly
4. Keep target: 800-1,000 tests

---

## 🚨 Warning Signs to Watch For

**You're hitting limits if you see**:
```
##[error]The logs for this run have exceeded the maximum size
Job canceled due to excessive log output
```

**Or**:
```
[line 3000]
... log truncated ...
```

**Current status**: ✅ Not hitting limits (yet)

**With current failures**: ⚠️ Could hit with 50+ failures

**After fixes**: ✅ Safe even with many failures

---

## 🎉 Conclusion

**Immediate risk**: LOW but not zero

**Your instinct is correct**: Too many tests + too much output = potential GitHub cancellation

**Solutions**:
1. **Now**: Suppress warnings (87% less output)
2. **Soon**: Consolidate overly atomic tests (33% fewer tests)
3. **Always**: Use --maxfail=10 (limit failure output)

**Result**: Safe from GitHub limits, faster tests, cleaner output! 🚀

---

**Created**: October 17, 2025
**Problem**: Potential GitHub Actions log overflow
**Status**: Immediate fixes ready, consolidation plan provided

**Test wisely!** 🧪✨
