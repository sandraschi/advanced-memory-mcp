# Claude Skills Integration Guide

**Advanced Memory + Claude Skills = Supercharged AI Assistant**

This guide explains how Advanced Memory integrates with Anthropic's Claude Skills (released October 15, 2025), enabling your zettelkasten notes to become Skills that Claude can discover and use.

## What Are Claude Skills?

**Claude Skills** are folders of instructions, scripts, and resources that Claude can discover and load dynamically to perform better at specific tasks. Each skill is a folder containing a `SKILL.md` file with:

- **YAML Frontmatter**: Name, description, license, allowed tools, metadata
- **Markdown Instructions**: Guidance for Claude on how to use the skill

## Why This Integration Matters

### The Synergy

**Advanced Memory MCP** provides:
- ✅ Knowledge storage and retrieval
- ✅ Semantic knowledge graphs
- ✅ Full-text search
- ✅ Entity relationships

**Claude Skills** provide:
- ✅ Procedural knowledge (how-to guides)
- ✅ Task-specific instructions
- ✅ Tool pre-approval
- ✅ Discoverable expertise

**Combined** = Claude has:
- 🧠 **Access to your knowledge** (via MCP)
- 📚 **Procedural guides** (via Skills)
- 🎯 **Context-aware assistance** (both working together)

### Real-World Example

**Without Skills**:
```
You: "Help me set up CI/CD for my Python project"
Claude: "Here's a general guide..." [generic advice]
```

**With Skills from Your Zettelkasten**:
```
You: "Help me set up CI/CD for my Python project"
Claude: [loads CI/CD Fundamentals skill from your zettelkasten]
Claude: "Based on your CI/CD Fundamentals skill, here's your specific setup..."
[Uses your documented best practices!]
```

## Export Your Zettelkasten as Skills

### Basic Export

Export all your zettelkasten templates as Claude Skills:

```python
adn_export(
    "claude_skills",
    export_path="~/Documents/claude-skills/"
)
```

**Result**: Creates a `claude-skills/` folder with:
```
claude-skills/
  developer/
    python-fundamentals/
      SKILL.md
      LICENSE.txt
    git-fundamentals/
      SKILL.md
      LICENSE.txt
  devops/
    docker-fundamentals/
      SKILL.md
      LICENSE.txt
  researcher/
    research-methods-overview/
      SKILL.md
      LICENSE.txt
```

### Filtered Export

Export only specific categories:

```python
# Export only developer zettel
adn_export(
    "claude_skills",
    export_path="~/Documents/claude-skills/developer/",
    source_folder="developer"
)

# Export only your custom notes
adn_export(
    "claude_skills",
    export_path="~/Documents/my-skills/",
    source_folder="my-custom-notes"
)
```

### Configure Claude Desktop

**Option 1: Global Skills Directory** (Recommended)

1. Open **Claude Desktop Settings**
2. Go to **Skills** section
3. Add skills directory: `~/Documents/claude-skills/`
4. Claude discovers all skills automatically

**Option 2: Per-Conversation Loading**

1. Find the skill folder (e.g., `claude-skills/developer/python-fundamentals/`)
2. Drag `SKILL.md` into Claude Desktop conversation
3. Claude loads the skill for that conversation only

## Import Anthropic's Official Skills

Import the official Anthropic skills into your Advanced Memory:

```python
# Import all official skills
adn_import(
    "claude_skills",
    source_path="~/temp-anthropic-skills/",
    destination_folder="skills/anthropic",
    preserve_structure=True
)
```

**Result**: Anthropic's skills become searchable in Advanced Memory:
- `mcp-builder` → Knowledge about building MCP servers
- `document-skills` → PDF/DOCX/PPTX manipulation
- `theme-factory` → Design themes
- And more...

**Benefits**:
- ✅ Search Anthropic skills: `search_notes("MCP server design patterns")`
- ✅ Link to official skills: `[[MCP Builder]]` in your notes
- ✅ Build knowledge graph: Your notes + official skills
- ✅ Two-way sync: Export your improvements back to Skills

## Frontmatter Format

### Advanced Memory Zettelkasten

```yaml
---
title: Python Fundamentals
type: note
permalink: python-fundamentals
tags: [python, programming]
created: 2024-12-21T14:00:00Z
modified: 2024-12-21T14:00:00Z
---

# Python Fundamentals

Core Python concepts and best practices...
```

### After Export to Claude Skills

```yaml
---
name: python-fundamentals
description: Guide for Python fundamentals - use when teaching or learning Python basics
license: MIT
metadata:
  advanced_memory:
    type: note
    permalink: python-fundamentals
    tags: [python, programming]
    created: 2024-12-21T14:00:00Z
    modified: 2024-12-21T14:00:00Z
  category: developer
---

# Python Fundamentals

Core Python concepts and best practices...
```

**Key Points**:
- ✅ `name` auto-generated from `title` (slugified)
- ✅ `description` from first paragraph or auto-generated
- ✅ Advanced Memory metadata preserved in `metadata.advanced_memory`
- ✅ Content unchanged (works for both!)

## Hybrid Notes (Best of Both)

Create notes that work natively in **both** systems:

```yaml
---
# Advanced Memory fields
title: Python Fundamentals
type: skill
permalink: python-fundamentals
tags: [python, programming, claude-skill]

# Claude Skills fields
name: python-fundamentals
description: Guide for Python fundamentals - use when teaching or learning Python basics
license: MIT
allowed-tools: [python, bash]
metadata:
  category: developer
  difficulty: beginner
  author: Your Name
---

# Python Fundamentals

[Content works in both Advanced Memory AND Claude Skills!]
```

