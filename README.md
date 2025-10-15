[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![PyPI version](https://badge.fury.io/py/advanced-memory.svg)](https://badge.fury.io/py/advanced-memory)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/basicmachines-co/advanced-memory/workflows/Tests/badge.svg)](https://github.com/basicmachines-co/advanced-memory/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![](https://badge.mcpx.dev?type=server 'MCP Server')
![](https://badge.mcpx.dev?type=dev 'MCP Dev')
[![smithery badge](https://smithery.ai/badge/@basicmachines-co/advanced-memory)](https://smithery.ai/server/@basicmachines-co/advanced-memory)

# Advanced Memory

> **Intelligent Knowledge Platform with AI-Curated Zettelkästen**

Build persistent knowledge through conversations with LLMs. Get 50-150 curated notes from day one based on your interests. Everything stays in Markdown files on your computer.

[Quick Start](#quick-start) | [Documentation](docs/) | [Discord](https://discord.gg/tyvKNccgqN)

## ✨ Key Features

- 🎨 **Personalized Starter Zettelkästen** - 50-150 curated notes from day one based on your interests
- 💰 **Cost-Conscious** - Free FOSS LLMs or affordable hybrid ($10-15/month)
- 🛡️ **Bulletproof Sync** - Never hangs on large files or malformed content
- 🎯 **Portmanteau Tools** - 40+ tools in just 8 (solves tool explosion)
- 🧪 **Self-Testing** - Only MCP with built-in validation

[See all features →](docs/features/)

## 🚀 Quick Start

### 1. Install
```bash
pip install advanced-memory
```

### 2. Configure Claude Desktop
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

### 3. Start Using
```
You: "Create a note about Python decorators"
Claude: ✓ Created note in your knowledge base

You: "Search for async patterns"
Claude: Found 3 notes about async patterns...
```

[Detailed installation →](INSTALLATION.md) | [Full user guide →](docs/user-guide/)

## 💡 Use Cases

### For Researchers
- Personal knowledge management
- Literature review organization
- Research notes and citations
[Learn more →](docs/user-guide/research.md)

### For Developers
- Code snippets and patterns
- Technical documentation
- Project notes and TODOs
[Learn more →](docs/user-guide/development.md)

### For Students
- Course notes and study materials
- Essay research and drafts
- Exam preparation
[Learn more →](docs/user-guide/students.md)

## 📚 Documentation

- **User Guide**
  - [Memory Access](docs/user-guide/memory-access.md) - Read & search
  - [Memory Writing](docs/user-guide/memory-writing.md) - Create & organize

- **Zettelkasten**
  - [Getting Started](docs/zettelkasten/getting-started.md) - Your first Zettelkasten
  - [LLM Generation](docs/zettelkasten/generation.md) - AI-assisted content
  - [Cost Guide](docs/zettelkasten/cost-guide.md) - Don't go bankrupt!

- **Integration**
  - [Claude Desktop](docs/integrations/claude.md) - Full setup guide
  - [Cursor IDE](docs/integrations/cursor.md) - IDE integration
  - [Obsidian](docs/integrations/obsidian.md) - Visual editing

[Complete documentation →](docs/)

## 🤝 Community & Support

- [Discord](https://discord.gg/tyvKNccgqN) - Chat with community
- [GitHub Discussions](https://github.com/basicmachines-co/advanced-memory-mcp/discussions) - Q&A
- [GitHub Issues](https://github.com/basicmachines-co/advanced-memory-mcp/issues) - Bug reports
- [Contributing Guide](CONTRIBUTING.md) - Help improve Advanced Memory

## 📄 License

AGPL-3.0 - See [LICENSE](LICENSE)

