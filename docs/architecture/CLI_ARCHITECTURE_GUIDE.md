# CLI Architecture Guide - Advanced Memory's Command-Line Interface

**Last Updated**: October 17, 2025
**Status**: Comprehensive CLI with 13 command groups

---

## Overview

Advanced Memory includes a **full-featured CLI** in addition to the MCP server. This is **NOT typical** for MCP servers - most provide only the server component.

**Why we have a CLI**:
- Inherited from Basic Memory MCP (original project)
- Direct file/database management
- Automation and scripting
- Human-friendly workflows
- Faster than MCP tools (3-15x for batch operations)

---

## Do All MCP Servers Have CLIs?

### Short Answer: NO

**Typical MCP Server**:
```
simple-mcp-server/
├── src/
│   └── index.ts  # or server.py
├── package.json
└── README.md
```

**Just the server** - no CLI component.

**Why**: Most MCP servers are:
- Single-purpose (e.g., "filesystem access")
- Stateless (no database)
- Simple (10-50 lines of code)
- Designed only for AI interaction

---

**Advanced Memory** (complex):
```
advanced-memory-mcp/
├── src/advanced_memory/
│   ├── cli/           # Full CLI ✅
│   ├── api/           # REST API ✅
│   ├── mcp/           # MCP Server ✅
│   ├── models/        # Database models ✅
│   ├── services/      # Business logic ✅
│   └── sync/          # File sync ✅
├── pyproject.toml
└── ...
```

**Full application** - CLI + MCP + API + Database

---

### Comparison with Other MCP Servers

| MCP Server Type | Has CLI? | Has Database? | Complexity |
|-----------------|----------|---------------|------------|
| **Typical MCP** | ❌ No | ❌ No | Low (50-200 lines) |
| **Filesystem MCP** | ❌ No | ❌ No | Low |
| **API Wrapper MCP** | ❌ No | ❌ No | Medium |
| **Basic Memory** | ✅ Yes | ✅ Yes (SQLite) | High |
| **Advanced Memory** | ✅ Yes | ✅ Yes (SQLite + FTS) | Very High |

**We're an outlier** - most MCP servers are thin wrappers, we're a full application.

---

## Our CLI Architecture

### Directory Structure

```
src/advanced_memory/cli/
├── __init__.py
├── app.py                      # Main Typer app, callback
├── main.py                     # Entry point (registered as script)
├── commands/                   # All subcommands
│   ├── __init__.py
│   ├── convert.py             # Document conversion (NEW!)
│   ├── db.py                  # Database management
│   ├── import_chatgpt.py      # ChatGPT import
│   ├── import_claude_conversations.py
│   ├── import_claude_projects.py
│   ├── import_memory_json.py
│   ├── mcp.py                 # Run MCP server
│   ├── onboard.py             # Zettelkasten onboarding
│   ├── project.py             # Project management
│   ├── status.py              # Sync status
│   ├── sync.py                # File sync
│   └── tool.py                # MCP tools from CLI
└── zettelkasten_content/      # Template data (being phased out)
    ├── creative.py
    ├── developer.py
    ├── researcher.py
    └── ... (10 category files)
```

---

## Command Groups (13 Total)

### 1. Core Operations

**`advanced-memory sync`**
- Sync markdown files with database
- Update search index
- Detect changes
- Watch mode (`--watch`)

**`advanced-memory status`**
- Show sync status
- Files added/modified/deleted
- Database vs filesystem comparison
- Tree view of changes

**`advanced-memory validate`**
- Validate YAML frontmatter
- Check markdown structure
- Verify WikiLinks
- Report errors

**`advanced-memory reset`**
- Drop all database tables
- Recreate from scratch
- Nuclear option for corruption

---

### 2. MCP Server

**`advanced-memory mcp`**
- Run MCP server
- stdio or SSE transport
- Connect Claude Desktop or other AI clients
- Background mode (`--background`)

**Purpose**: Start the MCP server that AI agents connect to

---

### 3. Project Management

**`advanced-memory project list`**
- List all configured projects
- Show active/default status
- Display paths

**`advanced-memory project add <name> <path>`**
- Create new project
- Configure directory
- Initialize database

**`advanced-memory project remove <name>`**
- Delete project configuration
- Optionally remove database

