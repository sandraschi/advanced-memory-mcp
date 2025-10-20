# Claude Skills Integration Guide (Experimental)

**Status**: Conversion tools functional. Full integration pending verification of deployment mechanisms.

This guide explains Advanced Memory's bidirectional conversion between zettelkasten notes and Anthropic's Claude Skills format (released October 15, 2024).

## What Are Claude Skills?

**Claude Skills** are folders of instructions, scripts, and resources that Claude can discover and load dynamically to perform better at specific tasks. Each skill is a folder containing a `SKILL.md` file with:

- **YAML Frontmatter**: Name, description, license, allowed tools, metadata
- **Markdown Instructions**: Guidance for Claude on how to use the skill

## What This Integration Provides

### Verified Functionality

**Export**: ✅ Converts zettelkasten notes → proper Claude Skills format (SKILL.md)
**Import**: ✅ Converts Claude Skills → Advanced Memory notes with metadata preservation
**Format**: ✅ Bidirectional conversion maintains both frontmatter formats

### Where Skills Work (Verified from Anthropic)

- **Claude.ai (web)**: Paid plans can upload and use custom skills
- **Claude Code**: Via plugin marketplace
- **Claude API**: Via Skills API

### Deployment Methods (Current Understanding)

**Known**:
- Skills are folder structures with `SKILL.md` files
- Multiple skills repositories emerging (Anthropic's official + community)
- Skills can be uploaded to claude.ai

**Pending Verification**:
- Claude Desktop local skills discovery mechanism (if any)
- Automatic skills directory monitoring
- Skills management UI in various Claude interfaces

### Value Proposition

Convert your knowledge base between formats for:
- Sharing zettelkasten as Skills packages
- Importing community skills into your knowledge base
- Maintaining single source of truth across both systems

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

### Deploy Skills

**For Claude.ai (Verified)**:
1. Export skills: `adn_export("claude_skills", export_path="~/my-skills/")`
2. Log into claude.ai (paid plan required)
3. Upload `SKILL.md` files via the web interface (check claude.ai documentation for current upload mechanism)

**For Claude API (Verified)**:
- Use the Skills API endpoint to upload skills programmatically
- See [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide)

**For Claude Desktop (Unverified)**:
- Skills discovery mechanism not yet confirmed
- May support drag-and-drop of `SKILL.md` into conversations
- Configuration method pending verification
- We're actively researching this and will update docs once confirmed

**For Claude Code (Verified)**:
- Use plugin marketplace system
- Can create `.claude-plugin/marketplace.json` for skill packages

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

## Emerging Skills Ecosystem

### Official Anthropic Skills
- [anthropics/skills](https://github.com/anthropics/anthropic-skills) - Official examples and reference implementations
- Includes: document-skills, mcp-builder, skill-creator, and more

### Community Skills (Growing)
The Claude Skills ecosystem is rapidly expanding with community-created skills:
- Search GitHub for "claude skills" to find emerging repositories
- Skills for specific domains, tools, and workflows
- Both individual skills and curated collections

### Import Community Skills
```python
# Import any Skills repository into Advanced Memory
adn_import("claude_skills", 
           source_path="~/downloaded-skills-repo/",
           destination_folder="community/skill-name")

# Makes them searchable, linkable, and editable in your knowledge base
```

## Integration Roadmap

### Current Status (v1.0.0b3)
- ✅ Export: zettelkasten → Claude Skills format
- ✅ Import: Claude Skills → Advanced Memory notes
- ✅ Bidirectional metadata preservation
- ✅ Format validation and conversion

### Pending Verification
- ⏳ Claude Desktop skills discovery mechanism
- ⏳ Skills management UI across Claude interfaces
- ⏳ Best practices for skills deployment

### Future Features (Post-Verification)
- Skills validation and linting tools
- Automatic skills packaging for distribution
- Skills analytics (usage, effectiveness)
- Bidirectional sync (detect changes on both sides)
- Skills recommendations based on knowledge graph

**We're actively researching deployment mechanisms. Documentation will be updated as we verify functionality.**

## References

- [Claude Skills Spec](https://github.com/anthropics/anthropic-skills/blob/main/agent_skills_spec.md) - Official format specification
- [Anthropic Skills Repository](https://github.com/anthropics/anthropic-skills) - Example skills
- [Claude Skills Documentation](https://support.claude.com/en/articles/12512176-what-are-skills) - Official support docs
- [Advanced Memory Zettelkasten Templates](../../zettelkasten/templates/) - 87+ templates ready for conversion
- [Integration Implementation](../integrations/CLAUDE_SKILLS_INTEGRATION.md) - Technical details

---

**Quick Start**:

```python
# 1. Export your zettel as Skills format
adn_export("claude_skills", export_path="~/Documents/claude-skills/")

# 2. Deploy to your preferred Claude interface:
# - Claude.ai: Upload SKILL.md files via web interface
# - Claude API: Use Skills API endpoint
# - Claude Desktop: Deployment mechanism pending verification

# 3. Import community skills into your knowledge base
adn_import("claude_skills", 
           source_path="~/anthropic-skills/",
           destination_folder="imported/anthropic")
```

**Status**: Conversion tools are fully functional. Deployment mechanisms vary by Claude interface. We're actively verifying Claude Desktop integration.

**Questions?** See [Troubleshooting Guide](../TROUBLESHOOTING_GUIDE.md) or [file an issue](https://github.com/sandraschi/advanced-memory-mcp/issues).




