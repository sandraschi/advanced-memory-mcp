# File Modification Policy

**When and how Advanced Memory modifies files**

---

## TL;DR

**Sync**: ❌ **NEVER modifies** existing files (read-only)  
**Write operations**: ✅ **ONLY when you explicitly create/edit** via MCP tools  
**Frontmatter**: ✅ **Added when YOU create** notes, NOT added to existing files  
**Relations**: ❌ **Stored in database only**, NOT written back to files

---

## The Two Modes

### Mode 1: Sync (Read-Only)

**Commands**:
```bash
advanced-memory sync
advanced-memory project add myrepo /path/to/repo
```

**What it does**:
1. **Reads** existing markdown files
2. **Parses** frontmatter (if present)
3. **Extracts** observations and relations
4. **Stores** in database
5. **Never modifies** the original files

**Your files are safe!** ✅

---

### Mode 2: Write Operations (User-Initiated)

**Commands/Tools**:
```bash
# Via CLI
advanced-memory tool write-note --title "My Note" --folder "notes" --content "Content"

# Via MCP
adn_content("create", title="My Note", content="Content")
```

**What it does**:
1. **Creates** new markdown file
2. **Adds** YAML frontmatter (title, permalink, type, etc.)
3. **Writes** your content
4. **Indexes** in database

**Only happens when YOU explicitly create/edit!** ✅

---

## What Gets Modified vs. What Doesn't

### ❌ Sync NEVER Modifies

**When you sync existing markdown files**:

**Your file** (before sync):
```markdown
# My Existing Note

This is my content. I wrote this in Obsidian.

- Some bullet points
- No frontmatter
- Just pure markdown
```

**After sync**: 
```markdown
# My Existing Note

This is my content. I wrote this in Obsidian.

- Some bullet points
- No frontmatter
- Just pure markdown
```

**NO CHANGES!** File remains exactly as you wrote it. ✅

**What happened**:
- File was **read**
- Content **indexed** in database
- File **not modified**

---

### ✅ Write Tools ADD Frontmatter

**When you create new notes via Advanced Memory**:

**You call**:
```python
adn_content("create", 
  title="Python Tips",
  content="Use type hints!",
  folder="dev"
)
```

**File created** (`dev/python-tips.md`):
```markdown
---
title: Python Tips
type: note
permalink: python-tips
created: 2025-10-17T10:30:00Z
modified: 2025-10-17T10:30:00Z
---

Use type hints!
```

**Frontmatter is added!** But only for files YOU create via Advanced Memory tools.

---

## Semantic Linking: Where Is It Stored?

### In Your Files (Optional)

**You can manually add wikilinks**:
```markdown
---
title: Flask
type: framework
---

Flask is a web framework for [[Python]].

- uses [[Jinja2]]
- depends_on [[Werkzeug]]
```

**These wikilinks**:
- Are **parsed** by Advanced Memory
- **Stored** in database as relations
- Remain in your file (you wrote them!)

---

### In Database (Always)

**After sync**, database stores:

**Entities table**:
```sql
id | title | permalink | file_path | type
1  | Flask | flask     | dev/flask.md | framework
2  | Python | python   | lang/python.md | language
3  | Jinja2 | jinja2   | lib/jinja2.md | library
```

**Relations table**:
```sql
from_id | to_id | relation_type | source
1       | 2     | uses          | wikilink
1       | 3     | uses          | wikilink  
1       | 4     | depends_on    | explicit_relation
```

**Search index table**:
```sql
permalink | title | content | ... (FTS5 full-text search)
flask     | Flask | Flask is a web framework...
```

---

## What About Relations?

### Relations Are Detected, Not Added

**Your file**:
```markdown
# Flask

Flask is a web framework.
```

**Advanced Memory detects**:
- No relations in file

**Database stores**:
- Entity "Flask"
- No relations

**File is NOT modified** to add relations! ❌

---

**Your file (with wikilinks)**:
```markdown
# Flask

Flask is a web framework for [[Python]].
```

**Advanced Memory detects**:
- Wikilink to [[Python]]
- Creates relation: Flask → uses → Python

**Database stores**:
- Entity "Flask"
- Relation: Flask → Python

**File remains unchanged!** ✅ (You wrote the wikilink, Advanced Memory just read it)

---

## When Files ARE Modified

### Scenario 1: You Create a Note

**Via MCP tool**:
```python
write_note("My Note", "Content", "folder")
```

**Result**: New file created **with frontmatter**

---

### Scenario 2: You Edit a Note