**`advanced-memory project default <name>`**
- Set default project
- Update config.toml

**`advanced-memory project sync-config`**
- Synchronize config with database
- Detect discrepancies

**`advanced-memory project info <name>`**
- Show project details
- Statistics, paths, status

---

### 4. Import Commands

**`advanced-memory import claude conversations`**
- Import Claude conversation exports
- Parse JSON format
- Create notes from messages

**`advanced-memory import claude projects`**
- Import Claude project exports
- Preserve structure

**`advanced-memory import chatgpt`**
- Import ChatGPT conversation exports
- Parse conversations.json
- Extract messages to notes

**`advanced-memory import memory-json`**
- Import from memory.json format
- Legacy format support

---

### 5. Document Conversion (NEW!)

**`advanced-memory convert file <file>`**
- Convert .docx, .html, .pdf, .txt to markdown
- Auto-detect format
- Output to specified path
- Uses Pandoc/pypdf

**`advanced-memory convert info`**
- Show supported formats
- Check dependencies (Pandoc, pypdf)
- Installation instructions

---

### 6. Onboarding

**`advanced-memory onboard wizard`**
- Interactive onboarding
- Select interests
- Generate starter zettelkasten
- Create 30-100 interconnected notes

**`advanced-memory onboard quick <category> <topic>`**
- Quick onboarding (no wizard)
- Generate specific topic
- Faster than wizard

---

### 7. MCP Tools Access

**`advanced-memory tool <tool-name>`**
- Access MCP tools from CLI
- Bridge between CLI and MCP
- All MCP tools available

**Available tool commands**:
- `write-note` - Create notes
- `read-note` - Read notes
- `build-context` - Build conversation context
- `recent-activity` - Show recent changes
- `search-notes` - Full-text search
- `continue-conversation` - Continue previous conversation

**Purpose**: Use MCP tools without running MCP server (direct invocation)

---

## CLI Implementation Details

### Technology Stack

**Framework**: Typer (modern Python CLI framework)
- Type-safe command definitions
- Automatic help generation
- Argument validation
- Rich terminal output

**Output Formatting**: Rich library
- Colored output
- Tables, panels, progress bars
- Syntax highlighting
- Beautiful CLI UX

**Architecture Pattern**: Subcommand groups
- Main app in `app.py`
- Each command group in `commands/` folder
- Registered in `__init__.py`
- Entry point in `main.py`

---

### Entry Points

**Defined in `pyproject.toml`**:

```toml
[project.scripts]
advanced-memory = "advanced_memory.cli.main:app"
am = "advanced_memory.cli.main:app"  # Short alias
```

**Usage**:
```bash
advanced-memory sync           # Full name
am sync                        # Short alias (same thing)
```

---

### Command Registration

**In `app.py`**:
```python
app = typer.Typer(name="advanced-memory")

# Callback for global options
@app.callback()
def app_callback(
    project: str | None = Option(None, "--project", "-p"),
    version: bool | None = Option(None, "--version", "-v"),
):
    # Initialize project session
    # Handle version display
```

**In `main.py`**:
```python
from advanced_memory.cli.app import app

# Register all command groups
from advanced_memory.cli.commands import (
    convert,
    db,
    import_chatgpt,
    # ... all commands
)

if __name__ == "__main__":
    app()
```

**In `commands/__init__.py`**:
```python
from . import (
    convert,
    db,
    mcp,
    # ... all commands
)

__all__ = ["convert", "db", "mcp", ...]
```

---

## Why Advanced Memory Has a CLI (History)

### Inherited from Basic Memory

**Basic Memory MCP** (original project):
- Started as note-taking system
- CLI for direct file management
- Later added MCP server for AI interaction

**Advanced Memory** (our fork):
- Kept the CLI (valuable for users)
- Enhanced MCP server (portmanteau tools)
- Added API layer (FastAPI)
- Result: 3-layer architecture

---

### Unique Among MCP Servers

**Most MCP servers**:
- Purpose: Bridge AI to external service
- Example: GitHub MCP, Filesystem MCP, Slack MCP
- Architecture: Server only

**Advanced Memory**:
- Purpose: Complete knowledge management system
- Architecture: CLI + API + MCP + Database
- Standalone value: CLI works without MCP server
- MCP is one interface, not the only interface

