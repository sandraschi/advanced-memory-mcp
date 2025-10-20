# Claude Skills Integration - Implementation Plan

**Created**: October 19, 2025  
**Status**: In Development  
**Target Release**: v1.0.0b4

## Executive Summary

Advanced Memory's zettelkasten templates are **already compatible** with Anthropic's Claude Skills format (released Oct 15, 2025). This integration enables:

1. **Bi-directional conversion**: Zettel ↔ Skills
2. **Claude discovery**: Our 87+ templates become Claude Skills
3. **Strategic advantage**: MCP (knowledge access) + Skills (procedures) = powerful AI
4. **Skill marketplace**: Import Anthropic's official skills into Advanced Memory

## Architecture Overview

### Current State (Compatible!)

**Our Zettelkasten**:
```yaml
---
title: Python Fundamentals
type: note
permalink: python-fundamentals
tags: [python, programming]
created: 2024-12-21T14:00:00Z
---

# Content with [[WikiLinks]] and observations
```

**Claude Skills Spec** (required):
```yaml
---
name: skill-name  # REQUIRED: hyphen-case
description: When Claude should use this  # REQUIRED
license: MIT  # OPTIONAL
allowed-tools: [bash, python]  # OPTIONAL
metadata:  # OPTIONAL
  key: value
---

# Instructions for Claude
```

### Hybrid Format (Solution)

```yaml
---
# Advanced Memory fields (preserved)
title: Python Fundamentals
type: skill  # NEW: special type for skills
permalink: python-fundamentals
tags: [python, programming, claude-skill]
created: 2024-12-21T14:00:00Z
modified: 2024-12-21T14:00:00Z

# Claude Skills fields (added)
name: python-fundamentals  # Auto-generated from title
description: Guide for Python fundamentals - use when teaching or learning Python basics
license: MIT
allowed-tools: [python, bash]
metadata:
  category: developer
  difficulty: beginner
  version: 1.0
  author: Advanced Memory Team
---

# Content (unchanged - works for both!)
```

## Implementation Plan

### Phase 1: Export to Skills ✅

**Tool**: `adn_export("claude_skills", ...)`

**Features**:
- Export zettelkasten templates → Claude Skills format
- Auto-generate `name` from `title` (slugify)
- Auto-generate `description` from first paragraph or metadata
- Preserve Advanced Memory metadata in Skills `metadata` field
- Create proper folder structure (`skills/category/skill-name/SKILL.md`)
- Validate against Skills spec before export

**Usage**:
```python
# Export all developer zettel as Skills
adn_export(
    "claude_skills",
    export_path="~/Documents/claude-skills/",
    category="developer",  # Optional: filter by category
    add_license=True,      # Add MIT license file
    validate=True          # Validate against Skills spec
)
```

**Output Structure**:
```
~/Documents/claude-skills/
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
```

### Phase 2: Import from Skills ✅

**Tool**: `adn_import("claude_skills", ...)`

**Features**:
- Import official Anthropic skills → Advanced Memory zettel
- Import community skills → Advanced Memory
- Convert Skills frontmatter → Advanced Memory frontmatter
- Preserve Skills metadata in Advanced Memory metadata
- Handle skills with additional resources (scripts, templates)

**Usage**:
```python
# Import Anthropic's official skills
adn_import(
    "claude_skills",
    source_path="~/temp-anthropic-skills/",
    destination_folder="skills/anthropic",
    preserve_structure=True,
    import_resources=True  # Import scripts, templates, etc.
)
```

### Phase 3: Bidirectional Sync (Future)

**Tool**: `adn_knowledge("sync_skills", ...)`

**Features**:
- Two-way sync: Zettel ↔ Skills
- Detect changes on both sides
- Merge conflicts intelligently
- Maintain version history

## Technical Implementation

### 1. Frontmatter Converter Utility

**File**: `src/advanced_memory/services/skills_converter.py`

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class SkillsFrontmatter:
    """Claude Skills frontmatter format."""
    name: str  # REQUIRED
    description: str  # REQUIRED
    license: str | None = None
    allowed_tools: list[str] | None = None
    metadata: dict[str, Any] | None = None

