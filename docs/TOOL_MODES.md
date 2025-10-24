# Tool Modes - Advanced Memory MCP

**Last Updated:** 2025-10-24  
**Status:** Production Feature

---

## 🎯 Overview

Advanced Memory MCP supports two tool exposure modes:

- **PORTMANTEAU MODE (default):** 15 well-organized tools - Clean UX for Claude Desktop
- **FULL MODE (opt-in):** 56 individual tools - Testing and development

**Default mode prevents tool explosion and provides excellent user experience.**

---

## 📊 Tool Modes Comparison

| Aspect | Portmanteau Mode (Default) | Full Mode (Opt-in) |
|--------|---------------------------|-------------------|
| **Tool Count** | 15 tools | 56 tools |
| **User Experience** | ✅ Clean, organized | ⚠️ Overwhelming |
| **Discovery** | ✅ Easy | ❌ Difficult |
| **Use Case** | Production | Testing/Development |
| **Configuration** | Default | Set env var |

---

## 🚀 Portmanteau Mode (Default)

**15 tools organized into logical categories:**

### Meta & Utilities (4 tools)
- `help` - Comprehensive help system
- `canvas` - Obsidian Canvas creation
- `typora_control` - Typora editor integration
- `view_note_rendered` - Rendered Mermaid diagrams

### Core Portmanteau Tools (11 tools)
- `adn_content` - Content CRUD (write, read, edit, move, delete, view)
- `adn_search` - Search across knowledge base and external systems
- `adn_export` - Export operations (pandoc, docsify, html, pdf, archive)
- `adn_import` - Import operations (Obsidian, Joplin, Notion, Evernote)
- `adn_audio` - Voice operations (dictate, speak)
- `adn_knowledge` - Knowledge operations and research orchestration
- `adn_zettelmaker` - Zettelkasten generation and management
- `adn_skills` - Claude Skills CRUD and bidirectional exchange
- `adn_navigation` - Navigate knowledge base (backlinks, context, recent activity)
- `adn_project` - Project management (create, switch, list, status)
- `adn_inbox` - Inbox file drop processing

**Result:** All functionality available through 15 organized tools!

---

## 🔧 Full Mode (Opt-in)

**56 individual tools for testing and development:**

Exposes every individual operation as a separate tool, useful for:
- Unit testing specific operations
- Development and debugging
- Legacy compatibility

**Enable via environment variable:**

```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/advanced-memory-mcp", "run", "advanced-memory", "mcp"],
      "env": {
        "ADVANCED_MEMORY_FULL_TOOLS_MODE": "true"
      }
    }
  }
}
```

---

## 🎯 How It Works

### Implementation

**Conditional imports control MCP registration:**

```python
# FastMCP registers tools when IMPORTED, not from __all__!

if not _FULL_TOOLS_MODE:
    # Import ONLY portmanteau tools
    from .help import help
    from .adn_content import adn_content
    # ... 15 tools total
else:
    # Import ALL tools
    from .help import help
    from .write_note import write_note
    from .read_note import read_note
    # ... 56 tools total
```

### Key Insight

FastMCP registers tools at **import time**, not based on `__all__` exports.

- When Python executes `from .tool import tool_func`
- FastMCP sees the `@mcp.tool` decorator
- Tool is immediately registered with MCP protocol

Therefore, controlling IMPORTS controls what Claude sees!

---

## ✅ Benefits of Portmanteau Mode

### User Experience
- **Clean tool list** - 15 vs 56 tools
- **Easy discovery** - Logical categories
- **Less overwhelming** - Manageable number
- **Better organization** - Related operations grouped

### Technical Benefits
- **Same functionality** - All features still available
- **Better discoverability** - `Literal` types show all operations
- **Easier maintenance** - Fewer tools to document
- **Claude-friendly** - Optimal for AI understanding

### Example

**Before (Full Mode):**
```
User: "What tools are available?"
Claude: Lists 56 tools... scrolls... scrolls...
User: "Uh, too many. What can you do with notes?"
Claude: "write_note, read_note, edit_note, delete_note, move_note..."
```

**After (Portmanteau Mode):**
```
User: "What tools are available?"
Claude: "I have 15 organized tools including adn_content for notes..."
User: "What can adn_content do?"
Claude: "adn_content handles: write, read, edit, move, delete, view, quick, daily"
```

---

## 🔄 Switching Modes

### Default Mode (No Configuration)

Just use Advanced Memory normally - portmanteau mode is automatic.

### Enable Full Mode

Add environment variable to Claude Desktop config:

```json
{
  "env": {
    "ADVANCED_MEMORY_FULL_TOOLS_MODE": "true"
  }
}
```

Restart Claude Desktop.

### Disable Full Mode

Remove the environment variable or set to `"false"`:

```json
{
  "env": {
    "ADVANCED_MEMORY_FULL_TOOLS_MODE": "false"
  }
}
```

Or just remove the `env` section entirely (default is false).

---

## 📚 Related Documentation

- [Portmanteau Pattern](../../../mcp-central-docs/patterns/PORTMANTEAU_CONCEPT.md) - Design pattern explanation
- [Tool Reference](TOOLS_REFERENCE.md) - Complete tool documentation
- [Integration Guide](INTEGRATION_GUIDE.md) - Setup instructions

---

**Recommendation:** Use portmanteau mode (default) for best experience!

**Version:** 1.0  
**Last Updated:** 2025-10-24