---

## Do Other MCP Servers Need CLIs?

### Analysis

**Simple MCP servers (No)**:
- Filesystem MCP - No need (just file access)
- GitHub MCP - No need (wraps GitHub API)
- Slack MCP - No need (wraps Slack API)

**These are thin adapters** - MCP is the entire interface.

---

**Complex MCP servers (Maybe)**:
- Database MCP with schema management - Could benefit
- Document processing MCP with batch operations - Could benefit
- Project management MCP with direct management - Could benefit

**If the system has value independent of AI interaction**, a CLI makes sense.

---

### When to Add a CLI to MCP Server

**Add CLI when**:
- ✅ System has database/state
- ✅ Users need direct management
- ✅ Batch operations are common
- ✅ Automation/scripting valuable
- ✅ Standalone value exists

**Skip CLI when**:
- ❌ Stateless adapter (just wraps API)
- ❌ Only used by AI
- ❌ Simple operations
- ❌ No direct user interaction

---

## Advanced Memory's Three Interfaces

### 1. CLI (Human Direct)

**Who uses**: You (human user)

**When**: Direct file operations, management, automation

**Examples**:
```bash
advanced-memory sync
advanced-memory convert file report.pdf
advanced-memory project list
```

**Value**: Fast, scriptable, automatable

---

### 2. MCP Tools (AI Interactive)

**Who uses**: Claude, GPT, other AI agents

**When**: Conversational workflows, complex tasks

**Examples**:
```python
adn_content("write", title="Note", content="...")
adn_inbox("process")
adn_project("sync")
```

**Value**: AI-friendly, structured, contextual

---

### 3. REST API (Programmatic)

**Who uses**: Advanced Memory Pro (desktop app), web clients, custom integrations

**When**: Programmatic access, GUI applications

**Examples**:
```python
GET  /api/entities
POST /api/entities
GET  /api/search?q=python
```

**Value**: Standard HTTP, any language, web-compatible

---

## Command Details

### Sync Commands

**`sync`** - Main sync operation
- Scans project directory
- Updates database
- Full-text search index
- Watch mode for live updates

**`status`** - Sync status
- Compare files vs database
- Show pending changes
- Tree view of differences

**`validate`** - YAML validation
- Check frontmatter syntax
- Verify required fields
- Report errors before sync

---

### Project Commands

**`project list`** - List all projects
**`project add`** - Create new project
**`project remove`** - Delete project
**`project default`** - Set default
**`project sync-config`** - Sync config ↔ database
**`project info`** - Project details

**Purpose**: Multi-project management (inherited from Basic Memory)

---

### Import Commands

**`import claude conversations`** - Claude exports
**`import claude projects`** - Claude project exports
**`import chatgpt`** - ChatGPT conversations.json
**`import memory-json`** - Legacy memory.json format

**Purpose**: Migrate from other tools

---

### Onboarding Commands

**`onboard wizard`** - Interactive wizard
- Ask about interests
- Select categories
- Generate 30-100 notes
- Build starter knowledge base

**`onboard quick`** - Quick start
- Skip wizard
- Generate specific topic
- Faster onboarding

**Purpose**: Get started quickly with pre-built templates

---

### Tool Commands

**`tool <tool-name>`** - Direct MCP tool access from CLI

**Available tools**:
- `write-note` - Create notes
- `read-note` - Read notes
- `search-notes` - Search
- `build-context` - Build context
- `recent-activity` - Recent changes
- `continue-conversation` - Resume conversation

**Purpose**: Use MCP tools without running MCP server (for scripting, automation)

---

### Conversion Commands (NEW!)

**`convert file <path>`** - Convert documents
- .docx → markdown (Pandoc)
- .html → markdown (Pandoc)
- .pdf → markdown (text extraction)
- .txt → markdown (wrapping)

**`convert info`** - Conversion capabilities
- Show supported formats
- Check dependencies
- Installation instructions

**Purpose**: Document ingestion

---

### MCP Server Command

**`mcp`** - Run the MCP server
- stdio transport (default)
- SSE transport (optional)
- Background mode
- Debug logging

**Purpose**: Start server for AI agent connections

---

### Database Commands

**`reset`** - Drop and recreate database
- Nuclear option
- Fresh start
- Resolves corruption

