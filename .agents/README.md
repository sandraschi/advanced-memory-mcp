# Antigravity IDE Skills Integration

## Directory Structure

```
.agents/
├── README.md              # This file
├── skills/                # Claude Skills for Antigravity IDE
│   ├── README.md         # Skills directory documentation
│   ├── config.json       # Skills configuration
│   └── [skill-folders]/  # Individual skill directories
└── [other-config]/       # Additional IDE configuration
```

## Skills Organization

Antigravity IDE expects Claude Skills in the following format:

### Skill Directory Structure
```
skills/
├── skill-name/
│   ├── SKILL.md          # Main skill file (YAML frontmatter + Markdown)
│   ├── modules/          # Optional detailed content
│   │   ├── core-guidance.md
│   │   ├── examples.md
│   │   └── research.md
│   └── assets/           # Optional supporting files
│       ├── diagrams/
│       └── examples/
```

### SKILL.md Format
```yaml
---
name: skill-name-in-hyphen-case
description: What this skill does and when to use it
license: MIT
category: technical|creative|scientific|etc.
difficulty: beginner|intermediate|advanced|expert
---

# Skill Title

Skill content in Markdown format...

## Usage
How to use this skill...

## Examples
Code examples and use cases...
```

## Integration with Advanced Memory

### Importing Skills from Advanced Memory

```bash
# Export skills from Advanced Memory to Antigravity format
adn_export(operation="skills", export_path=".agents/skills")
```

### Syncing Skills

```bash
# Keep skills in sync between systems
adn_export(operation="skills", export_path=".agents/skills", sync=true)
```

### Creating Custom Skills

```python
# Use Advanced Memory skills creator
adn_skills_creator("scaffold", skill_name="my-custom-skill", category="technical")

# Then move to Antigravity directory
Move-Item "skills/my-custom-skill" ".agents/skills/"
```

## Configuration

### config.json
```json
{
  "version": "1.0",
  "skills_path": ".agents/skills",
  "auto_sync": true,
  "sync_interval": 3600,
  "categories": {
    "enabled": ["technical", "creative", "scientific"],
    "default_category": "technical"
  }
}
```

## Best Practices

1. **Skill Naming**: Use hyphen-case (e.g., `python-debugging-expert`)
2. **Categories**: Choose from predefined categories for organization
3. **Validation**: Always validate skills before use
4. **Versioning**: Include version info in skill metadata
5. **Documentation**: Keep README.md files current

## Workflow

1. Create/Edit skills in Advanced Memory using MCP tools
2. Export to `.agents/skills/` directory
3. Antigravity IDE automatically detects and loads skills
4. Skills become available in IDE context menu

## Troubleshooting

### Skills Not Loading
- Check SKILL.md YAML frontmatter syntax
- Validate skill structure with `adn_skills_creator("validate")`
- Ensure skills directory is readable

### Sync Issues
- Check export path configuration
- Verify Advanced Memory project is active
- Review sync logs for errors

### Performance Issues
- Limit number of active skills per session
- Use skill sections on-demand rather than loading all at once
- Monitor memory usage with large skill libraries