**Via MCP tool**:
```python
adn_editor("edit", 
  identifier="my-note",
  operation="append",
  content="New paragraph"
)
```

**Result**: Existing file **modified** (content appended)

---

### Scenario 3: You Move a Note

**Via MCP tool**:
```python
adn_content("move",
  identifier="my-note",
  destination="new-folder/"
)
```

**Result**: File **moved** to new location

---

### Scenario 4: You Delete a Note

**Via MCP tool**:
```python
adn_content("delete",
  identifier="my-note"
)
```

**Result**: File **moved to trash** (`.trash/` folder)

---

## Summary Table

| Operation | Modifies Files? | When? | What Changes? |
|-----------|----------------|-------|---------------|
| **Sync** | ❌ NO | Always | Nothing - read-only |
| **Project add** | ❌ NO | Always | Nothing - just points to directory |
| **Status** | ❌ NO | Always | Nothing - read-only scan |
| **write_note** | ✅ YES | When you call it | Creates new file with frontmatter |
| **edit_note** | ✅ YES | When you call it | Modifies existing file content |
| **move_note** | ✅ YES | When you call it | Moves file to new location |
| **delete_note** | ✅ YES | When you call it | Moves file to trash |
| **Auto-sync** | ❌ NO | When files change | Reads changed files, updates DB |

---

## File Ownership Model

### Files You Own (Existing Markdown)

**Examples**:
- Obsidian vault you've been using for years
- GitHub repo READMEs and docs
- Notes from other tools

**Advanced Memory's behavior**:
- ✅ **Reads** them (parses content)
- ✅ **Indexes** them (adds to database)
- ❌ **Never modifies** them
- ❌ **Doesn't add frontmatter**

**You remain in control!** Files stay exactly as you wrote them.

---

### Files Advanced Memory Creates

**Examples**:
- Notes created via `write_note`
- Zettelkasten templates from `onboard`
- Imported conversations (from Claude/ChatGPT)

**Advanced Memory's behavior**:
- ✅ **Adds frontmatter** (title, type, permalink, dates)
- ✅ **Formats** consistently
- ✅ **Manages** metadata

**These are Advanced Memory's files**, so it controls format.

---

## Frontmatter Policy

### Existing Files Without Frontmatter

**Your file**:
```markdown
# Quick Note

Just some thoughts.
```

**After sync**:
```markdown
# Quick Note

Just some thoughts.
```

**NO frontmatter added!** Advanced Memory works with it as-is.

**Database stores**:
- Title: "Quick Note" (from H1 heading)
- Permalink: "quick-note" (generated)
- Type: "note" (default)
- But **file unchanged**!

---

### Existing Files With Frontmatter

**Your file**:
```markdown
---
title: My Note
tags: [research, python]
custom_field: my_value
---

Content here.
```

**After sync**:
```markdown
---
title: My Note
tags: [research, python]
custom_field: my_value
---

Content here.
```

**NO changes!** Advanced Memory reads your frontmatter and respects it.

**Database stores**:
- Title: "My Note" (from frontmatter)
- Tags: ["research", "python"]
- Custom metadata: `{"custom_field": "my_value"}`
- Permalink: "my-note" (generated if not in frontmatter)

---

### New Files Created by Advanced Memory

**You call**:
```python
write_note("Python Tips", "Use type hints!", "dev")
```

**File created** (`dev/python-tips.md`):
```markdown
---
title: Python Tips
type: note
permalink: python-tips
created: 2025-10-17T10:30:00Z
modified: 2025-10-17T10:30:00Z
---

Use type hints!
```

**Frontmatter automatically added!** ✅

---

## Relations: Database-Only Storage

### Key Insight

**Relations are stored in the database**, not written back to files!

**Your file**:
```markdown
---
title: Flask
---

Flask is a web framework for [[Python]].
```

**Database**:
```
Relations:
  Flask → uses → Python (detected from [[Python]] wikilink)
```

**But file is NOT modified** to add more relations!

---

### Example: Related Entities

**After you create many entities**, Advanced Memory knows:
- Flask → uses → Python
- Flask → uses → Jinja2
- Flask → depends_on → Werkzeug

**But it DOESN'T go back and modify `dev/flask.md`** to add:
```markdown
- uses [[Jinja2]]
- depends_on [[Werkzeug]]
```

**Why?** Files are source of truth. Advanced Memory only modifies files when YOU explicitly ask (via write/edit tools).

---

## Philosophy

### Principle 1: Files Are Source of Truth

