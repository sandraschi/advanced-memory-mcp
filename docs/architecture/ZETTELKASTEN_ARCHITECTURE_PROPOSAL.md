# Zettelkasten Architecture Refactoring Proposal

**Proposed by**: User observation (October 17, 2025)  
**Current Problem**: Templates buried in source code, no inbox workflow  
**Proposed Solution**: User-facing `zettelkasten/` folder with inbox and auto-conversion  
**Effort**: 18-23 hours (2-3 days)  
**Priority**: Medium-High (valuable features, but not urgent)

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Current Architecture](#current-architecture)
3. [Proposed Architecture](#proposed-architecture)
4. [New Features](#new-features)
5. [Migration Plan](#migration-plan)
6. [Implementation Details](#implementation-details)
7. [Benefits and Costs](#benefits-and-costs)
8. [Decision](#decision)

---

## Problem Statement

### Current Issues

**1. Templates Buried in Source Code**
```
src/advanced_memory/cli/zettelkasten_content/
└── developer.py (4,107 lines of string templates)
```

**Problems**:
- ❌ Mixed concerns (code + data)
- ❌ Users can't easily find templates
- ❌ Can't customize without editing Python code
- ❌ Large files (4,107 lines!)
- ❌ Not user-facing

---

**2. No Inbox Workflow**

**User pain point**:
> "I have a .docx file from a meeting. How do I get this into Advanced Memory?"

**Current process** (manual, painful):
1. Open .docx in Word
2. Copy content
3. Paste into new markdown file
4. Save as .md
5. Move to project folder
6. Run `advanced-memory sync`

**Better process** (proposed):
1. Drop .docx into `zettelkasten/inbox/`
2. Auto-converted to .md
3. Auto-synced to database
4. Done!

---

**3. No Office Document Support**

**User requests** (anticipated):
- Convert meeting notes (.docx) to markdown
- Extract text from PDFs
- Import HTML exports from other tools
- Convert presentations to notes

**Current answer**: "Sorry, manual conversion only"

**Better answer**: "Drop it in the inbox!"

---

## Current Architecture

### Directory Structure

```
src/advanced_memory/
├── cli/
│   └── zettelkasten_content/     ← TEMPLATES HERE (wrong place!)
│       ├── __init__.py
│       ├── developer.py          (4,107 lines!)
│       ├── devops.py
│       └── ... (10 category files)
```

**Size**: ~10,000 lines of Python strings

**Access**:
```python
from advanced_memory.cli.zettelkasten_content import DEVELOPER_TEMPLATES
```

---

### Why This Design Exists

**Historical reasons** (not architectural reasons):

1. **Inherited from Basic Memory** (2024)
   - Original design put templates in CLI
   - We forked and kept it

2. **Packaging convenience**
   - Python files auto-included in package
   - External files need `MANIFEST.in` configuration

3. **Import speed**
   - Python import: ~10ms
   - File reading: ~50-100ms
   - 5-10x faster

4. **Type safety**
   - Python dict validated at import
   - Syntax errors caught immediately

**But**: These are **convenience**, not **good architecture**!

---

## Proposed Architecture

### New Directory Structure

```
zettelkasten/                       ← NEW: Root-level, user-facing
├── README.md                       User guide ("What is this folder?")
│
├── templates/                      Pre-built templates (read-only)
│   ├── README.md                   Template catalog
│   ├── developer/
│   │   ├── python-basics/
│   │   │   ├── data-types.md
│   │   │   ├── functions.md
│   │   │   ├── classes.md
│   │   │   └── ...
│   │   ├── git/
│   │   │   ├── branching.md
│   │   │   ├── merging.md
│   │   │   └── ...
│   │   └── ...
│   ├── devops/
│   │   ├── docker/
│   │   ├── kubernetes/
│   │   └── ...
│   └── ... (10 categories, 150+ templates)
│
├── inbox/                          ← NEW: Drop files here!
│   ├── README.md                   Instructions for inbox
│   └── .gitkeep                    Keep folder in git
│
├── user-templates/                 ← NEW: Custom user templates
│   ├── README.md                   How to create templates
│   └── .gitkeep
│
└── converted/                      ← NEW: Auto-converted documents
    ├── README.md                   Conversion log
    └── .gitkeep
```

**Total size**: Same (~425 KB) but organized into 150+ files instead of 10 large files

---

### Code Changes

```
src/advanced_memory/
├── services/
│   ├── template_loader.py          ← NEW: Load templates from zettelkasten/
│   ├── inbox_processor.py          ← NEW: Watch and process inbox
│   └── doc_converter.py            ← NEW: Convert office docs to markdown
│
├── cli/
│   ├── commands/
│   │   └── convert.py              ← NEW: CLI for manual conversion
│   └── zettelkasten_content/       ← REMOVED: Migrate to zettelkasten/
│
└── mcp/
    └── tools/
        └── adn_inbox.py            ← NEW: MCP tool for inbox operations
```

---

## New Features

### Feature 1: Inbox Workflow

**User drops file** → `zettelkasten/inbox/meeting-notes.docx`

**System automatically**:
1. Detects new file (file watcher)
2. Identifies format (.docx)
3. Converts to markdown (via Pandoc)
4. Extracts metadata (title, date, author)
5. Moves to `converted/meeting-notes.md`
6. Syncs to database
7. Notifies user (optional)

**User result**: File appears in Advanced Memory!

---

### Feature 2: Document Conversion

**Supported formats**:

| Format | Tool | Quality | Status |
|--------|------|---------|--------|
| **.docx** | Pandoc | Excellent | Easy |
| **.odt** | Pandoc | Excellent | Easy |
| **.html** | Pandoc | Good | Easy |
| **.epub** | Pandoc | Good | Easy |
| **.pdf** (text) | pdftotext | Good | Medium |
| **.pdf** (scanned) | OCR (Tesseract) | Medium | Hard |
| **.txt** | Direct | Perfect | Trivial |

**Priority**: .docx first (most common), PDF second

---

### Feature 3: Template Discovery

**Users can browse**:
```bash
# List all templates
ls zettelkasten/templates/

# Browse category
ls zettelkasten/templates/developer/

# View template
cat zettelkasten/templates/developer/python-basics/data-types.md
```

**Users can customize**:
```bash
# Copy template
cp zettelkasten/templates/developer/python-basics/data-types.md \
   zettelkasten/user-templates/my-python-notes.md

# Edit
vim zettelkasten/user-templates/my-python-notes.md

# Generate from custom template
advanced-memory generate --template zettelkasten/user-templates/my-python-notes.md
```

---

### Feature 4: MCP Inbox Tool

```python
# New MCP tool
adn_inbox(
    operation="process",     # Process all inbox files
    convert=True,            # Auto-convert office docs
    move_to="imported"       # Destination folder
)
```

**Operations**:
- `list` - Show inbox contents
- `process` - Convert and import all
- `convert` - Convert single file
- `clear` - Empty inbox (after processing)

---

## Migration Plan

### Phase 1: Extract Templates (4-5 hours)

**Step 1**: Create directory structure
```bash
mkdir -p zettelkasten/templates/{developer,devops,data_scientist,...}
```

**Step 2**: Extract Python templates to markdown
```python
# Script: scripts/extract_templates.py
for category, topics in DEVELOPER_TEMPLATES.items():
    for title, content in topics.items():
        # Write to: zettelkasten/templates/developer/{category}/{title}.md
        write_file(path, content)
```

**Step 3**: Create template loader
```python
# src/advanced_memory/services/template_loader.py
class TemplateLoader:
    def load_category(self, category: str) -> dict:
        """Load all templates from zettelkasten/templates/{category}/"""
        
    def load_template(self, path: str) -> str:
        """Load single template file"""
        
    def list_available(self) -> dict:
        """List all available templates"""
```

**Step 4**: Update imports
```python
# Before:
from advanced_memory.cli.zettelkasten_content import DEVELOPER_TEMPLATES

# After:
from advanced_memory.services.template_loader import TemplateLoader
loader = TemplateLoader()
templates = loader.load_category("developer")
```

**Step 5**: Update packaging
```toml
# pyproject.toml
[tool.hatch.build.targets.wheel]
packages = ["src/advanced_memory"]

[tool.hatch.build.targets.wheel.force-include]
"zettelkasten" = "advanced_memory/data/zettelkasten"
```

---

### Phase 2: Inbox System (6-8 hours)

**Step 1**: Create inbox structure
```bash
mkdir -p zettelkasten/{inbox,user-templates,converted}
```

**Step 2**: Create inbox processor
```python
# src/advanced_memory/services/inbox_processor.py
class InboxProcessor:
    def __init__(self, inbox_path: Path):
        self.inbox_path = inbox_path
        
    async def watch_inbox(self):
        """Watch inbox folder for new files"""
        async for event in watch_directory(self.inbox_path):
            if event.type == "file_created":
                await self.process_file(event.path)
                
    async def process_file(self, file_path: Path):
        """Convert and import file"""
        # 1. Detect format
        # 2. Convert to markdown
        # 3. Move to converted/
        # 4. Sync to database
```

**Step 3**: Integrate with watch service
```python
# src/advanced_memory/sync/watch_service.py
class WatchService:
    def __init__(self):
        self.project_watcher = ProjectWatcher()
        self.inbox_watcher = InboxProcessor()  # NEW
        
    async def run(self):
        await asyncio.gather(
            self.project_watcher.watch(),
            self.inbox_watcher.watch_inbox()  # NEW
        )
```

---

### Phase 3: Document Conversion (8-10 hours)

**Step 1**: Create converter service
```python
# src/advanced_memory/services/doc_converter.py
class DocumentConverter:
    async def convert_docx(self, path: Path) -> str:
        """Convert .docx to markdown via Pandoc"""
        result = await subprocess.run([
            "pandoc",
            str(path),
            "-t", "markdown",
            "-o", str(output_path)
        ])
        
    async def convert_pdf(self, path: Path) -> str:
        """Extract text from PDF"""
        # Use pdftotext or PyPDF2
        
    async def convert_html(self, path: Path) -> str:
        """Convert HTML to markdown"""
        result = await subprocess.run([
            "pandoc",
            str(path),
            "-t", "markdown"
        ])
```

**Step 2**: Add CLI command
```bash
advanced-memory convert inbox --format docx
advanced-memory convert file.docx --output note.md
```

**Step 3**: Add MCP tool
```python
@mcp.tool
async def adn_inbox(
    operation: str,
    file_path: str | None = None,
    convert: bool = True
) -> str:
    """Process inbox files and convert documents to markdown"""
```

---

## Implementation Details

### Template Loader Service

```python
# src/advanced_memory/services/template_loader.py

from pathlib import Path
import frontmatter

class TemplateLoader:
    """Load zettelkasten templates from markdown files"""
    
    def __init__(self, templates_dir: Path | None = None):
        self.templates_dir = templates_dir or self._get_default_dir()
        
    def _get_default_dir(self) -> Path:
        """Get templates directory (bundled with package)"""
        # Option 1: In package data
        pkg_data = Path(__file__).parent.parent / "data" / "zettelkasten" / "templates"
        
        # Option 2: In repo root (development)
        repo_root = Path.cwd() / "zettelkasten" / "templates"
        
        return pkg_data if pkg_data.exists() else repo_root
        
    def load_category(self, category: str) -> dict[str, dict[str, str]]:
        """Load all templates for a category"""
        category_dir = self.templates_dir / category
        templates = {}
        
        for topic_dir in category_dir.iterdir():
            if not topic_dir.is_dir():
                continue
                
            topic_templates = {}
            for template_file in topic_dir.glob("*.md"):
                content = template_file.read_text(encoding="utf-8")
                title = template_file.stem.replace("-", " ").title()
                topic_templates[title] = content
                
            topic_name = topic_dir.name.replace("-", " ").title()
            templates[topic_name] = topic_templates
            
        return templates
        
    def list_available(self) -> dict[str, list[str]]:
        """List all available categories and topics"""
        categories = {}
        for category_dir in self.templates_dir.iterdir():
            if not category_dir.is_dir():
                continue
            topics = [d.name for d in category_dir.iterdir() if d.is_dir()]
            categories[category_dir.name] = topics
        return categories
```

---

### Inbox Processor Service

```python
# src/advanced_memory/services/inbox_processor.py

from pathlib import Path
from watchfiles import awatch
from advanced_memory.services.doc_converter import DocumentConverter

class InboxProcessor:
    """Process files dropped into inbox folder"""
    
    def __init__(
        self,
        inbox_path: Path,
        converted_path: Path,
        auto_sync: bool = True
    ):
        self.inbox_path = inbox_path
        self.converted_path = converted_path
        self.auto_sync = auto_sync
        self.converter = DocumentConverter()
        
    async def watch_inbox(self):
        """Watch inbox folder for new files"""
        async for changes in awatch(self.inbox_path):
            for change_type, path in changes:
                if change_type == "added":
                    await self.process_file(Path(path))
                    
    async def process_file(self, file_path: Path):
        """Process a single file from inbox"""
        suffix = file_path.suffix.lower()
        
        # Determine conversion method
        if suffix == ".md":
            # Already markdown, just move
            await self._move_to_converted(file_path)
        elif suffix in [".docx", ".odt", ".doc"]:
            # Convert office doc
            md_path = await self.converter.convert_docx(file_path)
            await self._move_to_converted(md_path)
            file_path.unlink()  # Remove original
        elif suffix == ".pdf":
            # Extract PDF text
            md_path = await self.converter.convert_pdf(file_path)
            await self._move_to_converted(md_path)
            file_path.unlink()
        elif suffix in [".html", ".htm"]:
            # Convert HTML
            md_path = await self.converter.convert_html(file_path)
            await self._move_to_converted(md_path)
            file_path.unlink()
        else:
            # Unknown format, skip
            logger.warning(f"Unknown format: {suffix}")
            return
            
        # Auto-sync if enabled
        if self.auto_sync:
            await self._trigger_sync()
            
    async def _move_to_converted(self, file_path: Path):
        """Move file to converted folder with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = self.converted_path / f"{timestamp}_{file_path.name}"
        file_path.rename(dest)
        
    async def _trigger_sync(self):
        """Trigger sync to database"""
        from advanced_memory.sync.sync_service import SyncService
        sync = SyncService()
        await sync.sync_project()
```

---

### Document Converter Service

```python
# src/advanced_memory/services/doc_converter.py

import subprocess
from pathlib import Path

class DocumentConverter:
    """Convert various document formats to markdown"""
    
    async def convert_docx(self, input_path: Path) -> Path:
        """Convert .docx to markdown via Pandoc"""
        output_path = input_path.with_suffix(".md")
        
        result = await asyncio.create_subprocess_exec(
            "pandoc",
            str(input_path),
            "-t", "markdown",
            "-o", str(output_path),
            "--extract-media", ".",  # Extract images
            "--wrap=none"  # Don't wrap long lines
        )
        await result.wait()
        
        if result.returncode != 0:
            raise ConversionError(f"Pandoc failed: {input_path}")
            
        return output_path
        
    async def convert_pdf(self, input_path: Path) -> Path:
        """Extract text from PDF"""
        output_path = input_path.with_suffix(".md")
        
        # Try pdftotext first (if available)
        try:
            result = await asyncio.create_subprocess_exec(
                "pdftotext",
                str(input_path),
                str(output_path)
            )
            await result.wait()
        except FileNotFoundError:
            # Fall back to PyPDF2
            import PyPDF2
            with open(input_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n\n".join(page.extract_text() for page in reader.pages)
                output_path.write_text(f"# {input_path.stem}\n\n{text}")
                
        return output_path
        
    async def convert_html(self, input_path: Path) -> Path:
        """Convert HTML to markdown via Pandoc"""
        output_path = input_path.with_suffix(".md")
        
        result = await asyncio.create_subprocess_exec(
            "pandoc",
            str(input_path),
            "-f", "html",
            "-t", "markdown",
            "-o", str(output_path)
        )
        await result.wait()
        
        return output_path
```

---

### New MCP Tool: adn_inbox

```python
# src/advanced_memory/mcp/tools/adn_inbox.py

@mcp.tool
async def adn_inbox(
    operation: str,
    file_path: str | None = None,
    convert: bool = True,
    auto_sync: bool = True
) -> str:
    """
    Process inbox files and convert documents to markdown.
    
    Operations:
    - list: Show inbox contents
    - process: Convert and import all inbox files
    - convert: Convert single file
    - clear: Empty inbox after processing
    
    Examples:
    - adn_inbox("list") → Show all files in inbox
    - adn_inbox("process") → Convert all files, sync to database
    - adn_inbox("convert", file_path="meeting.docx") → Convert single file
    """
    
    inbox_processor = InboxProcessor(
        inbox_path=get_inbox_path(),
        converted_path=get_converted_path(),
        auto_sync=auto_sync
    )
    
    if operation == "list":
        return _list_inbox_files()
    elif operation == "process":
        return await _process_all_inbox_files(inbox_processor)
    elif operation == "convert":
        return await _convert_single_file(file_path, inbox_processor)
    elif operation == "clear":
        return _clear_inbox()
```

---

## Benefits and Costs

### Benefits

**User Experience**:
- ✅ **Inbox workflow** - Drop files, auto-convert, auto-sync (killer feature!)
- ✅ **Template discovery** - Browse templates as markdown files
- ✅ **Customization** - Copy and modify templates easily
- ✅ **Office doc support** - .docx, .pdf → markdown
- ✅ **Clear organization** - User-facing `zettelkasten/` folder

**Architecture**:
- ✅ **Separation of concerns** - Data (templates) vs code (services)
- ✅ **Extensible** - Easy to add new converters
- ✅ **User-centric** - Files organized for users, not developers

**Features**:
- ✅ **New MCP tool** - `adn_inbox` for Claude Desktop users
- ✅ **New CLI commands** - `advanced-memory convert`
- ✅ **Smaller files** - 150 files of 50-200 lines vs 10 files of 1,000+ lines

---

### Costs

**Effort**:
- ⏱️ **18-23 hours** total (2-3 days of work)
- ⏱️ Phase 1: 4-5 hours (templates)
- ⏱️ Phase 2: 6-8 hours (inbox)
- ⏱️ Phase 3: 8-10 hours (conversion)

**Complexity**:
- ⚠️ **More complex packaging** - Need `MANIFEST.in` or `data_files`
- ⚠️ **File I/O overhead** - ~5-10x slower (10ms → 50ms) - still acceptable
- ⚠️ **Path resolution** - Need to find templates directory
- ⚠️ **New dependencies** - Pandoc (external), PyPDF2 (Python)

**Risk**:
- ⚠️ **Breaking changes** - Need to update all imports
- ⚠️ **Migration** - Users need to re-pull templates
- ⚠️ **Testing** - Comprehensive testing required

---

### Cost-Benefit Analysis

| Aspect | Current Design | Proposed Design | Winner |
|--------|----------------|-----------------|--------|
| **User experience** | ⭐⭐ Poor | ⭐⭐⭐⭐⭐ Excellent | Proposed |
| **Performance** | ⭐⭐⭐⭐⭐ 10ms | ⭐⭐⭐⭐ 50ms | Current |
| **Simplicity** | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐ Medium | Current |
| **Architecture** | ⭐⭐ Poor | ⭐⭐⭐⭐⭐ Clean | Proposed |
| **Features** | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ Rich | Proposed |
| **Maintenance** | ⭐⭐⭐⭐ Easy | ⭐⭐⭐ Medium | Current |

**Overall winner**: **Proposed design** (better UX and features outweigh complexity)

---

## Decision

### Recommendation: IMPLEMENT

**Why**:
1. **Inbox workflow** is a killer feature (drop files, auto-convert!)
2. **Office doc conversion** is valuable (.docx, .pdf support)
3. **Better architecture** (separation of concerns)
4. **User-centric** design (easy discovery and customization)

**When**: Phase 5+ (after dashboard implementation)

**Approach**: Incremental migration
1. **Week 1**: Create `zettelkasten/` structure, extract templates
2. **Week 2**: Implement inbox + file watcher
3. **Week 3**: Add document conversion (Pandoc, PDF)
4. **Week 4**: Testing, documentation, migration guide

---

### Migration Strategy

**Backward compatibility**:
```python
# Support both old and new locations during transition
try:
    # New location (preferred)
    from advanced_memory.services.template_loader import TemplateLoader
    loader = TemplateLoader()
    templates = loader.load_category("developer")
except (ImportError, FileNotFoundError):
    # Fall back to old location
    from advanced_memory.cli.zettelkasten_content import DEVELOPER_TEMPLATES
    templates = DEVELOPER_TEMPLATES
```

**Migration period**: 1-2 releases
- v1.0.x: Both locations work, deprecation warning
- v1.1.x: New location only

---

### Feature Flags

Enable gradual rollout:

```toml
# config.toml
[features]
inbox_processing = true          # Enable inbox workflow
auto_convert_docx = true         # Auto-convert .docx files
auto_convert_pdf = false         # PDF conversion (experimental)
template_migration = "new"       # "old", "new", or "both"
```

---

## Comparison with Competition

### Obsidian

**Obsidian approach**: User manages files directly
- Templates as markdown files in vault
- No auto-conversion
- Manual import

**Advanced Memory (proposed)**: Smart automation
- Templates + Inbox + Auto-conversion
- **More automated than Obsidian!**

---

### Notion

**Notion approach**: Cloud-based, drag-and-drop
- Supports .docx, .pdf, .txt import
- Auto-converts on upload
- Web interface

**Advanced Memory (proposed)**: Local-first with automation
- Same conversion features
- **Local files, no cloud!**

---

## Implementation Checklist

### Pre-Implementation

- [ ] Create architectural design document (this file) ✅
- [ ] Review with stakeholders
- [ ] Prioritize against other features
- [ ] Schedule implementation window

### Phase 1: Templates (Week 1)

- [ ] Create `zettelkasten/templates/` structure
- [ ] Write extraction script (`scripts/extract_templates.py`)
- [ ] Extract all 150+ templates to markdown
- [ ] Create `TemplateLoader` service
- [ ] Update imports in CLI (`onboard.py`)
- [ ] Update imports in MCP tools (`zettelmaker.py`)
- [ ] Update packaging (`pyproject.toml`)
- [ ] Test template loading
- [ ] Update documentation

### Phase 2: Inbox (Week 2)

- [ ] Create `zettelkasten/inbox/` structure
- [ ] Write inbox README with instructions
- [ ] Create `InboxProcessor` service
- [ ] Integrate with `WatchService`
- [ ] Add file detection logic
- [ ] Add basic file handling (.md files first)
- [ ] Test inbox workflow
- [ ] Create MCP tool (`adn_inbox`)

### Phase 3: Conversion (Week 3)

- [ ] Create `DocumentConverter` service
- [ ] Implement .docx conversion (Pandoc)
- [ ] Implement .html conversion (Pandoc)
- [ ] Implement .txt conversion (direct)
- [ ] Implement .pdf conversion (pdftotext)
- [ ] Add CLI command (`advanced-memory convert`)
- [ ] Test all conversions
- [ ] Handle errors gracefully

### Phase 4: Testing & Launch (Week 4)

- [ ] Comprehensive integration tests
- [ ] Migration testing (old → new)
- [ ] Documentation updates
- [ ] User guide for inbox workflow
- [ ] Conversion quality testing
- [ ] Performance benchmarks
- [ ] Beta release for testing
- [ ] Stable release

---

## Open Questions

### Q1: What about large PDFs?

**Issue**: OCR on 50-page PDF = slow (minutes)

**Options**:
1. Process in background, notify when done
2. Skip PDFs over certain size
3. Extract first N pages only

**Recommendation**: Background processing with notification

---

### Q2: What about images in .docx?

**Issue**: Images embedded in Word docs

**Options**:
1. Extract images to `assets/` folder (Pandoc supports this)
2. Skip images, text only
3. Convert images to base64 inline

**Recommendation**: Extract to `assets/`, reference in markdown

---

### Q3: Should inbox be per-project or global?

**Options**:
1. Global inbox: `zettelkasten/inbox/` (single)
2. Per-project: Each project has `inbox/` folder

**Recommendation**: Per-project (more flexible)

---

### Q4: Git ignore inbox contents?

**Issue**: Inbox might contain temporary files, sensitive docs

**Recommendation**: Add to `.gitignore`:
```gitignore
zettelkasten/inbox/*
!zettelkasten/inbox/README.md
!zettelkasten/inbox/.gitkeep
```

---

## Future Enhancements

### Phase 5+: Advanced Features

**Template Marketplace** (connects to Phase 5 from original plan):
- User templates can be shared
- Community template repository
- Template ratings and reviews

**Smart Conversion**:
- AI-enhanced PDF extraction (better OCR)
- Preserve formatting (tables, lists)
- Extract structured data from documents

**Inbox Intelligence**:
- Auto-categorize files (AI determines folder)
- Extract metadata from documents
- Suggest tags based on content

---

## Summary

### The Problem

- ❌ Templates in `src/advanced_memory/cli/` (wrong place - code, not user-facing)
- ❌ No inbox workflow (users manually convert docs)
- ❌ No office document support

### The Solution

- ✅ `zettelkasten/` folder in repo root (user-facing)
- ✅ `inbox/` for dropping files (auto-converts!)
- ✅ Support .docx, .pdf, .html → markdown
- ✅ Template discovery and customization

### The Effort

- **18-23 hours** total (2-3 days)
- Incremental implementation (4 phases)
- High value features (inbox + conversion)

### The Recommendation

**YES, implement this!**
- Better architecture
- Killer features (inbox, conversion)
- User-centric design
- Worth the effort

**When**: After current priorities (dashboard, etc.)

**Priority**: Medium-High (valuable, not urgent)

---

**Created**: October 17, 2025  
**Status**: Architectural proposal (design phase)  
**Next Step**: Review and prioritize against roadmap  
**Decision**: Pending (recommend: implement in Phase 5+)

