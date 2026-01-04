# Invisible Metadata in Markdown

**How to add tags and metadata that don't show in note viewers**

---

## TL;DR

**YAML frontmatter is the answer!**

```markdown
---
title: My Note
tags: [research, python]
custom_field: value
---

# My Note

This is what readers see.
(Frontmatter is hidden in most viewers)
```

**Hidden in**: Obsidian reading view, GitHub, rendered HTML, PDF exports
**Visible in**: Edit mode only
**Compatible with**: Obsidian, Advanced Memory, Hugo, Jekyll, all modern markdown tools

---

## Option 1: YAML Frontmatter (Recommended)

### What It Is

YAML metadata between `---` markers at the top of file:

```markdown
---
title: Machine Learning Fundamentals
tags: [ai, learning, data-science]
category: research
status: in-progress
difficulty: intermediate
---

# Machine Learning Fundamentals

Content starts here...
```

---

### How It's Displayed

**In Obsidian**:
- **Edit mode**: Frontmatter visible (like code)
- **Reading view**: Frontmatter **hidden** ✅
- **Graph view**: Tags from frontmatter used for connections

**In GitHub**:
- Rendered markdown: Frontmatter **hidden** ✅
- Shows only content

**In Advanced Memory**:
- **MCP tools**: Frontmatter parsed, stored in database
- **View/read**: Content displayed without frontmatter

**In PDF/HTML exports** (via Pandoc):
- Frontmatter **hidden** by default ✅
- Can optionally use for metadata (title, author, date)

---

### What Works in Frontmatter

**Standard fields** (widely supported):
```yaml
---
title: Note Title
date: 2025-10-17
tags: [tag1, tag2, tag3]
author: Sandra
category: research
---
```

**Custom fields** (any key you want):
```yaml
---
title: My Note
status: draft
priority: high
related_project: project-alpha
difficulty_level: 3
time_estimate: 30min
whatever_you_want: any_value
---
```

**All of these are**:
- ✅ Hidden in reading view
- ✅ Parsed by tools (Obsidian, Advanced Memory)
- ✅ Queryable in database
- ✅ Usable for filtering/searching

---

### Advanced Memory Support

**Advanced Memory**:
- ✅ Reads frontmatter (all fields)
- ✅ Stores in database (`entity_metadata` column)
- ✅ Searchable via full-text search
- ✅ Queryable via API
- ❌ Doesn't add frontmatter to existing files during sync
- ✅ Adds frontmatter when YOU create files via write tools

**Example**:
```markdown
---
title: Python Tips
tags: [python, programming, tips]
difficulty: beginner
reviewed: false
---

# Python Tips

Use type hints for better IDE support.
```

**After sync**, you can search:
```python
# Search by tag
search_notes("tag:python")

# Search by custom field
search_notes("difficulty:beginner")
```

---

## Option 2: HTML Comments (Limited Use)

### Syntax

```markdown
<!-- This is a comment -->

# My Note

Content here.

<!-- Another comment -->
```

---

### How It's Displayed

**In Obsidian**:
- Edit mode: Visible
- Reading view: **Hidden** ✅

**In GitHub**:
- Rendered: **Hidden** ✅

**In PDF exports**:
- Usually **hidden** ✅

---

### Limitations

**Can't use for structured metadata**:
```markdown
<!-- This is fine for notes -->

<!-- But this doesn't work for tags: -->
<!-- tags: python, research -->
<!-- Tools can't parse this reliably -->
```

**Best for**:
- ✅ Human-readable notes to self
- ✅ TODO markers
- ✅ Editor hints

**Not good for**:
- ❌ Structured metadata (use frontmatter)
- ❌ Tags (use frontmatter)
- ❌ Machine-readable data

---

### Example Use Cases

```markdown
---
title: My Note
tags: [python]
---

# My Note

<!-- TODO: Add example code -->
<!-- Note to self: Check this section later -->

Content here.

<!-- This section needs review -->
## Advanced Topics
```

**Comments are invisible** in reading view, but frontmatter is better for metadata!

