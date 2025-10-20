# Real-World Testing Checklist

**Purpose**: Verify all advertised features actually work before claiming them publicly.

**Status**: Tracking verification status for public release claims.

---

## Export Features

### Pandoc Export
**Prerequisites**: Pandoc installed (https://pandoc.org/)

| Format | Tested | Works | Notes |
|--------|--------|-------|-------|
| PDF | ⏳ | ? | Requires LaTeX (MiKTeX/TinyTeX) |
| HTML | ⏳ | ? | |
| DOCX | ⏳ | ? | |
| EPUB | ⏳ | ? | |
| ODT | ⏳ | ? | |

**Test commands**:
```python
adn_export("pandoc", export_path="test.pdf", format_type="pdf", source_folder="/developer")
adn_export("pandoc", export_path="test.html", format_type="html", source_folder="/developer")
adn_export("pandoc", export_path="test.docx", format_type="docx", source_folder="/developer")
```

### Docsify Export
**Prerequisites**: None (generates static files)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Basic export | ⏳ | ? | |
| Mermaid diagrams | ⏳ | ? | |
| Navigation | ⏳ | ? | |
| Search | ⏳ | ? | |
| Enhanced version | ⏳ | ? | With plugins |

**Test commands**:
```python
adn_export("docsify", export_path="./test-docsify/", source_folder="/developer")
# Then open index.html in browser
```

### HTML Export
**Prerequisites**: None (generates static files)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Basic HTML | ⏳ | ? | |
| Mermaid rendering | ⏳ | ? | Requires internet for CDN |
| Navigation | ⏳ | ? | |

**Test commands**:
```python
adn_export("html", export_path="./test-html/", source_folder="/developer")
```

### Claude Skills Export
**Prerequisites**: None (generates SKILL.md files)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Export to SKILL.md | ✅ | Yes | Implemented in v1.0.0b3 |
| YAML frontmatter | ✅ | Yes | Validated against spec |
| Metadata preservation | ✅ | Yes | |
| Directory structure | ✅ | Yes | |
| Deploy to claude.ai | ⏳ | ? | Requires paid plan |
| Deploy to Claude API | ⏳ | ? | Requires API access |

**Test commands**:
```python
adn_export("claude_skills", export_path="./test-skills/", source_folder="/developer")
# Manual: Try uploading to claude.ai
```

### Joplin Export
**Prerequisites**: Joplin installed (https://joplinapp.org/)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Export to Joplin format | ⏳ | ? | |
| Notebook structure | ⏳ | ? | |
| Tags preserved | ⏳ | ? | |
| Import into Joplin | ⏳ | ? | Manual verification needed |

**Test commands**:
```python
adn_export("joplin", export_path="./test-joplin/", source_folder="/developer")
# Then try importing in Joplin app
```

### PDF Book Export
**Prerequisites**: Pandoc + LaTeX

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Create PDF book | ⏳ | ? | |
| Table of contents | ⏳ | ? | |
| Chapter organization | ⏳ | ? | |

**Test commands**:
```python
adn_export("pdf_book", export_path="test-book.pdf", book_title="Test Book", source_folder="/developer")
```

### Archive Export
**Prerequisites**: None

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Create archive | ⏳ | ? | |
| Database included | ⏳ | ? | |
| Configuration included | ⏳ | ? | |

---

## Import Features

### Obsidian Import
**Prerequisites**: Obsidian vault (https://obsidian.md/)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Import vault | ⏳ | ? | Requires existing vault |
| WikiLinks conversion | ⏳ | ? | |
| Frontmatter preservation | ⏳ | ? | |
| Folder structure | ⏳ | ? | |
| Attachments | ⏳ | ? | |

**Test commands**:
```python
adn_import("obsidian", source_path="/path/to/obsidian-vault/", destination_folder="imported/obsidian")
```

**Test vault needed**: Create small test vault with:
- Notes with [[WikiLinks]]
- YAML frontmatter
- Nested folders
- Images/attachments

### Joplin Import
**Prerequisites**: Joplin export (https://joplinapp.org/)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Import export directory | ⏳ | ? | |
| Notebook structure | ⏳ | ? | |
| Tags preserved | ⏳ | ? | |
| Metadata | ⏳ | ? | |

**Test commands**:
```python
adn_import("joplin", source_path="/path/to/joplin-export/", destination_folder="imported/joplin")
```

### Notion Import
**Prerequisites**: Notion export (https://notion.so/)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Import HTML export | ⏳ | ? | |
| Import Markdown export | ⏳ | ? | |
| Import ZIP export | ⏳ | ? | |
| Page hierarchy | ⏳ | ? | |
| Databases | ⏳ | ? | |

**Test commands**:
```python
adn_import("notion", source_path="/path/to/notion-export.zip", destination_folder="imported/notion")
```

### Evernote Import
**Prerequisites**: Evernote ENEX file (https://evernote.com/)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Import ENEX | ⏳ | ? | |
| Notebook structure | ⏳ | ? | |
| Attachments | ⏳ | ? | |
| Tags | ⏳ | ? | |

**Test commands**:
```python
adn_import("evernote", source_path="/path/to/export.enex", destination_folder="imported/evernote")
```

### Claude Skills Import
**Prerequisites**: Skills repository

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Import SKILL.md | ✅ | Yes | Implemented in v1.0.0b3 |
| Frontmatter conversion | ✅ | Yes | |
| Metadata preservation | ✅ | Yes | |
| Directory structure | ✅ | Yes | |

**Test commands**:
```python
adn_import("claude_skills", source_path="./temp-anthropic-skills/", destination_folder="imported/anthropic")
```

---

## Zettelkasten Features

### Template Generation
| Category | Tested | Works | Templates Count |
|----------|--------|-------|-----------------|
| developer | ⏳ | ? | 30+ claimed |
| devops | ⏳ | ? | 15+ claimed |
| data-scientist | ⏳ | ? | 10+ claimed |
| researcher | ⏳ | ? | 12+ claimed |
| product-manager | ⏳ | ? | 8+ claimed |
| entrepreneur | ⏳ | ? | ? |
| creative | ⏳ | ? | ? |
| writer | ⏳ | ? | ? |
| uiux-designer | ⏳ | ? | ? |
| knowledge-worker | ⏳ | ? | ? |
| ai | ⏳ | ? | ? |
| philosophy | ⏳ | ? | ? |

**Test commands**:
```python
adn_zettelmaker("generate", category="developer", topic="python-core")
adn_zettelmaker("generate", category="researcher", topic="research-methods")
# Verify templates exist and have quality content
```

**Quality checks**:
- [ ] Templates have actual content (not placeholders)
- [ ] WikiLinks are valid
- [ ] Categories match claimed count
- [ ] Templates are useful for learning

---

## Editor Integration

### Notepad++ Integration
**Prerequisites**: Notepad++ installed (https://notepad-plus-plus.org/)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Export to workspace | ⏳ | ? | |
| Edit in Notepad++ | ⏳ | ? | |
| Import back | ⏳ | ? | |
| Backup creation | ⏳ | ? | |

**Test commands**:
```python
adn_editor("notepadpp_edit", note_identifier="test-note", workspace_path="./npp-workspace/")
# Edit in Notepad++
adn_editor("notepadpp_import", note_identifier="test-note")
```

### Typora Integration
**Prerequisites**: Typora + json_rpc plugin (https://typora.io/)

| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Export document | ⏳ | ? | Requires plugin |
| Get content | ⏳ | ? | |
| Set content | ⏳ | ? | |
| Theme control | ⏳ | ? | |

**Test commands**:
```python
adn_editor("typora_control", typora_operation="export", format="pdf", output_path="test.pdf")
```

---

## Search Features

### External Search (No Import)

| Source | Tested | Works | Prerequisites |
|--------|--------|-------|---------------|
| Obsidian vault | ⏳ | ? | Obsidian vault |
| Joplin export | ⏳ | ? | Joplin export |
| Notion export | ⏳ | ? | Notion export |
| Evernote ENEX | ⏳ | ? | ENEX file |

**Test commands**:
```python
adn_search("obsidian", query="test", source_path="/path/to/vault/")
adn_search("joplin", query="test", source_path="/path/to/export/")
```

---

## Core Features (Must Work!)

### Content Management
| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Write note | ⏳ | ? | |
| Read note | ⏳ | ? | |
| Edit note | ⏳ | ? | |
| Delete note | ⏳ | ? | |
| Move note | ⏳ | ? | |

### Project Management
| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Create project | ⏳ | ? | |
| Switch project | ⏳ | ? | |
| List projects | ⏳ | ? | |
| Delete project | ⏳ | ? | |
| Set default | ⏳ | ? | |

### Database
| Feature | Tested | Works | Notes |
|---------|--------|-------|-------|
| Global database | ⏳ | ? | ~/.advanced-memory/ |
| Project isolation | ⏳ | ? | Via project_id |
| Fast sync | ⏳ | ? | 2000+ notes claimed |

---

## Testing Priority

### P0 (Must work for public release)
- [ ] Basic content management (write, read, edit)
- [ ] Project creation and switching
- [ ] Database creation and isolation
- [ ] Search functionality
- [ ] Claude Skills export (already tested)
- [ ] Claude Skills import (already tested)

### P1 (Advertised features)
- [ ] Obsidian import (commonly used)
- [ ] Notion import (commonly used)
- [ ] Pandoc export (commonly used)
- [ ] Zettelkasten template generation
- [ ] Docsify export

### P2 (Nice to have)
- [ ] Joplin import/export
- [ ] Evernote import
- [ ] Typora integration
- [ ] Notepad++ integration
- [ ] PDF book generation

---

## Test Environment Setup

### Required Installations
1. **Pandoc**: https://pandoc.org/installing.html
2. **LaTeX** (for PDF): MiKTeX (Windows) or TinyTeX
3. **Obsidian**: https://obsidian.md/download (for testing imports)
4. **Joplin**: https://joplinapp.org/download/ (optional)
5. **Notion**: https://www.notion.so/ (optional, for exports)
6. **Notepad++**: https://notepad-plus-plus.org/downloads/ (optional)
7. **Typora**: https://typora.io/ (optional)

### Test Data Needed
1. Sample Obsidian vault (10-20 notes)
2. Sample Joplin export
3. Sample Notion export (HTML + Markdown)
4. Sample ENEX file from Evernote
5. Test zettelkasten notes

---

## Documentation Updates Needed

### For Each Import/Export

**Must include**:
1. ✅ Link to official homepage
2. ✅ Prerequisites clearly stated
3. ✅ Installation instructions or links
4. ✅ Test status (verified/untested)
5. ✅ Known limitations
6. ✅ Link to our docs

**Example template**:
```markdown
### Obsidian Import

**Prerequisites**: 
- Obsidian vault (https://obsidian.md/)
- Vault exported or accessible locally

**Status**: ⏳ Untested in real-world scenarios

**Usage**:
[code example]

**Documentation**: [Obsidian Integration Guide](docs/integrations/obsidian.md)
**Known limitations**: [list any]
```

---

## Continuous Testing

### Before Each Release
- [ ] Run core features test suite
- [ ] Test at least 2 import formats
- [ ] Test at least 2 export formats
- [ ] Verify zettelkasten templates exist
- [ ] Test on fresh installation

### After User Reports
- [ ] Document any failures
- [ ] Update test checklist
- [ ] Fix issues before claiming feature works
- [ ] Update documentation with accurate status

---

**Last Updated**: October 20, 2025  
**Next Review**: Before v1.0.0 final release

**Maintainer Note**: This is our accountability document. Mark features as tested only after real-world verification. Public repo = public reputation.

