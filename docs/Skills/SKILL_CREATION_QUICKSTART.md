# Skill Creation Quick Start

**TL;DR:** Create skills in 3 easy ways. Auto-detection handles frontmatter for you!

---

## Method 1: Auto-Detection (Recommended) ⭐

**Just write content to `skills/` folder:**

```python
adn_content("write",
    identifier="Python Expert",
    content="# Python Expert\n\nAdvanced Python guidance...",
    folder="skills/developer")
```

**Auto-generates:**
- ✅ YAML frontmatter
- ✅ Skill name: `python-expert`
- ✅ Category from path: `developer`
- ✅ Valid format

**That's it!** Frontmatter added automatically.

---

## Method 2: With Template

**Use `adn_skills` for structured template:**

```python
adn_skills("create",
    skill_name="python-expert",
    description="Expert Python guidance for advanced patterns...",
    category="developer",
    difficulty="advanced")
```

**Creates:**
- ✅ Complete YAML frontmatter
- ✅ Template structure (Overview, Usage, Examples)
- ✅ Resource folders (scripts/, references/, assets/)

---

## Method 3: Manual with Validation

**Write YAML yourself, validate for errors:**

```python
# Create skill manually
adn_content("write",
    identifier="my-skill",
    content="""---
name: my-skill
description: My skill description...
---

# My Skill
...""",
    folder="skills/general")

# Validate
adn_skills("validate", identifier="my-skill")
# Returns: ✅ Pass or ❌ Fail + repair suggestions
```

---

## Validation & Fixing

**Always validate after creation:**

```python
adn_skills("validate", identifier="skill-name")
```

**Returns:**
- ✅ **Pass** → Ready for Claude!
- ❌ **Fail** → Shows errors + repair suggestions

**Example repair output:**

```markdown
# Validation Failed

## Errors
❌ Name must be hyphen-case

# Repair Suggestions

**Suggested fix:**
```yaml
name: correct-skill-name
```

**Complete Example:**
[Shows full valid example]
```

---

## Required Fields

Every skill needs:

```yaml
---
name: skill-name-in-hyphen-case
description: When Claude should use this skill (20+ chars recommended)
---
```

**Optional but recommended:**

```yaml
metadata:
  category: developer
  difficulty: advanced
```

---

## Folder Structure

Organize skills by category:

```
skills/
├── developer/
│   ├── python-expert.md
│   └── git-workflows.md
├── researcher/
│   └── research-methods.md
└── writer/
    └── storytelling.md
```

**Auto-detection extracts category from path!**

---

## Common Patterns

### Pattern 1: Quick Capture

```python
adn_content("write",
    identifier="Quick Idea",
    content="# Quick Idea\n\nContent here...",
    folder="skills/general")
```

### Pattern 2: With Metadata

```python
adn_skills("create",
    skill_name="detailed-skill",
    description="Detailed description here...",
    category="developer",
    difficulty="expert",
    metadata={"version": "1.0.0", "author": "Sandra"})
```

### Pattern 3: Convert Note → Skill

```python
# Have an existing note? Convert it!
adn_skills("from_zettel",
    identifier="Existing Note",
    description="When to use this skill...",
    category="developer")
```

---

## Validation Rules

### Name

- ✅ `python-expert` (lowercase, hyphens)
- ❌ `Python Expert` (spaces)
- ❌ `python_expert` (underscores)
- ❌ `Python-Expert` (uppercase)

### Description

- ✅ 20+ characters recommended
- ✅ Include keywords and use cases
- ❌ No `<` or `>` characters

---

## Complete Example

```python
# Create skill
adn_content("write",
    identifier="AutoHotkey v2 Expert",
    content="""# AutoHotkey v2 Expert

## Core Competencies

- AHK v2 syntax and patterns
- Hotkey and hotstring creation
- Windows automation
- GUI development

## When to Use

Use this skill when:
- Writing AutoHotkey v2 scripts
- Automating Windows tasks
- Creating keyboard shortcuts
- Debugging AHK code

## Example: Simple Hotkey

```ahk
#n::  ; Win+N
{
    Run "notepad.exe"
}
```
""",
    folder="skills/developer")

# Validate
adn_skills("validate", identifier="autohotkey-v2-expert")
# Returns: ✅ Validation Passed

# Read back
adn_content("read", identifier="autohotkey-v2-expert")
```

**Auto-generated frontmatter:**

```yaml
---
name: autohotkey-v2-expert
description: Expert guidance for AutoHotkey v2 Expert. Use when working with autohotkey v2 expert or related topics.
type: skill
license: CC-BY-4.0
metadata:
  category: developer
---
```

---

## Troubleshooting

### "No YAML frontmatter found"

**Solution:** Let auto-detection add it!

```python
# Write to skills/ folder
adn_content("write", ..., folder="skills/developer")
```

### "Name must be hyphen-case"

**Solution:** Use lowercase with hyphens:

```yaml
name: my-skill-name  # ✅
```

### "Description too short"

**Solution:** Add more detail (20+ chars):

```yaml
description: Expert guidance for [topic]. Use when working with [use cases] and [specific scenarios].
```

---

## Next Steps

1. **Create your first skill** using Method 1 (auto-detection)
2. **Validate it** with `adn_skills("validate")`
3. **Read documentation** in `SKILL_METADATA_REFERENCE.md`
4. **See more examples** in `SKILL_CREATION_EXAMPLES.md`

---

## Reference

- [Metadata Reference](./SKILL_METADATA_REFERENCE.md) - Complete field documentation
- [Examples](./SKILL_CREATION_EXAMPLES.md) - Detailed examples and patterns
- [Anthropic Spec](https://github.com/anthropics/skills) - Official Claude Skills format

---

**Last Updated:** 2025-10-27  
**Version:** 1.0.0

