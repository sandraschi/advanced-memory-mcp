# Quick Start Guide
## Get Advanced Memory Running in 5 Minutes

## What is a Zettelkasten?

**Zettelkasten** (German: "slip box" or "note box") is a method of note-taking and knowledge management developed by German sociologist Niklas Luhmann. He used it to write 70 books and 400+ articles.

**Handbibliothek** (German: "hand library") refers to the personal reference library scholars kept within arm's reach of their Zettelkasten.

**Famous Zettelkästen in History**:
- **Niklas Luhmann** (1927-1998): 90,000 index cards, revolutionized sociology
- **Arno Schmidt** (1914-1979): Writer with massive card collection
- **Walter Benjamin** (1892-1940): Philosopher's extensive note system
- **Roland Barthes** (1915-1980): Literary theorist's fichier boîte

Modern digital versions let you create these powerful knowledge systems without 90,000 physical cards!

---

## 🚀 Installation

### Option 1: Quick Install (Recommended)
```bash
pip install advanced-memory
```

### Option 2: From Source
```bash
git clone https://github.com/basicmachines-co/advanced-memory-mcp.git
cd advanced-memory-mcp
pip install -e .
```

---

## 🔧 Configure Claude Desktop

**1. Find your config file:**
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**2. Add Advanced Memory:**
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

**3. Restart Claude Desktop**

---

## ✨ First Steps

### 1. Create Your First Note
```
You: "Create a note about Python decorators"
Claude: ✓ Created note in your knowledge base
```

### 2. Search Your Notes
```
You: "Search for async patterns"
Claude: Found 3 notes about async patterns...
```

### 3. Build Knowledge Connections
```
You: "Create a note about FastAPI that links to my async patterns note"
Claude: ✓ Created note with connection to [[Async Patterns]]
```

---

## 🎨 Get a Personalized Starter Zettelkasten

Instead of starting with an empty system:

```bash
# Run the onboarding wizard
advanced-memory onboard

# Answer a few questions about your interests
# Get 50-150 curated notes instantly!
```

**What you get**:
- **Developers**: JavaScript, Python, DevOps, AI/ML notes
- **Cooking Enthusiasts**: Techniques, recipes, kitchen science
- **AI Enthusiasts**: Latest AI news, history, Claude templates
- **Philosophers**: Consolations, neurophilosophy, critical thinking

**Cost**: Free with FOSS LLMs (Ollama), or $10-15/month hybrid approach

See [Cost Guide](docs/zettelkasten/cost-guide.md) for details.

---

## 📚 What's Next?

### Learn the Basics
- [Memory Access Guide](docs/user-guide/memory-access.md) - Read and search
- [Memory Writing Guide](docs/user-guide/memory-writing.md) - Create and organize

### Build Your Zettelkasten
- [Getting Started](docs/zettelkasten/getting-started.md) - Your first Zettelkasten
- [LLM Generation](docs/zettelkasten/generation.md) - AI-assisted content
- [Cost Guide](docs/zettelkasten/cost-guide.md) - Don't go bankrupt!

### Integration
- [Claude Desktop](docs/integrations/claude.md) - Full setup guide
- [Cursor IDE](docs/integrations/cursor.md) - IDE integration
- [Obsidian](docs/integrations/obsidian.md) - Visual editing

---

## 🆘 Need Help?

- **Discord**: [Join our community](https://discord.gg/tyvKNccgqN)
- **GitHub Issues**: [Report bugs](https://github.com/basicmachines-co/advanced-memory-mcp/issues)
- **Discussions**: [Ask questions](https://github.com/basicmachines-co/advanced-memory-mcp/discussions)

---

## 💡 Pro Tips

1. **Start small**: Create 5-10 notes manually to understand the system
2. **Use templates**: Claude can help you create note templates
3. **Link everything**: Use `[[Note Name]]` syntax to connect ideas
4. **Tag strategically**: Use tags for broad categories
5. **Export regularly**: Use `advanced-memory export` to backup

---

**You're ready!** Start building your knowledge empire! 🚀

*Following in the footsteps of Luhmann, Schmidt, and Benjamin - but with AI assistance!*
