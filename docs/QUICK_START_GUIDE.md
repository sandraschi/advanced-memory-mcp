# Advanced Memory MCP - Quick Start Guide

**Version:** 1.0.0b2  
**For:** New users getting started quickly

## 🚀 5-Minute Setup

### 1. Install Advanced Memory MCP

```bash
pip install advanced-memory-mcp
```

### 2. Initialize Database

```bash
advanced-memory init
```

### 3. Configure Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "ADVANCED_MEMORY_HOME": "C:/Users/username"
      }
    }
  }
}
```

### 4. Create Your First Project

```bash
advanced-memory project add main "~/Documents/notes"
advanced-memory sync
```

### 5. Restart Claude Desktop

That's it! You're ready to use Advanced Memory MCP.

---

## 🎯 Essential Commands

### In Claude Desktop, try these:

```python
# List your projects
adn_project("list")

# Create a note
adn_content("write", 
    title="My First Note", 
    content="# Hello World\n\nThis is my first note!",
    folder="getting-started")

# Search your notes
adn_search("notes", query="hello")

# Get recent activity
adn_navigation("recent", timeframe="today")
```

---

## 📚 Key Concepts

### Projects
- **Projects** = Collections of markdown files
- **Default Project** = Active project for operations
- **Multi-project** = Manage multiple knowledge bases

### Knowledge Graph
- **Entities** = Your markdown notes
- **Observations** = Facts with categories: `- [category] content`
- **Relations** = Links between notes: `- relation_type [[Target]]`

### Portmanteau Tools
- **8 consolidated tools** instead of 50+ individual tools
- **Consistent API** across all operations
- **Cursor IDE optimized** for AI coding assistants

---

## 🔧 Essential Tools

### adn_content - Content Management
```python
# Write notes
adn_content("write", title="Note Title", content="Content", folder="folder")

# Read notes  
adn_content("read", identifier="Note Title")

# Edit notes
adn_content("edit", identifier="Note Title", operation="append", content="New content")
```

### adn_project - Project Management
```python
# List projects
adn_project("list")

# Create project
adn_project("create", project_name="research", project_path="~/research")

# Sync project
adn_project("sync", project_name="research")
```

### adn_search - Search & Discovery
```python
# Search notes
adn_search("notes", query="your search terms")

# Search with filters
adn_search("notes", query="AI", project="research")
```

---

## 📁 File Organization

### Recommended Structure

```
~/Documents/notes/           # Your main knowledge base
├── daily/                  # Daily notes
├── projects/               # Project documentation  
├── research/               # Research notes
├── meetings/               # Meeting notes
└── archive/                # Archived content
```

### Markdown Patterns

#### Observations
```markdown
- [definition] Machine learning is a subset of AI
- [example] Linear regression predicts continuous values
- [reference] See [[Deep Learning Book]] Chapter 5
```

#### Relations
```markdown
- builds_on [[Machine Learning Fundamentals]]
- related_to [[Neural Networks]]
- contradicts [[Traditional Statistics]]
```

---

## 🔄 File Synchronization

### Automatic Sync
- **File watcher** monitors all active projects
- **Auto-syncs** when you add/edit/delete `.md` files
- **1-second debounce** waits for typing to finish

### Manual Sync
```bash
# Sync all projects
advanced-memory sync

# Sync specific project (in Claude)
adn_project("sync", project_name="research")
```

---

## 📥 Import Existing Notes

### From Obsidian
```python
adn_import("obsidian", 
    vault_path="~/obsidian-vault",
    destination_folder="imported/obsidian")
```

### From Joplin
```python
adn_import("joplin",
    export_path="~/joplin-export", 
    destination_folder="imported/joplin")
```

### From Notion
```python
adn_import("notion",
    export_path="~/notion-export",
    folder="imported/notion")
```

---

## 📤 Export Your Knowledge

### PDF Book
```python
adn_export("pdf_book",
    book_title="My Knowledge Base",
    source_folder="/research")
```

### HTML Website
```python
adn_export("html",
    export_path="~/website",
    include_index=True)
```

### Docsify Documentation
```python
adn_export("docsify",
    export_path="~/docs",
    site_title="Knowledge Base")
```

---

## 🆘 Quick Troubleshooting

### Claude Can't Connect
1. Check `claude_desktop_config.json` syntax
2. Verify `ADVANCED_MEMORY_HOME` path
3. Restart Claude Desktop

### Files Not Syncing
1. Check file watcher status: `adn_navigation("sync_status")`
2. Manual sync: `adn_project("sync", project_name="main")`
3. Restart Claude Desktop

### Import Failures
1. Verify source paths exist
2. Check file permissions
3. Check log files for details

---

## 📖 Next Steps

1. **Explore the Knowledge Graph**: Use `adn_navigation("context")` to explore relationships
2. **Import Existing Notes**: Migrate from your current system
3. **Create Project Structure**: Organize by topics, projects, or time
4. **Use Advanced Features**: Research orchestration, bulk operations
5. **Export Regularly**: Create backups and shareable formats

---

## 🔗 Resources

- **Complete Guide**: [ADVANCED_MEMORY_MCP_COMPLETE_GUIDE.md](ADVANCED_MEMORY_MCP_COMPLETE_GUIDE.md)
- **GitHub Repository**: https://github.com/sandraschi/advanced-memory-mcp
- **MCPB Package**: Download `.mcpb` file for one-click installation
- **Issues & Support**: GitHub Issues page

---

**Welcome to Advanced Memory MCP!** 🎉

Start with simple notes and gradually explore the advanced features. The knowledge graph will grow organically as you add more content and relationships.
