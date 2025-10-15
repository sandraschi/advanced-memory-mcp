# MCP Basics Guide
## Understanding the Model Context Protocol

## 🤖 What is MCP?

**MCP (Model Context Protocol)** is a revolutionary standard that allows Large Language Models like Claude to securely access and manipulate external tools and data sources.

### The Problem MCP Solves

Before MCP, AI assistants were limited to:
- Text-only conversations
- No access to your local files
- No ability to run commands
- Ephemeral memory (forgot everything between conversations)

**With MCP, Claude can:**
- Read and write files on your computer
- Execute commands and scripts
- Access databases and APIs
- Maintain persistent knowledge across conversations
- Use specialized tools for specific tasks

### How MCP Works

```
┌─────────────────┐    MCP Protocol    ┌──────────────────┐
│   Claude Desktop │◄─────────────────►│ Advanced Memory  │
│                 │                    │   MCP Server     │
│ • Chat Interface│                    │                  │
│ • File Access   │                    │ • Knowledge Base │
│ • Tool Calling  │                    │ • Note Management│
└─────────────────┘                    │ • Search & Sync  │
                                       └──────────────────┘
```

**The Flow:**
1. You ask Claude a question
2. Claude decides which MCP tools to use
3. Claude sends tool requests to Advanced Memory
4. Advanced Memory executes the tools and returns results
5. Claude incorporates the results into its response

## 🛠️ Advanced Memory's MCP Tools

Advanced Memory provides **40+ specialized tools** organized into **8 portmanteau tools** for maximum compatibility:

### Core Tools (Portmanteau Architecture)

| Tool | Purpose | Key Functions |
|------|---------|---------------|
| **`adn_editor`** | Note editing & management | create, read, edit, delete, move notes |
| **`adn_search`** | Finding content | full-text search, recent activity, context building |
| **`adn_navigation`** | Knowledge graph traversal | browse folders, explore connections, list content |
| **`adn_export`** | Content export | HTML, PDF, Docsify, Joplin, Pandoc formats |
| **`adn_import`** | Data migration | Obsidian, Notion, Evernote, Joplin vaults |
| **`adn_knowledge`** | Bulk operations | tag management, content consolidation, project stats |
| **Project Management** | Multi-project support | switch projects, create/delete projects |
| **Status & Sync** | System monitoring | sync status, diagnostics, health checks |

### Individual Tools Available

**Content Creation:**
- `write_note(title, content, folder)` - Create new notes with semantic linking
- `edit_note(identifier, operation)` - Modify existing notes surgically
- `move_note(identifier, destination)` - Relocate notes with link preservation

**Content Access:**
- `read_note(identifier)` - Retrieve full note content with context
- `view_note(identifier)` - Display notes in formatted artifacts
- `read_content(path)` - Access raw file content (images, binaries)

**Knowledge Discovery:**
- `search_notes(query)` - Full-text search with filtering
- `build_context(url, depth)` - Navigate knowledge graph connections
- `recent_activity(timeframe)` - See what changed recently

**Organization:**
- `list_directory(path)` - Browse folder structure
- `project_management` - Multi-project workflow support

**Export & Import:**
- `export_html_notes()` - Create standalone HTML websites
- `export_pandoc()` - Convert to PDF, Word, HTML, 40+ formats
- `load_obsidian_vault()` - Import Obsidian knowledge bases
- `load_notion_export()` - Migrate Notion workspaces

## 🚀 Getting Started with MCP

### 1. Installation

First, install and configure Advanced Memory (see [Installation Guide](../../INSTALLATION.md)).

### 2. Claude Desktop Configuration

**Automatic Setup (Recommended):**
```bash
npx @modelcontextprotocol/inspector npx -y @smithery/cli@latest install @basicmachines-co/advanced-memory --client claude
```

**Manual Setup:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "advanced-memory",
      "args": ["mcp"]
    }
  }
}
```

### 3. Test the Connection

Restart Claude Desktop and ask:
```
You: "What MCP tools do you have available?"
Claude: I can see Advanced Memory tools including adn_editor, adn_search, adn_navigation...
```

## 💬 How to Use MCP Effectively

### Natural Language Commands

**Instead of technical tool calls, use natural language:**

```
❌ Technical: "Use adn_editor_write_note with title 'Python Tips' and content '...'"

✅ Natural: "Create a note about Python tips I should know"
```

Claude automatically selects the right tools and handles the technical details.

### Conversational Workflow

**Build knowledge iteratively:**

```
You: "Create a note about Docker basics"
Claude: ✓ Created note: "Docker Basics"

You: "Add Docker Compose examples to that note"
Claude: ✓ Updated note with Docker Compose section

You: "Link it to my containerization concepts note"
Claude: ✓ Added wikilink to [[Containerization]]
```

### Context Preservation

**MCP enables persistent context across conversations:**

```
Today:
You: "Create a note about React hooks"
Claude: ✓ Created "React Hooks" note

Tomorrow:
You: "Update my React hooks note with the new useEffect changes"
Claude: [Automatically loads and updates the existing note]
```

## 🎯 MCP Tool Categories

### Content Management Tools

**Creating & Editing:**
```python
# Natural language approach
"Create a note about async programming patterns"