class SkillsConverter:
    """Convert between Advanced Memory and Claude Skills formats."""
    
    @staticmethod
    def zettel_to_skill(zettel_frontmatter: dict) -> SkillsFrontmatter:
        """Convert zettel frontmatter to Skills format."""
        # Generate name from title (slugify)
        name = zettel_frontmatter.get("title", "").lower()
        name = name.replace(" ", "-").replace("_", "-")
        
        # Extract or generate description
        description = zettel_frontmatter.get("description")
        if not description:
            # Use first sentence or generate from title
            description = f"Guide for {zettel_frontmatter.get('title')} - use when working with this topic"
        
        # Preserve Advanced Memory metadata
        metadata = {
            "advanced_memory": {
                "type": zettel_frontmatter.get("type", "note"),
                "permalink": zettel_frontmatter.get("permalink"),
                "tags": zettel_frontmatter.get("tags", []),
                "created": str(zettel_frontmatter.get("created", "")),
                "category": zettel_frontmatter.get("category"),
            }
        }
        
        return SkillsFrontmatter(
            name=name,
            description=description,
            license="MIT",
            allowed_tools=None,  # Can be specified per-skill
            metadata=metadata
        )
    
    @staticmethod
    def skill_to_zettel(skills_frontmatter: SkillsFrontmatter) -> dict:
        """Convert Skills frontmatter to zettel format."""
        # Convert name to title
        title = skills_frontmatter.name.replace("-", " ").title()
        
        # Extract Advanced Memory metadata if preserved
        am_metadata = skills_frontmatter.metadata.get("advanced_memory", {})
        
        return {
            "title": am_metadata.get("title") or title,
            "type": am_metadata.get("type", "skill"),
            "permalink": am_metadata.get("permalink") or skills_frontmatter.name,
            "tags": am_metadata.get("tags", []) + ["claude-skill"],
            "description": skills_frontmatter.description,
            # Skills fields (preserved)
            "skills_name": skills_frontmatter.name,
            "skills_license": skills_frontmatter.license,
            "skills_allowed_tools": skills_frontmatter.allowed_tools,
            "skills_metadata": skills_frontmatter.metadata,
        }
