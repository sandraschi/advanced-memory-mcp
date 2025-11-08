# Portmanteau Parameter Signature Mismatch Audit

**Date:** 2025-10-30  
**Status:** Critical Design Issue  
**Severity:** High - Breaking API Consistency

## Executive Summary

Portmanteau tools have **inconsistent parameter signatures** compared to their standalone counterparts. This violates the principle that portmanteau tools should be functionally equivalent drop-in replacements.

## Critical Findings

### 1. ✅ CONFIRMED: `write_note` vs `adn_content(operation="write")`

**Standalone:** `write_note.py`
```python
async def write_note(
    title: str,        # Required
    content: str,      # Required
    folder: str,       # Required
    tags=None,
    entity_type: str = "note",
    project: str | None = None,
) -> str
```

**Portmanteau:** `content_manager.py`
```python
async def adn_content(
    operation: Literal[...],
    identifier: str | None = None,  # ❌ DIFFERENT NAME
    content: str | None = None,     # ❌ NOW OPTIONAL
    folder: str | None = None,      # ❌ NOW OPTIONAL
    tags: TagType | None = None,
    entity_type: str = "note",
    page: int = 1,                  # Extra - not in standalone
    page_size: int = 10,            # Extra - not in standalone
    project: str | None = None
) -> str
```

**Issues:**
- ❌ Parameter name mismatch: `title` → `identifier`
- ❌ Required → Optional parameters (less safe)
- ❌ Extra parameters (`page`, `page_size`) that don't apply to write

### 2. ✅ VERIFIED: `read_note` vs `adn_content(operation="read")`

**Standalone:** `read_note.py`
```python
async def read_note(
    identifier: str,           # Required
    page: int = 1,
    page_size: int = 10,
    project: str | None = None
) -> str
```

**Portmanteau:** `content_manager.py`
```python
async def adn_content(
    operation: Literal["read", ...],
    identifier: str | None = None,  # ❌ NOW OPTIONAL
    ...
    page: int = 1,
    page_size: int = 10,
    ...
) -> str
```

**Issues:**
- ✅ Parameter names match (good!)
- ❌ Required → Optional (less safe)
- Uses same `identifier` name - consistent with read_note

### 3. ✅ CONFIRMED: `search_notes` vs `adn_search(operation="notes")`

**Standalone:** `search.py`
```python
async def search_notes(
    query: str,
    page: int = 1,
    results_per_page: int = 10,   # ❌ DIFFERENT NAME
    search_type: str = "text",
    types: list[str] | None = None,
    entity_types: list[str] | None = None,
    after_date: str | None = None,
    before_date: str | None = None,
    tags: list[str] | None = None,
    projects: str | None = None
) -> SearchResponse | str
```

**Portmanteau:** `adn_search.py`
```python
async def adn_search(
    operation: Literal["notes", ...],
    query: str,
    ...
    page: int = 1,
    page_size: int = 10,           # ❌ DIFFERENT NAME
    ...
    types: list[str] | None = None,
    entity_types: list[str] | None = None,
    after_date: str | None = None,
    before_date: str | None = None,
    tags: list[str] | None = None,
    ...
) -> str
```

**Issues:**
- ❌ Parameter name mismatch: `results_per_page` → `page_size`
- ✅ Most other parameters match

## Patterns Identified

### Common Issues Across Portmanteau Tools

1. **Parameter Naming Inconsistency**
   - `title` → `identifier` (adn_content write)
   - `results_per_page` → `page_size` (adn_search)

2. **Required → Optional Degradation**
   - Standalone tools: `title: str` (required)
   - Portmanteau: `identifier: str | None = None` (optional)
   - Makes APIs less safe and type-checkable

3. **Extra Parameters**
   - `adn_content` has `page` and `page_size` for all operations
   - These only make sense for read/list operations
   - Confusing for write/edit operations

4. **Operation-Specific Validation**
   - Portmanteau validates parameters manually after routing
   - Standalone tools validate at function signature level
   - Duplicates error checking logic

## Impact Analysis

### User-Facing Impact