---

## Option 3: Link Reference Comments (Hacky)

### Syntax

```markdown
[comment]: # (This is a comment)
[note]: # (This won't render)

# My Note

Content here.
```

---

### How It's Displayed

**In most renderers**: **Hidden** ✅

**Explanation**: This is a reference-style link with no corresponding link text, so it's not rendered.

---

### Limitations

**Very hacky**:
- ❌ Not standard
- ❌ Some renderers might show it
- ❌ Can't be reliably parsed for metadata
- ❌ Confusing to readers

**Recommendation**: Don't use this. Use frontmatter or HTML comments instead.

---

## Option 4: Custom Divs (Advanced)

### Syntax

```markdown
::: metadata
status: draft
priority: high
:::

# My Note

Content here.
```

---

### Support

**Pandoc**: ✅ Supports with extensions
**Obsidian**: ⚠️ Partial (via plugins)
**GitHub**: ❌ Not supported
**Advanced Memory**: ❌ Not parsed

**Recommendation**: Use frontmatter instead (wider support)

---

## Comparison Table

| Method | Hidden in View? | Structured Data? | Tool Support | Recommendation |
|--------|-----------------|------------------|--------------|----------------|
| **YAML Frontmatter** | ✅ YES | ✅ YES | ✅ Excellent | ⭐ **Use this!** |
| **HTML Comments** | ✅ YES | ❌ NO | ✅ Good | For notes only |
| **Link References** | ✅ YES | ❌ NO | ⚠️ Poor | Don't use |
| **Custom Divs** | ⚠️ Maybe | ✅ YES | ❌ Poor | Don't use |

---

## Best Practices

### 1. Use YAML Frontmatter for All Metadata

**Good**:
```markdown
---
title: Flask Tutorial
tags: [python, flask, web]
category: tutorial
difficulty: intermediate
estimated_time: 45min
prerequisites: [python-basics, http-fundamentals]
---

# Flask Tutorial

Content...
```

**Why**:
- ✅ Hidden in reading view (Obsidian, GitHub, etc.)
- ✅ Structured data (easily parsed)
- ✅ Widely supported
- ✅ Queryable in Advanced Memory database

---

### 2. Use HTML Comments for Human Notes

**Good**:
```markdown
---
title: My Note
tags: [research]
---

# My Note

<!-- TODO: Add references section -->
<!-- Review this section with Jane on Friday -->

Content here.
```

**Why**:
- ✅ Hidden in reading view
- ✅ Human-readable
- ✅ Doesn't interfere with tools

---

### 3. Don't Use Link Reference Comments

**Bad**:
```markdown
[comment]: # (This is confusing)
```

**Why**: Hacky, unreliable, confusing

---

## Advanced Frontmatter Tricks

### Nested Data Structures

**YAML supports complex data**:
```yaml
---
title: Project Alpha
tags: [project, active]
team:
  lead: Sandra
  members:
    - Alice
    - Bob
  start_date: 2025-01-15
milestones:
  - name: MVP
    date: 2025-03-01
    status: in-progress
  - name: Beta
    date: 2025-04-15
    status: planned
---
```

**All hidden in reading view!** ✅

**Advanced Memory stores** in `entity_metadata` as JSON.

---

### Multi-Line Values

**YAML supports multi-line**:
```yaml
---
title: Research Notes
summary: |
  This is a multi-line summary.
  It can span multiple lines.
  Perfect for longer descriptions.
notes: >
  This is folded into a single line.
  Useful for long text without line breaks.
---
```

**Hidden in reading view!** ✅

---

### Lists and Arrays

**Multiple ways**:
```yaml
---
# Array notation (JSON-style)
tags: [python, flask, web]

# YAML list notation
prerequisites:
  - python-basics
  - http-fundamentals
  - terminal-basics

# Mixed
related:
  topics: [web, backend]
  notes:
    - python-intro
    - http-guide
---
```

**All work!** Choose what's most readable for you.

---

## Obsidian-Specific Features