**Files**: What you wrote (immutable by sync)  
**Database**: Index for fast search (derived from files)

**Sync direction**: Files → Database (one-way for existing files)

---

### Principle 2: Respect Existing Content

**Your files** (from Obsidian, GitHub, etc.):
- ✅ Read as-is
- ✅ Indexed as-is
- ❌ Never modified by sync

**Advanced Memory's files** (created via tools):
- ✅ Frontmatter added
- ✅ Format controlled
- ✅ Metadata managed

---

### Principle 3: Explicit Modification Only

**Modifications only happen when**:
- ✅ You call `write_note` (create new)
- ✅ You call `edit_note` (edit existing)
- ✅ You call `move_note` (move)
- ✅ You call `delete_note` (delete)

**Never happens during**:
- ❌ Sync
- ❌ Project add
- ❌ Status check
- ❌ Search

---

## Safety Features

### 1. Backups on Overwrite

**When modifying existing file**:
```python
# Advanced Memory creates backup first
original.md → original.20251017_103000.bak
```

**Then modifies** `original.md`

**You can recover** if something goes wrong!

---

### 2. Atomic Writes

**Advanced Memory uses atomic writes**:
1. Write to temporary file: `note.md.tmp`
2. If successful, rename: `note.md.tmp` → `note.md`
3. If failed, temp file deleted

**Result**: Never partial writes! File is either old version or new version (never corrupted).

---

### 3. Trash Instead of Delete

**When you delete a note**:
```python
delete_note("old-note")
```

**Advanced Memory**:
1. Creates `.trash/` folder
2. Moves file: `notes/old-note.md` → `.trash/old-note.md`
3. Doesn't permanently delete

**You can recover deleted files!** Check `.trash/` folder.

---

## Real-World Scenarios

### Scenario 1: Import Obsidian Vault

```bash
advanced-memory project add obsidian ~/Documents/ObsidianVault
advanced-memory sync
```

**Your Obsidian files**:
- ❌ **Not modified** in any way
- ✅ **Indexed** in database
- ✅ **Searchable** via Advanced Memory

**You can continue using Obsidian!** Both tools work on same files.

---

### Scenario 2: Import GitHub Repo Docs

```bash
advanced-memory project add my-repo D:/Dev/repos/my-project
advanced-memory sync
```

**Your README.md and docs/\*.md**:
- ❌ **Not modified** by sync
- ✅ **Indexed** for search
- ✅ Can still commit to Git (no changes!)

**No Git diff!** Sync is read-only.

---

### Scenario 3: Create Note via Advanced Memory

```python
# Via MCP tool
write_note("Architecture Decision", "Use SQLite", "decisions")
```

**New file created**: `decisions/architecture-decision.md`
```markdown
---
title: Architecture Decision
type: note
permalink: architecture-decision
created: 2025-10-17T10:30:00Z
modified: 2025-10-17T10:30:00Z
---

Use SQLite
```

**This file has frontmatter** because Advanced Memory created it.

---

### Scenario 4: Edit Existing Obsidian Note

**You edit in Obsidian**:
```markdown
# My Note

Original content

[You add this line in Obsidian]
```

**Auto-sync detects change**:
1. Reads updated file
2. Updates database
3. **Does NOT modify file**

**Git diff**:
```diff
+ [You add this line in Obsidian]
```

**Only YOUR changes!** Advanced Memory didn't touch the file.

---

## Frontmatter Behavior

### Scenario A: File Has No Frontmatter

**Your file** (`notes/simple.md`):
```markdown
# Simple Note

Just text, no frontmatter.
```

**After sync**:
- File: **Unchanged**
- Database: Title extracted from H1, permalink generated

**Frontmatter NOT added to file!** ❌

---

### Scenario B: File Has Frontmatter

**Your file** (`notes/structured.md`):
```markdown
---
title: Structured Note
tags: [research]
---

Content.
```

**After sync**:
- File: **Unchanged**
- Database: Uses frontmatter values

**Frontmatter respected, not modified!** ✅

---

### Scenario C: You Create via Advanced Memory

**You call**:
```python
write_note("New Note", "Content", "notes")
```

**File created** (`notes/new-note.md`):
```markdown
---
title: New Note
type: note
permalink: new-note
created: 2025-10-17T10:30:00Z
modified: 2025-10-17T10:30:00Z
---

Content
```

**Frontmatter automatically added!** ✅ (Because Advanced Memory created the file)

---

## Database vs. File Storage

### What's Stored in Database

