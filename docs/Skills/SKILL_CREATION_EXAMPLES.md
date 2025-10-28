# Skill Creation Examples - Improvements Showcase

**Date:** 2025-10-27  
**Purpose:** Demonstrate improved skill creation workflow with auto-detection and validation

---

## Overview of Improvements

This document showcases the three main improvements to skill creation:

1. **Auto-detection in `adn_content`** - Write skills like notes, frontmatter added automatically
2. **Validation with repair suggestions** - `adn_skills("validate")` provides actionable fixes
3. **Shared helper utilities** - Consistent frontmatter generation across tools

---

## Example 1: Simple Skill Creation with adn_content

### Before (Manual Frontmatter)

❌ **Old way** - Had to write YAML manually:

```python
adn_content("write",
    identifier="autohotkey-v2-expert",
    content="""---
name: autohotkey-v2-expert
description: Expert guidance for AutoHotkey v2...
license: CC-BY-4.0
metadata:
  category: developer
  difficulty: advanced
---

# AutoHotkey v2 Expert

Expert guidance for AutoHotkey v2 scripting...
""",
    folder="skills/developer")
```

**Problems:**
- Manual YAML construction
- Easy to make syntax errors
- Repetitive metadata setup
- Forgot required fields? No help!

---

### After (Auto-Detection)

✅ **New way** - Just write content:

```python
adn_content("write",
    identifier="AutoHotkey v2 Expert",
    content="# AutoHotkey v2 Expert\n\nExpert guidance for AutoHotkey v2 scripting...",
    folder="skills/developer")
```

**What happens automatically:**
1. Detects `skills/` folder path
2. Generates YAML frontmatter:
   - `name: autohotkey-v2-expert` (from title)
   - `description: Expert guidance for AutoHotkey v2 Expert...`
   - `metadata.category: developer` (from folder path)
3. Sets `entity_type: skill`
4. Validates frontmatter format

**Result:**
```yaml
---
name: autohotkey-v2-expert
description: Expert guidance for AutoHotkey v2 Expert. Use when working with autohotkey v2 expert or related topics.
type: skill
license: CC-BY-4.0
metadata:
  category: developer
---

# AutoHotkey v2 Expert

Expert guidance for AutoHotkey v2 scripting...
```

---

## Example 2: Validation with Repair Suggestions

### Scenario: Broken Skill (No Frontmatter)

Someone created a skill manually without frontmatter:

```markdown
# Vienna Cooking Skill

## Metadata
- **name**: vienna-cooking
- **description**: Traditional Viennese cuisine...
```

**This is NOT valid YAML frontmatter!**

---

### Before (Unhelpful Error)

❌ **Old validation:**

```python
adn_skills("validate", identifier="vienna-cooking")

# Returns:
# ❌ Validation Failed
# No YAML frontmatter found
```

**No help fixing it!**

---

### After (Repair Suggestions)

✅ **New validation with suggestions:**

```python
adn_skills("validate", identifier="vienna-cooking")
```

**Returns:**

```markdown
# Validation Failed

**Skill:** vienna-cooking

## Errors

❌ No YAML frontmatter found. Skills must start with ---

# Repair Suggestions

## Add YAML Frontmatter

Your skill is missing YAML frontmatter. Add this at the top of the file:

```yaml
---
name: your-skill-name  # hyphen-case, lowercase
description: When Claude should use this skill
license: CC-BY-4.0
metadata:
  category: developer  # or researcher, writer, etc.
  difficulty: intermediate  # beginner, intermediate, advanced, expert
---
```

**Then add your content below the frontmatter.**

**After fixing, run:** `adn_skills("validate", identifier="vienna-cooking")`
```

**Actionable and helpful!**

---

## Example 3: Invalid Name Format

### Scenario: Name with Spaces

```yaml
---
name: Python Expert
description: Expert Python guidance
---
```

---

### Validation Output

```python
adn_skills("validate", identifier="python-skill")
```

**Returns:**

```markdown
# Validation Failed

**Skill:** python-skill

## Errors (1)

❌ Name must be hyphen-case (lowercase letters, digits, hyphens only). Got: Python Expert

# Repair Suggestions

## Fix Skill Name

Current name: `Python Expert`

Problems:
- Name must be hyphen-case (lowercase letters, digits, hyphens only). Got: Python Expert

**Suggested fix:**
```yaml
name: python-expert
```

## Complete Example

Here's a complete, valid frontmatter example:

```yaml
---
name: autohotkey-v2-expert
description: Expert guidance for AutoHotkey v2 scripting, automation, and best practices. Use when working with AHK v2, creating hotkeys, or automating Windows tasks.
license: CC-BY-4.0
metadata:
  category: developer
  difficulty: advanced
  created: 2025-10-27
---
```

**After fixing, run:** `adn_skills("validate", identifier="python-skill")`
```

---

## Example 4: Short Description Warning

### Scenario: Description Too Short

