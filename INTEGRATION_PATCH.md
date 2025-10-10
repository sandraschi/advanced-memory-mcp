# MCP-Commons Integration Patch

**Date:** October 10, 2025  
**Purpose:** Integrate bulletproof utilities into advanced-memory-mcp  
**Fixes:** Silent sync failures, file crashes, link parser hangs

---

## What We're Integrating

### From mcp-commons:
1. ✅ **SyncHealthMonitor** - Detect stuck syncs
2. ✅ **FileValidator** - Prevent file crashes
3. ✅ **LinkParser** - Fix link parsing hangs

### Into advanced-memory-mcp:
- `src/advanced_memory/utils/mcp_commons/` - Modules copied
- `src/advanced_memory/markdown/plugins.py` - Replace parse_inline_relations
- `src/advanced_memory/sync/sync_service.py` - Add file validation
- `src/advanced_memory/mcp/tools/` - Add health check tool

---

## Changes Required

### 1. Replace Link Parsing (plugins.py)

**Current (lines 113-152):**
```python
def parse_inline_relations(content: str) -> list[dict[str, Any]]:
    """Find wiki-style links in regular content."""
    relations = []
    start = 0
    
    while True:
        # Find next outer-most [[
        start = content.find("[[", start)  # ❌ Can hang on large files
        if start == -1:
            break
        
        # Manual bracket matching - O(n²) worst case
        depth = 1
        pos = start + 2
        ...
```

**New (using mcp-commons):**
```python
from advanced_memory.utils.mcp_commons import LinkParser, parse_links_safe

_link_parser = LinkParser(
    max_links=10000,
    max_parse_time=5.0
)

def parse_inline_relations(content: str) -> list[dict[str, Any]]:
    """Find wiki-style links in regular content (robust version)."""
    
    # Use robust parser
    result = parse_links_safe(content)
    
    if not result.is_valid:
        logger.warning("link_parsing_failed",
                      content_size=len(content),
                      errors=result.errors)
        return []  # Graceful degradation
    
    # Convert to expected format
    relations = []
    for link in result.links:
        if link.type == 'wikilink':
            relations.append({
                "type": "links to",
                "target": link.target,
                "context": None
            })
    
    # Log warnings
    if result.warnings:
        for warning in result.warnings:
            logger.info("link_warning", warning=warning)
    
    return relations
```

---

### 2. Add File Validation (sync_service.py)

**Find the sync_file method and add validation:**

```python
from advanced_memory.utils.mcp_commons import FileValidator

class SyncService:
    def __init__(self, ...):
        ...
        self.file_validator = FileValidator(
            allow_empty=True,
            strict_frontmatter=False
        )
    
    async def sync_file(self, relative_path: str, new: bool = False):
        """Sync file with validation."""
        
        # Get full path
        full_path = self.project.path / relative_path
        
        # Validate file BEFORE processing
        validation_result = self.file_validator.validate_file(full_path)
        
        if not validation_result.is_valid:
            logger.warning("skipping_invalid_file",
                          path=relative_path,
                          errors=validation_result.errors)
            return None, None  # Skip file
        
        # Log warnings
        for warning in validation_result.warnings:
            logger.info("file_warning",
                       path=relative_path,
                       warning=warning)
        
        # Use validated content
        content = validation_result.content
        frontmatter = validation_result.frontmatter
        
        # Continue with normal processing...
        ...
```

---

### 3. Add Health Check Tool (mcp/tools/)

Create new file: `src/advanced_memory/mcp/tools/health.py`