**Scenario:** User wants to switch between tools
```python
# Using standalone tool
write_note(title="My Note", content="# Hello", folder="notes")

# Try to use portmanteau equivalent - BROKEN
adn_content(operation="write", title="My Note", ...)  # ❌ Doesn't work - 'title' not accepted
adn_content(operation="write", identifier="My Note", ...)  # ✅ Works but inconsistent
```

**Breaking changes:**
- Documentation examples don't match
- Parameter names differ for same concept
- Type safety reduced (optional vs required)

### Developer Impact

**Internal inconsistency:**
- Can't easily swap between standalone and portmanteau
- Must remember different parameter names
- Tests can't easily validate equivalence

## Affected Tools

| Portmanteau | Standalone Counterpart | Status | Mismatch Type |
|-------------|----------------------|--------|---------------|
| `adn_content` (write) | `write_note` | 🔴 Critical | Name + Required |
| `adn_content` (read) | `read_note` | 🟡 Minor | Required only |
| `adn_search` | `search_notes` | 🟡 Minor | Name only |
| `adn_navigation` | `recent_activity` | ⚪ Unknown | Needs audit |
| `adn_knowledge` | Various | ⚪ Unknown | Needs audit |
| `adn_skills` | Various | ⚪ Unknown | Needs audit |
| `adn_export` | Various | ⚪ Unknown | Needs audit |
| `adn_import` | Various | ⚪ Unknown | Needs audit |

## Recommended Solutions

### Option A: Parameter Aliasing (Quick Fix)

Add backward compatibility by accepting both parameter names:

```python
async def adn_content(
    operation: Literal[...],
    identifier: str | None = None,
    title: str | None = None,  # NEW: Alias for identifier
    ...
):
    # Map title to identifier for compatibility
    if title and not identifier:
        identifier = title
    
    # Continue with normal logic
    if operation == "write" and not identifier:
        return "# Error\n\nWrite operation requires: title or identifier parameter"
```

**Pros:**
- ✅ Backward compatible
- ✅ Quick to implement
- ✅ Low risk

**Cons:**
- ❌ Still inconsistent conceptually
- ❌ Band-aid solution
- ❌ Doesn't address optional vs required

### Option B: Unified Parameter Schema (Correct Fix)

Standardize all tools to use same parameter names:

```python
# Decision: Use "title" everywhere, not "identifier"
# Update read_note.py to match write_note.py
async def read_note(
    title: str,  # Changed from identifier
    ...
) -> str
```

**Pros:**
- ✅ Consistent across all tools
- ✅ Clearer API
- ✅ Proper fix

**Cons:**
- ❌ Breaking change for read_note
- ❌ Larger refactor required
- ❌ Need migration guide

### Option C: Document Divergence (Avoid)

Accept the difference and document extensively.

**Pros:**
- ✅ No code changes

**Cons:**
- ❌ Confusing for users
- ❌ Ongoing maintenance burden
- ❌ Violates API design principles

## Immediate Actions

1. ✅ **Document all mismatches** (this report)
2. 🔲 **Audit remaining portmanteau tools**
3. 🔲 **Create GitHub issue** with full findings
4. 🔲 **Decide on fix strategy** (Option A/B/C)
5. 🔲 **Implement fix** for high-priority mismatches
6. 🔲 **Add validation tests** ensuring portmanteau ≡ standalone
7. 🔲 **Update documentation** with correct examples

## Priority Matrix

| Mismatch | User Impact | Frequency | Priority |
|----------|-------------|-----------|----------|
| `title` vs `identifier` (write) | High | High | P0 - Fix immediately |
| `results_per_page` vs `page_size` | Medium | Medium | P1 - Fix soon |
| Required → Optional | Medium | High | P1 - Fix soon |
| Extra parameters | Low | Low | P2 - Nice to have |

## Conclusion

This audit confirms a **critical design flaw** in portmanteau tool implementation. The parameter signature mismatches create:
- ❌ User confusion
- ❌ Breaking changes for tool migration
- ❌ Reduced type safety
- ❌ Duplicated validation logic

**Recommendation:** Implement Option A (aliasing) as immediate fix, then Option B (unification) in next major version.

---

**Next Steps:**
1. Audit remaining tools (adn_navigation, adn_knowledge, etc.)
2. Create comprehensive fix plan
3. Implement parameter aliasing for P0 issues
4. Add integration tests

