# Claude Skills - Actual Format (October 16, 2025 Release)

**Release Date**: October 16, 2025
**Source**: https://github.com/anthropics/skills (official Anthropic repository)
**Status**: ✅ CONFIRMED - This is the real format!

---

## Official Specification

**From Anthropic's `agent_skills_spec.md`:**

> "A skill is a folder of instructions, scripts, and resources that agents can discover and load dynamically to perform better at specific tasks."

**Required**: Single `SKILL.md` file in folder

---

## The ACTUAL Format (Way Simpler Than Speculation!)

### Minimal Skill

```
my-skill/
  └── SKILL.md (required)
```

### Full Skill Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   └── Markdown body (required)
├── scripts/          (optional) - Executable code
├── references/       (optional) - Documentation to load as needed
└── assets/           (optional) - Files used in output (templates, fonts, etc.)
```

---

## SKILL.md Format

### Required YAML Frontmatter

**Only 2 fields required!**

```yaml
---
name: skill-name-in-hyphen-case
description: Clear description of what skill does and when Claude should use it
---
```

**That's it!** Much simpler than my 40-field speculation!

---

### Optional YAML Fields

```yaml
---
name: skill-name
description: What the skill does and when to use it
license: MIT  # or path to LICENSE.txt
allowed-tools:  # Pre-approved tools (Claude Code only)
  - tool_name_1
  - tool_name_2
metadata:  # Custom key-value pairs
  version: "1.0.0"
  author: "your-name"
  category: "programming"
---
```

---

### Markdown Body

**Free-form instructions** - no structure required, but typical patterns:

```markdown
# Skill Name

## When to use this skill
- Use case 1
- Use case 2

## How to use this skill

1. Step 1
2. Step 2
3. Step 3

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2

## Keywords
keyword1, keyword2, keyword3
```

---

## Real Example: Brand Guidelines

**File**: `brand-guidelines/SKILL.md`

```yaml
---
name: brand-guidelines
description: Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand colors or style guidelines, visual formatting, or company design standards apply.
license: Complete terms in LICENSE.txt
---

# Anthropic Brand Styling

## Overview

To access Anthropic's official brand identity and style resources, use this skill.

**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography

## Brand Guidelines

### Colors

**Main Colors:**
- Dark: `#141413` - Primary text and dark backgrounds
- Light: `#faf9f5` - Light backgrounds and text on dark
- Mid Gray: `#b0aea5` - Secondary elements

**Accent Colors:**
- Orange: `#d97757` - Primary accent
- Blue: `#6a9bcc` - Secondary accent
- Green: `#788c5d` - Tertiary accent

### Typography

- **Headings**: Poppins (with Arial fallback)
- **Body Text**: Lora (with Georgia fallback)
```

---

## Real Example: MCP Builder

**File**: `mcp-builder/SKILL.md`

```yaml
---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: Complete terms in LICENSE.txt
---

# MCP Server Development Guide

## Overview

To create high-quality MCP servers that enable LLMs to effectively interact with external services, use this skill.

## Process

### Phase 1: Deep Research and Planning

1. Understand agent-centric design principles
2. Study MCP protocol documentation
3. Study framework documentation
4. Exhaustively study API documentation
5. Create comprehensive implementation plan

### Phase 2: Implementation

1. Set up project structure
2. Implement core infrastructure first
3. Implement tools systematically
4. Follow language-specific best practices

[... continues with detailed process ...]

# Reference Files

## 📚 Documentation Library

Load these resources as needed during development:

- MCP Protocol: Fetch from https://modelcontextprotocol.io/llms-full.txt
- [📋 MCP Best Practices](./reference/mcp_best_practices.md)
- [🐍 Python Guide](./reference/python_mcp_server.md)
- [⚡ TypeScript Guide](./reference/node_mcp_server.md)
```

**Note**: This skill has `reference/` folder with 4 additional markdown files!

---

## Real Example: Internal Comms

**File**: `internal-comms/SKILL.md`

```yaml
---
name: internal-comms
description: A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenever asked to write some sort of internal communications (status reports, leadership updates, 3P updates, company newsletters, FAQs, incident reports, project updates, etc.).
license: Complete terms in LICENSE.txt
---

## When to use this skill
- 3P updates (Progress, Plans, Problems)
- Company newsletters
- FAQ responses
- Status reports
- Leadership updates

## How to use this skill

1. **Identify the communication type** from the request
2. **Load the appropriate guideline file** from `examples/` directory:
   - `examples/3p-updates.md` - For Progress/Plans/Problems
   - `examples/company-newsletter.md` - For newsletters
   - `examples/faq-answers.md` - For FAQs
   - `examples/general-comms.md` - For anything else
3. **Follow the specific instructions** in that file

