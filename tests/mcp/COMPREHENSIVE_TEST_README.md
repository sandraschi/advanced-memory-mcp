# Comprehensive CRUD and Search Test Suite

## Overview

This test suite provides extensive coverage for:
- **Note CRUD Operations**: Create, Read, Update, Delete
- **Search Functionality**: All parameter combinations and edge cases
- **Parameter Validation**: Tests the fixes for list parameter schema validation
- **Error Handling**: Edge cases and error scenarios

## Test Coverage

### CRUD Operations (13 tests)
1. **Create Basic Note** - Basic note creation with tags
2. **Create Note with Metadata** - Notes with observations and relations
3. **Read Note by Title** - Reading notes using title identifier
4. **Read Note by Permalink** - Reading notes using permalink
5. **Update Note Append** - Appending content to existing notes (verified by reading back)
6. **Update Note Prepend** - Prepending content to existing notes (verified by reading back)
7. **Update Find Replace Simple** - Simple string replacement (e.g., "json" → "jason")
8. **Update Find Replace Not Regex** - Verifies it's simple string matching, not regex patterns
9. **Update Replace Section** - Replacing content within a markdown section (verified by reading back)
10. **Update Tags Add** - Adding tags to notes (verified by reading back)
11. **Update Tags Remove** - Removing tags from notes (verified by reading back)
12. **Update Tags Replace** - Replacing all tags (verified by reading back)
13. **Update Tags Clear** - Clearing all tags (verified by reading back)
14. **Delete Note** - Deleting notes and verifying deletion

### Search Operations (12 tests)
1. **Basic Text Search** - Simple text-based search
2. **Tags Parameter (List Format)** - Tests the fixed list parameter schema validation
3. **Tags Parameter (String Format)** - Tests comma-separated string format
4. **Entity Types Parameter** - Tests entity type filtering with list format
5. **Types Parameter** - Tests content type filtering with list format
6. **Date Range Filter** - Tests after_date and before_date parameters
7. **Search Type Title** - Tests title-only search
8. **Search Type Permalink** - Tests permalink search (the bug we fixed)
9. **Pagination** - Tests page and page_size parameters
10. **Complex Parameter Combination** - Tests multiple parameters together
11. **Results Per Page Alias** - Tests results_per_page compatibility parameter
12. **Empty Query** - Edge case handling

### Edge Cases (3 tests)
1. **Read Nonexistent Note** - Error handling for missing notes
2. **Empty Search Query** - Handling empty queries
3. **Invalid Search Operation** - Error handling for invalid operations

## Running the Tests

### Run All Tests
```powershell
uv run python -m pytest tests/mcp/test_comprehensive_crud_and_search.py -v
```

### Run Specific Test Category
```powershell
# CRUD tests only
uv run python -m pytest tests/mcp/test_comprehensive_crud_and_search.py -v -k "CRUD"

# Search tests only
uv run python -m pytest tests/mcp/test_comprehensive_crud_and_search.py -v -k "Search"

# Edge case tests only
uv run python -m pytest tests/mcp/test_comprehensive_crud_and_search.py -v -k "Edge"
```

### Using the Test Runner Script
```powershell
.\scripts\run_comprehensive_tests.ps1
```

## Test Report

After running the tests, a detailed report is automatically generated at:
- `test_report_crud_search.md`

The report includes:
- **Summary Statistics**: Total tests, pass/fail counts, pass rate
- **Results by Category**: Grouped by CRUD, Search, Edge Cases
- **Detailed Failure Report**: Full error messages and context for failed tests
- **Timestamps**: When each test ran

## Key Features

### Parameter Normalization Testing
The test suite specifically exercises the parameter normalization fixes:
- List format: `tags=["tag1", "tag2"]`
- String format: `tags="tag1,tag2"`
- Single value: `tags="tag1"`

### Search Type Testing
Tests all search types including the fixed permalink search:
- `search_type="text"` (default)
- `search_type="title"`
- `search_type="permalink"` (previously broken, now fixed)

### Comprehensive Parameter Combinations
Tests complex parameter combinations to ensure all parameters work together:
```python
adn_search(
    operation="notes",
    query="test",
    tags=["test", "search"],
    entity_types=["entity"],
    types=["note"],
    after_date="2024-01-01",
    page=1,
    page_size=10,
)
```

## Test Report Format

The generated report is in Markdown format with:
- Executive summary with pass/fail statistics
- Categorized test results
- Detailed failure information with error messages
- JSON-formatted details for debugging

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines:

```yaml
- name: Run Comprehensive Tests
  run: |
    uv run python -m pytest tests/mcp/test_comprehensive_crud_and_search.py -v
    # Report is automatically generated
```

## Edit Operation Details

### Find Replace Operation
The `find_replace` operation uses **simple string replacement**, NOT regex patterns.

**How it works:**
- Uses Python's `str.replace()` method
- Exact string matching only
- Validates expected replacement count
- Replaces ALL occurrences of the exact string

**Example:**
```python
# Replace "json" with "jason" (all occurrences)
adn_content(
    operation="edit",
    identifier="My Note",
    edit_operation="find_replace",
    find_text="json",
    content="jason",
    expected_replacements=2,  # Must match actual count
)
```

**NOT supported:**
- Regex patterns (e.g., `\d+\.\d+\.\d+` won't work)
- Pattern matching (e.g., `version *` won't match "version 1.2.3")
- Case-insensitive replacement (use exact case)

**Supported operations:**
- `append` - Add content to end
- `prepend` - Add content after frontmatter, before body
- `find_replace` - Replace exact string occurrences
- `replace_section` - Replace content under a markdown header

### Tag Operations
All tag operations are verified by reading the note back:
- `add` - Adds tags (preserves existing)
- `remove` - Removes specified tags
- `replace` - Replaces all tags
- `clear` - Removes all tags

## Notes

- Tests use the `app` fixture from `tests/mcp/conftest.py`
- All tests are async and use pytest-asyncio
- Test data is created in `test/crud/` and `test/search/` folders
- The report is generated automatically after all tests complete
- Unicode characters are avoided for Windows compatibility
- **All update operations verify changes by reading the note back** to ensure edits actually worked
