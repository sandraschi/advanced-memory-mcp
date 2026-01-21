# Pre-Release Testing & Quality Assurance Plan

## 🎯 **Release Readiness Assessment**

**Current Version:** 1.2.0 (Research-Driven Skills Ecosystem)
**Last Release Date:** 2025-12-02 (about 1.5 months ago)
**Target Release:** v1.2.1 or v1.3.0 (TBD based on scope)

**Status:** Major new features added, needs comprehensive testing before release

---

## 🧪 **Comprehensive Testing Strategy**

### Phase 1: Code Quality & Linting (2-3 hours)

#### Ruff Quality Checks
```bash
# Run all ruff checks
ruff check src/ tests/ --fix

# Format all code
ruff format src/ tests/

# Check for security issues
ruff check src/ --select S

# Performance checks
ruff check src/ --select PERF

# Complexity analysis
ruff check src/ --select C4
```

**Expected Outcomes:**
- ✅ Zero ruff errors
- ✅ Consistent code formatting
- ✅ No security vulnerabilities
- ✅ Performance optimizations applied
- ✅ Complexity within acceptable limits

#### MyPy Strict Mode Validation
```bash
# Run with strict mode (already enabled)
mypy src/ --strict

# Check for missing imports
mypy src/ --no-error-summary | grep "error: Skipping analyzing"

# Generate type coverage report
mypy src/ --html-report mypy_report
```

**Expected Outcomes:**
- ✅ All type annotations present
- ✅ No type errors in strict mode
- ✅ Full type coverage
- ✅ Type safety verified

### Phase 2: PyPy Compatibility Testing (2 hours)

#### PyPy Installation & Setup
```bash
# Install PyPy
# Windows: Download from https://www.pypy.org/download.html
# Or use conda: conda install pypy

# Create PyPy virtual environment
pypy3 -m venv pypy_env
pypy_env\Scripts\activate  # Windows
# source pypy_env/bin/activate  # Unix

# Install dependencies with PyPy
pip install -e ".[dev]"
```

#### PyPy Test Execution
```bash
# Run full test suite with PyPy
pypy3 -m pytest tests/ -v --tb=short

# Performance comparison (optional)
time python -m pytest tests/unit/test_basic.py
time pypy3 -m pytest tests/unit/test_basic.py

# Memory usage testing
pypy3 -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

**Expected Outcomes:**
- ✅ All tests pass with PyPy
- ✅ No PyPy-specific compatibility issues
- ✅ Performance benchmarks documented
- ✅ Memory usage within acceptable limits

### Phase 3: Research Tools Test Scaffold Enhancement (4-6 hours)

#### Current Test Coverage Analysis
```bash
# Generate coverage report
pytest --cov=src/advanced_memory --cov-report=html --cov-report=term-missing

# Check research tools coverage specifically
pytest --cov=src/advanced_memory/mcp/tools --cov-report=term-missing | grep "adn_"

# Identify missing test files
find tests/ -name "*.py" | wc -l
find src/advanced_memory/mcp/tools/ -name "adn_*.py" | wc -l
```

#### New Research Tools Test Scaffold

**Required Test Files:**
- `tests/mcp/test_adn_web_search.py` - Web search functionality
- `tests/mcp/test_adn_github_research.py` - GitHub repository analysis
- `tests/mcp/test_adn_arxiv_research.py` - Academic paper search
- `tests/mcp/test_adn_tvtropes_research.py` - Narrative patterns
- `tests/mcp/test_adn_document_ingest.py` - Document processing
- `tests/mcp/test_adn_rag.py` - Vector search and retrieval
- `tests/mcp/test_make_skill_advanced.py` - Research-driven skill creation

#### Enhanced Test Patterns

**Research Tools Testing Template:**
```python
import pytest
from unittest.mock import AsyncMock, patch
from advanced_memory.mcp.tools.adn_web_search import adn_web_search


class TestADNWebSearch:
    """Test suite for adn_web_search tool."""

    @pytest.mark.asyncio
    async def test_basic_web_search_duckduckgo(self):
        """Test basic web search with DuckDuckGo."""
        # Mock the web search response
        mock_response = {
            "results": [
                {"title": "Test Result", "url": "https://example.com", "snippet": "Test content"}
            ]
        }

        with patch("advanced_memory.services.research.web_search.duckduckgo_search",
                  return_value=mock_response) as mock_search:

            result = await adn_web_search(
                operation="search",
                query="test query",
                provider="duckduckgo"
            )

            assert "Test Result" in result
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_web_search_with_time_filter(self):
        """Test web search with time-based filtering."""
        # Test implementation
        pass

    @pytest.mark.asyncio
    async def test_web_search_domain_filtering(self):
        """Test web search with domain-specific filtering."""
        # Test implementation
        pass

    @pytest.mark.asyncio
    async def test_web_search_error_handling(self):
        """Test error handling for web search failures."""
        # Test implementation
        pass
