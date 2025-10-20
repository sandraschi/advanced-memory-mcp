# Tool Exposure Control - Portmanteau vs. Full

**Problem**: Some clients (Cursor IDE) have tool limits. We need flexible control over which tools are exposed.

---

## Current Architecture

### 1. MCPB Version (Portmanteau Only)

**Location**: `mcpb/src/advanced_memory/mcp/tools/__init__.py`

**Exports**: **11 tools** (portmanteau only)
- `adn_content`
- `adn_project`
- `adn_zettelmaker`
- `adn_inbox`
- `adn_export`
- `adn_import`
- `adn_search`
- `adn_knowledge`
- `adn_navigation`
- `adn_editor`
- `view_note_rendered`

**Use case**: Cursor IDE, restrictive clients

**Installation**: Drop `.mcpb` file in Claude Desktop

### 2. Standard Package (Full Toolset)

**Location**: `src/advanced_memory/mcp/tools/__init__.py`

**Exports**: **~50+ tools** (portmanteau + individual legacy tools)

**Use case**: Claude Desktop (unrestricted), API usage, full functionality

**Installation**: `pip install advanced-memory`

---

## Problem: Standard Package Flexibility

**User wants**: Ability to use standard package (PyPI) but expose **only portmanteau tools** for restrictive clients.

**Without**: Modifying existing tool files or reducing functionality.

---

## Solution Options

### Option 1: Environment Variable Control ⭐ RECOMMENDED

**Mechanism**: Check `ADVANCED_MEMORY_PORTMANTEAU_ONLY` environment variable

**Implementation**:

```python
# In src/advanced_memory/mcp/tools/__init__.py

import os

# ... imports ...

# Determine which tools to expose
_PORTMANTEAU_ONLY = os.getenv("ADVANCED_MEMORY_PORTMANTEAU_ONLY", "false").lower() in ("true", "1", "yes")

if _PORTMANTEAU_ONLY:
    # Expose ONLY portmanteau tools (11 total)
    __all__ = [
        "view_note_rendered",
        "adn_content",
        "adn_project",
        "adn_zettelmaker",
        "adn_inbox",
        "adn_export",
        "adn_import",
        "adn_search",
        "adn_knowledge",
        "adn_navigation",
        "adn_editor",
    ]
else:
    # Expose ALL tools (default behavior)
    __all__ = [
        # Portmanteau tools
        "adn_content",
        "adn_project",
        # ... etc ...
        # Individual legacy tools
        "write_note",
        "read_note",
        # ... etc ...
    ]
```

**Usage**:

```json
// In claude_desktop_config.json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "uvx",
      "args": ["advanced-memory"],
      "env": {
        "ADVANCED_MEMORY_PORTMANTEAU_ONLY": "true"
      }
    }
  }
}
```

**Pros**:
- ✅ Zero code modification to existing tools
- ✅ User-controlled at runtime
- ✅ Same package for both modes
- ✅ Easy to toggle
- ✅ No functionality loss

**Cons**:
- ⚠️ Requires environment variable documentation

### Option 2: Config File Setting

**Mechanism**: Add `portmanteau_only: true` to `config.json`

**Implementation**:

```python
# In src/advanced_memory/mcp/tools/__init__.py

from advanced_memory.config import AdvancedMemoryConfig

config = AdvancedMemoryConfig.load()

if config.get("portmanteau_only", False):
    __all__ = [...]  # Portmanteau only
else:
    __all__ = [...]  # All tools
```

**Pros**:
- ✅ Persistent configuration
- ✅ User-friendly
- ✅ No environment variables needed

**Cons**:
- ⚠️ Requires config file modification
- ⚠️ More complex to implement

### Option 3: Two Separate Server Commands

**Mechanism**: Provide two entry points in `pyproject.toml`

**Implementation**:

```toml
[project.scripts]
advanced-memory = "advanced_memory.cli:main"
advanced-memory-lite = "advanced_memory.cli:main_portmanteau_only"
```

**Usage**:

