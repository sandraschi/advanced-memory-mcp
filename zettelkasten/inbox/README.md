# Inbox - Automatic Document Conversion

**Drop files here** and they'll automatically be converted to markdown and imported into Advanced Memory!

---

## Supported Formats

| Format | Conversion | Quality | Auto-Process |
|--------|------------|---------|--------------|
| `.md` | None (direct) | Perfect | ✅ |
| `.docx` | Pandoc | Excellent | ✅ |
| `.odt` | Pandoc | Excellent | ✅ |
| `.html` | Pandoc | Good | ✅ |
| `.txt` | None (direct) | Perfect | ✅ |
| `.pdf` | Text extraction | Good | ⏳ Coming soon |

---

## How It Works

### Automatic Processing (Recommended)

**If Advanced Memory MCP server is running with file watching enabled**:

1. **Drop file** into this folder
   ```bash
   cp ~/Downloads/meeting-notes.docx zettelkasten/inbox/
   ```

2. **Wait ~5 seconds** (file watcher detects it)

3. **Check converted/** folder for result
   ```bash
   ls ../converted/
   # → 20251017_143045_meeting-notes.md
   ```

4. **File appears in Advanced Memory** automatically!

---

### Manual Processing

**If file watcher is not running**:

```bash
# Process all inbox files
advanced-memory convert inbox

# Or via MCP
adn_inbox("process")
```

---

## Workflow Examples

### Example 1: Meeting Notes (.docx)

**Scenario**: You have meeting notes from Word

```bash
# 1. Drop file
cp ~/Documents/team-meeting-2025-10-17.docx zettelkasten/inbox/

# 2. Auto-converted to markdown
# → zettelkasten/converted/20251017_143045_team-meeting-2025-10-17.md

# 3. Synced to database automatically

# 4. Search for it
advanced-memory search "team meeting"
```

---

### Example 2: Research Paper (.pdf)

**Scenario**: You have a research paper PDF

```bash
# 1. Drop file
cp ~/Papers/ml-research-2025.pdf zettelkasten/inbox/

# 2. Text extracted from PDF
# → zettelkasten/converted/20251017_150000_ml-research-2025.md

# 3. Appears in Advanced Memory
```

⚠️ **Note**: PDF conversion quality depends on source (text PDF vs scanned image)

---

### Example 3: Web Page (.html)

**Scenario**: You saved a blog post as HTML

```bash
# 1. Save web page as HTML (Ctrl+S in browser)
# 2. Drop into inbox
cp ~/Downloads/blog-post.html zettelkasten/inbox/

# 3. Converted to clean markdown
# → zettelkasten/converted/20251017_161500_blog-post.md
```

---

### Example 4: Plain Text Notes (.txt)

**Scenario**: You have notes in a .txt file

```bash
# 1. Drop file
cp ~/notes.txt zettelkasten/inbox/

# 2. Converted to markdown (adds # title)
# → zettelkasten/converted/20251017_170000_notes.md
```

---

## Configuration

### Enable/Disable Inbox Processing

**In Advanced Memory config**:
```toml
# config.toml
[sync]
sync_changes = true          # Enable file watching

[features]
inbox_processing = true      # Enable inbox auto-processing
auto_convert_docx = true     # Auto-convert Word docs
auto_convert_pdf = false     # PDF conversion (experimental)
```

---

### File Watching

**Inbox is watched when**:
- Advanced Memory MCP server is running
- `sync_changes = true` in config
- `inbox_processing = true` in config

**Check status**:
```bash
advanced-memory status
# Shows: "Inbox processing: Enabled"
```

---

## Troubleshooting

### Issue 1: Files Not Converting

**Problem**: Dropped file, nothing happened

**Check**:
```bash
# Is file watcher running?
advanced-memory status

# Process manually
advanced-memory convert inbox
```

---

### Issue 2: Pandoc Not Found

**Problem**: `.docx` conversion fails with "Pandoc not found"

**Solution**:
```bash
# Install Pandoc
scoop install pandoc  # Windows
brew install pandoc   # macOS
```

---

### Issue 3: Poor PDF Quality

**Problem**: PDF converted but text is garbled

**Cause**: Scanned PDF (image-based, needs OCR)

**Solutions**:
1. Use text-based PDF instead
2. Enable OCR (requires Tesseract)
3. Manual conversion

---

### Issue 4: File Stuck in Inbox

**Problem**: File in inbox but not processed

**Causes**:
- Unsupported format
- Conversion error
- File watcher not running

**Debug**:
```bash
# Check logs
advanced-memory logs

# Try manual processing
advanced-memory convert inbox --verbose
```

---

## Advanced Usage

### Convert Single File

```bash
# Convert specific file
advanced-memory convert zettelkasten/inbox/meeting.docx

# Specify output
advanced-memory convert meeting.docx --output custom-name.md
```

---

### Process Inbox via MCP

```python
# List inbox contents
adn_inbox("list")

# Process all files
adn_inbox("process")

# Convert single file
adn_inbox("convert", file_path="meeting.docx")

# Clear inbox (after processing)
adn_inbox("clear")
```

---

## Best Practices

### 1. Clear Inbox Regularly

**Inbox is temporary**:
- Files are converted and moved
- Originals are deleted after conversion
- Don't use inbox for long-term storage

**Recommendation**: Check `converted/` weekly, move files to project folders

---

### 2. Filename Conventions

**Use descriptive filenames**:
- ✅ `team-meeting-2025-10-17.docx`
- ✅ `research-paper-ml-transformers.pdf`
- ❌ `notes.docx` (too generic)
- ❌ `untitled.docx` (not descriptive)

**Why**: Filenames become note titles!

---

### 3. Organize After Conversion

**After conversion**, organize files:
```bash
# Move to appropriate project
mv zettelkasten/converted/meeting-notes.md \
   ~/advanced-memory/work-project/meetings/

# Or create new note with content
advanced-memory write-note "Team Meeting 2025-10-17" \
   --content "$(cat zettelkasten/converted/meeting-notes.md)" \
   --folder "meetings"
```

---

### 4. Batch Processing

**Drop multiple files at once**:
```bash
# Copy all meeting notes
cp ~/Documents/meetings/*.docx zettelkasten/inbox/

# All will be processed automatically!
```

---

## Supported Conversions (Detailed)

### Word Documents (.docx, .odt)

**Conversion tool**: Pandoc

**What's preserved**:
- ✅ Text content
- ✅ Headings (# ## ###)
- ✅ Lists (bullets, numbered)
- ✅ Tables
- ✅ Links
- ✅ Bold, italic, code
- ✅ Images (extracted to assets/)

**What's lost**:
- ❌ Complex formatting (colors, fonts)
- ❌ Page breaks
- ❌ Comments
- ❌ Track changes

**Quality**: Excellent (90-95% accurate)

---

### HTML Files

**Conversion tool**: Pandoc

**What's preserved**:
- ✅ Text content
- ✅ Structure (headings, lists)
- ✅ Links
- ✅ Code blocks
- ✅ Basic formatting

**What's lost**:
- ❌ CSS styling
- ❌ JavaScript
- ❌ Complex layouts

**Quality**: Good (80-90% accurate)

---

### PDF Files (Coming Soon)

**Conversion tool**: pdftotext or PyPDF2

**What's preserved**:
- ✅ Text content (if text-based PDF)

**Limitations**:
- ❌ Scanned PDFs need OCR (complex)
- ❌ Tables often garbled
- ❌ Multi-column layouts problematic
- ❌ Images not extracted

**Quality**: Good for simple PDFs (70-80%), poor for complex PDFs

**Recommendation**: Use text-based PDFs, or manually copy-paste complex content

---

## See Also

- **Pre-Built Templates**: [../templates/README.md](../templates/README.md)
- **Custom Templates**: [../user-templates/README.md](../user-templates/README.md)
- **Document Conversion**: [docs/integrations/pandoc-integration-guide.md](../../docs/integrations/pandoc-integration-guide.md)
- **Architecture**: [docs/architecture/ZETTELKASTEN_ARCHITECTURE_PROPOSAL.md](../../docs/architecture/ZETTELKASTEN_ARCHITECTURE_PROPOSAL.md)

---

**Created**: October 17, 2025  
**Purpose**: Automatic document import for Advanced Memory  
**Status**: Implementation in progress 🚧