**Advantages**:
- ✅ No export needed (already in Skills format)
- ✅ Advanced Memory can index and search
- ✅ Claude can discover directly
- ✅ Single source of truth

## Use Cases

### 1. Personal Knowledge → Claude Skills

**Scenario**: You've documented your team's coding standards in Advanced Memory

```python
# Export your team standards as Skills
adn_export(
    "claude_skills",
    export_path="~/team-skills/",
    source_folder="team/standards"
)

# Claude now follows YOUR standards when helping you code!
```

### 2. Zettelkasten → Learning Library

**Scenario**: You've built a zettelkasten on machine learning

```python
# Export ML zettel as Skills
adn_export(
    "claude_skills",
    export_path="~/ml-skills/",
    source_folder="data-scientist"
)

# Claude uses YOUR notes to teach ML concepts!
```

### 3. Import Official Skills → Enhance

**Scenario**: Import Anthropic's skills, enhance them, re-export

```python
# 1. Import official skills
adn_import("claude_skills", source_path="~/anthropic-skills/mcp-builder/", 
           destination_folder="skills/mcp")

# 2. Enhance in Advanced Memory (add your team's patterns)
# ... edit notes, add links, add observations ...

# 3. Export enhanced version
adn_export("claude_skills", export_path="~/enhanced-skills/",
           source_folder="skills/mcp")

# Claude now has official guidance + your team's enhancements!
```

## Best Practices

### 1. **Use Descriptive Titles**

❌ Bad:
```yaml
title: Notes
```

✅ Good:
```yaml
title: Python Testing Best Practices
```

Skills work better with clear, specific titles.

### 2. **Write Good Descriptions**

❌ Bad:
```yaml
description: About Python
```

✅ Good:
```yaml
description: Guide for Python testing with pytest, mocking, and TDD. Use when writing or debugging Python tests.
```

Claude uses descriptions to know **when** to load skills.

### 3. **Tag Appropriately**

```yaml
tags: [python, testing, tdd, claude-skill]
```

- Use `claude-skill` tag to mark Skills-compatible notes
- Other tags help with Advanced Memory search

### 4. **Structure for Reuse**

Write notes that serve **both** purposes:
- ✅ Reference for you (Advanced Memory search)
- ✅ Instructions for Claude (Skills)

Example structure:
```markdown
# Python Testing

## Overview
[What and why - good for both!]

## Core Concepts
[Fundamental knowledge - good for both!]

## Examples
[Code samples - especially useful for Claude!]

## Best Practices
[Your team's standards - crucial for Claude!]

## Relations
- uses [[pytest]]
- enables [[TDD]]
```

## Troubleshooting

### Skill Not Discovered

**Problem**: Claude doesn't see your exported skill

**Solutions**:
1. Check skills directory in Claude Desktop Settings
2. Verify `SKILL.md` exists in skill folder
3. Check frontmatter has required `name` and `description`
4. Restart Claude Desktop

### Validation Errors

**Problem**: Export fails with validation errors

**Solutions**:
1. Check skill name is hyphen-case (lowercase + hyphens only)
2. Verify `description` is not empty
3. Check for special characters in title/name
4. Review error messages for specific issues

### Import Conflicts

**Problem**: Imported skill has same name as existing note

**Solutions**:
1. Use different `destination_folder`
2. Rename one of the notes
3. Merge content manually

## Advanced: Custom Skill Workflows

### Create Skills from Templates

```python
# 1. Generate zettelkasten from template
adn_zettelmaker("generate", category="developer", topic="python-core")

# 2. Customize the generated notes
# ... edit notes in Advanced Memory ...

# 3. Export as Skills
adn_export("claude_skills", export_path="~/my-custom-skills/",
           source_folder="developer")
```

### Build Skill Marketplace

```python
# 1. Collect skills from various sources
adn_import("claude_skills", source_path="~/anthropic-skills/")
adn_import("claude_skills", source_path="~/community-skills/")

# 2. Curate and organize
# ... use Advanced Memory to tag, link, improve ...

# 3. Export curated collection
adn_export("claude_skills", export_path="~/curated-skills/")

# 4. Share with team!
```

## Future Roadmap

### Planned Features

**v1.0.0b5**:
- ✅ Skills import from Claude Skills format
- ✅ Bidirectional sync (detect changes on both sides)
- ✅ Skills validation and linting

**v1.0.1+**:
- Skills marketplace (browse, install, share)
- Skills analytics (usage tracking, effectiveness)
- Skills recommendations (based on your knowledge graph)
- Auto-generate Skills from existing notes

## References

- [Claude Skills Spec](https://github.com/anthropics/anthropic-skills/blob/main/agent_skills_spec.md)
- [Anthropic Skills Repository](https://github.com/anthropics/anthropic-skills)
- [Advanced Memory Zettelkasten Templates](../../zettelkasten/templates/)
- [Integration Plan](../integrations/CLAUDE_SKILLS_INTEGRATION.md)

---

**Quick Start**:

```python
# Export your zettel as Skills
adn_export("claude_skills", export_path="~/Documents/claude-skills/")

# Configure Claude Desktop to discover them
# Settings → Skills → Add Directory → ~/Documents/claude-skills/

# Done! Claude can now use your knowledge as skills!
```

**Questions?** See [Troubleshooting Guide](../TROUBLESHOOTING_GUIDE.md) or [file an issue](https://github.com/advanced-memory-mcp/issues).