### Obsidian Recognizes These Frontmatter Fields

**Standard fields**:
```yaml
---
title: Note Title
tags: [tag1, tag2]
aliases: [Alternative Name, Another Name]
cssclass: custom-style
---
```

**What Obsidian does with them**:
- `tags`: Adds to tag pane, shows in graph
- `aliases`: Alternative names for linking
- `cssclass`: Applies custom CSS

**All still hidden in reading view!** ✅

---

### Obsidian Properties (New Feature)

**Obsidian now has "Properties" UI** (as of v1.4+):
- Frontmatter shown as form fields
- Can edit without touching YAML
- Still stored as frontmatter
- Still hidden in reading view

**Example**:
```yaml
---
title: My Note
status: in-progress
priority: high
---
```

**In Obsidian**: Shows as editable property fields (not raw YAML)

---

## Advanced Memory Best Practices

### Recommended Frontmatter Schema

**For notes created by Advanced Memory**:
```yaml
---
title: Note Title
type: note  # or: guide, reference, concept, person, project
permalink: note-title  # Auto-generated
created: 2025-10-17T10:30:00Z
modified: 2025-10-17T10:35:00Z
tags: [tag1, tag2]
---
```

**For your own notes** (no frontmatter required):
```markdown
# Just Write

No frontmatter needed!
Advanced Memory will index this as-is.
```

---

### Custom Metadata Examples

**Research notes**:
```yaml
---
title: Research Paper Notes
tags: [research, ml]
paper_title: "Deep Learning for NLP"
authors: [Smith, Jones]
year: 2024
citations: 150
status: reading
pages_read: 45/200
---
```

**Project notes**:
```yaml
---
title: Project Alpha Sprint 3
tags: [project, sprint]
project: project-alpha
sprint: 3
start_date: 2025-10-14
end_date: 2025-10-28
velocity: 23
completed_stories: 12
---
```

**Learning notes**:
```yaml
---
title: TypeScript Generics
tags: [typescript, programming]
topic: generics
difficulty: intermediate
time_spent: 2h
mastery_level: 3/5
reviewed: true
next_review: 2025-10-24
---
```

**All this metadata**:
- ✅ Hidden in Obsidian reading view
- ✅ Hidden in GitHub rendered markdown
- ✅ Stored in Advanced Memory database
- ✅ Searchable and queryable

---

## Markdown Comment Syntax Reference

### 1. YAML Frontmatter (Best)

```markdown
---
key: value
---
```

**Visibility**: Hidden in reading view ✅
**Structured**: YES ✅
**Recommended**: ⭐⭐⭐⭐⭐

---

### 2. HTML Comments

```markdown
<!-- This is a comment -->
```

**Visibility**: Hidden in reading view ✅
**Structured**: NO ❌
**Recommended**: ⭐⭐⭐ (for notes only)

---

### 3. Link Reference Comments

```markdown
[comment]: # (This is a comment)
```

