# Inbox Workflow - Drop Files into Your Knowledge Base

**Last Updated**: October 2025  
**Feature Status**: ✅ Available in v1.0.0b3+

---

## Overview

The **Inbox Workflow** allows you to drop files (markdown, Word docs, PDFs, HTML, text) into a watched directory. Files are automatically converted to markdown and added to your knowledge base.

**Think of it as**: A universal "knowledge inbox" that accepts anything you throw at it.

---

## What It Does

1. **Drop files** into `zettelkasten/inbox/`
2. **Auto-convert** documents to markdown (if needed)
3. **Move to project** directory
4. **Trigger sync** to index in database
5. **Preserve originals** in `zettelkasten/converted/` for reference

---

## Supported File Formats

### ✅ Always Supported

**Markdown Files (`.md`)**
- **Processing**: Moved directly to project
- **Requirements**: None
- **Best for**: Ready-to-use notes, documentation

**Plain Text (`.txt`)**
- **Processing**: Wrapped in markdown header
- **Requirements**: None
- **Best for**: Quick notes, pasted content

---

### 📦 Requires Dependencies

**Word Documents (`.docx`, `.doc`)**
- **Processing**: Converted via Pandoc
- **Requirements**: Pandoc installed
- **Best for**: Research papers, reports, drafts
- **Quality**: Excellent (preserves formatting, images)

**HTML Files (`.html`, `.htm`)**
- **Processing**: Converted via Pandoc
- **Requirements**: Pandoc installed
- **Best for**: Saved web pages, documentation
- **Quality**: Good (structure preserved)

**PDF Documents (`.pdf`)**
- **Processing**: Text extraction
- **Requirements**: `pypdf` (recommended) or `pdftotext`
- **Best for**: Papers, ebooks, scanned documents
- **Quality**: Varies (depends on PDF format)
- **Limitations**: No images, formatting may be lost

---

## Installation

### Core System (Always Works)

Advanced Memory inbox system is built-in. No setup needed for `.md` and `.txt` files.

### Optional Dependencies

**Install Pandoc** (for `.docx` and `.html` conversion):
```bash
# macOS (Homebrew)
brew install pandoc

# Windows (Chocolatey)
choco install pandoc

# Linux (apt)
sudo apt install pandoc

# Or download from: https://pandoc.org/installing.html
```

**Install pypdf** (for better PDF extraction):
```bash
pip install pypdf

# Or via uv (recommended)
uv pip install pypdf
```

---

## Usage

### Method 1: Manual Processing (Recommended)

**Step 1**: Drop files into inbox
```
zettelkasten/inbox/
├── research-paper.pdf
├── meeting-notes.docx
├── web-article.html
└── quick-note.txt
```

**Step 2**: Process manually
```bash
# Via CLI
advanced-memory inbox process

# Or via MCP tool (in Claude Desktop)
adn_inbox("process")
```

**Step 3**: Check status
```bash
advanced-memory inbox status
```

---

### Method 2: Automatic Processing (Background)

**Enable in config**:
```toml
# ~/.advanced-memory/config.toml
sync_changes = true
```

Files dropped into inbox are automatically processed in the background.

**Or use MCP tool**:
```python
adn_inbox("watch")
```

---

## Workflows

### Workflow 1: Research Paper Capture

**Scenario**: You downloaded a PDF research paper and want it in your knowledge base.

```bash
# 1. Drop PDF into inbox
cp ~/Downloads/neural-networks-2025.pdf zettelkasten/inbox/

# 2. Process
advanced-memory inbox process

# 3. Find in knowledge base
advanced-memory search "neural networks"
```

**Result**: 
- PDF text extracted to markdown
- Original PDF preserved in `zettelkasten/converted/`
- Note indexed and searchable

---

### Workflow 2: Meeting Notes from Word

**Scenario**: You have meeting notes in a Word document.

```bash
# 1. Drop .docx into inbox
cp ~/Documents/team-meeting-2025-10-17.docx zettelkasten/inbox/

# 2. Process
advanced-memory inbox process
```

**Result**:
- Word doc converted to markdown (formatting preserved)
- Images extracted
- Note added to knowledge base

---

### Workflow 3: Web Article Capture

**Scenario**: You saved an article as HTML and want to reference it.