```

### 2. Export Implementation

**File**: `src/advanced_memory/mcp/tools/adn_export.py` (extend existing)

Add new operation: `"claude_skills"`

```python
async def _export_claude_skills(
    export_path: str,
    source_folder: str = "/",
    category: str | None = None,
    add_license: bool = True,
    validate: bool = True,
    project: str | None = None,
) -> str:
    """Export zettelkasten templates to Claude Skills format."""
    
    export_dir = Path(export_path)
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Get zettel to export
    zettel = await _get_zettel_for_export(source_folder, category, project)
    
    skills_created = 0
    errors = []
    
    for note in zettel:
        try:
            # Convert frontmatter
            skills_fm = SkillsConverter.zettel_to_skill(note.frontmatter.metadata)
            
            # Validate
            if validate:
                _validate_skill(skills_fm)
            
            # Create skill directory
            skill_dir = export_dir / (note.category or "general") / skills_fm.name
            skill_dir.mkdir(parents=True, exist_ok=True)
            
            # Write SKILL.md
            skill_content = _format_skill_markdown(skills_fm, note.content)
            (skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")
            
            # Add LICENSE.txt if requested
            if add_license:
                _write_license_file(skill_dir)
            
            skills_created += 1
            
        except Exception as e:
            errors.append(f"{note.title}: {e}")
    
    # Generate summary
    summary = f"✅ Exported {skills_created} Claude Skills to {export_path}\n\n"
    
    if errors:
        summary += f"⚠️ Errors: {len(errors)}\n"
        for error in errors[:10]:  # Show first 10
            summary += f"  - {error}\n"
    
    summary += "\n📖 Usage:\n"
    summary += f"  1. Point Claude Desktop to: {export_path}\n"
    summary += "  2. Claude will discover these skills automatically\n"
    summary += "  3. Skills appear in Claude's skill picker\n"
    
    return summary
```

### 3. Import Implementation

**File**: `src/advanced_memory/mcp/tools/adn_import.py` (extend existing)

Add new operation: `"claude_skills"`

```python
async def _import_claude_skills(
    source_path: str,
    destination_folder: str = "skills/imported",
    preserve_structure: bool = True,
    import_resources: bool = True,
    project: str | None = None,
) -> str:
    """Import Claude Skills into Advanced Memory."""
    
    source_dir = Path(source_path)
    skills_imported = 0
    errors = []
    
    # Find all SKILL.md files
    skill_files = list(source_dir.rglob("SKILL.md"))
    
    for skill_file in skill_files:
        try:
            # Parse SKILL.md
            content = skill_file.read_text(encoding="utf-8")
            skills_fm = _parse_skills_frontmatter(content)
            skills_content = _remove_skills_frontmatter(content)
            
            # Convert to zettel format
            zettel_fm = SkillsConverter.skill_to_zettel(skills_fm)
            
            # Determine folder
            if preserve_structure:
                # Preserve relative path structure
                rel_path = skill_file.parent.relative_to(source_dir)
                folder = f"{destination_folder}/{rel_path}"
            else:
                folder = destination_folder
            
            # Create note in Advanced Memory
            await adn_content(
                operation="write",
                identifier=zettel_fm["title"],
                content=skills_content,
                folder=folder,
                tags=zettel_fm["tags"]
            )
            
            # Import additional resources if requested
            if import_resources:
                await _import_skill_resources(skill_file.parent, folder)
            
            skills_imported += 1
            
        except Exception as e:
            errors.append(f"{skill_file.name}: {e}")
    
    # Generate summary
    summary = f"✅ Imported {skills_imported} Claude Skills\n\n"
    
    if errors:
        summary += f"⚠️ Errors: {len(errors)}\n"
        for error in errors[:10]:
            summary += f"  - {error}\n"
    
    return summary
```

## Testing Strategy

### Test 1: Export Existing Templates

```bash
# Export developer category
adn_export(
    "claude_skills",
    export_path="./test-skills-export/",
    category="developer",
    validate=True
)

# Verify:
# 1. SKILL.md files created
# 2. Frontmatter valid per spec
# 3. Content preserved
# 4. LICENSE.txt added
```

### Test 2: Import Anthropic Skills

```bash
# Import official skills
adn_import(
    "claude_skills",
    source_path="./temp-anthropic-skills/",
    destination_folder="skills/anthropic",
    preserve_structure=True
)

# Verify:
# 1. Notes created in Advanced Memory
# 2. Frontmatter converted correctly
# 3. Resources imported (scripts, templates)
# 4. Searchable via Advanced Memory
```

### Test 3: Round-Trip Conversion

```bash
# Export → Import → Export
# Verify identical output
```

## Documentation Updates

### User Guide

**File**: `docs/user-guide/claude-skills.md`

- What are Claude Skills
- How Advanced Memory integrates
- Export workflow
- Import workflow
- Best practices

### API Reference

**File**: `docs/tools/adn_export.md`

- `claude_skills` operation docs
- Parameters and examples
- Validation rules

**File**: `docs/tools/adn_import.md`

- `claude_skills` operation docs
- Import options
- Resource handling

## Future Enhancements

### v1.0.1+

1. **Skills Marketplace**
   - Browse community skills
   - Install skills with one command
   - Share your skills

2. **Skills Discovery**
   - Auto-discover skills in project
   - Index skills for fast search
   - Skill recommendations

3. **Skills Validation**
   - Lint skills before export
   - Check against best practices
   - Suggest improvements

4. **Skills Analytics**
   - Track skill usage
   - Most popular skills
   - Skill effectiveness metrics

## Success Metrics

- ✅ 87+ zettelkasten templates exportable as Skills
- ✅ All Anthropic skills importable to Advanced Memory
- ✅ Round-trip conversion preserves data
- ✅ Claude Desktop discovers our skills
- ✅ Zero manual conversion required

## References

- [Anthropic Skills Spec](https://github.com/anthropics/anthropic-skills/blob/main/agent_skills_spec.md)
- [Anthropic Skills Repo](https://github.com/anthropics/anthropic-skills)
- [Advanced Memory Zettelkasten](../../zettelkasten/templates/)

---

**Next Steps**:
1. ✅ Implement `SkillsConverter` utility
2. ✅ Add `claude_skills` export to `adn_export`
3. ✅ Add `claude_skills` import to `adn_import`
4. ✅ Test with existing templates
5. ✅ Document in user guide
6. 🚀 Release in v1.0.0b4