```

#### Integration Test Patterns

**Research Pipeline Integration Tests:**
```python
class TestResearchPipeline:
    """Test complete research pipelines."""

    @pytest.mark.asyncio
    async def test_skill_creation_pipeline(self):
        """Test end-to-end skill creation with research."""
        # Mock all research services
        with patch.multiple(
            "advanced_memory.services.research",
            web_search=AsyncMock(return_value={"results": [...]})
            github_search=AsyncMock(return_value={"repositories": [...]})
            arxiv_search=AsyncMock(return_value={"papers": [...]})
        ):
            # Test full pipeline
            result = await make_skill_advanced({
                "topic": "quantum computing",
                "enable_web_search": True,
                "enable_github_search": True,
                "enable_academic_search": True
            })

            assert "quantum computing" in result.lower()
            assert "research" in result.lower()

    @pytest.mark.asyncio
    async def test_multi_source_research_aggregation(self):
        """Test aggregation of multiple research sources."""
        # Test implementation
        pass
```

### Phase 4: Performance & Load Testing (2 hours)

#### Research Tools Performance Benchmarks
```python
import time
import asyncio
from advanced_memory.mcp.tools import adn_web_search, adn_github_research

async def benchmark_research_tools():
    """Benchmark research tool performance."""

    # Web search benchmark
    start_time = time.time()
    result = await adn_web_search("operation", "search", "query", "benchmark test")
    web_search_time = time.time() - start_time

    # GitHub search benchmark
    start_time = time.time()
    result = await adn_github_research("search_code", "python neural network")
    github_search_time = time.time() - start_time

    print(f"Web search: {web_search_time:.2f}s")
    print(f"GitHub search: {github_search_time:.2f}s")

    # Assert performance requirements
    assert web_search_time < 5.0, f"Web search too slow: {web_search_time}s"
    assert github_search_time < 3.0, f"GitHub search too slow: {github_search_time}s"
```

#### Memory Usage Testing
```python
import tracemalloc
from advanced_memory.mcp.tools import adn_document_ingest

async def test_memory_usage():
    """Test memory usage for large document processing."""

    tracemalloc.start()

    # Process a large document
    result = await adn_document_ingest("path/to/large/document.pdf")

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Current memory: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

    # Assert memory limits
    assert peak < 500 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.2f} MB"
```

### Phase 5: Cross-Platform Compatibility (1 hour)

#### Multiple Python Versions
```bash
# Test with Python 3.11, 3.12, 3.13
for version in 3.11 3.12 3.13; do
    echo "Testing Python $version"
    pyenv local $version
    python -m pytest tests/unit/test_basic.py -v
done
```

#### Operating System Compatibility
```bash
# Windows testing
# macOS testing (if available)
# Linux testing (CI/CD handles this)
```

---

## 📊 **Test Coverage Goals**

### Current Status
- **Overall Coverage:** 54%
- **Target Coverage:** 90%+
- **Research Tools:** ~70% (needs improvement)

### Coverage Requirements by Component

| Component | Current | Target | Priority |
|-----------|---------|--------|----------|
| Core MCP Tools | 80% | 95% | High |
| Research Tools | 70% | 90% | High |
| Document Processing | 60% | 85% | Medium |
| RAG System | 50% | 80% | Medium |
| Skill Creation | 75% | 90% | High |
| Import/Export | 65% | 85% | Medium |
| Configuration | 70% | 85% | Low |

---

## 🔧 **Test Infrastructure Improvements**

### Enhanced Test Fixtures
```python
# tests/conftest.py - Enhanced fixtures

@pytest.fixture
async def mock_research_services():
    """Mock all research services for testing."""
    with patch.multiple(
        "advanced_memory.services.research",
        web_search=AsyncMock(),
        github_search=AsyncMock(),
        arxiv_search=AsyncMock(),
        document_processor=AsyncMock(),
        rag_service=AsyncMock()
    ) as mocks:
        yield mocks

@pytest.fixture
async def research_test_data():
    """Provide test data for research tools."""
    return {
        "web_results": [...],
        "github_repos": [...],
        "arxiv_papers": [...],
        "documents": [...],
        "skills": [...]
    }

@pytest.fixture
async def performance_monitor():
    """Monitor performance during tests."""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss

    yield

    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss

    duration = end_time - start_time
    memory_delta = end_memory - start_memory

    print(f"Test duration: {duration:.2f}s")
    print(f"Memory delta: {memory_delta / 1024 / 1024:.2f} MB")
```

### Automated Test Generation
```python
# scripts/generate_test_scaffolds.py