```bash
# 1. Save article as HTML (Ctrl+S in browser)
# 2. Drop HTML into inbox
mv ~/Downloads/ai-trends-article.html zettelkasten/inbox/

# 3. Process
advanced-memory inbox process
```

**Result**:
- HTML converted to clean markdown
- Links preserved
- Searchable in knowledge base

---

### Workflow 4: Quick Text Notes

**Scenario**: You pasted some content into a text file and want to capture it.

```bash
# 1. Create/paste text file
echo "# Insight\n\nThis is important..." > insight.txt

# 2. Drop into inbox
mv insight.txt zettelkasten/inbox/

# 3. Process
advanced-memory inbox process
```

**Result**:
- Text wrapped in markdown
- Header added automatically
- Ready to search and link

---

## MCP Tool Usage (Claude Desktop)

### Check Inbox Status

```
Can you check my inbox status?
```

Claude uses:
```python
adn_inbox("status")
```

**Response**:
```
📥 Inbox Status

Files in Inbox: 3
Breakdown: .pdf: 1, .docx: 1, .md: 1

Previously Converted: 5

✅ Process 3 file(s): adn_inbox('process')
```

---

### Process Files

```
Process the files in my inbox
```

Claude uses:
```python
adn_inbox("process")
```

**Response**:
```
📥 Inbox Processing Complete

Total Files: 3
Successful: 3
Errors: 0

Results:
✅ research-paper.pdf - Converted to markdown and synced
✅ meeting-notes.docx - Converted to markdown and synced
✅ quick-note.md - Markdown file moved to project and synced
```

---

### Get Info

```
Tell me about the inbox system
```

Claude uses:
```python
adn_inbox("info")
```

Shows: Directories, supported formats, dependencies, status.

---

## CLI Commands

### Status

```bash
advanced-memory inbox status
```

Shows:
- Files in inbox
- Previously converted files
- Breakdown by type

---

### Process

```bash
# Process all files
advanced-memory inbox process

# Process specific file
advanced-memory inbox process meeting-notes.docx
```

---

### Info

```bash
advanced-memory inbox info
```

Shows:
- Directory locations
- Supported formats
- Dependency status
- Installation links

---

## File Conversion Details

### .md → Project (Direct Move)

**Input**: `note.md`
```markdown
# My Note

Content here.
```

**Output**: Same file, moved to project directory

**Processing**: Instant

---

### .docx → Markdown (Pandoc Conversion)

**Input**: `document.docx` (Word doc with formatting, images)

**Output**: `document.md`
```markdown
# Document Title

> **Source:** document.docx (Word document)

Content with **bold** and *italic*...

## Section

- List item
- Another item
```

**Processing**: ~1-2 seconds

---

### .pdf → Markdown (Text Extraction)

**Input**: `paper.pdf` (PDF with text)

**Output**: `paper.md`
```markdown
# Paper Title

> **Source:** paper.pdf (PDF document)
> **Note:** Extracted text may have formatting issues

## Page 1

Extracted text from page 1...

## Page 2

Extracted text from page 2...
```

**Processing**: ~2-5 seconds (depends on PDF size)

---

### .html → Markdown (Pandoc Conversion)

**Input**: `article.html` (saved web page)

**Output**: `article.md`
```markdown
# Article Title

> **Source:** article.html (HTML file)

Article content with [links](https://example.com)...
```

**Processing**: ~1-2 seconds

---

### .txt → Markdown (Wrapper)

**Input**: `notes.txt`
```
Some plain text notes here.
Multiple lines.
```

**Output**: `notes.md`
```markdown
# Notes

> **Source:** notes.txt (text file)

Some plain text notes here.
Multiple lines.
```

**Processing**: Instant

---

## Troubleshooting

### Problem: "Conversion failed" for .docx/.html

**Cause**: Pandoc not installed

**Solution**:
```bash
# Install Pandoc
# macOS
brew install pandoc

# Windows
choco install pandoc

# Verify
pandoc --version
```

---

### Problem: PDF extraction produces gibberish

**Cause**: PDF is image-based (scanned) or encrypted

**Solutions**:
1. Use OCR software to convert image PDF to text PDF first
2. Manually copy/paste text into `.txt` file
3. Use Adobe Acrobat's "Export to Text" feature

