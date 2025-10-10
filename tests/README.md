# Advanced Memory Test Suite

This directory contains all tests for the Advanced Memory project, organized by test type and module.

## Directory Structure

### 📦 Root Test Files
Core test files that don't fit into specific module categories:
- `test_all_portmanteau_tools.py` - Comprehensive portmanteau tools testing
- `test_ci_basic.py` - Basic CI pipeline tests
- `test_config.py` - Configuration management tests
- `test_db_migration_deduplication.py` - Database migration tests
- `test_fastmcp.py` - FastMCP functionality tests
- `test_search.py` - Search functionality tests
- `conftest.py` - Shared pytest configuration and fixtures
- `__init__.py` - Package initialization

### 🔧 Module Tests
Tests organized by application module:

- **api/** (16 tests) - FastAPI endpoint tests
- **cli/** (11 tests) - Command-line interface tests
- **importers/** (2 tests) - Import functionality tests (Claude, ChatGPT, etc.)
- **markdown/** (8 tests) - Markdown parsing and processing tests
- **mcp/** (21 tests) - Model Context Protocol server tests
- **repository/** (8 tests) - Data access layer tests
- **schemas/** (4 tests) - Pydantic schema validation tests
- **services/** (10 tests) - Business logic layer tests
- **sync/** (5 tests) - File synchronization tests
- **utils/** (6 tests) - Utility function tests

### 🔄 Integration Tests
End-to-end integration tests for complex workflows:

- **integration/** (12 tests)
  - `conftest.py` - Integration test configuration
  - `mcp/` - MCP tool integration tests
    - `test_build_context_validation.py`
    - `test_delete_note_integration.py`
    - `test_edit_note_integration.py`
    - `test_list_directory_integration.py`
    - `test_move_note_integration.py`
    - `test_project_management_integration.py`
    - `test_project_state_sync_integration.py`
    - `test_read_content_integration.py`
    - `test_read_note_integration.py`
    - `test_search_integration.py`
    - `test_write_note_integration.py`

### 📂 Test Fixtures
Test data and sample files used across test suites:

- **fixtures/**
  - `test_joplin_export/` - Sample Joplin export data for import testing
  - `test_obsidian_vault/` - Sample Obsidian vault for import testing
  - `test_canvas.canvas` - Sample Obsidian canvas file for testing

## Running Tests

### All Tests
```bash
uv run pytest -p pytest_mock -v
```
or
```bash
just test
```

### Specific Test File
```bash
pytest tests/path/to/test_file.py::test_function_name
```

### Module Tests Only
```bash
pytest tests/api/  # API tests only
pytest tests/mcp/  # MCP tests only
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### With Coverage
```bash
pytest --cov=advanced_memory --cov-report=html
```

## Test Configuration

- **Database**: Tests use in-memory SQLite for isolation
- **File System**: Each test gets a temporary directory
- **Async Support**: Tests use pytest-asyncio for async code
- **Fixtures**: Shared fixtures in `conftest.py` files
- **Mocking**: Avoid mocks when possible; use real in-memory DB

## Test Development Guidelines

1. **Isolation**: Each test should be independent
2. **No Mocks**: Prefer real in-memory DB over mocks
3. **Fixtures**: Use pytest fixtures for shared setup
4. **Async**: Use `@pytest.mark.asyncio` for async tests
5. **Coverage**: Maintain high test coverage (aim for 80%+)
6. **Naming**: Use descriptive test names (`test_<what>_<when>_<expected>`)

## Test Types

- **Unit Tests**: Test individual functions/methods in isolation
- **Integration Tests**: Test multiple components working together
- **API Tests**: Test HTTP endpoints and request/response handling
- **Service Tests**: Test business logic and workflows
- **Repository Tests**: Test data access patterns

## Continuous Integration

Tests run automatically on:
- Every push to `main` branch
- All pull requests
- Release tags

See `.github/workflows/` for CI configuration.