**Purpose**: Database management

---

## CLI vs MCP Tools: The Trade-offs

### CLI Advantages

**Speed**:
- 0.5-1s per command
- Can parallelize
- No protocol overhead

**Composability**:
```bash
# Pipe, filter, chain
advanced-memory tool search-notes "python" | grep "advanced" | wc -l
```

**Automation**:
```bash
# Scripts, cron jobs, CI/CD
#!/bin/bash
advanced-memory sync
advanced-memory status
```

**Direct Access**:
- No MCP server needed
- Works offline
- Simple to debug

---

### MCP Tools Advantages

**Context Awareness**:
- Maintains conversation state
- Multi-turn workflows
- Structured errors

**AI Integration**:
- Native Claude Desktop
- Formatted responses
- Interactive experience

**Complexity Handling**:
- Multi-step workflows
- Intelligent error recovery
- Contextual decisions

---

## Real-World Usage Patterns

### Pattern 1: Automation Scripts

```bash
#!/bin/bash
# daily-sync.sh

# Sync all projects
for project in myproject myai advanced-memory-mcp; do
  advanced-memory --project "$project" sync
done

# Convert new documents
find ~/Documents/Inbox -name "*.pdf" -exec \
  advanced-memory convert file {} \;

# Report status
advanced-memory status
```

**Why CLI**: Fast, scriptable, non-interactive

---

### Pattern 2: Interactive Workflows

```
User: "Find Python notes, read the top 3, and summarize knowledge gaps"

Claude:
1. adn_search("search", query="python")
2. [picks top 3 from results]
3. adn_content("read", identifier="Note 1")
4. adn_content("read", identifier="Note 2")
5. adn_content("read", identifier="Note 3")
6. [analyzes, synthesizes, responds]
```

**Why MCP**: Context matters, multi-step intelligence

---

### Pattern 3: Hybrid (Best!)

```
# Step 1: CLI gathers data (fast, parallel)
$ for topic in python rust golang; do
    advanced-memory tool search-notes "$topic" > "$topic-notes.txt" &
  done
  wait

# Step 2: Give to Claude
User: "Here are notes on 3 languages [attach files]. Compare and create study plan."

# Step 3: Claude processes (intelligent)
Claude: [analyzes, compares, creates structured plan]
      adn_content("write", title="Language Comparison Study Plan", ...)

# Result: Fast data + intelligent processing
```

**Why hybrid**: Leverages strengths of both

---

## The Three Layers in Practice

### Layer 1: CLI (You, Direct)

```bash
$ advanced-memory sync
Syncing 1,234 files...
✅ 1,234 files processed, 0 errors

$ advanced-memory convert file ~/Downloads/paper.pdf
🔄 Converting paper.pdf to markdown...
✅ Conversion successful! Output: paper.md
```

**Characteristics**:
- Direct execution
- Terminal output
- Fast (0.5-1s)
- Scriptable

---

### Layer 2: MCP Tools (Claude, Interactive)

```
User (in Claude Desktop): "Process my inbox files"

Claude: "I'll process the files in your inbox..."

[Uses: adn_inbox("process")]

Response:
📥 Inbox Processing Complete
Total Files: 3
Successful: 3
✅ research-paper.pdf - Converted and synced
✅ meeting-notes.docx - Converted and synced
✅ quick-note.md - Moved to project
```

**Characteristics**:
- Conversational
- Formatted responses
- Context-aware
- Slower (2-5s)

---

### Layer 3: REST API (Programs, GUIs)

```python
# Advanced Memory Pro (desktop app)
import requests

response = requests.get("http://localhost:8000/api/entities")
entities = response.json()

# Display in GUI table
```

**Characteristics**:
- HTTP standard
- Any language
- Web-compatible
- Programmatic

---

## Why This Architecture is Powerful

### Flexibility

**Same backend, multiple interfaces**:
- Humans use CLI (fast, direct)
- AIs use MCP (intelligent, conversational)
- Programs use API (standard, integrable)

**No lock-in**:
- Don't like MCP? Use CLI
- Don't like CLI? Use MCP
- Need programmatic access? Use API

---

### Performance Optimization

**Choose the right tool**:
- Batch sync: CLI (3x faster)
- Interactive search: MCP (better UX)
- Bulk convert: CLI (10x faster, parallel)
- Complex workflow: MCP (context matters)