## Keywords
3P updates, company newsletter, weekly update, faqs, common questions
```

**Structure**:
```
internal-comms/
├── SKILL.md
├── examples/
│   ├── 3p-updates.md
│   ├── company-newsletter.md
│   ├── faq-answers.md
│   └── general-comms.md
└── LICENSE.txt
```

---

## Bundled Resources Explained

### `scripts/` - Executable Code

**Purpose**: Code that gets executed, not loaded into context

**When to use**:
- Same code rewritten repeatedly
- Deterministic reliability needed
- Token efficiency (execute without reading)

**Example**: `scripts/rotate_pdf.py` for PDF rotation

**Benefits**:
- May be executed without loading into context
- Deterministic (not LLM-generated each time)
- Token efficient

---

### `references/` - Load-as-Needed Documentation

**Purpose**: Documentation Claude loads when needed

**When to use**:
- API documentation
- Database schemas
- Company policies
- Detailed workflow guides
- Domain knowledge

**Example**: `references/schema.md` for BigQuery table schemas

**Benefits**:
- Keeps SKILL.md lean
- Loaded only when needed
- Avoids context window bloat

**Best practice**: If >10k words, include grep search patterns in SKILL.md

---

### `assets/` - Output Resources

**Purpose**: Files used in output (NOT loaded into context)

**When to use**:
- Templates
- Images, icons, fonts
- Boilerplate code
- Sample documents to copy/modify

**Example**: `assets/frontend-template/` for webapp boilerplate

**Benefits**:
- Separates output resources from documentation
- Claude uses files without loading them
- Efficient for large binary files

---

## Progressive Disclosure

**Three-level loading system** (brilliant design!):

1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words recommended)
3. **Bundled resources** - As needed by Claude (unlimited for scripts that execute)

**Why this matters**:
- Efficient context window usage
- Claude loads only what's needed
- Skills can be large but don't bloat context

---

## How Skills Work

### In Claude.ai (Paid Plans)

1. User uploads skill folder (zip)
2. Claude detects when skill is relevant (from description + keywords)
3. Loads SKILL.md into context
4. Follows instructions
5. Loads bundled resources as needed

---

### In Claude Code

```bash
# Register marketplace
/plugin marketplace add anthropics/skills

# Use skill
"Use the mcp-builder skill to create a GitHub MCP server"
```

Claude loads skill automatically based on description match.

---

### Via API

```python
# Create skill
POST /skills

# List skills
GET /skills

# Use skill in conversation
{
  "model": "claude-3-5-sonnet-20241022",
  "skills": ["skill-id"],
  "messages": [...]
}
```

---

## Key Differences from My Speculation

| Aspect | My Speculation | Actual Reality |
|--------|---------------|----------------|
| **YAML Fields** | 40+ fields | 2 required, 3 optional |
| **Structure** | Complex nested | Simple folder + SKILL.md |
| **Versioning** | Built-in version field | Optional in metadata |
| **Dependencies** | Explicit dependency list | Implicit via references |
| **Activation** | Complex trigger system | Description + keywords |
| **Storage** | Zettelkasten integration | Folder-based (portable!) |

**Reality is simpler!** (And better for our purposes)

---

## Zettelkasten = Skills Parallel CONFIRMED

### The Structure Matches Perfectly

**Zettelkasten Note**:
```yaml
---
title: "Python Best Practices"
tags: ["python", "programming"]
---

# Python Best Practices

## Principles
1. Follow PEP 8
2. Use type hints
...
```

**Anthropic Skill**:
```yaml
---
name: python-best-practices
description: Guide for writing clean Python code following community standards
---

# Python Best Practices

## Principles
1. Follow PEP 8
2. Use type hints
...
```

**Difference**: Minimal - just field names!

---

### Our Templates Are Already 95% There

**Current Advanced Memory template**:
```markdown
# Python Fundamentals

> **Category:** developer/python

## Overview
Python is a high-level language...

## Key Concepts
[content]

## Observations
- [best-practice] Follow PEP 8

## Relations
- prerequisite_for [[Python Advanced]]
```

**Convert to skill** (add 2 lines of YAML):
```yaml
---
name: python-fundamentals
description: Introduction to Python programming covering syntax, data types, control flow, and best practices. Use when teaching or learning Python basics.
---

# Python Fundamentals

[... rest unchanged ...]
```

**DONE!** Template → Skill with 2 lines of YAML.

---

## Implications for Advanced Memory

### We're 95% There, Not 80%!

**What we have**:
- ✅ Markdown + YAML format (exactly matches!)
- ✅ 43 templates (= 43 potential skills)
- ✅ Folder structure (zettelkasten/templates/)
- ✅ Version control (Git)
- ✅ WikiLinks (= skill dependencies)
- ✅ Search/discovery
- ✅ MCP integration

**What we need to add**:
- Update YAML frontmatter (change `title` → `name`, add `description`)
- Optional: Add `scripts/`, `references/`, `assets/` folders
- MCP tool: `adn_skill` for skill management

**Estimated work**: 2-3 hours to convert all templates to skill format!

---

## Real Skills Available

From Anthropic's repository (public, Apache 2.0):

**Creative & Design**:
- algorithmic-art
- canvas-design
- slack-gif-creator

**Development**:
- artifacts-builder
- mcp-builder
- webapp-testing

**Enterprise**:
- brand-guidelines
- internal-comms
- theme-factory

**Meta**:
- skill-creator (guides creating new skills!)
- template-skill (starter template)

**Document Skills** (source-available, reference only):
- docx, pdf, pptx, xlsx skills

---

## How to Use These Skills

### 1. Clone the Repository (Already Done!)

```bash
git clone https://github.com/anthropics/skills.git
```

### 2. Browse Examples

Each skill folder is self-contained and can be:
- Read for inspiration
- Copied as starting point
- Modified for your needs
- Uploaded to Claude

### 3. Create Your Own

```bash
# Use their init script
python temp-anthropic-skills/skill-creator/scripts/init_skill.py my-skill --path ./my-skill

