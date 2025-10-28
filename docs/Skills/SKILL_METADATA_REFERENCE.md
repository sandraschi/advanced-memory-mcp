# Claude Skills Metadata Reference

**Last Updated:** 2025-10-27  
**Advanced Memory MCP Version:** 1.0.0+  
**Claude Skills Spec:** Anthropic (October 2025)

---

## Overview

This document defines the complete metadata structure for Claude Skills in Advanced Memory.
Skills can be created using either `adn_skills` or `adn_content` tools with auto-detection.

---

## YAML Frontmatter Structure

### Required Fields

Every skill MUST have these fields:

```yaml
---
name: skill-name-in-hyphen-case
description: When Claude should use this skill and what it provides
---
```

**Field Specifications:**

| Field | Type | Format | Required | Description |
|-------|------|--------|----------|-------------|
| `name` | string | hyphen-case | ✅ YES | Unique identifier (lowercase, hyphens only) |
| `description` | string | free-form text | ✅ YES | When Claude should use skill (20+ chars recommended) |

---

### Optional Fields

```yaml
---
name: skill-name
description: Skill description
license: CC-BY-4.0
allowed-tools:
  - tool_name_1
  - tool_name_2
metadata:
  category: developer
  difficulty: advanced
  created: 2025-10-27
  custom_field: custom_value
---
```

**Optional Field Specifications:**

| Field | Type | Format | Description |
|-------|------|--------|-------------|
| `license` | string | License name or path | Default: CC-BY-4.0 |
| `allowed-tools` | list | Tool names | Pre-approved tools (Claude Code only) |
| `metadata` | dict | key-value pairs | Custom metadata |

---

### Metadata Section

The `metadata` dict can contain any key-value pairs. Common fields:

```yaml
metadata:
  # Categorization
  category: developer       # developer, researcher, writer, knowledge-worker, etc.
  difficulty: advanced      # beginner, intermediate, advanced, expert
  
  # Timestamps
  created: 2025-10-27
  modified: 2025-10-27
  
  # Authorship
  author: Sandra Schipal
  version: 1.2.0
  
  # Organization
  tags: ["python", "automation", "scripting"]
  project: personal-skills
  
  # Custom fields (anything you need!)
  language: English
  domain: programming
  estimated_time: 30m
```

---

## Complete Example

```yaml
---
name: autohotkey-v2-expert
description: Expert guidance for AutoHotkey v2 scripting, automation, and best practices. Use when working with AHK v2, creating hotkeys, or automating Windows tasks.
license: CC-BY-4.0
allowed-tools:
  - read_file
  - write_file
  - run_terminal_cmd
metadata:
  category: developer
  difficulty: advanced
  created: 2025-10-27
  author: Sandra Schipal
  version: 1.0.0
  tags: ["autohotkey", "windows", "automation"]
---

# AutoHotkey v2 Expert

[Skill content goes here...]
```

---

## Validation Rules

### Name Field

**Format:** `^[a-z0-9-]+$` (hyphen-case)

✅ **Valid Names:**
- `python-expert`
- `autohotkey-v2-guide`
- `research-methodology-101`

❌ **Invalid Names:**
- `Python Expert` (spaces not allowed)
- `python_expert` (underscores not allowed)
- `Python-Expert` (uppercase not allowed)
- `-python-expert` (cannot start with hyphen)
- `python-expert-` (cannot end with hyphen)
- `python--expert` (consecutive hyphens not allowed)

### Description Field

**Requirements:**
- Minimum 20 characters (recommended)
- No angle brackets (`<` or `>`)
- Should describe WHEN to use the skill
- Include keywords for discoverability

✅ **Good Description:**
```yaml
description: Expert Python guidance for advanced patterns, best practices, and architectural decisions. Use when writing Python code, debugging issues, or discussing Python-specific design patterns.
```

❌ **Poor Description:**
```yaml
description: Python help  # Too short, no context
```

### License Field

**Common Values:**
- `MIT`
- `CC-BY-4.0` (Creative Commons Attribution)
- `CC-BY-SA-4.0` (Creative Commons ShareAlike)
- `Apache-2.0`
- Path to LICENSE file: `LICENSE.txt`

### Metadata Field

**Must be:** Dictionary (key-value pairs)

```yaml
metadata:
  category: developer  # string
  difficulty: advanced  # string
  tags: ["tag1", "tag2"]  # list
```

---

## Auto-Detection in Advanced Memory

### Using `adn_content`

When writing to `skills/` folder, frontmatter is auto-generated:

```python
# Just write content - frontmatter added automatically!
adn_content("write",
    identifier="Python Expert",
    content="# Python Expert\n\nAdvanced guidance...",
    folder="skills/developer")

# Generated frontmatter:
# ---
# name: python-expert
# description: Expert guidance for Python Expert. Use when working with python expert or related topics.
# type: skill
# metadata:
#   category: developer
# ---
```