---

### Problem: File still in inbox after processing

**Cause**: Processing failed silently

**Solution**:
```bash
# Check detailed log
advanced-memory inbox process

# Look for error messages
# Common issues:
# - File locked (close in other app)
# - Permission denied (check file ownership)
# - Corrupted file
```

---

### Problem: Converted markdown has formatting issues

**Cause**: Complex formatting in source document

**Solutions**:
1. Manually clean up the markdown after conversion
2. Simplify source document before conversion
3. For critical documents, convert manually with more control

---

## Best Practices

### 1. Name Files Descriptively

```
❌ Bad:
doc1.pdf
notes.txt
temp.docx

✅ Good:
research-neural-networks-2025.pdf
meeting-notes-team-sync-2025-10-17.txt
project-proposal-draft-v2.docx
```

**Why**: Filenames become note titles.

---

### 2. Process Regularly

```bash
# Weekly workflow
cd zettelkasten/inbox
ls  # See what's accumulated
advanced-memory inbox process
```

**Why**: Prevents inbox bloat, keeps knowledge base current.

---

### 3. Review Converted Files

After processing, review markdown output:
```bash
# Search for recently added notes
advanced-memory search --recent 7d
```

Clean up formatting, add tags, create links.

---

### 4. Preserve Originals

Don't delete files from `zettelkasten/converted/`:
- Originals are your backup
- Re-convert if needed
- Reference source if conversion was imperfect

---

### 5. Use for Bulk Imports

```bash
# Import entire folder of documents
cp ~/Research/*.pdf zettelkasten/inbox/
advanced-memory inbox process
```

Great for:
- Migrating from another system
- Importing research libraries
- Batch processing documents

---

## Advanced: Custom Inbox Directory

**Override default inbox location**:

```bash
# Set environment variable
export ADVANCED_MEMORY_INBOX=~/Documents/MyInbox

# Or via config.toml
[paths]
inbox_dir = "~/Documents/MyInbox"
```

---

## Advanced: Conversion Scripts

**Pre-process files before inbox**:

```bash
#!/bin/bash
# pre-process.sh - Clean PDFs before inbox

for pdf in *.pdf; do
    # Extract text, clean, save as .md
    pdftotext "$pdf" - | sed 's/[^[:print:]]//g' > "${pdf%.pdf}.md"
    mv "${pdf%.pdf}.md" zettelkasten/inbox/
done
```

---

## Integration with Other Tools

### Obsidian → Advanced Memory

```bash
# Drop Obsidian vault into inbox
cp -r ~/ObsidianVault/*.md zettelkasten/inbox/
advanced-memory inbox process
```

### Notion Export → Advanced Memory

```bash
# Export Notion as Markdown
# Drop into inbox
cp -r ~/NotionExport/**/*.md zettelkasten/inbox/
advanced-memory inbox process
```

### Evernote → Advanced Memory

```bash
# Export notes as HTML
# Drop into inbox
cp ~/Evernote/*.html zettelkasten/inbox/
advanced-memory inbox process
```

---

## Performance

**Processing Speed** (approximate):
- `.md`: Instant (0.1s)
- `.txt`: Instant (0.1s)
- `.docx`: 1-2s per file
- `.html`: 1-2s per file
- `.pdf`: 2-5s per file (depends on size)

**Batch Processing** (50 files):
- Mixed formats: ~2-3 minutes
- Markdown only: ~10 seconds

---

## Summary

**Inbox workflow is**:
- ✅ Universal file drop zone
- ✅ Automatic conversion
- ✅ Safe (originals preserved)
- ✅ Fast and efficient
- ✅ MCP-integrated (Claude Desktop)
- ✅ CLI-accessible (automation-friendly)

**Use it for**:
- Research paper capture
- Meeting notes import
- Web article archiving
- Bulk document migration
- Quick note capture

**Start using**:
```bash
# 1. Drop files
cp ~/Downloads/document.pdf zettelkasten/inbox/

# 2. Process
advanced-memory inbox process

# 3. Done!
```

---

**Related Guides**:
- [Document Conversion Guide](../integrations/pandoc-integration-guide.md)
- [Import/Export Guide](../integrations/README.md)
- [CLI Reference](../README.md)