```yaml
---
name: python-expert
description: Python help
---
```

**Validation:**

```python
adn_skills("validate", identifier="python-expert")
```

**Returns:**

```markdown
# Validation Passed ✅

**Skill:** python-expert
**Name:** python-expert
**Description:** Python help

## Checks

✅ YAML frontmatter present
✅ Required field 'name' present and valid
✅ Required field 'description' present and valid
✅ Naming convention correct (hyphen-case)
✅ No invalid characters

## Warnings (1)

⚠️ Description is quite short (< 20 chars). Consider expanding for better discoverability.

**Status:** Ready for export to Claude! 🚀

**Next steps:**
- Export: `adn_skills("export", export_path="./claude-skills/")`
- Package: `adn_skills("package", identifier="python-expert")`
```

---

## Example 5: Using adn_skills("create") for Template

### Explicit Skill Creation

```python
adn_skills("create",
    skill_name="autohotkey-v2-expert",
    description="Expert guidance for AutoHotkey v2 scripting, automation, and best practices. Use when working with AHK v2, creating hotkeys, or automating Windows tasks.",
    category="developer",
    difficulty="advanced")
```

**Returns:**

```markdown
# Created note
file_path: skills/developer/autohotkey-v2-expert.md
permalink: autohotkey-v2-expert
checksum: a1b2c3d4

## Next Steps

1. Edit the skill to complete TODO sections
2. Add scripts/ folder with helper scripts (optional)
3. Add references/ folder with documentation (optional)
4. Add assets/ folder with templates/files (optional)
5. Validate: adn_skills("validate", identifier="autohotkey-v2-expert")
6. Export: adn_skills("export", export_path="./claude-skills/")

✅ Skill created following skill-creator pattern!
```

**Created File:**

```yaml
---
name: autohotkey-v2-expert
description: Expert guidance for AutoHotkey v2 scripting, automation, and best practices. Use when working with AHK v2, creating hotkeys, or automating Windows tasks.
type: skill
license: CC-BY-4.0
metadata:
  category: developer
  difficulty: advanced
---

# Autohotkey V2 Expert

## Overview

[TODO: Add 1-2 sentences explaining what this skill enables]

## When to use this skill

- Use case 1
- Use case 2
- Use case 3

## How to use this skill

1. Step 1
2. Step 2
3. Step 3

## Examples

Example usage 1:
```
[Example code or workflow]
```

Example usage 2:
```
[Example code or workflow]
```

## Guidelines

- Guideline 1
- Guideline 2
- Guideline 3

## Resources

This skill can include bundled resources:

### scripts/
Executable code that Claude can run directly.

### references/
Documentation loaded as needed.

### assets/
Files used in output (templates, boilerplate, etc.).

---

**Next steps:** Customize this skill by filling in the TODO sections and adding relevant scripts, references, or assets.
```

---

## Example 6: Complete Workflow

### Step 1: Create Skill with adn_content

```python
# Quick skill creation - frontmatter added automatically
adn_content("write",
    identifier="Python Testing Best Practices",
    content="""# Python Testing Best Practices

## Core Principles

1. Write tests first (TDD)
2. Test behavior, not implementation
3. Keep tests isolated and independent

## Recommended Tools

- pytest for unit tests
- pytest-cov for coverage
- hypothesis for property-based testing

## Example Test Structure

```python
def test_user_creation():
    user = User(name="Alice", age=30)
    assert user.name == "Alice"
    assert user.age == 30
```

## Common Patterns

### Fixtures
Use pytest fixtures for setup/teardown...

### Mocking
Use unittest.mock for external dependencies...
""",
    folder="skills/developer")
```

---

### Step 2: Validate

```python
adn_skills("validate", identifier="python-testing-best-practices")
```

**Returns:**

```markdown
# Validation Passed ✅

**Skill:** python-testing-best-practices
**Name:** python-testing-best-practices
**Description:** Expert guidance for Python Testing Best Practices. Use when working with python testing best practices or related topics.

## Checks

✅ YAML frontmatter present
✅ Required field 'name' present and valid
✅ Required field 'description' present and valid
✅ Naming convention correct (hyphen-case)
✅ No invalid characters

**Status:** Ready for export to Claude! 🚀

**Next steps:**
- Export: `adn_skills("export", export_path="./claude-skills/")`
- Package: `adn_skills("package", identifier="python-testing-best-practices")`
```

---

### Step 3: Read and Verify

```python
adn_content("read", identifier="python-testing-best-practices")
```

**Shows complete skill with auto-generated frontmatter:**

```yaml
---
name: python-testing-best-practices
description: Expert guidance for Python Testing Best Practices. Use when working with python testing best practices or related topics.
type: skill
license: CC-BY-4.0
metadata:
  category: developer
---

# Python Testing Best Practices

[Content as written above...]
```

---

### Step 4: Improve Description (Optional)

The auto-generated description is functional but generic. Let's improve it:

```python
# Edit to add better description
adn_content("edit",
    identifier="python-testing-best-practices",
    edit_operation="find_replace",
    find_text="description: Expert guidance for Python Testing Best Practices. Use when working with python testing best practices or related topics.",
    content="description: Comprehensive guide for Python testing best practices including TDD, pytest patterns, mocking strategies, and coverage optimization. Use when writing Python tests, setting up test infrastructure, or improving test quality.")
```

---

### Step 5: Validate Again

```python
adn_skills("validate", identifier="python-testing-best-practices")
```

**Now passes with improved description!**

---

## Example 7: Repair Broken Skill

### Scenario: Multiple Issues

```yaml
---
name: Python-Expert
description: Help with <Python>
metadata: not-a-dict
---
```

**Problems:**
1. Name has uppercase (should be hyphen-case)
2. Description has angle brackets (not allowed)
3. Description is short
4. Metadata is not a dictionary

---

### Validation with Repair

```python
adn_skills("validate", identifier="broken-skill")
```

**Returns comprehensive repair suggestions:**

```markdown
# Validation Failed

**Skill:** broken-skill

## Errors (3)

❌ Name 'Python-Expert' must be hyphen-case (lowercase letters, digits, hyphens only)
❌ Description cannot contain angle brackets (< or >)

## Warnings (1)

⚠️ metadata should be a dictionary

# Repair Suggestions

## Fix Skill Name

Current name: `Python-Expert`

Problems:
- Name 'Python-Expert' must be hyphen-case (lowercase letters, digits, hyphens only)

**Suggested fix:**
```yaml
name: python-expert
```

## Improve Description

Current description (16 chars): "Help with <Python>"

**Why longer is better:**
- Claude uses description to decide when to load the skill
- More keywords = better discoverability
- Include specific use cases

**Example good description:**
```yaml
description: Expert Python guidance for advanced patterns, best practices, and architectural decisions. Use when writing Python code, debugging issues, or discussing Python-specific design patterns.
```

## Complete Example

Here's a complete, valid frontmatter example:

```yaml
---
name: autohotkey-v2-expert
description: Expert guidance for AutoHotkey v2 scripting, automation, and best practices. Use when working with AHK v2, creating hotkeys, or automating Windows tasks.
license: CC-BY-4.0
metadata:
  category: developer
  difficulty: advanced
  created: 2025-10-27
---
```

**After fixing, run:** `adn_skills("validate", identifier="broken-skill")`
```

---

## Summary of Improvements

### 1. Auto-Detection (adn_content)

**Benefits:**
- ✅ No manual YAML construction
- ✅ Automatic name generation (title → skill-name)
- ✅ Category extraction from folder path
- ✅ Consistent frontmatter format
- ✅ Less error-prone

**Usage:**
```python
adn_content("write",
    identifier="Skill Title",
    content="# Content...",
    folder="skills/category")  # Auto-detects and adds frontmatter
```

---

### 2. Validation with Repair (adn_skills)

**Benefits:**
- ✅ Actionable error messages
- ✅ Suggested fixes for each error
- ✅ Complete examples shown
- ✅ Warns about quality issues
- ✅ Links to next steps

**Usage:**
```python
adn_skills("validate", identifier="skill-name")
# Returns detailed report with repair suggestions
```

---

### 3. Shared Helpers (skill_helpers.py)

**Benefits:**
- ✅ Consistent behavior across tools
- ✅ Single source of truth for validation
- ✅ Reusable utility functions
- ✅ Maintainable codebase

**Functions:**
- `generate_skill_frontmatter()` - Create YAML frontmatter
- `validate_skill_name()` - Check name format
- `parse_skill_frontmatter()` - Parse YAML from content
- `validate_skill_frontmatter()` - Validate fields
- `generate_repair_suggestions()` - Create actionable fixes
- `detect_skill_path()` - Check if path is skills/
- `title_to_skill_name()` - Convert title to hyphen-case

---

## Migration Guide

### If You Have Existing Skills

**Check all skills:**
```python
adn_skills("list")
# Shows all skills

# Validate each one
adn_skills("validate", identifier="skill-name")
```

**Fix broken skills:**
Follow repair suggestions from validation output.

**Update descriptions:**
Make them more detailed for better discoverability.

---

## Best Practices

1. **Use adn_content for quick skill creation**
   - Let auto-detection handle frontmatter
   - Write content naturally

2. **Use adn_skills("create") for templates**
   - Get structured template
   - Includes resource folders

3. **Always validate after creation**
   - Catch issues early
   - Improve description quality

4. **Improve auto-generated descriptions**
   - Auto-generation is a starting point
   - Add specific use cases and keywords

5. **Use category folders**
   - `skills/developer/` → category: developer
   - `skills/researcher/` → category: researcher
   - Automatic categorization!

---

**Last Updated:** 2025-10-27  
**Author:** Sandra Schipal  
**Version:** 1.0.0