# Behind the scenes: write_note() tool
# Creates: async-programming-patterns.md
# With semantic links and proper formatting
```

**Reading & Searching:**
```python
# "Find my notes about Python decorators"
# Behind the scenes: search_notes() + read_note()
# Returns formatted results with context
```

### Knowledge Graph Tools

**Navigation:**
```python
# "Show me what's connected to my Python basics note"
# Uses: build_context() with depth=2
# Returns: related notes, backlinks, recent changes
```

**Context Building:**
```python
# "Give me context about my current project"
# Uses: recent_activity() + list_directory()
# Builds comprehensive project overview
```

### Export & Integration Tools

**Document Generation:**
```python
# "Export all my Python notes as a PDF book"
# Uses: make_pdf_book() with pandoc backend
# Creates: professional-formatted PDF
```

**Knowledge Import:**
```python
# "Import my Obsidian vault"
# Uses: load_obsidian_vault() with link conversion
# Migrates: all notes, preserving wikilinks
```

## 🔧 Advanced MCP Usage

### Tool Chaining

Claude can combine multiple tools automatically:

```
You: "Research React 18 features and create organized notes"

Claude's workflow:
1. Uses web search tools to research React 18
2. Creates multiple interconnected notes
3. Links related concepts
4. Tags appropriately
5. Provides summary of created content
```

### Context Awareness

**MCP tools share context:**

```
You: "Update my FastAPI note"
Claude: [Loads existing FastAPI note automatically]

You: "Add authentication examples"
Claude: [Appends to the already-loaded note]
```

### Error Handling

**MCP provides intelligent error recovery:**

```
Tool fails: "Note 'xyz' not found"
Claude: "I couldn't find that note. Did you mean one of these: [suggestions]"
```

## 🏗️ MCP Architecture Benefits

### Why Portmanteau Tools Matter

**The Tool Explosion Problem:**
- Standard MCP servers expose 50+ individual tools
- Cursor IDE limits: **50 tools maximum**
- Result: Many powerful servers are **unusable in Cursor**

**Advanced Memory Solution:**
- **8 portmanteau tools** with `adn_` prefix
- Each tool handles multiple related operations
- **Universal compatibility** across all MCP clients
- **No functionality lost** - just better organized

### Performance & Compatibility

**Optimized for all clients:**
- ✅ **Cursor IDE**: Full compatibility (8 tools)
- ✅ **Claude Desktop**: Native support
- ✅ **VS Code**: MCP extension compatible
- ✅ **Future clients**: Ready for broader adoption

## 🐛 Troubleshooting MCP Issues

### "Tools not appearing"

**Symptoms:** Claude doesn't see Advanced Memory tools

**Solutions:**
```bash
# Check configuration syntax
python -c "import json; json.load(open('path/to/claude_desktop_config.json'))"

# Verify installation
advanced-memory --version

# Restart Claude Desktop completely
# (Quit and reopen, not just refresh)
```

### "Tool execution failed"

**Symptoms:** Tools run but return errors

**Solutions:**
```bash
# Check sync status
advanced-memory status

# Force reindex
advanced-memory reindex

# Check file permissions
ls -la ~/.advanced-memory/
```

### "Slow tool responses"

**Symptoms:** Tools take long to respond

**Solutions:**
```bash
# Check database size
du -sh ~/.advanced-memory/

# Optimize search index
advanced-memory reindex

# Check system resources
top  # or Task Manager
```

### "Connection lost"

**Symptoms:** Tools work then suddenly stop

**Solutions:**
- Restart Claude Desktop
- Check if Advanced Memory process crashed
- Verify configuration didn't change
- Update to latest version

## 🔄 MCP vs Traditional APIs

### Traditional Approach
```
Application → API Calls → Database
LLM has no direct access
```

### MCP Approach
```
LLM → MCP Protocol → Tools → Direct file/database access
LLM acts as peer, not just client
```

### Benefits of MCP

**For Users:**
- **Natural conversations** instead of API calls
- **Persistent context** across sessions
- **Direct tool access** without intermediaries

**For AI Assistants:**
- **Tool selection** based on context
- **Error recovery** and intelligent fallbacks
- **Multi-step workflows** with state preservation

## 🚀 Future of MCP

### Emerging Standards

**MCP is evolving rapidly:**
- Resource access patterns
- Streaming responses
- Tool chaining standards
- Cross-server communication

### Advanced Memory Leadership

**We're pushing MCP boundaries:**
- Portmanteau tool architecture
- Comprehensive knowledge graph integration
- Multi-modal content support (text, images, diagrams)
- Enterprise-grade reliability

## 📚 Learn More

### Documentation Links

- [Memory Access Guide](memory-access.md) - Reading and searching
- [Memory Writing Guide](memory-writing.md) - Creating and organizing
- [Installation Guide](../../INSTALLATION.md) - Setup and configuration
- [Zettelkasten System](../zettelkasten/) - Advanced knowledge management

### Community Resources

- **Discord**: [MCP discussions](https://discord.gg/tyvKNccgqN)
- **GitHub**: [MCP specification](https://github.com/modelcontextprotocol/specification)
- **Smithery**: [MCP server registry](https://smithery.ai/)

---

**Ready to harness the power of MCP?** Start with [Quick Start](../../QUICKSTART.md) and let Claude become your knowledge management co-pilot!

*MCP: Where AI meets your data, naturally! 🤖🔗*