**Visibility**: Hidden ✅
**Structured**: NO ❌
**Recommended**: ⭐ (don't use)

---

### 4. Empty Link References

```markdown
[]: # (Comment)
```

**Visibility**: Hidden ✅
**Structured**: NO ❌
**Recommended**: ⭐ (don't use)

---

## Testing Compatibility

### Test File

Create this file and test in different tools:

```markdown
---
title: Test Note
tags: [test, metadata]
custom: This is custom metadata
hidden_note: Only visible in frontmatter
---

<!-- HTML comment: This is hidden -->

# Test Note

This is the content that's always visible.

[invisible]: # (This is a link reference comment)

More content here.

<!-- Another hidden comment -->
```

**Test in**:
1. Obsidian (reading view vs. edit mode)
2. GitHub (rendered view)
3. VS Code (markdown preview)
4. Pandoc (PDF export)
5. Advanced Memory (view_note tool)

**Expected result**:
- **Reading view**: Only sees "# Test Note" and content
- **Edit mode**: Sees everything (including frontmatter/comments)
- **Tools**: Parse frontmatter, ignore HTML comments

---

## Obsidian Compatibility

### What Obsidian Does With Frontmatter

**Frontmatter in Obsidian**:
```yaml
---
title: My Note
tags: [research, python]
aliases: [Alternative Name]
cssclass: my-custom-style
---
```

**Obsidian's behavior**:
1. **Reading view**: Frontmatter **completely hidden** ✅
2. **Edit mode**: Frontmatter visible (as YAML code)
3. **Properties pane** (v1.4+): Shows as editable form fields
4. **Tags pane**: Shows tags from frontmatter
5. **Graph view**: Uses tags for connections
6. **Search**: Can search by frontmatter fields

**Your content**:
```markdown
# My Note

Content here.
```

**Reading view shows**: Only the "# My Note" heading and content

---

### Obsidian Properties Feature

**New Obsidian feature** (v1.4+): Properties UI

**Before** (raw YAML):
```yaml
---
status: in-progress
priority: high
---
```

**Now** (Obsidian Properties UI):
- Shows as form fields: `Status: [in-progress ▼]`
- Edit directly in UI (no YAML syntax)
- Still stored as frontmatter
- Still hidden in reading view

**Compatible with Advanced Memory**: ✅ YES
- Advanced Memory reads frontmatter regardless of how you edited it
- Works perfectly!

---

## GitHub Compatibility

### GitHub Markdown Rendering

**Your file**:
```markdown
---
title: README
tags: [documentation]
---

# My Project

Documentation here.
```

**GitHub shows**:
```
My Project
Documentation here.
```

**Frontmatter completely hidden!** ✅

---

## Advanced Memory Compatibility

### What Advanced Memory Does

**Reads frontmatter**:
```python
# Parses this:
---
title: My Note
tags: [python, flask]
custom_field: custom_value
---
```

**Stores in database**:
```python
entity.title = "My Note"
entity.entity_metadata = {
    "tags": ["python", "flask"],
    "custom_field": "custom_value"
}
```

**You can search**:
```python
search_notes("tag:python")
search_notes("custom_field:custom_value")
```

---

### Frontmatter Fields Advanced Memory Uses

**Standard fields**:
```yaml
---
title: Note Title           # Entity title
type: note                  # Entity type (note, guide, concept, etc.)
permalink: custom-permalink # Custom permalink (optional)
tags: [tag1, tag2]         # Tags for categorization
---
```

**Custom fields** (any YAML key):
```yaml
---
status: draft
priority: high
project: project-alpha
custom_anything: value
---
```

**All stored in `entity_metadata`!** Queryable via database.

---

## HTML Comments for Inline Notes

### Use Case: Editor Notes That Don't Export

```markdown
---
title: Article Draft
status: draft
---

# Article Title

This is the introduction.

<!-- TODO: Add statistics here -->
<!-- Source: https://example.com/data -->

This is the main content.

<!-- NOTE: This paragraph needs fact-checking -->
The claim is that...

<!-- REVIEW: Is this too technical? -->
## Technical Details
```

**In reading view**: All comments hidden ✅
**In PDF export**: Comments hidden ✅
**For you in edit mode**: Comments visible (helpful reminders)

---

## Combining Both

### Frontmatter + HTML Comments

**Best practice**:
```markdown
---
title: Research Notes
tags: [research, ai]
status: in-progress
reviewed: false
---

<!-- Started: 2025-10-15 -->
<!-- Last review: 2025-10-17 -->

# Research Notes

<!-- TODO: Add section on transformers -->

Content here.

<!-- Source: Paper by Smith et al. 2024 -->
Key insight: ...
```

**Why this works**:
- **Frontmatter**: Structured metadata (searchable)
- **HTML comments**: Inline notes (not searchable, but helpful for you)

---

## Special Cases

### Case 1: Shared Notes (GitHub, Team)

**Problem**: You want personal tags that teammates don't see

**Solution**: Use frontmatter (hidden in reading view)
```yaml
---
title: Team Documentation
# Public tags
tags: [team, documentation]

# Your personal metadata (hidden in reading view)
my_notes: needs_review
my_priority: high
my_status: read_later
---
```

**GitHub shows**: Only content, not frontmatter ✅

---

### Case 2: Published Notes (Blog, Wiki)

**Problem**: Metadata for site generator, hidden from readers

**Solution**: Frontmatter (used by Hugo, Jekyll, etc.)
```yaml
---
title: Blog Post Title
date: 2025-10-17
author: Sandra
categories: [tech, ai]
draft: false
featured_image: /images/post.jpg
---

# Blog Post Title

Content here.
```

**Hugo/Jekyll**: Uses frontmatter for site generation
**Readers**: See only content, not frontmatter ✅

---

### Case 3: Private Annotations

**Problem**: Add personal notes without changing public content

**Solution**: HTML comments
```markdown
# Public Documentation

This is the official content.

<!-- Personal note: This is outdated, check new API -->

More official content.
```

**Readers**: See only official content ✅
**You**: See your personal notes in edit mode ✅

---

## Testing Visibility

### Quick Test

Create this file:

```markdown
---
title: Visibility Test
secret_tag: only_in_frontmatter
hidden_field: this_is_invisible_in_reading_view
---

<!-- HTML comment: This is also hidden -->

# Visibility Test

This is the only text you should see in reading view.

[invisible]: # (Link reference comment)

More visible content.
```

**Open in**:
1. **Obsidian reading view**: Should only see heading + content
2. **GitHub**: Should only see heading + content
3. **VS Code preview**: Should only see heading + content

**Frontmatter and comments should be invisible!** ✅

---

## Advanced Memory Specific Tips

### Tip 1: Use Custom Fields Liberally

**Advanced Memory stores ALL frontmatter fields**:
```yaml
---
title: My Note
# Standard
tags: [python]

# Your custom fields (anything you want!)
difficulty: 3/5
time_invested: 2h
review_date: 2025-10-24
related_project: project-alpha
confidence_level: high
source_url: https://example.com
---
```

**All queryable** via Advanced Memory database! 🎯

---

### Tip 2: Consistent Schemas for Entity Types

**For "person" entities**:
```yaml
---
title: John Doe
type: person
email: john@example.com
role: Developer
company: Acme Inc
---
```

**For "project" entities**:
```yaml
---
title: Project Alpha
type: project
status: active
start_date: 2025-01-15
end_date: 2025-12-31
team_size: 5
---
```

**Benefits**:
- Consistent structure
- Easy to query
- Generate reports

---

### Tip 3: Tags in Frontmatter vs. Inline

**Frontmatter tags** (hidden):
```yaml
---
title: My Note
tags: [python, web, tutorial]
---
```

**Inline tags** (visible):
```markdown
# My Note

This tutorial covers #python and #web development.
```

**Advanced Memory**:
- ✅ Parses both
- ✅ Both searchable
- ⚠️ Frontmatter tags hidden in reading view
- ⚠️ Inline tags visible in content

**Choose based on preference!**

---

## Conclusion

### Answer to Your Question

**"Is it possible to write tags in frontmatter that don't show in note viewer?"**

✅ **YES! Use YAML frontmatter!**

```markdown
---
title: My Note
tags: [tag1, tag2, tag3]
any_custom_field: any_value
---

# My Note

This is what readers see.
```

**Frontmatter is**:
- ✅ Completely hidden in Obsidian reading view
- ✅ Hidden in GitHub rendered markdown
- ✅ Hidden in PDF exports
- ✅ Parsed by Advanced Memory (stored in database)
- ✅ Compatible with all modern markdown tools

**"What does markdown provide for that?"**

1. **YAML frontmatter** (best option) ⭐⭐⭐⭐⭐
2. **HTML comments** (for inline notes) ⭐⭐⭐
3. Link reference comments (hacky, don't use) ⭐

**Recommendation**: Use YAML frontmatter for all structured metadata! 🎯

---

*Created: 2025-10-17*
*Purpose: Guide for invisible metadata in markdown*
