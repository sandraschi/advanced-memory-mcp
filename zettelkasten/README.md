# Zettelkasten - Knowledge Templates and Inbox

**Purpose**: Pre-built templates, custom templates, and document inbox for Advanced Memory
**User-Facing**: This folder is for you to use, browse, and customize!

---

## What's Here?

### 📚 `templates/`
**Pre-built knowledge templates** across 10 professional categories

Browse, use, and learn from these high-quality zettelkasten notes:
- Developer (40+ templates)
- DevOps Engineer (20+ templates)
- Data Scientist (15+ templates)
- UI/UX Designer (15+ templates)
- Product Manager (10+ templates)
- Entrepreneur (10+ templates)
- Creative Professional (15+ templates)
- Knowledge Worker (10+ templates)
- Researcher (10+ templates)
- Writer (10+ templates)

**Total**: 150+ interconnected templates

**How to use**:
```bash
# Generate templates via CLI
advanced-memory onboard

# Or via MCP tool
adn_zettelmaker("generate", category="developer", topic="Python Basics")
```

---

### 📥 `inbox/`
**Drop files here** for automatic conversion and import!

**Supported formats**:
- ✅ `.md` - Markdown (direct import)
- ✅ `.docx` - Word documents (auto-converted)
- ✅ `.html` - Web pages (auto-converted)
- ✅ `.txt` - Text files (direct import)
- ⏳ `.pdf` - PDF files (text extraction)

**Workflow**:
1. Drop file into `inbox/`
2. File watcher detects it
3. Auto-converts to markdown (if needed)
4. Moves to `converted/`
5. Syncs to Advanced Memory database
6. Appears in your knowledge base!

**Example**:
```bash
# Drop meeting notes
cp ~/Downloads/meeting-notes.docx zettelkasten/inbox/

# Automatic processing happens!
# Result: meeting-notes.md in your knowledge base
```

---

### 👤 `user-templates/`
**Your custom templates** for recurring note patterns

Create reusable templates for your workflow:
- Meeting notes template
- Research paper template
- Project planning template
- Daily journal template

**How to create**:
1. Copy a pre-built template or start fresh
2. Customize for your needs
3. Save in `user-templates/`
4. Generate from it via MCP or CLI

**Example**:
```bash
# Copy existing template
cp zettelkasten/templates/knowledge-worker/meeting-notes.md \
   zettelkasten/user-templates/my-meeting-template.md

# Customize it
vim zettelkasten/user-templates/my-meeting-template.md

# Generate from it
advanced-memory generate --template zettelkasten/user-templates/my-meeting-template.md
```

---

### 🔄 `converted/`
**Auto-converted documents** from inbox

Files that were auto-converted from office formats:
- Timestamped for tracking
- Markdown format
- Ready to edit or move to projects

**Example contents**:
```
converted/
├── 20251017_143045_meeting-notes.md
├── 20251017_150123_research-paper.md
└── 20251017_161534_presentation.md
```

---

## Quick Start

### Generate Pre-Built Templates

```bash
# Interactive onboarding
advanced-memory onboard

# Programmatic generation
adn_zettelmaker("generate", category="developer", topic="Python Basics")
```

---

### Use the Inbox

**Step 1**: Drop file into inbox
```bash
cp ~/Documents/meeting.docx zettelkasten/inbox/
```

**Step 2**: Wait for auto-processing (or manually trigger)
```bash
# Auto-processing happens via file watcher

# Or manually process
advanced-memory convert inbox
```

**Step 3**: Find converted file
```bash
# Check converted/
ls zettelkasten/converted/
```

---

### Create Custom Templates

**Step 1**: Create template file
```bash
# Create new template
vim zettelkasten/user-templates/my-template.md
```

**Step 2**: Use template
```bash
# Via CLI
advanced-memory generate --template zettelkasten/user-templates/my-template.md

# Via MCP
adn_zettelmaker("generate", template_path="zettelkasten/user-templates/my-template.md")
```

---

## Folder Guidelines

### `templates/` (Read-Only)

**Do**:
- ✅ Browse and explore
- ✅ Copy to `user-templates/` for customization
- ✅ Use as learning examples

**Don't**:
- ❌ Edit directly (will be overwritten on update)
- ❌ Delete (use .gitignore if you want to hide)

---

### `inbox/` (Active Processing)

**Do**:
- ✅ Drop any supported file format
- ✅ Use for quick imports
- ✅ Clear periodically (files moved to converted/)

**Don't**:
- ❌ Store files permanently (they'll be moved/deleted)
- ❌ Edit files in inbox (edit in converted/ or projects)

**Git**: Inbox contents are `.gitignore`d (temporary workspace)

---

### `user-templates/` (Your Custom Templates)

**Do**:
- ✅ Create your own templates
- ✅ Customize pre-built templates
- ✅ Version control (committed to git)
- ✅ Share with others

**Don't**:
- ❌ Include sensitive information (templates are code)

---

### `converted/` (Processed Files)

**Do**:
- ✅ Review converted files
- ✅ Edit if conversion needs fixes
- ✅ Move to project folders
- ✅ Clear old files periodically

**Don't**:
- ❌ Store permanently (use project folders)

**Git**: Converted files are `.gitignore`d (temporary staging)

---

## See Also

- **Template Guide**: `templates/README.md`
- **Inbox Guide**: `inbox/README.md`
- **Architecture**: `docs/architecture/ZETTELKASTEN_ARCHITECTURE_PROPOSAL.md`
- **Source Code**: `src/advanced_memory/cli/zettelkasten_content/README.md`

---

**Created**: October 17, 2025
**Purpose**: User-facing zettelkasten system with inbox and conversion
**Status**: Under construction 🚧