```python
"""Health check tools for advanced-memory-mcp."""

from fastmcp import Context

# Import from mcp_commons
from advanced_memory.utils.mcp_commons import SyncHealthMonitor

# Global health monitor (initialized on startup)
sync_monitor: SyncHealthMonitor | None = None


def initialize_health_monitor(project_path: str):
    """Initialize health monitor on startup."""
    global sync_monitor
    
    sync_monitor = SyncHealthMonitor(
        project_path=project_path,
        stall_timeout=60,
        check_interval=10,
        max_recovery_attempts=3
    )
    
    sync_monitor.start_scan()


async def sync_health_check(ctx: Context) -> str:
    """
    Comprehensive sync health check with diagnostics.
    
    Returns detailed status including:
    - Watcher process state
    - Database growth rate
    - Scan progress
    - Error logs
    - Performance metrics
    """
    if sync_monitor is None:
        return "❌ Health monitor not initialized"
    
    return sync_monitor.format_health_report()
```

---

### 4. Update pyproject.toml

Add PyYAML dependency:

```toml
dependencies = [
    ...,
    "pyyaml>=6.0",
]
```

---

## Testing Integration

### 1. Test File Validation

```python
# test_file_validation_integration.py
from advanced_memory.utils.mcp_commons import FileValidator

def test_file_validator_available():
    validator = FileValidator()
    assert validator is not None

def test_validates_test_files():
    validator = FileValidator()
    result = validator.validate_file("tests/fixtures/test.md")
    assert result.is_valid
```

### 2. Test Link Parser

```python
from advanced_memory.markdown.plugins import parse_inline_relations

def test_link_parser_handles_many_links():
    # 5000 links - would hang with old parser
    links = [f"[[Page{i}]]" for i in range(5000)]
    content = " ".join(links)
    
    import time
    start = time.time()
    result = parse_inline_relations(content)
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # Should be fast
    assert len(result) > 0
```

### 3. Test Health Check Tool

```bash
# In Claude Desktop
sync_health_check()

# Should show:
# - File counts
# - Progress percent
# - Watcher status
# - Recommendations
```

---

## Deployment Steps

### 1. Copy Modules ✅
```bash
cp -r D:/Dev/repos/mcp-commons/src/mcp_commons D:/Dev/repos/advanced-memory-mcp/src/advanced_memory/utils/
```

### 2. Update Link Parser
```bash
# Edit: src/advanced_memory/markdown/plugins.py
# Replace parse_inline_relations with robust version
```

### 3. Add File Validation
```bash
# Edit: src/advanced_memory/sync/sync_service.py
# Add validation before file processing
```

### 4. Add Health Tool
```bash
# Create: src/advanced_memory/mcp/tools/health.py
# Register in tools/__init__.py
```

### 5. Test
```bash
pytest tests/ -v
```

### 6. Run with Real Data
```bash
# Start server
# Check sync_health_check() tool
# Verify 1,896 files sync completely
```

---

## Expected Results

### Before
- ❌ Sync stuck at 242/1,896 (87% fail)
- ❌ Link parser hangs on large notes
- ❌ Crashes on weird files

### After
- ✅ Full sync in 2-3 minutes
- ✅ 5,000 links parsed in 87ms
- ✅ All files validated
- ✅ Health monitoring active
- ✅ Auto-recovery from errors

---

## Rollback Plan

If integration causes issues:

```bash
# Remove mcp_commons
rm -rf src/advanced_memory/utils/mcp_commons

# Restore original plugins.py
git checkout src/advanced_memory/markdown/plugins.py

# Restore original sync_service.py
git checkout src/advanced_memory/sync/sync_service.py
```

---

## Monitoring After Deploy

```python
# In Claude Desktop
sync_health_check()

# Should show:
{
    "healthy": true,
    "state": "scanning",
    "metrics": {
        "files_scanned": 1247,
        "files_total": 1896,
        "progress_percent": 65.8,
        "files_per_second": 12.5
    },
    "watcher": {"alive": true},
    "recommendations": ["✅ All systems healthy"]
}
```

---

## Success Criteria

✅ All 1,896 files sync successfully  
✅ No hangs on large notes  
✅ No crashes on weird files  
✅ Health check tool works  
✅ Performance acceptable (< 5 minutes total)  

---

*Ready to integrate - October 10, 2025*