**Auto-detection rules:**
1. Folder path starts with `skills/`
2. If no frontmatter detected → auto-generate
3. Extract category from path: `skills/developer` → `category: developer`
4. Convert title to skill name: `Python Expert` → `python-expert`
5. Set `entity_type` to `skill` automatically

### Using `adn_skills("create")`

Explicit skill creation with template:

```python
adn_skills("create",
    skill_name="python-expert",
    description="Expert Python guidance for advanced patterns...",
    category="developer",
    difficulty="advanced")

# Generates complete skill with:
# - Proper YAML frontmatter
# - Template structure (Overview, Usage, Examples, Guidelines)
# - Resource folders (scripts/, references/, assets/)
```

---

## Skill Categories

Standard categories (customizable):

| Category | Description | Examples |
|----------|-------------|----------|
| `developer` | Programming and development | Python, Git, Testing, Architecture |
| `researcher` | Research and analysis | Research methods, Critical thinking |
| `writer` | Writing and content creation | Storytelling, Editing, Publishing |
| `knowledge-worker` | Productivity and PKM | Productivity, Note-taking, Communication |
| `devops` | Infrastructure and deployment | Docker, Kubernetes, CI/CD |
| `data-scientist` | Data and ML | Machine Learning, Statistics |
| `uiux-designer` | Design and UX | Design Principles, Figma, User Research |
| `product-manager` | Product management | Strategy, Roadmaps, Metrics |
| `entrepreneur` | Business and startups | Business Models, Fundraising |
| `creative` | Creative work | Photography, Video, Audio |

---

## Difficulty Levels

| Level | Meaning | Target Audience |
|-------|---------|-----------------|
| `beginner` | Fundamentals and basics | New to the topic |
| `intermediate` | Practical application | Some experience |
| `advanced` | Complex patterns and best practices | Experienced users |
| `expert` | Cutting-edge and nuanced | Deep expertise |

---

## Validation

### Validate a Skill

```python
# Validate skill format
adn_skills("validate", identifier="autohotkey-v2-expert")

# Returns:
# ✅ Validation Passed
# OR
# ❌ Validation Failed + Repair Suggestions
```

### Validation Checks

1. **Frontmatter presence** - Must start with `---`
2. **YAML syntax** - Valid YAML format
3. **Required fields** - `name` and `description` present
4. **Name format** - Hyphen-case validation
5. **Description quality** - Length and content checks
6. **Metadata types** - Dictionary validation

---

## Migration and Conversion

### Convert Note → Skill

```python
# Convert existing note to skill
adn_skills("from_zettel",
    identifier="Python Best Practices",
    description="Guide for Python best practices...",
    category="developer")

# Adds Claude Skills frontmatter to existing note
```

### Convert Skill → Note

```python
# Convert skill back to regular note
adn_skills("to_zettel",
    identifier="python-expert")

# Removes Claude Skills frontmatter, keeps content
```

---

## Best Practices

### 1. Write Detailed Descriptions

❌ Bad:
```yaml
description: Python help
```

✅ Good:
```yaml
description: Expert Python guidance for advanced patterns, best practices, and architectural decisions. Use when writing Python code, debugging issues, or discussing Python-specific design patterns.
```

### 2. Use Consistent Naming

- Always lowercase
- Hyphens for word separation
- Descriptive but concise
- No abbreviations unless well-known

### 3. Include Category and Difficulty

```yaml
metadata:
  category: developer
  difficulty: advanced
```

Helps with:
- Organization
- Filtering
- User expectations

### 4. Add Timestamps

```yaml
metadata:
  created: 2025-10-27
  modified: 2025-10-27
  version: 1.0.0
```

Track skill evolution over time.

### 5. Version Your Skills

```yaml
metadata:
  version: 1.2.0
```

Use semantic versioning:
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

---

## Troubleshooting

### Common Errors

**Error:** "No YAML frontmatter found"
- **Fix:** Add `---` at the very top of the file

**Error:** "Missing required field: name"
- **Fix:** Add `name: skill-name` in frontmatter

**Error:** "Name must be hyphen-case"
- **Fix:** Convert to lowercase with hyphens: `Python Expert` → `python-expert`

**Error:** "Description too short"
- **Fix:** Expand to 20+ characters with context

### Getting Help

```python
# Validate with repair suggestions
adn_skills("validate", identifier="my-skill")

# Returns actionable fixes for all errors
```

---

## References

- [Anthropic Claude Skills Spec](https://github.com/anthropics/skills)
- [Advanced Memory Skills Documentation](../architecture/CLAUDE_SKILLS_ACTUAL_FORMAT.md)
- [Skill Creation Guide](./SKILL_CREATION_GUIDE.md)

---

**Last Updated:** 2025-10-27  
**Maintainer:** Sandra Schipal  
**Version:** 1.0.0

