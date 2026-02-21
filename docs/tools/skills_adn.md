# adn_skills

Claude Skills management portmanteau for Advanced Memory.

RESPONSES:
- **Success**: `{"success": true, "operation": "...", "summary": "...", "result": {...}}`
- **Error**: `{"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}`

## Overview
This comprehensive tool consolidates skill management operations to provide a unified interface for creating, managing, and distributing Claude Skills (Anthropic Skills).

## Supported Operations

### CRUD & Management
- **create**: Initialize new skill with template (skill-creator pattern).
- **read**: Read skill in SKILL.md format.
- **update**: Update skill metadata or content.
- **delete**: Remove skill from knowledge base.
- **list**: List all skills with filtering.
- **validate**: Check skill format compliance (Anthropic spec).
- **export**: Export skills to Claude Skills format (folders/zips).
- **import**: Import Claude Skills from folders/zips.
- **package**: Create distributable .zip (package pattern).
- **from_zettel**: Convert zettelkasten note to Claude Skill.
- **to_zettel**: Convert Claude Skill back to regular note.

### Import & Distillation
- **import_from_github**: Import skill from GitHub repository.
- **distill_from_wikipedia**: Create skill from Wikipedia article.
- **distill_from_arxiv**: Create skill from arXiv research papers.
- **distill_from_textbook**: Create skill from textbook PDF.
- **distill_from_text**: Create skill from famous text/document.
- **distill_from_expert**: Create skill from SOTA thinker's work.

### Skill Activation (THE DOOR)
- **activate**: Load skill TOC into context (staged loading - saves tokens!).
- **deactivate**: Remove skill from active context.
- **active**: List currently active skills.
- **load_section**: Load specific section from active skill (on-demand).
- **load_resource**: Load specific resource file from active skill.

## Claude Skills Format
Skills are folders containing `SKILL.md` with YAML frontmatter:
- `name`: (required) skill-name-in-hyphen-case
- `description`: (required) When Claude should use this skill
- `license`: (optional) License name or file
- `allowed-tools`: (optional) Pre-approved tools list
- `metadata`: (optional) Custom key-value pairs

## Parameters
- `operation`: The skills operation to perform (Required).
- `identifier`: Skill name or note identifier (Required for read/update/delete/validate).
- `skill_name`: Name for new skill (hyphen-case) (Required for create).
- `description`: Description of when to use this skill (Required for create).
- `content`: Skill instructions/markdown body (Optional for update).
- `source_path`: Path to import from (Required for import).
- `export_path`: Path to export to (Optional).
- `category`: Skill category (Optional).
- `difficulty`: beginner/intermediate/advanced/expert (Optional).
- `scope`: Activation scope (message/session/persistent) (Default: "session").
- `section`: Section header to load (Required for load_section).
- `resource`: Resource path to load (Required for load_resource).

## Examples

### Create a new skill
```python
adn_skills("create", skill_name="python-expert", description="Expert Python guidance", category="developer")
```

### Activate a skill (Staged Loading)
```python
adn_skills("activate", identifier="python-expert")
```

### Load specific section
```python
adn_skills("load_section", identifier="python-expert", section="Decorators")
```

## Errors & Troubleshooting
- **Missing Required Parameter**: identifier parameter missing for read, update, delete, etc.
- **Invalid Skills Operation**: Specified operation is not supported.
- **Skill name must be hyphen-case**: Violates Anthropic naming conventions (lowercase, hyphens).
- **Angle brackets are not allowed**: Skill description contains `<` or `>` characters.
