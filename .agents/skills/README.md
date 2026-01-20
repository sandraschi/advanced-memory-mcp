# Antigravity IDE Skills Directory

This directory contains Claude Skills formatted for use with Antigravity IDE.

## Directory Structure

```
skills/
├── README.md              # This documentation
├── config.json           # Skills configuration
├── windsurf-ide-integration/
│   └── SKILL.md         # Example skill
└── [other-skills]/
    ├── SKILL.md
    └── modules/
```

## Skills Format

Each skill must be in its own directory with a `SKILL.md` file containing:

### Required YAML Frontmatter
```yaml
---
name: skill-name-in-hyphen-case
description: Brief description of what the skill does
license: MIT|Apache-2.0|Proprietary
---
```

### Optional Metadata
```yaml
category: technical|creative|scientific|linguistic|etc.
difficulty: beginner|intermediate|advanced|expert
version: 1.0.0
author: Your Name
tags: [tag1, tag2, tag3]
```

### Markdown Content
Follow the Anthropic Skills specification with clear sections for:
- Overview/Description
- Usage Instructions
- Examples
- Best Practices
- Troubleshooting

## Importing from Advanced Memory

### Export Command
```bash
# Export all skills to Antigravity format
adn_export(operation="skills", export_path=".agents/skills")
```

### Selective Export
```bash
# Export specific categories
adn_export(operation="skills", export_path=".agents/skills",
           categories=["technical", "creative"])
```

### Sync Mode
```bash
# Keep in sync with Advanced Memory changes
adn_export(operation="skills", export_path=".agents/skills", sync=true)
```

## Skill Categories

### Technical Skills
- `python-debugging-expert`
- `api-design-architect`
- `database-optimization-guru`
- `docker-kubernetes-pro`

### Creative Skills
- `content-strategy-planner`
- `graphic-design-fundamentals`
- `video-editing-advisor`
- `presentation-design-expert`

### Scientific Skills
- `physics-fundamentals-tutor`
- `biology-comprehensive-guide`
- `chemistry-lab-techniques`
- `neuroscience-fundamentals`

### Linguistic Skills
- `japanese-grammar-master`
- `business-japanese-specialist`
- `spanish-language-tutor`
- `translation-techniques-specialist`

## Validation

### Automatic Validation
Skills are automatically validated when:
- IDE loads the skills directory
- Skills are modified
- Configuration changes

### Manual Validation
```bash
# Validate all skills
adn_skills_creator("validate", skill_path=".agents/skills/*")

# Validate specific skill
adn_skills_creator("validate", skill_path=".agents/skills/python-debugging-expert")
```

## Performance Considerations

### Loading Strategy
- Skills load on-demand to minimize memory usage
- Large skill libraries may impact IDE startup time
- Consider archiving unused skills

### Memory Management
- Each loaded skill consumes memory
- Monitor IDE performance with many active skills
- Use skill sections selectively

## Troubleshooting

### Common Issues

#### YAML Syntax Errors
```
Error: while parsing a block mapping
```
**Solution**: Check YAML frontmatter syntax, ensure proper indentation

#### Missing SKILL.md
```
Error: SKILL.md not found in skill directory
```
**Solution**: Ensure each skill directory contains a SKILL.md file

#### Invalid Category
```
Warning: Unknown category 'custom'
```
**Solution**: Use predefined categories or add to config.json

#### License Issues
```
Warning: License field missing
```
**Solution**: Add license field to YAML frontmatter

### Debug Mode
Enable debug logging in Antigravity IDE to see detailed skill loading information.