**Hybrid workflows**:
- CLI for speed-critical parts
- MCP for intelligence-critical parts
- Best of both worlds

---

### Evolution Path

**Started**: Basic Memory with CLI
**Added**: MCP server (AI integration)
**Added**: REST API (GUI support)
**Result**: Three interfaces, shared backend

**Benefits**:
- Each interface optimized for use case
- No single point of failure
- Multiple integration paths
- Future-proof (can add more interfaces)

---

## Comparison with Typical MCP Servers

### Simple MCP Server Example

**Filesystem MCP** (typical):
```typescript
// src/index.ts (entire server)

import { MCPServer } from "@modelcontextprotocol/sdk";

const server = new MCPServer({
  name: "filesystem",
  version: "1.0.0"
});

server.registerTool({
  name: "read_file",
  description: "Read a file",
  parameters: { path: { type: "string" } },
  handler: async (params) => {
    return await fs.readFile(params.path, 'utf-8');
  }
});

server.listen();
```

**Total**: 50 lines, no CLI, no database, stateless

**Entry point**: `node src/index.ts` (runs server, that's it)

---

### Advanced Memory (our architecture)

**Lines of code**: ~30,000+
**Components**: CLI + API + MCP + Database + Sync + Services
**Entry points**:
- `advanced-memory <command>` (CLI)
- `advanced-memory mcp` (MCP server)
- API runs embedded in MCP server
- Multiple access patterns

**Complexity**: Full application, not just server

---

## Should You Add a CLI to Your MCP Server?

### Decision Matrix

**If your MCP server is**:
- Simple API wrapper → ❌ Skip CLI
- Stateless → ❌ Skip CLI
- <500 lines code → ❌ Skip CLI
- AI-only interaction → ❌ Skip CLI

**If your MCP server is**:
- Has database/state → ✅ Consider CLI
- Batch operations common → ✅ Consider CLI
- Direct management needed → ✅ Consider CLI
- Automation valuable → ✅ Consider CLI
- >5000 lines code → ✅ Probably needs CLI

---

### Effort vs Value

**Adding basic CLI**:
- Effort: 2-4 hours (Typer setup)
- Value: High (if you have state/database)

**Adding comprehensive CLI** (like ours):
- Effort: 1-2 weeks
- Value: Very high (becomes standalone tool)

**Our case**:
- Inherited from Basic Memory (already existed)
- Enhanced over time
- Now 13 command groups
- Substantial value for non-AI workflows

---

## Summary

### Key Points

**1. Advanced Memory HAS a comprehensive CLI** (13 command groups)
- sync, status, validate, reset
- project management (6 commands)
- import (4 sources)
- convert (NEW - documents to markdown)
- onboard (wizard + quick)
- tool (MCP tools from CLI)
- mcp (run server)

**2. This is NOT typical for MCP servers**
- Most MCP servers: Server only
- We're a full application: CLI + MCP + API

**3. CLI is faster than MCP tools**
- 3-15x speedup for batch operations
- 50-60% token savings
- Can parallelize

**4. Best approach: Hybrid**
- CLI for data gathering (fast)
- MCP for intelligent processing
- CLI for bulk operations

**5. Architecture inherited from Basic Memory**
- Not standard MCP pattern
- Valuable for our use case (knowledge management)
- Enables automation, scripting, direct management

---

## Commands Quick Reference

```bash
# Core
advanced-memory sync [--watch]
advanced-memory status
advanced-memory validate
advanced-memory reset

# Projects
advanced-memory project list
advanced-memory project add <name> <path>
advanced-memory project default <name>

# Import
advanced-memory import claude conversations
advanced-memory import chatgpt
advanced-memory import memory-json

# Convert (NEW!)
advanced-memory convert file <file>
advanced-memory convert info

# Onboarding
advanced-memory onboard wizard
advanced-memory onboard quick <category> <topic>

# MCP Tools from CLI
advanced-memory tool write-note <title>
advanced-memory tool search-notes <query>

# Run MCP Server
advanced-memory mcp [--transport stdio|sse]
```

**Alias**: Use `am` instead of `advanced-memory` for short form

---

*Understanding Advanced Memory's multi-interface architecture*
*October 17, 2025*
