# Import & Export Guide

Complete guide to importing content from other tools and exporting from Advanced Memory.

**Testing Status**: See [Real-World Testing Checklist](../testing/REAL_WORLD_TESTING_CHECKLIST.md) for current verification status of each feature.

---

## Prerequisites by Tool

### Import Prerequisites

| Tool | Requirement | Download | Documentation |
|------|-------------|----------|---------------|
| **Obsidian** | Existing vault | [obsidian.md](https://obsidian.md/) | [Obsidian Docs](https://help.obsidian.md/) |
| **Notion** | Exported workspace | [notion.so](https://www.notion.so/) | [Export Guide](https://www.notion.so/help/export-your-content) |
| **Joplin** | Exported notes | [joplinapp.org](https://joplinapp.org/) | [Export Guide](https://joplinapp.org/help/#exporting) |
| **Evernote** | ENEX export file | [evernote.com](https://evernote.com/) | [Export Guide](https://help.evernote.com/hc/en-us/articles/209005557) |
| **Claude Skills** | Skills repository | [GitHub](https://github.com/anthropics/anthropic-skills) | [Skills Docs](https://support.claude.com/en/sections/12512173-skills) |

### Export Prerequisites

| Format | Requirement | Download | Documentation |
|--------|-------------|----------|---------------|
| **PDF (Pandoc)** | Pandoc + LaTeX | [Pandoc](https://pandoc.org/installing.html), [MiKTeX](https://miktex.org/) | [Pandoc Manual](https://pandoc.org/MANUAL.html) |
| **HTML/Docsify** | None | - | - |
| **Claude Skills** | None | - | [Skills Spec](https://github.com/anthropics/anthropic-skills/blob/main/agent_skills_spec.md) |
| **Joplin** | Joplin app (for import) | [joplinapp.org](https://joplinapp.org/) | [Import Guide](https://joplinapp.org/help/#importing) |

---

## Import Guides

### Obsidian Import

**What it does**: Imports Obsidian vault into Advanced Memory

**Prerequisites**:
- Existing Obsidian vault
- Download: https://obsidian.md/

**Features**:
- Converts `[[WikiLinks]]` to Advanced Memory entity references
- Preserves YAML frontmatter
- Maintains folder structure
- Optional: Import attachments

**Usage**:
```python
adn_import(
    "obsidian",
    source_path="~/Documents/ObsidianVault/",
    destination_folder="imported/obsidian",
    preserve_structure=True,
    convert_links=True,
    include_attachments=False
)
```

**Testing Status**: ⏳ Pending real-world verification

**Known Limitations**:
- Large vaults may take time to process
- Some Obsidian plugins may create non-standard markdown
- Graph view data not imported

**Troubleshooting**: See [Obsidian Integration](../integrations/obsidian.md)

---

### Notion Import

**What it does**: Imports Notion workspace export into Advanced Memory

**Prerequisites**:
- Notion export (HTML or Markdown)
- Export from: https://www.notion.so/ → Settings → Export All Workspace Content

**Features**:
- Converts Notion blocks to markdown
- Preserves page hierarchy
- Handles databases (converts to tables)
- Extracts images from ZIP exports

**Usage**:
```python
adn_import(
    "notion",
    source_path="~/Downloads/Notion-Export.zip",  # or directory path
    destination_folder="imported/notion",
    preserve_hierarchy=True
)
```

**Testing Status**: ⏳ Pending real-world verification

**Known Limitations**:
- Complex databases may not convert perfectly
- Some Notion blocks (e.g., embeds) may lose formatting
- Collaborative features (comments) not preserved

**Export Instructions**:
1. Open Notion → Settings & Members → Settings
2. Export All Workspace Content
3. Select Format: Markdown & CSV (recommended) or HTML
4. Include files: Yes (to get images)
5. Wait for export email, download ZIP

**Troubleshooting**: See [Notion Integration](../integrations/notion.md)

---

### Joplin Import

**What it does**: Imports Joplin notes into Advanced Memory

**Prerequisites**:
- Joplin export directory
- Download: https://joplinapp.org/

**Features**:
- Preserves notebooks as folders
- Maintains tags
- Converts metadata
- Handles attachments

**Usage**:
```python
adn_import(
    "joplin",
    source_path="~/Documents/joplin-export/",
    destination_folder="imported/joplin",
    preserve_structure=True,
    skip_existing=True
)
```

**Testing Status**: ⏳ Pending real-world verification

**Export Instructions** (from Joplin):
1. Open Joplin
2. File → Export All → JEX (Joplin Export) or MD (Markdown)
3. Choose directory
4. Wait for export to complete

**Troubleshooting**: See [Joplin Integration](../integrations/joplin.md)

---

### Evernote Import

**What it does**: Imports Evernote ENEX files into Advanced Memory

**Prerequisites**:
- Evernote ENEX export file
- Account: https://evernote.com/

**Features**:
- Converts HTML to markdown
- Preserves notebooks as folders
- Maintains tags
- Extracts attachments from ENEX

**Usage**:
```python
adn_import(
    "evernote",
    source_path="~/Downloads/MyNotes.enex",
    destination_folder="imported/evernote",
    preserve_notebooks=True,
    include_attachments=True
)
```

**Testing Status**: ⏳ Pending real-world verification

**Export Instructions** (from Evernote):
1. Open Evernote desktop app
2. Select notebook(s)
3. File → Export Notes → ENEX format
4. Save file

**Known Limitations**:
- ENEX format can be large with many attachments
- Some Evernote-specific formatting may not convert perfectly
- Web clipper metadata may be lost

**Troubleshooting**: See [Evernote Integration](../integrations/evernote.md)

---

### Claude Skills Import

**What it does**: Imports Claude Skills repositories into Advanced Memory

**Prerequisites**:
- Skills repository (e.g., Anthropic's official skills)
- Download: https://github.com/anthropics/anthropic-skills

**Features**:
- Converts SKILL.md to Advanced Memory notes
- Preserves frontmatter
- Maintains directory structure
- Imports resources (scripts, references)

**Usage**:
```python
adn_import(
    "claude_skills",
    source_path="~/repos/anthropic-skills/",
    destination_folder="skills/anthropic",
    preserve_structure=True,
    import_resources=True
)
```

**Testing Status**: ✅ Verified functional

**Troubleshooting**: See [Claude Skills Integration](claude-skills.md)

---

## Export Guides

### Pandoc Export

**What it does**: Exports to PDF, DOCX, HTML, EPUB, and 40+ formats using Pandoc

**Prerequisites**:
- **Pandoc**: https://pandoc.org/installing.html
- **For PDF**: LaTeX distribution
  - Windows: [MiKTeX](https://miktex.org/) (full) or [TinyTeX](https://yihui.org/tinytex/) (minimal)
  - macOS: [MacTeX](https://tug.org/mactex/) or TinyTeX
  - Linux: `sudo apt-get install texlive` or TinyTeX

**Features**:
- 40+ output formats
- Table of contents
- Custom templates
- Syntax highlighting
- Bibliography support

**Usage**:
```python
# PDF
adn_export(
    "pandoc",
    export_path="output.pdf",
    format_type="pdf",
    source_folder="/developer",
    toc=True,
    pdf_engine="pdflatex"
)

# DOCX
adn_export(
    "pandoc",
    export_path="output.docx",
    format_type="docx",
    source_folder="/developer"
)

# HTML
adn_export(
    "pandoc",
    export_path="output.html",
    format_type="html",
    source_folder="/developer",
    self_contained=True
)
```

**Testing Status**: ⏳ Pending real-world verification with all formats

**Troubleshooting**:
- **PDF fails**: Ensure LaTeX is installed (`pdflatex --version`)
- **Fonts missing**: Install required fonts or use different template
- **Large files**: Increase LaTeX memory or split documents

---

### Docsify Export

**What it does**: Creates a Docsify documentation website

**Prerequisites**: None (generates static files)

**Features**:
- Beautiful documentation sites
- Built-in search
- Responsive design
- No build step required
- Mermaid diagram support

**Usage**:
```python
adn_export(
    "docsify",
    export_path="./my-docs/",
    source_folder="/",
    site_title="My Knowledge Base",
    site_description="Documentation from Advanced Memory"
)
```

**Testing Status**: ⏳ Pending real-world verification

**Deployment**:
1. Export creates static HTML/JS/CSS
2. Host on GitHub Pages, Netlify, or any web server
3. Open `index.html` in browser to test locally

**Enhanced Version**: Use `export_docsify_enhanced` for additional features (pagination, themes, etc.)

---

### HTML Export

**What it does**: Creates standalone HTML website with navigation

**Prerequisites**: None (internet for Mermaid CDN)

**Features**:
- Self-contained HTML files
- Mermaid diagram rendering
- Navigation index
- Responsive design
- Works offline after first load

**Usage**:
```python
adn_export(
    "html",
    export_path="./html-site/",
    source_folder="/developer",
    include_index=True
)
```

**Testing Status**: ⏳ Pending real-world verification

---

### Claude Skills Export

**What it does**: Exports notes as Claude Skills format

**Prerequisites**: None

**Features**:
- Creates proper SKILL.md files
- Validates against Anthropic spec
- Generates frontmatter
- Preserves Advanced Memory metadata

**Usage**:
```python
adn_export(
    "claude_skills",
    export_path="~/claude-skills/",
    source_folder="/developer"
)
```

**Testing Status**: ✅ Verified functional

**Deployment**: See [Claude Skills Guide](claude-skills.md)

---

### PDF Book Export

**What it does**: Creates professional PDF book with chapters

**Prerequisites**: Same as Pandoc export (Pandoc + LaTeX)

**Features**:
- Title page
- Table of contents
- Chapter organization
- Professional formatting
- Page numbers

**Usage**:
```python
adn_export(
    "pdf_book",
    export_path="my-book.pdf",
    book_title="Developer Knowledge Base",
    source_folder="/developer",
    author="Your Name",
    toc_depth=2
)
```

**Testing Status**: ⏳ Pending real-world verification

---

## Round-Trip Testing

### Verify Data Integrity

**Test workflow**:
1. Export from Advanced Memory
2. Import to target application
3. Export from target application
4. Import back to Advanced Memory
5. Compare content

**Example (Obsidian)**:
```python
# 1. Export to Obsidian-compatible markdown
adn_export("obsidian", export_path="./test-export/")

# 2. Open in Obsidian, edit some notes

# 3. Import back
adn_import("obsidian", source_path="./test-export/", destination_folder="round-trip-test")

# 4. Verify changes preserved
```

---

## Batch Operations

### Export Multiple Categories

```python
for category in ["developer", "researcher", "devops"]:
    adn_export(
        "claude_skills",
        export_path=f"~/skills/{category}/",
        source_folder=f"/{category}"
    )
```

### Import Multiple Sources

```python
sources = [
    ("obsidian", "~/vaults/personal/", "imported/personal"),
    ("obsidian", "~/vaults/work/", "imported/work"),
    ("notion", "~/exports/notion.zip", "imported/notion"),
]

for import_type, source, dest in sources:
    adn_import(import_type, source_path=source, destination_folder=dest)
```

---

## Troubleshooting

### General Issues

**Import fails**:
- Verify source path exists
- Check file permissions
- Ensure source format is correct
- Check logs for specific errors

**Export fails**:
- Verify export path is writable
- Check prerequisites installed (Pandoc, LaTeX)
- Ensure sufficient disk space
- Test with smaller source folder first

### Format-Specific Issues

See individual integration guides:
- [Obsidian Integration](../integrations/obsidian.md)
- [Notion Integration](../integrations/notion.md)
- [Joplin Integration](../integrations/joplin.md)
- [Evernote Integration](../integrations/evernote.md)
- [Claude Skills Integration](claude-skills.md)

---

## Testing Your Setup

### Quick Test

```python
# 1. Create test note
adn_content("write", identifier="Test Note", content="# Test\n\nHello World", folder="test")

# 2. Export to multiple formats
adn_export("html", export_path="./test-export-html/", source_folder="test")
adn_export("docsify", export_path="./test-export-docsify/", source_folder="test")
adn_export("claude_skills", export_path="./test-export-skills/", source_folder="test")

# 3. Verify files created
# Check each export directory for expected files
```

---

## Best Practices

### Before Importing

1. **Backup**: Create backup of source data
2. **Clean**: Remove test/draft content if not needed
3. **Organize**: Structure source data clearly
4. **Test**: Try small import first

### Before Exporting

1. **Review**: Check content quality
2. **Tag**: Ensure proper tagging
3. **Links**: Verify internal links work
4. **Test**: Export small sample first

### After Operations

1. **Verify**: Check import/export success
2. **Validate**: Spot-check random notes
3. **Compare**: Use diffs to verify integrity
4. **Clean**: Remove test exports

---

## Related Documentation

- [File Type Filtering](file-type-filtering.md) - Control what gets indexed
- [Claude Skills Integration](claude-skills.md) - Skills export/import details
- [Real-World Testing Checklist](../testing/REAL_WORLD_TESTING_CHECKLIST.md) - Feature verification status

---

**Questions?** See [Troubleshooting Guide](../TROUBLESHOOTING_GUIDE.md) or [file an issue](https://github.com/sandraschi/advanced-memory-mcp/issues).