# Edit SKILL.md
# Package it
python temp-anthropic-skills/skill-creator/scripts/package_skill.py ./my-skill
```

---

## Converting Advanced Memory Templates to Skills

### The Process (Simple!)

**For each template in `zettelkasten/templates/`**:

1. **Add YAML frontmatter**:
```yaml
---
name: python-fundamentals
description: Introduction to Python programming covering syntax, data types, control flow, and best practices. Use when teaching or learning Python basics.
---
```

2. **Optionally add metadata**:
```yaml
---
name: python-fundamentals
description: [as above]
metadata:
  version: "1.0.0"
  category: "developer"
  difficulty: "beginner"
  author: "advanced-memory"
---
```

3. **Keep markdown body unchanged** (it's already good!)

4. **Done!** Template → Skill

---

### Automation Script

**We can automate this**:

```python
# scripts/convert_templates_to_skills.py

for template_file in zettelkasten/templates/**/*.md:
    # Parse existing frontmatter
    frontmatter = parse_yaml(template_file)

    # Convert to skill format
    skill_yaml = {
        "name": kebab_case(frontmatter["title"]),
        "description": generate_description(template_file),
        "metadata": {
            "version": "1.0.0",
            "category": frontmatter.get("category"),
            "original_template": True
        }
    }

    # Write back
    write_skill_format(template_file, skill_yaml)
```

**Result**: 43 templates → 43 skills in ~10 minutes

---

## Next Steps (Concrete!)

### Immediate (This Week)

1. ✅ Clone Anthropic skills repo (done!)
2. ✅ Read spec and examples (done!)
3. ⏳ Convert our templates to skill format (2-3 hours)
4. ⏳ Test skills with Claude.ai
5. ⏳ Document our skills in same style

### Short-Term (Next Sprint)

6. Implement `adn_skill` MCP tool:
   - List skills
   - Read skill (load into context)
   - Create skill from template
   - Package skill (zip)

7. Skill discovery/search:
   - Search by description keywords
   - Filter by category
   - Show skill dependencies

### Medium-Term (Next Release)

8. Skills marketplace integration:
   - Import Anthropic official skills
   - Export our skills for sharing
   - Community skill contributions

9. Advanced features:
   - Skill usage tracking
   - Skill effectiveness ratings
   - Automatic skill suggestions

---

## Portability Confirmed!

### Cross-AI Usage

**Skills are just folders** with markdown files:

**Claude** → Creates skill, uploads
**You (Human)** → Browse folder, read SKILL.md
**GPT-4** → Read SKILL.md via MCP, apply patterns
**Cursor** → Load skill into context, use for autocomplete
**Local LLM** → Read skill offline, follow instructions

**Format is portable!** Any AI that can read markdown can use skills.

---

## Comparison: Speculation vs Reality

### What I Got Right ✅

- ✅ YAML + Markdown format
- ✅ Folder-based structure
- ✅ Metadata in frontmatter
- ✅ Free-form markdown body
- ✅ Portable across AIs
- ✅ Version control friendly

### What I Got Wrong ❌

- ❌ Over-complicated YAML (40 fields vs 2 required)
- ❌ Assumed built-in versioning (it's optional metadata)
- ❌ Assumed explicit dependencies (implicit via references)
- ❌ Complex activation system (just description matching)

### What's Better Than Expected 🎉

- 🎉 **Simpler format** (easier to create)
- 🎉 **Bundled resources** (scripts, references, assets)
- 🎉 **Progressive disclosure** (3-level loading)
- 🎉 **Already in production** (Claude.ai paid plans)
- 🎉 **Open sourced examples** (Apache 2.0)

---

## Summary

**Official Format** (October 16, 2025):
- Folder with `SKILL.md` file
- YAML frontmatter: `name` + `description` (required only!)
- Markdown body: Free-form instructions
- Optional: `scripts/`, `references/`, `assets/` folders
- Works in Claude.ai, Claude Code, API

**Advanced Memory's Position**:
- We're 95% there (not 80%)
- Our templates need just 2 YAML fields added
- Can convert all 43 templates in 2-3 hours
- Can implement `adn_skill` tool in 1 day
- Can be universal skills hub immediately

**Action Plan**:
1. Convert templates to skill format (this weekend)
2. Test with Claude.ai
3. Implement `adn_skill` MCP tool
4. Become portable skills hub

**The parallel confirmed**: Zettelkasten = Skills (when content is actionable)

---

*Based on official Anthropic skills repository*
*Release: October 16, 2025*
*Repository: https://github.com/anthropics/skills*
