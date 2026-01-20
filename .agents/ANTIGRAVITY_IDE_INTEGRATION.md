# Antigravity IDE Skills Integration Guide

## Overview

Antigravity IDE supports Claude Skills integration through the `.agents/skills/` directory structure in your repository root. This guide explains how to set up and use Advanced Memory's skills system with Antigravity IDE.

## Directory Structure

```
repo-root/
├── .agents/
│   ├── README.md                    # Main integration guide
│   ├── sync-skills.ps1             # Sync script
│   └── skills/                     # Skills directory
│       ├── README.md               # Skills documentation
│       ├── config.json             # Skills configuration
│       └── [skill-directories]/    # Individual skills
│           ├── skill-name/
│           │   ├── SKILL.md        # Main skill file
│           │   └── modules/        # Optional detailed content
```

## Setup Instructions

### 1. Create Directory Structure
```powershell
# Create the .agents/skills directory
New-Item -ItemType Directory -Path ".agents/skills" -Force
```

### 2. Configure Skills
The `config.json` file controls:
- Which skill categories to enable
- Validation rules
- Performance settings
- Sync preferences

### 3. Sync Skills from Advanced Memory
```powershell
# Run the sync script
.\.agents\sync-skills.ps1

# Or sync with validation
.\.agents\sync-skills.ps1 -Validate -Backup
```

## Skills Format Requirements

### SKILL.md Structure
```yaml
---
name: skill-name-in-hyphen-case
description: Brief description of skill purpose
license: MIT
category: technical|creative|scientific|etc.
difficulty: beginner|intermediate|advanced|expert
---

# Skill Title

## Overview
What this skill does and when to use it.

## Usage
How to activate and use the skill.

## Examples
Code examples and use cases.

## Best Practices
Tips for effective usage.
```

### Directory Structure per Skill
```
skill-name/
├── SKILL.md              # Required: Main skill file
├── modules/              # Optional: Detailed content
│   ├── core-guidance.md
│   ├── examples.md
│   └── research.md
└── assets/               # Optional: Supporting files
    ├── diagrams/
    └── examples/
```

## Advanced Memory Integration

### Exporting Skills
```bash
# Export all skills to Antigravity format
adn_export operation="skills" export_path=".agents/skills"

# Export specific categories
adn_export operation="skills" export_path=".agents/skills" categories="technical,creative"

# Sync mode (continuous updates)
adn_export operation="skills" export_path=".agents/skills" sync=true
```

### Creating Custom Skills
```python
# Scaffold new skill in Advanced Memory
adn_skills_creator("scaffold", skill_name="my-custom-skill", category="technical")

# Validate the skill
adn_skills_creator("validate", skill_path="skills/my-custom-skill")

# Package for distribution
adn_skills_creator("package", skill_path="skills/my-custom-skill")
```

### Syncing Workflow
1. Create/edit skills in Advanced Memory using MCP tools
2. Export skills to `.agents/skills/` directory
3. Antigravity IDE automatically detects changes
4. Skills become available in IDE context

## Configuration Options

### config.json Settings

```json
{
  "categories": {
    "technical": { "enabled": true, "priority": "high" },
    "creative": { "enabled": true, "priority": "medium" },
    "scientific": { "enabled": false, "priority": "low" }
  },
  "validation_rules": {
    "require_name": true,
    "require_description": true,
    "check_yaml_syntax": true
  },
  "performance": {
    "max_loaded_skills": 50,
    "lazy_loading": true
  }
}
```

## Available Skill Categories

### Technical (700+ skills)
- Programming languages (Python, JavaScript, Rust, etc.)
- Development tools (Git, Docker, databases)
- Architecture patterns and best practices
- Debugging and performance optimization

### Creative
- Content creation and strategy
- Graphic design and visual communication
- Video editing and production
- Writing and storytelling

### Scientific
- Physics, chemistry, biology fundamentals
- Research methodologies
- Data analysis and visualization
- Academic writing

### Linguistic
- Language learning and teaching
- Translation techniques
- Business communication
- Cultural fluency

## Troubleshooting

### Skills Not Loading
**Issue**: Antigravity IDE doesn't recognize skills
**Solutions**:
- Check SKILL.md YAML frontmatter syntax
- Validate with `adn_skills_creator("validate")`
- Ensure directory permissions are correct
- Restart Antigravity IDE

### YAML Syntax Errors
**Issue**: "while parsing a block mapping" errors
**Solutions**:
- Use proper YAML indentation (2 spaces)
- Ensure frontmatter is between `---` markers
- Validate YAML syntax online
- Check for special characters in description

### Performance Issues
**Issue**: IDE slow with many skills
**Solutions**:
- Reduce `max_loaded_skills` in config.json
- Enable lazy loading
- Archive unused skills
- Use categories to limit loaded skills

### Sync Failures
**Issue**: Skills not syncing from Advanced Memory
**Solutions**:
- Check Advanced Memory MCP server is running
- Verify export paths are correct
- Review sync logs for errors
- Try manual export first

## Best Practices

### Skill Organization
- Use consistent naming (hyphen-case)
- Choose appropriate categories
- Include comprehensive descriptions
- Document usage examples

### Performance Optimization
- Limit active skills per session
- Use on-demand loading for large skills
- Regularly archive unused skills
- Monitor memory usage

### Version Control
- Commit skill changes with meaningful messages
- Tag skill versions for releases
- Document breaking changes
- Maintain changelog in skill README

### Collaboration
- Share skill libraries across team
- Use consistent formatting standards
- Review skills before team-wide deployment
- Document skill dependencies

## Advanced Features

### Custom Categories
Add custom categories in `config.json`:
```json
"custom_category": {
  "enabled": true,
  "description": "Custom skill category",
  "priority": "medium"
}
```

### Automated Sync
Set up CI/CD to automatically sync skills:
```yaml
# .github/workflows/sync-skills.yml
name: Sync Skills
on:
  push:
    paths:
      - 'skills/**'
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync Skills
        run: ./sync-skills.ps1 -Validate
```

### Skill Dependencies
Document skill relationships in SKILL.md:
```markdown
## Dependencies
- Requires: python-debugging-expert
- Related: api-design-architect
- Conflicts: None
```

## Support

### Documentation
- [Advanced Memory Skills Guide](../docs/Skills/)
- [Claude Skills Specification](https://github.com/anthropics/skills)
- [Antigravity IDE Documentation](https://antigravity-ide.com/docs)

### Community
- Advanced Memory Discord
- Claude Skills GitHub Discussions
- Antigravity IDE Forums

### Issue Reporting
Report integration issues to:
- Advanced Memory: GitHub Issues
- Antigravity IDE: Support Ticket
- Claude Skills: Anthropic Forums

---

**Last Updated**: January 15, 2026
**Version**: 1.0
**Compatible With**: Antigravity IDE v2.0+, Advanced Memory v0.13+
