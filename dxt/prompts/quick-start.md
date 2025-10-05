# Advanced Memory MCP - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install the Package
- Drop `advanced-memory-mcp.mcpb` into Claude Desktop extensions
- Configure your project path in settings
- Enable portmanteau tools (recommended)

### 2. Create Your First Note
```python
# Create a simple note
adn_content("write", identifier="Welcome Note", content="# Welcome to Advanced Memory\n\nThis is your first note!", folder="getting-started")
```

### 3. List Your Projects
```python
# See available projects
adn_project("list")
```

### 4. Search Your Knowledge
```python
# Search for content
adn_search("notes", query="welcome", page=1, page_size=5)
```

### 5. Check System Status
```python
# Verify everything is working
adn_navigation("status")
```

## 🎯 Essential Commands

### Content Management
```python
# Create note
adn_content("write", identifier="Note Title", content="Content here", folder="folder-name")

# Read note
adn_content("read", identifier="Note Title")

# Edit note (add content)
adn_content("edit", identifier="Note Title", edit_operation="append", content="Additional content")
```

### Project Management
```python
# List projects
adn_project("list")

# Switch project
adn_project("switch", project_name="project-name")

# Create project
adn_project("create", project_name="new-project", project_path="/path/to/project")
```

### Search and Discovery
```python
# Search notes
adn_search("notes", query="search term")

# Recent activity
adn_navigation("recent_activity", timeframe="today")

# List directory
adn_navigation("list_directory", dir_name="/folder")
```

## 📁 Common Workflows

### Daily Note Taking
```python
# Create daily note
from datetime import date
adn_content("write", identifier=f"Daily {date.today()}", content="# Daily Note\n\n## Tasks\n- [ ] Task 1\n- [ ] Task 2", folder="daily")
```

### Meeting Notes
```python
# Create meeting note
adn_content("write", identifier="Team Meeting 2024-01-15", content="# Team Meeting\n\n## Attendees\n- Person 1\n- Person 2\n\n## Agenda\n1. Topic 1\n2. Topic 2\n\n## Decisions\n- Decision 1\n- Decision 2", folder="meetings")
```

### Research Notes
```python
# Create research note
adn_content("write", identifier="Research: Machine Learning", content="# Machine Learning Research\n\n## Key Points\n- Point 1\n- Point 2\n\n## Sources\n- Source 1\n- Source 2\n\n## Analysis\nAnalysis here...", folder="research")
```

## 🔧 Configuration Tips

### For Cursor IDE Users
- Enable portmanteau tools in settings
- Set maximum tools to 50 or fewer
- Use `adn_*` tools for best compatibility

### Project Organization
- Create separate projects for different areas (work, personal, research)
- Use folders to organize notes within projects
- Use tags for cross-cutting themes

### Performance
- Use pagination for large search results
- Limit directory depth for better performance
- Regular exports for backup

## 🆘 Need Help?

### Check Status
```python
# System health
adn_navigation("status")

# Sync status
adn_navigation("sync_status")
```

### Validate Setup
```python
# Check content quality
adn_knowledge("validate_content")

# Analyze tags
adn_knowledge("tag_analytics", action={"analyze_usage": True})
```

### Get More Information
- Read the full guide: `prompts/advanced-memory-guide.md`
- Check tool descriptions for detailed parameters
- Visit GitHub for documentation and examples

---

*Ready to explore? Try the commands above and then dive into the full guide for advanced features!*