```json
// For full tools
"command": "advanced-memory"

// For portmanteau only
"command": "advanced-memory-lite"
```

**Pros**:
- ✅ Clear separation
- ✅ Easy to understand
- ✅ No env vars or config needed

**Cons**:
- ⚠️ Requires two entry points
- ⚠️ Package size (minimal)

### Option 4: Two Separate MCPB Packages

**Current**: One MCPB (portmanteau only)

**Proposed**: Two MCPBs
- `advanced-memory-full.mcpb` - All tools
- `advanced-memory-lite.mcpb` - Portmanteau only (current)

**Pros**:
- ✅ Clear user choice
- ✅ Already have lite version

**Cons**:
- ⚠️ Maintenance overhead (two packages)
- ⚠️ Larger download size

---

## Recommendation

**Use Option 1: Environment Variable** ⭐

**Why**:
1. ✅ Minimal code change
2. ✅ User has full control
3. ✅ Same package for both modes
4. ✅ Easy to document
5. ✅ Consistent with current MCPB approach

**Implementation Plan**:

### Step 1: Update `src/advanced_memory/mcp/tools/__init__.py`

Add environment variable check:

```python
import os

# ... all imports ...

# Determine tool exposure mode
_PORTMANTEAU_ONLY = os.getenv("ADVANCED_MEMORY_PORTMANTEAU_ONLY", "false").lower() in ("true", "1", "yes")

if _PORTMANTEAU_ONLY:
    # PORTMANTEAU MODE: Only 11 consolidated tools
    __all__ = [
        "view_note_rendered",
        "adn_content",
        "adn_project",
        "adn_zettelmaker",
        "adn_inbox",
        "adn_export",
        "adn_import",
        "adn_search",
        "adn_knowledge",
        "adn_navigation",
        "adn_editor",
    ]
else:
    # FULL MODE: All ~50+ tools (default)
    __all__ = [
        # Portmanteau tools
        "adn_content",
        # ... everything ...
    ]
```

### Step 2: Update Documentation

**User Guide**: `docs/user-guide/tool-mode-selection.md`

```markdown
# Choosing Tool Mode

## For Restrictive Clients (Cursor IDE)

Set environment variable:

\```json
{
  "mcpServers": {
    "advanced-memory": {
      "env": {
        "ADVANCED_MEMORY_PORTMANTEAU_ONLY": "true"
      }
    }
  }
}
\```

**Result**: 11 portmanteau tools

## For Unrestricted Clients (Claude Desktop)

Default behavior - no env var needed.

**Result**: ~50+ tools (full functionality)
```

### Step 3: Add to README

```markdown
## Tool Modes

- **Full Mode** (default): ~50+ tools
- **Lite Mode**: 11 portmanteau tools (set `ADVANCED_MEMORY_PORTMANTEAU_ONLY=true`)

Perfect for Cursor IDE and other restrictive clients.
```

---

## Comparison Matrix

| Approach | Code Change | User Control | Maintenance | Clarity |
|----------|-------------|--------------|-------------|---------|
| **Env Var** | Minimal | High | Low | Medium |
| Config File | Medium | High | Medium | High |
| Two Commands | Medium | High | Low | High |
| Two MCPBs | None (already done) | High | High | High |

---

## Current Deployment

**We already have 2 modes**:

1. **MCPB** (`.mcpb` file) → Portmanteau only (11 tools)
2. **PyPI** (`pip install`) → Full toolset (~50+ tools)

**Missing**: Ability for PyPI users to switch to portmanteau mode.

**Solution**: Add environment variable check (10 minutes of work).

---

## Implementation Now?

Want me to implement Option 1 (environment variable)?

**Changes needed**:
1. Modify `src/advanced_memory/mcp/tools/__init__.py` (5 lines)
2. Create `docs/user-guide/tool-mode-selection.md` (documentation)
3. Update README with tool mode information

**Time**: 15 minutes

**Benefit**: PyPI users can choose portmanteau-only mode without switching to MCPB.