**Entities**:
- Title, permalink, type
- File path, checksum
- Created/modified timestamps
- Tags (from frontmatter)
- Custom metadata (from frontmatter)

**Observations**:
- Category, content, context
- Tags (from observation)
- Link to parent entity

**Relations**:
- From entity → to entity
- Relation type
- Context (if provided)
- Resolved/unresolved status

**Search Index**:
- Full-text search data (FTS5)
- Entity content, observations, relations
- Optimized for fast queries

---

### What's Stored in Files

**Only what YOU write**:
- Content (markdown)
- Frontmatter (if you add it)
- Wikilinks (if you add them)
- Observations (if you write them as markdown)
- Relations (if you write them as markdown)

**Advanced Memory reads these** but doesn't add them during sync!

---

## When Files Get Modified

### Explicit Write Operations

| Tool | Operation | File Change |
|------|-----------|-------------|
| `write_note` | Create | New file with frontmatter |
| `write_note` | Update | Overwrites existing (creates backup) |
| `adn_editor` | Append | Adds content to end of file |
| `adn_editor` | Prepend | Adds content to start of file |
| `adn_editor` | Replace | Finds and replaces content |
| `adn_content` | Move | Moves file to new location |
| `adn_content` | Delete | Moves file to `.trash/` |

---

### Read-Only Operations

| Tool | Operation | File Change |
|------|-----------|-------------|
| `sync` | Index | ❌ No change |
| `status` | Scan | ❌ No change |
| `search_notes` | Search | ❌ No change |
| `read_note` | Read | ❌ No change |
| `build_context` | Query | ❌ No change |
| `project add` | Register | ❌ No change |

---

## Can I Mix Tools?

### ✅ Yes! Mix freely!

**Obsidian + Advanced Memory**:
- Edit in Obsidian → Advanced Memory auto-syncs (reads only)
- Search in Advanced Memory → finds Obsidian changes
- Both tools work on same files!

**GitHub + Advanced Memory**:
- Edit docs in VS Code → commit to Git
- Advanced Memory syncs → indexes changes
- No conflicts!

**Manual editing + Advanced Memory**:
- Edit files in any text editor
- Run `advanced-memory sync`
- Changes indexed

**Key**: Advanced Memory **reads** your changes but doesn't modify files (unless you use write tools).

---

## Edge Case: Conflicting Edits

### What if you edit while MCP tool also edits?

**Scenario**:
1. You edit `note.md` in Obsidian: "Adding content..."
2. Obsidian saves
3. Simultaneously, MCP tool edits same file: `edit_note(...)`

**Result**:
- **Last write wins** (standard file system behavior)
- Could lose changes!

**Recommendation**: 
- Use auto-sync for reading Obsidian changes
- Don't use MCP write tools on files you're actively editing elsewhere
- Or: Use Advanced Memory OR Obsidian for editing (not both simultaneously)

---

## Best Practices

### 1. Read-Only Repositories

**For GitHub repos**, documentation, etc.:
- ✅ Use sync to index (read-only)
- ❌ Don't use write tools on these files
- ✅ Edit in your normal editor/IDE

---

### 2. Advanced Memory-Managed Notes

**For personal zettelkasten**:
- ✅ Use write tools to create notes
- ✅ Frontmatter managed automatically
- ✅ Consistent format

---

### 3. Hybrid Approach

**Obsidian vault**:
- ✅ Edit in Obsidian (no frontmatter needed)
- ✅ Sync to Advanced Memory (index only)
- ✅ Search via Advanced Memory
- ✅ Best of both worlds!

---

## Summary

### Your Questions Answered

**1. Does Advanced Memory change files?**
- ❌ **NO** during sync (read-only)
- ✅ **YES** when you use write/edit tools (explicit)

**2. Is semantic linking only in DB?**
- ✅ **Relations stored in database** (always)
- ⚠️ **Wikilinks in files** (if YOU write them)
- ❌ **Relations NOT written back to files** (database-only)

**3. Does it put in frontmatter?**
- ✅ **YES** for files it creates (via write_note)
- ❌ **NO** for existing files during sync (read-only)
- ✅ **Respects** existing frontmatter (doesn't modify)

---

## Key Principle

**Files are the source of truth. Database is the index.**

**Sync**: Files → Database (read-only)  
**Write tools**: YOU create/modify files → Database updates  
**Relations**: Detected from files, stored in database, not written back

**Your files stay safe!** 🛡️

---

*Created: 2025-10-17*  
*Purpose: Clarify file modification policy and user concerns*

