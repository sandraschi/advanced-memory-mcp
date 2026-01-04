# Obsidian Integration Guide for Advanced Memory

## Overview

Obsidian is a powerful knowledge base that works on top of a local folder of plain text Markdown files. Advanced Memory provides robust integration with Obsidian, allowing you to leverage both tools together for an enhanced knowledge management workflow.

## Why Use Obsidian with Advanced Memory?

### Obsidian Strengths
- **Visual Knowledge Graph** - See connections between notes
- **Canvas** - Create visual mind maps and diagrams
- **Rich Plugin Ecosystem** - Hundreds of community plugins
- **Beautiful UI** - Native desktop app with live preview
- **Graph View** - Visualize your entire knowledge base

### Advanced Memory Strengths
- **AI Integration** - Natural language interaction via Claude and other LLMs
- **MCP Protocol** - Standard integration with AI assistants
- **Automated Knowledge Building** - AI creates and links notes
- **Semantic Search** - Full-text search with context
- **Multi-Project Support** - Organize separate knowledge bases

### Combined Benefits
✅ **Best of Both Worlds** - Visual editing (Obsidian) + AI assistance (Advanced Memory)
✅ **Bidirectional Sync** - Changes in either tool reflect in the other
✅ **Canvas Visualization** - Create mind maps, view in Obsidian
✅ **Import/Export** - Seamlessly move between tools
✅ **Wikilink Compatibility** - Both support `[[wikilinks]]`

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Workflow Options](#workflow-options)
3. [Importing Obsidian Vaults](#importing-obsidian-vaults)
4. [Creating Canvas Files](#creating-canvas-files)
5. [Exporting to Obsidian](#exporting-to-obsidian)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Installation & Setup

### Prerequisites

1. **Install Obsidian**
   ```bash
   # Download from https://obsidian.md
   # Or use package managers:

   # macOS
   brew install --cask obsidian

   # Windows
   winget install Obsidian.Obsidian

   # Linux
   flatpak install flathub md.obsidian.Obsidian
   ```

2. **Install Advanced Memory**
   ```bash
   # Install with uv (recommended)
   uv tool install advanced-memory

   # Or with pip
   pip install advanced-memory

   # Or with Homebrew
   brew install advanced-memory
   ```

3. **Configure Claude Desktop** (for AI integration)
   ```json
   {
     "mcpServers": {
       "advanced-memory": {
         "command": "uvx",
         "args": ["advanced-memory", "mcp"]
       }
     }
   }
   ```

### Configuration

#### Option 1: Use Obsidian Vault as Advanced Memory Project

Point Advanced Memory directly at your Obsidian vault:

```bash
# Create a new project pointing to your Obsidian vault
advanced-memory project add my-vault ~/Documents/ObsidianVault

# Set it as default
advanced-memory project set-default my-vault

# Start sync
advanced-memory sync --watch
```

**Benefits:**
- ✅ Single source of truth
- ✅ Real-time sync between tools
- ✅ No duplication

**Considerations:**
- ⚠️ Advanced Memory adds `.advanced-memory/` metadata folder
- ⚠️ Both tools write to the same files simultaneously

#### Option 2: Import Obsidian Vault into Advanced Memory

Import a copy of your vault into Advanced Memory:

```bash
# Use Claude Desktop with Advanced Memory MCP
# In Claude:
"Import my Obsidian vault from ~/Documents/ObsidianVault"
```

Or via CLI:
```bash
# Using MCP tools via CLI
advanced-memory tools load-obsidian-vault \
  --vault-path ~/Documents/ObsidianVault \
  --destination-folder imported/obsidian \
  --preserve-structure true \
  --convert-links true
```

**Benefits:**
- ✅ Independent knowledge bases
- ✅ Safe experimentation
- ✅ Version control

**Considerations:**
- ⚠️ Manual sync required
- ⚠️ Changes need to be synchronized

---

## Workflow Options

### Workflow 1: Obsidian as Primary Editor

**Use Case:** You prefer Obsidian's visual editor but want AI assistance.

**Setup:**
1. Point Advanced Memory at Obsidian vault (Option 1)
2. Edit in Obsidian
3. Ask Claude to analyze/extend your notes
4. Claude updates files in the vault
5. Obsidian auto-reloads changes

**Example:**
```
You (in Obsidian): Create note "Coffee Brewing Methods.md"
You (in Claude): "Summarize my coffee brewing notes and add espresso techniques"
Claude: [Reads, analyzes, adds content]
You (in Obsidian): [See updated content with espresso section]
```

### Workflow 2: Advanced Memory as Primary, Obsidian for Visualization

**Use Case:** You want AI to build your knowledge base, then visualize in Obsidian.

**Setup:**
1. Use Advanced Memory to create notes via Claude
2. Open Obsidian in the Advanced Memory project folder
3. Use Obsidian's Graph View to visualize connections
4. Use Canvas to create mind maps

**Example:**
```
You (in Claude): "Research quantum computing and create notes"
Claude: [Creates interconnected notes about quantum computing]
You (in Obsidian): Open Graph View → See visual network
You (in Obsidian): Create Canvas → Visual mind map
```

### Workflow 3: Bidirectional Collaboration

**Use Case:** Leverage both tools for their strengths.

**Setup:**
1. Use shared folder approach
2. Edit visual/creative content in Obsidian
3. Use Claude for research and content generation
4. Sync automatically via watch mode

**Example:**
```
Morning (Obsidian): Sketch out project structure in Canvas
Afternoon (Claude): "Fill in project details and add research"
Evening (Obsidian): Review in Graph View, refine connections
```

---

## Importing Obsidian Vaults

### Full Vault Import

Import an entire Obsidian vault into Advanced Memory:

**Via Claude Desktop:**
```
"Import my Obsidian vault from ~/Documents/MyVault into advanced-memory folder"
```

**Via CLI Tool:**
```bash
advanced-memory tools load-obsidian-vault \
  --vault-path ~/Documents/MyVault \
  --destination-folder obsidian-import \
  --preserve-structure true \
  --convert-links true \
  --include-attachments false
```

**Parameters:**
- `vault-path`: Path to Obsidian vault root
- `destination-folder`: Where to place imported notes in Advanced Memory
- `preserve-structure`: Keep folder hierarchy (default: true)
- `convert-links`: Convert `[[wikilinks]]` to Advanced Memory entities (default: true)
- `include-attachments`: Import images/files (default: false)
- `skip-existing`: Skip notes already in Advanced Memory (default: true)

### Selective Import

Import specific folders or notes:

```
"Import only my research notes from ~/Documents/MyVault/Research"
```

### Import Results

After import, you'll see:
- ✅ Number of notes imported
- ✅ Number of links converted
- ✅ Folder structure preserved
- ✅ Metadata extracted (tags, frontmatter)
- ⚠️ Any warnings or skipped files

---

## Creating Canvas Files

Advanced Memory can create Obsidian Canvas files that visualize your knowledge graph.

### What is Canvas?

Obsidian Canvas is a visual tool for:
- Creating mind maps
- Connecting related notes
- Visualizing workflows
- Building project boards

### Creating a Canvas

**Via Claude:**
```
"Create a canvas showing my coffee-related notes and their connections"
```

**Via MCP Tool:**
```python
# Canvas structure
{
  "nodes": [
    {"id": "1", "type": "file", "file": "Coffee Basics.md", "x": 0, "y": 0},
    {"id": "2", "type": "text", "text": "Brewing Methods", "x": 200, "y": 0},
    {"id": "3", "type": "file", "file": "Espresso.md", "x": 400, "y": 0}
  ],
  "edges": [
    {"id": "e1", "fromNode": "1", "toNode": "2"},
    {"id": "e2", "fromNode": "2", "toNode": "3"}
  ]
}
```

**Example Usage:**
```
You: "Create a canvas for my project management notes"
Claude: [Creates canvas.canvas file with:
  - Project nodes
  - Task connections
  - Reference links
]
You: Open in Obsidian → Beautiful visual mind map!
```

### Canvas Best Practices

1. **Group by Topic** - Use colors to categorize nodes
2. **Logical Layout** - Left-to-right flow for processes
3. **Link Related Notes** - Connect notes that reference each other
4. **Add Context** - Use text nodes for explanations
5. **Keep It Focused** - One canvas per major topic

---

## Exporting to Obsidian

### Export Single Note

Export a note from Advanced Memory to Obsidian format:

```bash
# Via CLI
advanced-memory tools write-note \
  --title "My Note" \
  --content "# My Note\n\nContent here" \
  --folder "obsidian-export"
```

### Export Entire Project

Export your Advanced Memory project as an Obsidian vault:

```
"Export my advanced-memory project to ~/Documents/ObsidianExport"
```

This creates:
- ✅ All notes as `.md` files
- ✅ Preserved folder structure
- ✅ Wikilinks maintained
- ✅ Frontmatter metadata
- ✅ Tags and properties

### Export Format

Advanced Memory exports are fully compatible with Obsidian:

```markdown
---
title: Coffee Brewing
tags: [coffee, brewing, methods]
created: 2025-01-10
---

# Coffee Brewing

## Overview
Different methods for brewing coffee.

## Methods
- [[Pour Over]]
- [[French Press]]
- [[Espresso]]

## Related
- [coffeeTechniques] Great for beginners
- related to [[Coffee Beans]]
```

---

## Best Practices

### 1. Folder Structure

Organize both tools with consistent structure:

```
knowledge-base/
├── 00-inbox/           # Quick captures
├── 01-projects/        # Active projects
├── 02-areas/           # Areas of responsibility
├── 03-resources/       # Reference materials
├── 04-archive/         # Completed/old content
└── .advanced-memory/   # Advanced Memory metadata (gitignore this)
```

### 2. Wikilink Format

Both tools support `[[wikilinks]]`:

```markdown
# Best Practices

Use [[wikilinks]] for connections:
- [[Related Topic]]
- [[Another Note|Display Text]]
- [[Nested/Folder/Note]]
```

### 3. Frontmatter

Use YAML frontmatter for metadata:

```markdown
---
title: My Note
tags: [tag1, tag2]
created: 2025-01-10
updated: 2025-01-10
---

# Content starts here
```

### 4. Tags

Consistent tagging:
- Use `#` for inline tags: `#important`
- Use `tags:` in frontmatter: `tags: [important, urgent]`
- Both tools recognize both formats

### 5. File Naming

Best practices for file names:
- ✅ Use descriptive names: `Coffee Brewing Methods.md`
- ✅ Avoid special characters: `/`, `:`, `*`, `?`
- ✅ Use spaces or hyphens: `My Note.md` or `my-note.md`
- ❌ Avoid: `note:2025.md`, `*important*.md`

### 6. Sync Strategy

**Real-time Collaboration:**
```bash
# Terminal 1: Watch mode
advanced-memory sync --watch

# Terminal 2: Obsidian running
# Both tools update in real-time!
```

**Periodic Sync:**
```bash
# Sync manually when needed
advanced-memory sync

# Or via cron/scheduled task
*/15 * * * * advanced-memory sync  # Every 15 minutes
```

---

## Advanced Features

### 1. Graph View Integration

Use Obsidian's Graph View to visualize Advanced Memory's knowledge graph:

1. Open Obsidian in your Advanced Memory project folder
2. Press `Ctrl/Cmd + G` for Graph View
3. See all connections created by AI
4. Filter by tags, folders, or search terms

### 2. Search Across Both Tools

**In Obsidian:**
- `Ctrl/Cmd + O` - Quick switcher
- `Ctrl/Cmd + Shift + F` - Search in all files
- Graph view filters

**In Advanced Memory (via Claude):**
```
"Search my notes for quantum computing"
"Find all notes tagged with #research"
"Show notes related to machine learning"
```

### 3. Dataview Queries (Obsidian Plugin)

If you use Dataview plugin in Obsidian, query Advanced Memory notes:

```dataview
LIST
FROM #project
WHERE contains(file.tags, "active")
SORT file.name ASC
```

### 4. Templates

Share templates between tools:

**Obsidian Template:**
```markdown
---
title: {{title}}
created: {{date}}
tags: [template]
---

# {{title}}

## Overview

## Notes

## Related
```

**Use in Claude:**
```
"Create a new project note using my template for 'Quantum AI Research'"
```

---

## Troubleshooting

### Issue: Changes Not Syncing

**Problem:** Edits in one tool don't appear in the other

**Solutions:**
1. Check if watch mode is running:
   ```bash
   advanced-memory sync --watch
   ```

2. Manual sync:
   ```bash
   advanced-memory sync
   ```

3. Verify file permissions (both tools can read/write)

4. Check `.gitignore` or `.advanced-memoryignore`

### Issue: Duplicate Notes

**Problem:** Same note appears twice after import

**Solution:**
```bash
# Use skip-existing flag
advanced-memory tools load-obsidian-vault \
  --skip-existing true
```

### Issue: Wikilinks Not Working

**Problem:** `[[links]]` don't resolve properly

**Solutions:**
1. Ensure `convert-links` is enabled during import
2. Use full note titles in links
3. Check for special characters in note names
4. Verify folder structure matches

### Issue: Canvas Files Not Rendering

**Problem:** `.canvas` files don't open in Obsidian

**Solutions:**
1. Update Obsidian to latest version (Canvas requires v1.1.0+)
2. Check canvas file syntax (must be valid JSON)
3. Verify file extension is `.canvas`
4. Try opening/closing Obsidian

### Issue: Large Vault Import Fails

**Problem:** Import hangs on large vaults

**Solutions:**
1. Import in smaller batches (by folder)
2. Use `skip-existing` to resume
3. Exclude attachments initially:
   ```bash
   --include-attachments false
   ```
4. Check Advanced Memory logs for errors:
   ```bash
   advanced-memory sync --verbose
   ```

### Issue: Metadata Conflicts

**Problem:** Frontmatter differs between tools

**Solution:**
- Choose one tool as source of truth for metadata
- Use Obsidian's properties panel to match Advanced Memory format
- Or let Advanced Memory manage metadata automatically

---

## Comparison: Obsidian vs Advanced Memory

| Feature | Obsidian | Advanced Memory |
|---------|----------|-----------------|
| **Visual Editor** | ✅ Excellent | ❌ No (markdown files) |
| **Graph View** | ✅ Beautiful | ⚠️ Via Obsidian |
| **AI Integration** | ⚠️ Via plugins | ✅ Native (MCP) |
| **Canvas** | ✅ Built-in | ✅ Can create |
| **Search** | ✅ Fast | ✅ Semantic |
| **Multi-Project** | ⚠️ Vault-based | ✅ Full support |
| **Wikilinks** | ✅ Yes | ✅ Yes |
| **Tags** | ✅ Yes | ✅ Yes |
| **Plugins** | ✅ 1000+ | ❌ No |
| **Cross-Platform** | ✅ All platforms | ✅ All platforms |
| **Offline** | ✅ Yes | ✅ Yes |
| **AI Content Generation** | ❌ No | ✅ Yes |
| **Knowledge Graph** | ✅ Visual | ✅ Semantic |

**Recommendation:** Use both! Obsidian for editing/visualization, Advanced Memory for AI-powered knowledge building.

---

## Example Workflows

### Workflow: Research Project

1. **Start in Claude:**
   ```
   "Research blockchain technology and create organized notes"
   ```

2. **Claude Creates:**
   - `Blockchain Basics.md`
   - `Consensus Mechanisms.md`
   - `Smart Contracts.md`
   - `Blockchain Applications.md`
   - Canvas showing connections

3. **Open in Obsidian:**
   - View in Graph View
   - Add visual elements to Canvas
   - Create diagrams with Excalidraw plugin

4. **Refine in Claude:**
   ```
   "Add more details about Proof of Stake to my blockchain notes"
   ```

5. **Final Review in Obsidian:**
   - Polish formatting
   - Add images
   - Create presentation slides

### Workflow: Meeting Notes

1. **During Meeting (Obsidian):**
   - Quick capture with templates
   - Add action items with checkboxes

2. **After Meeting (Claude):**
   ```
   "Summarize my meeting notes and create action item tasks"
   ```

3. **Claude Creates:**
   - Summary note
   - Individual task notes
   - Links to related projects

4. **Track Progress (Obsidian):**
   - Use Kanban plugin
   - Check off completed tasks
   - Visualize in Canvas

### Workflow: Personal Knowledge Base

1. **Daily Notes (Obsidian):**
   - Journal entries
   - Quick thoughts
   - Links to topics

2. **Weekly Review (Claude):**
   ```
   "Review my daily notes from this week and extract key insights"
   ```

3. **Claude Organizes:**
   - Creates topic notes
   - Links related concepts
   - Builds knowledge graph

4. **Monthly Reflection (Obsidian):**
   - Graph View shows growth
   - Canvas for planning
   - Visual connections emerge

---

## Resources

### Official Documentation
- [Obsidian Help](https://help.obsidian.md/)
- [Advanced Memory Documentation](https://memory.basicmachines.co)
- [MCP Protocol](https://modelcontextprotocol.io/)

### Community
- [Obsidian Forum](https://forum.obsidian.md/)
- [Obsidian Discord](https://discord.gg/obsidianmd)
- [Advanced Memory Discord](https://discord.gg/tyvKNccgqN)

### Recommended Obsidian Plugins
- **Dataview** - Query your notes like a database
- **Excalidraw** - Sketch diagrams and drawings
- **Kanban** - Project management boards
- **Calendar** - Visual calendar view of daily notes
- **Graph Analysis** - Advanced graph analytics

### Additional Guides
- [Obsidian Canvas Guide](https://help.obsidian.md/Plugins/Canvas)
- [Wikilinks Guide](https://help.obsidian.md/Linking+notes+and+files/Internal+links)
- [Advanced Memory MCP Tools](../development/MCP_TOOLS.md)

---

## Conclusion

Obsidian and Advanced Memory complement each other perfectly:

- **Obsidian** excels at visual editing, graph visualization, and human-friendly interfaces
- **Advanced Memory** excels at AI integration, automated knowledge building, and semantic understanding

Together, they create a powerful knowledge management system that combines:
✅ Visual clarity (Obsidian)
✅ AI assistance (Advanced Memory)
✅ Automated organization (Advanced Memory)
✅ Beautiful presentation (Obsidian)

**Get Started:**
```bash
# 1. Install both tools
brew install obsidian advanced-memory

# 2. Point Advanced Memory at Obsidian vault
advanced-memory project add my-vault ~/Documents/ObsidianVault

# 3. Start sync
advanced-memory sync --watch

# 4. Open Obsidian
# 5. Ask Claude to help build your knowledge base!
```

Happy knowledge building! 🚀
