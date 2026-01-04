# Advanced Memory CLI Command Reference

**Complete documentation of all CLI commands inherited from Basic Memory MCP**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Commands](#core-commands)
3. [Project Management](#project-management)
4. [Import Commands](#import-commands)
5. [Tool Access](#tool-access)
6. [Utility Commands](#utility-commands)
7. [Command Registration](#command-registration)
8. [Usage Patterns](#usage-patterns)

---

## Architecture Overview

### Entry Point

**Entry point** (defined in `pyproject.toml`):
```toml
[project.scripts]
advanced-memory = "advanced_memory.cli.main:app"
```

**Main CLI app** (`src/advanced_memory/cli/app.py`):
- Built with [Typer](https://typer.tiangolo.com/) - modern Python CLI framework
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Global callback runs initialization for every command
- Project context set via `--project` flag or `ADVANCED_MEMORY_PROJECT` env var

**Command registration** (`src/advanced_memory/cli/main.py`):
- Imports all command modules to trigger `@app.command()` decorators
- Commands self-register when imported

---

## Core Commands

### `advanced-memory sync`

**File**: `src/advanced_memory/cli/commands/sync.py`

**Purpose**: Synchronize markdown files with the SQLite database index

**Usage**:
```bash
advanced-memory sync                    # Quick summary
advanced-memory sync --verbose          # Detailed file listing
advanced-memory sync -v                 # Short form
```

**What it does**:
1. Scans project directory for markdown files
2. Compares file checksums with database
3. Updates database for new/modified/moved/deleted files
4. Parses YAML frontmatter, wikilinks, observations, relations
5. Rebuilds full-text search index

**Options**:
- `--verbose / -v`: Show detailed sync results with file trees

**Output**:
- **Summary mode**: `Synced 5 files (2 new, 1 modified, 1 moved, 1 deleted)`
- **Verbose mode**: Rich tree view grouped by directory with checksums

**Triggered by**:
- Manual: `advanced-memory sync`
- Automatic: File watcher (if `sync_changes: true` in config)
- Post-import: After any import command

**Technical details**:
- Uses `SyncService` to orchestrate sync
- Handles markdown parsing via `EntityParser` and `MarkdownProcessor`
- Updates `entities`, `observations`, `relations`, `search_index` tables
- Gracefully handles YAML errors (skips invalid files, doesn't crash)

---

### `advanced-memory validate`

**File**: `src/advanced_memory/cli/commands/sync.py`

**Purpose**: Validate YAML frontmatter before syncing

**Usage**:
```bash
advanced-memory validate                # Check for issues
advanced-memory validate --fix          # Auto-fix simple issues
```

**What it does**:
1. Scans all markdown files for YAML frontmatter errors
2. Reports files with malformed YAML
3. Provides hints for fixing issues
4. Optionally attempts auto-fixes (e.g., quote unquoted strings)

**Output**:
```
Found 2 files with YAML issues:

- notes/my-note.md
  Error: expected '<document start>', but found '<scalar>'

- projects/test.md
  Error: found unexpected ':'

Tips to fix YAML issues:
   - Check for missing quotes around string values
   - Ensure proper YAML indentation (spaces, not tabs)
   - Fix malformed YAML aliases (&/*)
```

**Why it exists**:
- **Problem**: Malformed YAML crashes sync
- **Solution**: Pre-validate, provide helpful errors, continue with valid files

---

### `advanced-memory status`

**File**: `src/advanced_memory/cli/commands/status.py`

**Purpose**: Show sync status without making changes

**Usage**:
```bash
advanced-memory status                  # Summary by directory
advanced-memory status --verbose        # Full file listing
advanced-memory status -v               # Short form
```

**What it does**:
1. Scans files (like `sync`) but doesn't update database
2. Shows what **would** change if you ran `sync`
3. Useful for checking if files need syncing

**Output** (summary mode):
```
Project 'my-project': Status
  notes/ +2 new, ~1 modified
  projects/ <->1 moved
```

**Output** (verbose mode):
- Full tree with file names and checksums

**Triggered by**:
- Manual: `advanced-memory status`
- API: `GET /projects/status` (via MCP tool `adn_project`)

---

### `advanced-memory mcp`

**File**: `src/advanced_memory/cli/commands/mcp.py`

**Purpose**: Start the MCP server

**Usage**:
```bash
# Standard I/O (Claude Desktop)
advanced-memory mcp

# HTTP transport (web/LAN)
advanced-memory mcp --transport streamable-http --host 0.0.0.0 --port 8000

# SSE transport (legacy compatibility)
advanced-memory mcp --transport sse --host 127.0.0.1 --port 3000
```

**What it does**:
1. Imports and registers all MCP tools
2. Imports and registers all MCP prompts
3. Starts background file watcher (if `sync_changes: true`)
4. Runs MCP server with specified transport

**Transport options**:
- **stdio** (default): Standard I/O for local usage (Claude Desktop)
- **streamable-http**: HTTP with streaming, recommended for web/LAN
- **sse**: Server-Sent Events for legacy clients

**Options**:
- `--transport`: Transport type (stdio, streamable-http, sse)
- `--host`: Bind address for HTTP transports (default: 0.0.0.0)
- `--port`: Port for HTTP transports (default: 8000)
- `--path`: Path prefix for streamable-http (default: /mcp)

**Background services**:
- **File watcher** (if enabled): Monitors project directory, auto-syncs changes
- Runs in separate thread with dedicated event loop

**Triggered by**:
- Claude Desktop: Configured in `claude_desktop_config.json`
- Manual testing: `advanced-memory mcp`
- Web deployment: `advanced-memory mcp --transport streamable-http`

---

## Project Management

### `advanced-memory project list`

**File**: `src/advanced_memory/cli/commands/project.py`

**Purpose**: List all configured projects

**Usage**:
```bash
advanced-memory project list
```

**Output**:
```
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┓
┃ Name            ┃ Path                    ┃ Default ┃ Active ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━┩
│ my-project      │ ~/documents/notes       │ YES     │ YES    │
│ work            │ ~/work/knowledge        │         │        │
│ personal        │ ~/personal/zettelkasten │         │        │
└─────────────────┴─────────────────────────┴─────────┴────────┘
```

**What it shows**:
- **Name**: Project identifier
- **Path**: Filesystem location (uses `~` for home)
- **Default**: Is this the default project?
- **Active**: Is this the current session project?

**Triggered by**:
- Manual: `advanced-memory project list`
- API: `GET /projects/projects` (via MCP tool `adn_project`)

---

### `advanced-memory project add`

**File**: `src/advanced_memory/cli/commands/project.py`

**Purpose**: Add a new project

**Usage**:
```bash
advanced-memory project add my-new-project /path/to/directory
advanced-memory project add work ~/work/notes --default
```

**Arguments**:
- `name`: Project name (becomes identifier)
- `path`: Directory path (resolves `~` and relative paths)

**Options**:
- `--default`: Set as default project immediately

**What it does**:
1. Resolves path to absolute
2. Creates project entry in database
3. Adds project to `config.toml`
4. Optionally sets as default

**Output**:
```
✅ Project 'my-new-project' added successfully

To use this project:
  advanced-memory --project=my-new-project <command>
  # or
  advanced-memory project default my-new-project
```

**Triggered by**:
- Manual: `advanced-memory project add ...`
- API: `POST /projects/projects` (via MCP tool `adn_project`)

---

### `advanced-memory project remove`

**File**: `src/advanced_memory/cli/commands/project.py`

**Purpose**: Remove a project from configuration

**Usage**:
```bash
advanced-memory project remove old-project
```

**What it does**:
1. Removes project from database
2. Removes project from `config.toml`
3. **Does not** delete files from disk

**Output**:
```
✅ Project 'old-project' removed
⚠️  Note: The project files have not been deleted from disk.
```

**Safety**:
- Files are never deleted
- Only configuration is removed

**Triggered by**:
- Manual: `advanced-memory project remove ...`
- API: `DELETE /projects/{name}` (via MCP tool `adn_project`)

---

### `advanced-memory project default`

**File**: `src/advanced_memory/cli/commands/project.py`

**Purpose**: Set default project and activate for session

**Usage**:
```bash
advanced-memory project default my-project
```

**What it does**:
1. Sets `default_project` in `config.toml`
2. Activates project for current MCP session
3. Future commands use this project unless `--project` specified

**Output**:
```
✅ Default project set to 'my-project'
✅ Project activated for current session
```

**Triggered by**:
- Manual: `advanced-memory project default ...`
- API: `PUT /projects/{name}/default` (via MCP tool `adn_project`)

---

### `advanced-memory project sync-config`

**File**: `src/advanced_memory/cli/commands/project.py`

**Purpose**: Synchronize config.toml with database

**Usage**:
```bash
advanced-memory project sync-config
```

**What it does**:
- Ensures `config.toml` and database are in sync
- Useful after manual config edits

**When to use**:
- After manually editing `config.toml`
- After database recovery
- Troubleshooting configuration issues

**Triggered by**:
- Manual: `advanced-memory project sync-config`
- API: `POST /projects/sync`

---

### `advanced-memory project info`

**File**: `src/advanced_memory/cli/commands/project.py`

**Purpose**: Display detailed project statistics and system status

**Usage**:
```bash
advanced-memory project info              # Rich formatted output
advanced-memory project info --json       # JSON output
```

**What it shows**:

**Project Configuration**:
- Current project name
- Project path
- Default project

**Statistics**:
- Total entities
- Total observations
- Total relations
- Unresolved relations
- Isolated entities (no connections)

**Entity Types** (breakdown by type):
- note: 150
- person: 23
- project: 12
- etc.

**Most Connected Entities** (top 5):
- Entity title, permalink, relation count

**Recent Activity** (last 5 updated):
- Entity title, type, last updated timestamp

**System Status**:
- Advanced Memory version
- Database path and size
- Watch service status (running/stopped, files synced, errors)

**Available Projects**:
- List of all projects with paths and default marker

**Output format**:
- **Default**: Beautiful Rich panels, tables, trees
- **JSON**: Structured JSON for programmatic use

**Triggered by**:
- Manual: `advanced-memory project info`
- API: `GET /projects/info` (via MCP resource `project_info`)

---

## Import Commands

All import commands follow the same pattern:
1. Read source file (JSON, etc.)
2. Parse and convert to markdown
3. Write markdown files to project directory
4. Prompt user to run `sync` to index

### `advanced-memory import chatgpt`

**File**: `src/advanced_memory/cli/commands/import_chatgpt.py`

**Purpose**: Import ChatGPT conversation export

**Usage**:
```bash
advanced-memory import chatgpt conversations.json
advanced-memory import chatgpt data.json --folder chat-history
```

**Arguments**:
- `conversations_json`: Path to ChatGPT export (default: `conversations.json`)

**Options**:
- `--folder`: Destination folder within project (default: `conversations`)

**What it does**:
1. Parses ChatGPT's complex tree structure
2. Converts nested messages to linear markdown
3. Creates one file per conversation
4. Preserves user/assistant message structure

**Output**:
```
Importing chats from conversations.json...writing to ~/notes/conversations

╭──────────────────────────╮
│ Import complete!         │
│                          │
│ Imported 15 conversations│
│ Containing 234 messages  │
╰──────────────────────────╯

Run 'advanced-memory sync' to index the new files.
```

**Triggered by**:
- Manual: `advanced-memory import chatgpt ...`

---

### `advanced-memory import claude conversations`

**File**: `src/advanced_memory/cli/commands/import_claude_conversations.py`

**Purpose**: Import Claude.ai conversation export

**Usage**:
```bash
advanced-memory import claude conversations conversations.json
advanced-memory import claude conversations data.json --folder claude-chats
```

**Arguments**:
- `conversations_json`: Path to Claude conversations export

**Options**:
- `--folder`: Destination folder (default: `conversations`)

**What it does**:
1. Parses Claude conversations format
2. Converts to clean markdown
3. Preserves conversation structure

**Output**: Similar to ChatGPT import

**Triggered by**:
- Manual: `advanced-memory import claude conversations ...`

---

### `advanced-memory import claude projects`

**File**: `src/advanced_memory/cli/commands/import_claude_projects.py`

**Purpose**: Import Claude.ai project data

**Usage**:
```bash
advanced-memory import claude projects projects.json
advanced-memory import claude projects data.json --base-folder claude-work
```

**Arguments**:
- `projects_json`: Path to Claude projects export

**Options**:
- `--base-folder`: Base folder for projects (default: `projects`)

**What it does**:
1. Creates directory for each Claude project
2. Stores project documents in `docs/` subdirectory
3. Places prompt templates in project root
4. Preserves project organization

**Structure created**:
```
projects/
  my-claude-project/
    README.md              (prompt template)
    docs/
      document-1.md
      document-2.md
```

**Output**:
```
╭──────────────────────────────╮
│ Import complete!             │
│                              │
│ Imported 8 project documents │
│ Imported 3 prompt templates  │
╰──────────────────────────────╯

Run 'advanced-memory sync' to index the new files.
```

**Triggered by**:
- Manual: `advanced-memory import claude projects ...`

---

### `advanced-memory import memory-json`

**File**: `src/advanced_memory/cli/commands/import_memory_json.py`

**Purpose**: Import from JSON memory format (entities + relations)

**Usage**:
```bash
advanced-memory import memory-json memory.json
advanced-memory import memory-json backup.json --destination-folder archive
```

**Arguments**:
- `json_path`: Path to memory JSON file (default: `memory.json`)

**Options**:
- `--destination-folder`: Destination within project (default: root)

**What it does**:
1. Reads JSON log format (one JSON object per line)
2. Extracts entities and relations
3. Creates markdown files with YAML frontmatter
4. Includes outgoing relations in each entity

**JSON format expected**:
```json
{"entity": {"name": "Python", "type": "language"}, "relations": [{"to": "Flask", "type": "uses"}]}
{"entity": {"name": "Flask", "type": "framework"}, "relations": []}
```

**Output**:
```
╭───────────────────────╮
│ Import complete!      │
│                       │
│ Created 42 entities   │
│ Added 67 relations    │
╰───────────────────────╯

Run 'advanced-memory sync' to index the new files.
```

**Triggered by**:
- Manual: `advanced-memory import memory-json ...`

---

## Tool Access

### Overview

The `tool` subcommand provides CLI access to MCP tools, enabling:
- Batch operations via shell scripts
- Piping content from other commands
- Automation without MCP client

**Key insight**: CLI is 3-15x faster than MCP for bulk operations!

---

### `advanced-memory tool write-note`

**File**: `src/advanced_memory/cli/commands/tool.py`

**Purpose**: Create or update markdown notes

**Usage**:
```bash
# Using --content parameter
advanced-memory tool write-note --title "My Note" --folder "notes" --content "Content here"

# Piping from stdin
echo "# My Note" | advanced-memory tool write-note --title "My Note" --folder "notes"

# Using heredoc
cat << EOF | advanced-memory tool write-note --title "Research" --folder "projects"
# Research Notes

- Point 1
- Point 2
EOF

# Reading from file
cat document.md | advanced-memory tool write-note --title "Document" --folder "docs"
```

**Options**:
- `--title`: Note title (required)
- `--folder`: Destination folder (required)
- `--content`: Note content (optional if using stdin)
- `--tags`: Comma-separated tags (optional)

**What it does**:
1. Accepts content from `--content` or stdin
2. Calls `mcp_write_note.fn()` (same as MCP tool)
3. Creates markdown file with YAML frontmatter
4. Returns note details (title, permalink, path)

**Output** (Rich formatted):
```python
{
  "title": "My Note",
  "permalink": "my-note",
  "path": "notes/my-note.md",
  "created_at": "2025-10-17T10:30:00Z"
}
```

**Stdin detection**:
- Checks `sys.stdin.isatty()` to determine if data is piped
- Errors if no content provided and no stdin

**Triggered by**:
- Manual: `advanced-memory tool write-note ...`
- Batch scripts: `for file in *.txt; do cat "$file" | advanced-memory tool write-note --title "$file" --folder "imports"; done`

---

### `advanced-memory tool read-note`

**File**: `src/advanced_memory/cli/commands/tool.py`

**Purpose**: Read a markdown note

**Usage**:
```bash
advanced-memory tool read-note "my-note"
advanced-memory tool read-note "memory://my-note"
advanced-memory tool read-note "notes/project.md"
```

**Arguments**:
- `identifier`: Title, permalink, memory:// URL, or file path

**Options**:
- `--page`: Page number for pagination (default: 1)
- `--page-size`: Items per page (default: 10)

**What it does**:
1. Resolves identifier (title/permalink/path)
2. Fetches note from database
3. Returns note content with metadata

**Output**: Full note content in Rich format

**Triggered by**:
- Manual: `advanced-memory tool read-note ...`

---

### `advanced-memory tool build-context`

**File**: `src/advanced_memory/cli/commands/tool.py`

**Purpose**: Build context for conversation continuity

**Usage**:
```bash
advanced-memory tool build-context "memory://my-note"
advanced-memory tool build-context "memory://my-note" --depth 2 --timeframe 30d
```

**Arguments**:
- `url`: memory:// URL

**Options**:
- `--depth`: Traversal depth for relations (default: 1)
- `--timeframe`: How far back to look (e.g., "7d", "1 week") (default: 7d)
- `--page`: Page number (default: 1)
- `--page-size`: Items per page (default: 10)
- `--max-related`: Max related entities to include (default: 10)

**What it does**:
1. Fetches entity from memory:// URL
2. Traverses related entities (by depth)
3. Filters by timeframe (recently updated)
4. Returns context bundle (entity + related + observations + relations)

**Output**: JSON context object

**Triggered by**:
- Manual: `advanced-memory tool build-context ...`
- MCP: `build_context` tool

---

### `advanced-memory tool recent-activity`

**File**: `src/advanced_memory/cli/commands/tool.py`

**Purpose**: Get recent activity across knowledge base

**Usage**:
```bash
advanced-memory tool recent-activity
advanced-memory tool recent-activity --type note --type project
advanced-memory tool recent-activity --timeframe 30d
```

**Options**:
- `--type`: Filter by entity types (can specify multiple)
- `--depth`: Traversal depth (default: 1)
- `--timeframe`: How far back (default: 7d)
- `--page`: Page number (default: 1)
- `--page-size`: Items per page (default: 10)
- `--max-related`: Max related entities (default: 10)

**What it does**:
1. Queries recently updated entities
2. Filters by type and timeframe
3. Returns activity context

**Output**: JSON context with recent entities

**Triggered by**:
- Manual: `advanced-memory tool recent-activity ...`
- MCP: `recent_activity` tool

---

### `advanced-memory tool search-notes`

**File**: `src/advanced_memory/cli/commands/tool.py`

**Purpose**: Search across all content

**Usage**:
```bash
# Full-text search
advanced-memory tool search-notes "machine learning"

# Search titles only
advanced-memory tool search-notes "Python" --title

# Search permalinks
advanced-memory tool search-notes "my-note" --permalink

# Time-filtered search
advanced-memory tool search-notes "AI" --after_date "1 week"
```

**Arguments**:
- `query`: Search query

**Options**:
- `--permalink`: Search permalink values
- `--title`: Search title values
- `--after_date`: Filter results after date (e.g., "2d", "1 week")
- `--page`: Page number (default: 1)
- `--page-size`: Results per page (default: 10)

**Search types**:
- **text** (default): Full-text search (content, observations, relations)
- **title**: Title search
- **permalink**: Permalink exact match
- **permalink_match**: Permalink wildcard match (if `*` in query)

**What it does**:
1. Performs SQLite FTS5 full-text search
2. Returns ranked results with snippets
3. Includes highlights and context

**Output**: JSON search results

**Triggered by**:
- Manual: `advanced-memory tool search-notes ...`
- MCP: `search_notes` tool

---

### `advanced-memory tool continue-conversation`

**File**: `src/advanced_memory/cli/commands/tool.py`

**Purpose**: Generate prompt to continue a previous conversation

**Usage**:
```bash
advanced-memory tool continue-conversation
advanced-memory tool continue-conversation --topic "AI"
advanced-memory tool continue-conversation --topic "Python" --timeframe "30d"
```

**Options**:
- `--topic`: Topic or keyword to search for (optional)
- `--timeframe`: How far back to look (optional, default: 7d)

**What it does**:
1. Searches for relevant recent activity (by topic or all)
2. Retrieves context from related entities
3. Generates formatted prompt for LLM

**Output**: Markdown-formatted prompt with:
- Context summary
- Recent activity
- Suggested topics
- Links to related entities

**Use case**:
- **Human**: "Continue our discussion about X"
- **AI**: Uses this prompt to retrieve context and continue seamlessly

**Triggered by**:
- Manual: `advanced-memory tool continue-conversation ...`
- MCP: `continue_conversation` prompt

---

## Utility Commands

### `advanced-memory reset`

**File**: `src/advanced_memory/cli/commands/db.py`

**Purpose**: Reset database and configuration

**Usage**:
```bash
advanced-memory reset                   # Reset database only
advanced-memory reset --reindex         # Reset and rebuild from files
```

**Options**:
- `--reindex`: Rebuild database index from filesystem after reset

**What it does**:
1. **Warns** and asks for confirmation
2. Deletes database file
3. Resets `config.toml` to defaults
4. Runs migrations to create empty database
5. Optionally runs `sync` to rebuild index

**Output**:
```
This will delete all data in your db. Are you sure? [y/N]: y
Database file deleted: ~/.advanced-memory/advanced_memory.db
Project configuration reset to default
Database reset complete
Rebuilding search index from filesystem...
```

**Use cases**:
- **Corrupted database**: Nuclear option to fix issues
- **Fresh start**: Clear everything and rebuild
- **Testing**: Reset to clean state

**⚠️ WARNING**: This is destructive! Markdown files are safe, but database is wiped.

**Triggered by**:
- Manual: `advanced-memory reset`

---

### `advanced-memory convert file`

**File**: `src/advanced_memory/cli/commands/convert.py`

**Purpose**: Convert documents to markdown

**Usage**:
```bash
# Auto-detect type
advanced-memory convert file document.docx
advanced-memory convert file report.pdf -o output.md

# Specify type explicitly
advanced-memory convert file data.html --type html --output result.md
```

**Arguments**:
- `file_path`: Path to file to convert

**Options**:
- `--output / -o`: Output file path (default: same name with .md)
- `--type / -t`: Document type (docx, html, pdf, txt). Auto-detected if omitted.

**Supported formats**:
- `.docx`: Word documents (requires Pandoc)
- `.html`: HTML files (requires Pandoc)
- `.pdf`: PDF documents (pypdf or pdftotext)
- `.txt`: Plain text

**What it does**:
1. Auto-detects document type from extension
2. Uses appropriate converter:
   - **Pandoc**: .docx, .html
   - **pypdf**: .pdf
   - **Built-in**: .txt
3. Writes markdown to output file
4. Shows summary (lines, characters)

**Output**:
```
🔄 Converting document.docx to markdown...
✅ Conversion successful!
Output: document.md
Lines: 150, Characters: 4823
```

**Triggered by**:
- Manual: `advanced-memory convert file ...`
- Workflow: `for file in *.docx; do advanced-memory convert file "$file"; done`

---

### `advanced-memory convert info`

**File**: `src/advanced_memory/cli/commands/convert.py`

**Purpose**: Show conversion capabilities and requirements

**Usage**:
```bash
advanced-memory convert info
```

**What it shows**:
- Supported formats
- Required dependencies
- Installation status

**Output**:
```
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Format          ┃ Extension  ┃ Method   ┃ Requires ┃ Status         ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Word Documents  │ .docx, .doc│ Pandoc   │ Pandoc   │ ✅ Available   │
│ HTML Files      │ .html, .htm│ Pandoc   │ Pandoc   │ ✅ Available   │
│ PDF Documents   │ .pdf       │ pypdf    │ pypdf    │ ✅ Available   │
│ Plain Text      │ .txt       │ Built-in │ None     │ ✅ Always      │
└─────────────────┴────────────┴──────────┴──────────┴────────────────┘

💡 Install Pandoc for .docx and .html conversion:
   https://pandoc.org

💡 Install pypdf for better PDF extraction:
   pip install pypdf
```

**Triggered by**:
- Manual: `advanced-memory convert info`

---

### `advanced-memory onboard wizard`

**File**: `src/advanced_memory/cli/commands/onboard.py`

**Purpose**: Interactive wizard to create personalized starter Zettelkasten

**Usage**:
```bash
advanced-memory onboard wizard
```

**What it does**:
1. **Interactive prompts**:
   - Shows 10 available categories
   - User selects interests (comma-separated or "all")
   - For each category, select sub-topics
2. **Generates content**:
   - Creates 50-60 high-quality starter notes
   - Covers selected topics
   - Includes Mermaid diagrams, code examples, wikilinks
3. **Provides guidance**:
   - Next steps for exploring notes
   - How to connect ideas
   - How to build on foundation

**Categories available**:
1. Developer (Python, Git, Testing, Architecture)
2. Researcher (Methods, Critical Thinking, Writing)
3. Writer (Craft, Storytelling, Publishing)
4. Knowledge Worker (Productivity, PKM, Communication)
5. DevOps Engineer (Docker, Kubernetes, CI/CD, IaC)
6. Data Scientist (ML, Statistics, Data Analysis)
7. UI/UX Designer (Design Principles, Figma, Research)
8. Product Manager (Strategy, Roadmaps, Metrics)
9. Entrepreneur (Business Models, Fundraising, Growth)
10. Creative Professional (Photography, Video, Design)

**Output**:
```
Welcome to Advanced Memory Onboarding! 🚀
Let's create your personalized starter Zettelkasten.

Available Categories:
1. Developer (Python, Git, Testing, Architecture)
2. Researcher (Methods, Critical Thinking, Writing)
...

Select categories (comma-separated numbers, or 'all'): 1,5,6

Developer focus areas:
  1. Python Fundamentals
  2. Git & Version Control
  ...

Select Developer areas (comma-separated, or 'all'): all

[Progress spinner showing note creation...]

🎉 Success!
Created 58 high-quality starter notes in your knowledge base!

What's next?
• Explore your new notes with: advanced-memory search "Python"
• Start connecting ideas by adding wikilinks [[Note Name]]
• Create your own notes to build on this foundation
```

**Triggered by**:
- Manual: `advanced-memory onboard wizard`
- First-time setup: Recommended after installation

---

### `advanced-memory onboard quick`

**File**: `src/advanced_memory/cli/commands/onboard.py`

**Purpose**: Quick non-interactive onboarding

**Usage**:
```bash
advanced-memory onboard quick --interests developer,devops
advanced-memory onboard quick -i "data-scientist,researcher"
```

**Options**:
- `--interests / -i`: Comma-separated interests (required)

**Valid interests**:
- developer
- researcher
- writer
- knowledge-worker
- devops
- data-scientist
- uiux-designer
- product-manager
- entrepreneur
- creative

**What it does**:
1. Parses interests from CLI arg
2. Uses **all** sub-topics for each category
3. Generates starter notes
4. Shows summary

**Output**:
```
Creating starter Zettelkasten for: developer, devops

[Progress...]

✅ Created 45 excellent starter notes!
Run advanced-memory onboard wizard for interactive setup anytime.
```

**Use case**:
- **Automation**: Scripts, setup tools
- **Quick start**: No interaction needed
- **Batch setup**: Multiple projects

**Triggered by**:
- Manual: `advanced-memory onboard quick -i ...`
- Setup scripts: `advanced-memory onboard quick -i developer`

---

### `advanced-memory --version`

**File**: `src/advanced_memory/cli/app.py`

**Purpose**: Show version and configuration

**Usage**:
```bash
advanced-memory --version
advanced-memory -v
```

**Output**:
```
Advanced Memory version: 1.0.0b3
Current project: my-project
Project path: ~/documents/notes
```

**What it shows**:
- Software version
- Currently active project
- Project filesystem path

**Triggered by**:
- Manual: `advanced-memory --version`
- Debugging: Check version and project context

---

## Command Registration

### How Commands Are Registered

**Step 1: Decorator registration** (in command files):
```python
# src/advanced_memory/cli/commands/sync.py
from advanced_memory.cli.app import app

@app.command()
def sync(verbose: bool = False):
    """Sync knowledge files with the database."""
    # ...
```

**Step 2: Import in main** (`src/advanced_memory/cli/main.py`):
```python
from advanced_memory.cli.app import app

# Importing triggers @app.command() decorators
from advanced_memory.cli.commands import (
    sync,
    status,
    project,
    # ... all commands
)

if __name__ == "__main__":
    app()  # Run Typer app
```

**Step 3: Entry point** (in `pyproject.toml`):
```toml
[project.scripts]
advanced-memory = "advanced_memory.cli.main:app"
```

### Command Hierarchy

**Top-level commands**:
- `advanced-memory sync`
- `advanced-memory status`
- `advanced-memory validate`
- `advanced-memory mcp`
- `advanced-memory reset`
- `advanced-memory --version`

**Subcommand groups**:
- `advanced-memory project <subcommand>`
  - `list`, `add`, `remove`, `default`, `sync-config`, `info`
- `advanced-memory import <subcommand>`
  - `chatgpt`, `memory-json`
- `advanced-memory import claude <subcommand>`
  - `conversations`, `projects`
- `advanced-memory tool <subcommand>`
  - `write-note`, `read-note`, `build-context`, `recent-activity`, `search-notes`, `continue-conversation`
- `advanced-memory onboard <subcommand>`
  - `wizard`, `quick`
- `advanced-memory convert <subcommand>`
  - `file`, `info`

### Global Options

**Every command** supports:
- `--project <name>`: Override default project
- `-p <name>`: Short form

**Environment variable**:
- `ADVANCED_MEMORY_PROJECT`: Set project for all commands

**Example**:
```bash
# Override for one command
advanced-memory --project work sync

# Set for session
export ADVANCED_MEMORY_PROJECT=work
advanced-memory sync
advanced-memory status
```

---

## Usage Patterns

### Pattern 1: Daily Workflow

```bash
# Morning: Check what changed
advanced-memory status

# Sync if needed
advanced-memory sync

# Work on notes (via Claude MCP or manual editing)
# ...

# Evening: Check and sync again
advanced-memory status
advanced-memory sync
```

### Pattern 2: Multi-Project Workflow

```bash
# Work project
advanced-memory --project work sync
advanced-memory --project work search "Q4 goals"

# Personal project
advanced-memory --project personal sync
advanced-memory --project personal recent-activity
```

### Pattern 3: Import Workflow

```bash
# Import ChatGPT history
advanced-memory import chatgpt conversations.json --folder chatgpt-archive

# Import Claude projects
advanced-memory import claude projects projects.json --base-folder claude-work

# Sync to index everything
advanced-memory sync
```

### Pattern 4: Batch Conversion

```bash
# Convert all Word docs in a directory
for file in *.docx; do
  advanced-memory convert file "$file"
done

# Move converted markdown to project
mv *.md ~/notes/imported/

# Sync
advanced-memory sync
```

### Pattern 5: Bulk Note Creation (CLI > MCP)

**Bad** (via MCP, 30-50 seconds):
```python
# Claude calls adn_content 10 times sequentially
for title in titles:
    await adn_content("create", title=title, ...)
```

**Good** (via CLI, 5-10 seconds):
```bash
# Parallel execution
for file in *.txt; do
  cat "$file" | advanced-memory tool write-note \
    --title "$file" --folder "imports" &
done
wait
```

**Result**: 3-15x faster! 🚀

### Pattern 6: Search & Extract

```bash
# Search for topic
advanced-memory tool search-notes "machine learning" > results.json

# Parse JSON and extract permalinks
cat results.json | jq -r '.results[].permalink' > permalinks.txt

# Read each note
while read permalink; do
  advanced-memory tool read-note "$permalink" >> ml-context.md
done < permalinks.txt
```

### Pattern 7: Onboarding New Users

```bash
# Interactive
advanced-memory onboard wizard

# Or quick setup for developers
advanced-memory onboard quick -i developer,devops

# Sync
advanced-memory sync
```

---

## Summary

### Command Categories

| Category | Commands | Purpose |
|----------|----------|---------|
| **Core** | `sync`, `validate`, `status`, `mcp` | Database sync, validation, MCP server |
| **Project** | `project list/add/remove/default/info` | Multi-project management |
| **Import** | `import chatgpt/claude/memory-json` | Data import from external sources |
| **Tool Access** | `tool write-note/read-note/search-notes/...` | CLI access to MCP tools |
| **Utility** | `reset`, `convert`, `onboard` | Database reset, conversion, setup |

### Key Insights

1. **CLI = 3-15x faster than MCP** for bulk operations
2. **All commands support `--project`** for multi-project workflows
3. **Import + sync pattern** is standard for external data
4. **Tool commands** expose MCP functionality for scripting
5. **Onboarding wizard** creates excellent starter content
6. **File watcher** auto-syncs when MCP server runs
7. **Validation** prevents YAML errors from breaking sync

### When to Use CLI vs MCP

**CLI** (batch, speed, automation):
- Bulk operations (10+ notes)
- Complex multi-step workflows
- Automated scripts
- Data import/export

**MCP** (interactive, structured, conversational):
- Single note creation during chat
- Context-aware operations
- Semantic search with AI
- Conversational knowledge building

---

## Further Reading

- **MCP Tool Reference**: See `docs/mcp/tool-reference.md` for MCP tools
- **Architecture**: See `docs/architecture/CLI_ARCHITECTURE_GUIDE.md`
- **CLI vs MCP Efficiency**: See `docs/development/CLI_VS_MCP_TOOLS_EFFICIENCY.md`
- **Project Configuration**: See `docs/user-guide/project-configuration.md`

---

*Last updated: 2025-10-17*