def generate_tool_test_scaffold(tool_name: str) -> str:
    """Generate test scaffold for a new tool."""

    template = f'''
import pytest
from unittest.mock import AsyncMock, patch
from advanced_memory.mcp.tools.{tool_name} import {tool_name}


class Test{tool_name.title()}:
    """Test suite for {tool_name} tool."""

    @pytest.mark.asyncio
    async def test_basic_functionality(self):
        """Test basic {tool_name} functionality."""
        # TODO: Implement basic test
        pass

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in {tool_name}."""
        # TODO: Implement error handling test
        pass

    @pytest.mark.asyncio
    async def test_edge_cases(self):
        """Test edge cases for {tool_name}."""
        # TODO: Implement edge case tests
        pass
'''

    return template
```

---

## 📈 **Release Readiness Checklist**

### Pre-Release Quality Gates

#### ✅ Code Quality
- [ ] Ruff check passes with zero errors
- [ ] Ruff format applied consistently
- [ ] MyPy strict mode passes
- [ ] No security vulnerabilities (bandit/safety)
- [ ] Complexity metrics within limits

#### ✅ Testing
- [ ] All existing tests pass (98%+ rate)
- [ ] New research tools have comprehensive tests
- [ ] PyPy compatibility verified
- [ ] Cross-platform testing completed
- [ ] Performance benchmarks documented

#### ✅ Documentation
- [ ] CHANGELOG.md updated with new features
- [ ] README.md reflects current capabilities
- [ ] API documentation complete
- [ ] Migration guides for breaking changes (if any)

#### ✅ Compatibility
- [ ] Python 3.11, 3.12, 3.13 support verified
- [ ] PyPy compatibility confirmed
- [ ] Windows/macOS/Linux compatibility tested
- [ ] Dependency versions pinned appropriately

### Release Decision Criteria

#### Patch Release (v1.2.1) - If:
- Only bug fixes and minor improvements
- No breaking changes
- Backward compatibility maintained
- Low risk changes

#### Minor Release (v1.3.0) - If:
- New research tools added
- Major testing improvements
- Performance enhancements
- API improvements without breaking changes

#### Major Release (v2.0.0) - If:
- Breaking API changes
- Major architectural changes
- Significant new capabilities

---

## 🚀 **Release Execution Plan**

### Phase 1: Final Testing (1-2 hours)
```bash
# Run comprehensive test suite
pytest tests/ --cov=src/advanced_memory --cov-report=html -x

# PyPy testing
pypy3 -m pytest tests/unit/ -x

# Ruff final check
ruff check src/ tests/
ruff format src/ tests/
```

### Phase 2: Version Bump & Documentation (30 minutes)
```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
# Update README.md badges
# Commit changes
```

### Phase 3: Build & Test Distribution (30 minutes)
```bash
# Build package
python -m build

# Test installation
pip install dist/advanced_memory-*.whl --force-reinstall

# Test basic functionality
advanced-memory --version
advanced-memory status
```

### Phase 4: PyPI Publication (15 minutes)
```bash
# Upload to PyPI
twine upload dist/*

# Verify publication
pip install advanced-memory --upgrade
```

---

## 📊 **Success Metrics**

### Quality Metrics
- **Test Pass Rate:** 98%+ (current: 98%)
- **Code Coverage:** 85%+ (current: 54% → needs improvement)
- **Ruff Score:** 10/10 (zero errors)
- **MyPy Strict:** ✅ All checks pass
- **PyPy Compatible:** ✅ All tests pass

### Performance Metrics
- **Test Execution Time:** < 5 minutes for full suite
- **Memory Usage:** < 500MB peak for large document processing
- **API Response Time:** < 3 seconds for typical queries
- **Concurrent Users:** Support for 10+ simultaneous research operations

### Compatibility Metrics
- **Python Versions:** 3.11, 3.12, 3.13 ✅
- **Operating Systems:** Windows, macOS, Linux ✅
- **Python Implementations:** CPython, PyPy ✅
- **MCP Clients:** Claude Desktop, Cursor, Windsurf ✅

---

## 🎯 **Timeline & Milestones**

### Week 1: Quality Assurance (Jan 20-26, 2026)
- **Jan 20:** Ruff and MyPy improvements
- **Jan 21:** PyPy compatibility testing
- **Jan 22:** Research tools test scaffold enhancement
- **Jan 23:** Performance and load testing
- **Jan 24:** Cross-platform compatibility verification
- **Jan 25-26:** Integration testing and bug fixes

### Week 2: Release Preparation (Jan 27-Feb 2, 2026)
- **Jan 27:** Final testing and bug fixes
- **Jan 28:** Documentation updates and version bump
- **Jan 29:** Build testing and distribution verification
- **Jan 30:** PyPI publication and post-release validation
- **Jan 31-Feb 2:** Community announcement and feedback collection

**Target Release Date:** End of Week 2 (January 31 - February 2, 2026)
**Release Version:** v1.3.0 (based on new research capabilities and testing improvements)
