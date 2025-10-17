# Cursor Memory Import - Design Proposal

**Importing Cursor IDE memories into Advanced Memory MCP**

---

## Overview

[Cursor IDE](https://cursor.sh) has a built-in "Memories" feature that allows the AI assistant to remember key facts from conversations. This proposal outlines how to import these memories into Advanced Memory MCP.

---

## Cursor Memories Feature

### What Are Cursor Memories?

**Purpose**: Allow Cursor's AI to remember:
- Project-specific conventions
- User preferences
- Coding patterns
- Architectural decisions
- Team standards

**Storage**: Likely stored as:
- `.cursor/` directory (local workspace)
- SQLite database
- JSON files
- Or cloud-synced (Cursor account)

**Format**: Likely includes:
- Memory content (text)
- Timestamp (when created)
- Context (which file/project)
- Tags/categories
- Source (which conversation)

---

## Import Strategy

### Discovery Phase

**Step 1: Locate Cursor memory storage**
```bash
# Likely locations (to investigate):
~/.cursor/memories.db                  # Global memories
~/.cursor/memories.json                # JSON export
.cursor/workspace-memories.json        # Workspace-specific
```

**Step 2: Analyze format**
- Export a few memories manually from Cursor
- Inspect file structure
- Identify fields: content, timestamp, metadata

**Step 3: Design importer**
- Similar to ChatGPT/Claude importers
- Parse Cursor's format → markdown
- Preserve metadata in YAML frontmatter

---

## Implementation Plan

### CLI Command

**Command**: `advanced-memory import cursor`

**Usage**:
```bash
# Auto-detect Cursor memories
advanced-memory import cursor

# Specify memory file
advanced-memory import cursor --file ~/.cursor/memories.json

# Workspace-specific import
advanced-memory import cursor --workspace-only

# Specify destination folder
advanced-memory import cursor --folder cursor-memories
```

**Options**:
- `--file`: Path to Cursor memory export file
- `--workspace-only`: Import only workspace-specific memories
- `--global`: Import global Cursor memories
- `--folder`: Destination folder in project (default: `cursor-memories`)
- `--tag`: Add tags to imported memories (e.g., `cursor,ai-memory`)

---

### File Structure

**Source** (hypothetical Cursor format):
```json
{
  "memories": [
    {
      "id": "mem_abc123",
      "content": "User prefers functional programming style in TypeScript",
      "created_at": "2024-10-15T10:30:00Z",
      "context": {
        "workspace": "/path/to/project",
        "file": "src/utils.ts"
      },
      "tags": ["preference", "typescript"],
      "source_conversation": "conv_xyz789"
    },
    {
      "id": "mem_def456",
      "content": "This project uses Vitest instead of Jest for testing",
      "created_at": "2024-10-16T14:20:00Z",
      "context": {
        "workspace": "/path/to/project"
      },
      "tags": ["convention", "testing"]
    }
  ]
}
```

**Destination** (Advanced Memory markdown):
```markdown
---
title: "Cursor Memory: TypeScript Preferences"
created_at: 2024-10-15T10:30:00Z
tags:
  - cursor-memory
  - preference
  - typescript
source: cursor
cursor_memory_id: mem_abc123
context_file: src/utils.ts
---

# Cursor Memory: TypeScript Preferences

User prefers functional programming style in TypeScript

## Context

- **Workspace**: /path/to/project
- **File**: src/utils.ts
- **Source Conversation**: conv_xyz789
- **Imported**: 2024-10-17T12:00:00Z

## Related

- [[TypeScript Best Practices]]
- [[Functional Programming]]
```

---

### Importer Code Structure

**File**: `src/advanced_memory/importers/cursor_importer.py`

```python
"""Importer for Cursor IDE memories."""

from pathlib import Path
from typing import Any

from advanced_memory.importers.base_importer import BaseImporter, ImportResult
from advanced_memory.schemas.import_data import ImportStats


class CursorImporter(BaseImporter):
    """Import memories from Cursor IDE."""

    async def import_data(
        self, 
        data: dict[str, Any], 
        destination_folder: str = "cursor-memories"
    ) -> ImportResult:
        """Import Cursor memories to markdown files.
        
        Args:
            data: Cursor memory export (JSON)
            destination_folder: Destination folder in project
            
        Returns:
            ImportResult with stats
        """
        memories = data.get("memories", [])
        stats = ImportStats(entities=0, relations=0)
        
        for memory in memories:
            # Convert to markdown
            markdown = self._convert_memory_to_markdown(memory)
            
            # Generate filename
            memory_id = memory.get("id", "unknown")
            filename = f"{memory_id}.md"
            file_path = self.base_path / destination_folder / filename
            
            # Write file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(markdown, encoding="utf-8")
            
            stats.entities += 1
        
        return ImportResult(
            success=True,
            entities=stats.entities,
            relations=0,
            conversations=len(memories),
            messages=0
        )
    
    def _convert_memory_to_markdown(self, memory: dict[str, Any]) -> str:
        """Convert a Cursor memory to markdown format."""
        content = memory.get("content", "")
        created_at = memory.get("created_at", "")
        tags = memory.get("tags", [])
        memory_id = memory.get("id", "")
        context = memory.get("context", {})
        
        # Build YAML frontmatter
        frontmatter = f"""---
title: "Cursor Memory: {content[:50]}"
created_at: {created_at}
tags:
  - cursor-memory
{chr(10).join(f'  - {tag}' for tag in tags)}
source: cursor
cursor_memory_id: {memory_id}
"""
        
        if context.get("file"):
            frontmatter += f"context_file: {context['file']}\n"
        
        frontmatter += "---\n\n"
        
        # Build markdown body
        markdown = frontmatter
        markdown += f"# Cursor Memory\n\n{content}\n\n"
        
        # Add context section
        markdown += "## Context\n\n"
        if context.get("workspace"):
            markdown += f"- **Workspace**: {context['workspace']}\n"
        if context.get("file"):
            markdown += f"- **File**: {context['file']}\n"
        if memory.get("source_conversation"):
            markdown += f"- **Source Conversation**: {memory['source_conversation']}\n"
        
        return markdown
```

**File**: `src/advanced_memory/cli/commands/import_cursor.py`

```python
"""Import command for Cursor IDE memories."""

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel

from advanced_memory.cli.app import import_app
from advanced_memory.config import get_project_config
from advanced_memory.importers.cursor_importer import CursorImporter
from advanced_memory.markdown import EntityParser, MarkdownProcessor

console = Console()


async def get_markdown_processor() -> MarkdownProcessor:
    """Get MarkdownProcessor instance."""
    config = get_project_config()
    entity_parser = EntityParser(config.home)
    return MarkdownProcessor(entity_parser)


@import_app.command(name="cursor", help="Import memories from Cursor IDE.")
def import_cursor(
    memories_file: Annotated[
        Path, typer.Argument(help="Path to Cursor memories export file")
    ] = Path("~/.cursor/memories.json"),
    folder: Annotated[
        str, typer.Option(help="Destination folder within project")
    ] = "cursor-memories",
    workspace_only: Annotated[
        bool, typer.Option(help="Import only workspace-specific memories")
    ] = False,
):
    """Import Cursor IDE memories.
    
    This command will:
    1. Read Cursor memory export file
    2. Convert memories to markdown notes
    3. Preserve metadata in YAML frontmatter
    
    After importing, run 'advanced-memory sync' to index the new files.
    """
    # Expand ~ in path
    memories_file = memories_file.expanduser()
    
    try:
        if not memories_file.exists():
            typer.echo(f"Error: File not found: {memories_file}", err=True)
            typer.echo("\nTo export memories from Cursor:", err=True)
            typer.echo("  1. Open Cursor IDE", err=True)
            typer.echo("  2. Go to Settings > AI > Memories", err=True)
            typer.echo("  3. Click 'Export Memories'", err=True)
            raise typer.Exit(1)
        
        # Get markdown processor
        markdown_processor = asyncio.run(get_markdown_processor())
        config = get_project_config()
        
        # Create importer
        importer = CursorImporter(config.home, markdown_processor)
        
        # Process the file
        base_path = config.home / folder
        console.print(f"\nImporting Cursor memories from {memories_file}...")
        console.print(f"Writing to {base_path}")
        
        # Load JSON
        with memories_file.open("r", encoding="utf-8") as file:
            json_data = json.load(file)
        
        # Filter if workspace-only
        if workspace_only:
            workspace_path = str(Path.cwd())
            memories = json_data.get("memories", [])
            filtered = [
                m for m in memories 
                if m.get("context", {}).get("workspace") == workspace_path
            ]
            json_data["memories"] = filtered
            console.print(
                f"Filtered to {len(filtered)} workspace-specific memories"
            )
        
        # Run import
        result = asyncio.run(importer.import_data(json_data, folder))
        
        if not result.success:
            typer.echo(f"Error during import: {result.error_message}", err=True)
            raise typer.Exit(1)
        
        # Show results
        console.print(
            Panel(
                f"[green]Import complete![/green]\n\n"
                f"Imported {result.conversations} Cursor memories",
                expand=False,
            )
        )
        
        console.print("\nRun 'advanced-memory sync' to index the new files.")
    
    except Exception as e:
        logger.error("Import failed")
        typer.echo(f"Error during import: {e}", err=True)
        raise typer.Exit(1) from e
```

---

## Alternative: Direct Cursor API Integration

If Cursor provides an API or plugin system:

**Option 1: Cursor Extension**
- Build Cursor extension that auto-exports memories
- Watches for new memories
- Auto-syncs to Advanced Memory

**Option 2: Cursor API Integration**
- Use Cursor API (if available) to fetch memories programmatically
- No manual export needed
- Real-time sync

**Option 3: SQLite Direct Read**
- If Cursor uses SQLite, read directly from database
- More brittle (breaks if Cursor changes format)
- But no export step needed

---

## Testing Strategy

1. **Manual Export Test**:
   - Create test memories in Cursor
   - Export manually
   - Run importer
   - Verify markdown output

2. **Format Validation**:
   - Test with various memory types
   - Test with missing fields
   - Test with special characters

3. **Integration Test**:
   - Import → Sync → Search
   - Verify full pipeline

---

## Future Enhancements

1. **Bi-directional Sync**:
   - Export Advanced Memory notes → Cursor memories
   - Keep in sync automatically

2. **Conflict Resolution**:
   - Detect duplicate memories
   - Merge or keep both

3. **Selective Import**:
   - Filter by tags
   - Filter by date range
   - Filter by workspace

4. **Analytics**:
   - Show memory usage stats
   - Most referenced memories
   - Memory age distribution

---

## Status

**Current**: Proposal phase  
**Next Steps**:
1. Research Cursor memory storage format
2. Create prototype importer
3. Test with real Cursor memories
4. Implement CLI command

---

*Proposal created: 2025-10-17*

