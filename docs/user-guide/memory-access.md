# Memory Access Guide
## Reading and Searching Your Knowledge Base

## 🔍 Searching Your Notes

### Basic Search

Ask Claude to search for you:

```
You: "Search for Python decorators"
Claude: Found 3 notes about decorators...
```

Behind the scenes, this uses:
```python
advanced-memory search "Python decorators"
```

### Advanced Search

**By tags**:
```
You: "Find all notes tagged 'python' and 'advanced'"
```

**By date**:
```
You: "Show me notes created this week"
```

**By content**:
```
You: "Find notes mentioning FastAPI and async"
```

## 📖 Reading Notes

### Direct Access

```
You: "Show me my note about async patterns"
Claude: [Displays full note content]
```

### Browse by Category

```
You: "What notes do I have about web development?"
Claude: You have 15 notes in web-development/:
- REST API Design
- GraphQL Basics
- ...
```

### Follow Links

```
You: "Show me the note about decorators, and then show related notes"
Claude: [Shows decorator note, then follows wikilinks to related concepts]
```

## 🗺️ Navigating Your Knowledge Graph

### See Connections

```
You: "What notes link to my Python basics note?"
Claude: 7 notes link to Python Basics:
- Decorators
- Async Programming
- ...
```

### Explore Topics

```
You: "Show me everything related to AI"
Claude: Found 23 notes about AI across 4 categories...
```

## 📊 Viewing Structure

### List Folders

```
You: "What folders do I have?"
Claude: Your knowledge base has 8 folders:
- development/
- cooking/
- ai-research/
...
```

### Browse Hierarchy

```
You: "Show me what's in my development folder"
Claude: development/ contains:
├── python/
│   ├── decorators.md
│   └── async-patterns.md
└── javascript/
    └── react-hooks.md
```

## 🎯 Smart Features

### Context Building

Advanced Memory automatically provides relevant context to Claude:

```
You: "Update my FastAPI note with CORS information"
Claude: [Automatically loads FastAPI note, adds CORS section]
```

### Recent Activity

```
You: "What have I added to my knowledge base this week?"
Claude: This week you added 12 notes, including:
- WebSocket Patterns (today)
- Database Indexing (yesterday)
...
```

### Related Suggestions

```
You: "I'm reading about React hooks"
Claude: Related notes you might find useful:
- State Management Patterns
- Component Lifecycle
- Custom Hooks Examples
```

## 📱 Export and Share

### Export Single Note

```
You: "Export my Python decorators note as PDF"
Claude: ✓ Exported to python-decorators.pdf
```

### Export Collection

```
You: "Export all my Python notes as a website"
Claude: ✓ Created Docsify site in exports/python-docs/
```

### Share with Others

```bash
# Export as Markdown
advanced-memory export --format markdown --output my-notes.zip

# Export as HTML
advanced-memory export --format html --output my-notes-website/
```

## 🔒 Privacy & Security

**Your data stays local**:
- All notes stored in Markdown files on your computer
- No cloud sync (unless you configure it)
- Full control over your knowledge base

**File locations**:
- **Mac**: `~/Documents/advanced-memory/`
- **Windows**: `%USERPROFILE%\Documents\advanced-memory\`
- **Linux**: `~/advanced-memory/`

## 💡 Pro Tips

1. **Use natural language**: Ask Claude like you'd ask a person
2. **Be specific**: "Python async patterns" vs "async"
3. **Follow connections**: Explore wikilinks to discover related content
4. **Regular searches**: Search often to rediscover old notes
5. **Export regularly**: Back up your knowledge base

## 🆘 Troubleshooting

### "Note not found"
- Check spelling of note title
- Use search instead of direct access
- Verify note exists: `advanced-memory list`

### "Search returns no results"
- Try broader search terms
- Check if notes are synced: `advanced-memory status`
- Rebuild search index: `advanced-memory reindex`

### "Can't access notes"
- Verify Advanced Memory is running
- Check Claude Desktop configuration
- Restart Claude Desktop

---

**Next**: [Memory Writing Guide](memory-writing.md) - Learn to create and organize content

*Your knowledge, always at your fingertips!*





