# Claude Skills IDE Integration Guide

## Overview

This guide explains how to properly integrate Claude Skills across different IDEs (Cursor, Windsurf, Antigravity) using Advanced Memory MCP.

## The Problem

When skills are loaded via the old `adn_skills_creator` tool, IDEs receive string data instead of structured data, causing warnings like:
```
"adn complaining getting string in tool return instead of structured data"
```

## The Solution

Use the new `adn_skills_reader` tool which returns properly structured data for IDE integration.

## IDE Configuration

### Windsurf Setup

1. **Configure Advanced Memory MCP** in Windsurf's MCP settings
2. **Use structured format** when loading skills:

```javascript
// Instead of copying files manually, use the MCP tool:
await adn_skills_reader("skills/technical/python-debugging", "structured")
```

3. **Expected structured response**:
```json
{
  "skill": {
    "name": "python-debugging",
    "description": "Expert Python debugging techniques",
    "metadata": {
      "name": "python-debugging",
      "description": "Expert Python debugging techniques",
      "category": "technical"
    },
    "content": "# Python Debugging Techniques\n\n...",
    "structure": {
      "has_frontmatter": true,
      "body_length": 1234,
      "sections": 5
    }
  },
  "format": "structured",
  "path": "/path/to/skill",
  "compatibility": {
    "windsurf": true,
    "cursor": true,
    "antigravity": true
  }
}
```

### Cursor Setup

Cursor natively supports skills in the `.claude/skills/` directory. For cross-IDE compatibility:

1. **Copy skills** from Advanced Memory to `.claude/skills/`
2. **Use MCP integration** for dynamic skill loading:

```javascript
// Load skill via MCP for structured access
const skill = await adn_skills_reader("skills/creative/writing", "structured");
```

### Antigravity Setup

Similar to Windsurf, configure the Advanced Memory MCP server and use structured loading.

## Direct Folder Access (Not Recommended)

**❌ Manual copying doesn't work reliably** because:
- IDEs have different skill discovery mechanisms
- No automatic updates when skills change
- No validation or structured loading
- Manual sync required

**✅ MCP-based loading is preferred** because:
- Structured data format
- Automatic validation
- Cross-IDE compatibility
- Centralized skill management

## Troubleshooting

### "String instead of structured data" error

**Solution**: Use `adn_skills_reader` instead of `adn_skills_creator` for loading skills.

```javascript
// ❌ Wrong - returns string data
await adn_skills_creator("inspect", skill_path="skills/example")

// ✅ Correct - returns structured data
await adn_skills_reader("skills/example", "structured")
```

### Skill not loading in IDE

1. **Check MCP server** is running and configured
2. **Verify skill path** exists and contains `SKILL.md`
3. **Use structured format** for IDE integration
4. **Check IDE logs** for specific error messages

### Skills folder not recognized

Each IDE has its own skill directory:
- **Cursor**: `.claude/skills/`
- **Windsurf**: `.codeium/windsurf/skills/`
- **Antigravity**: Check documentation

For reliable cross-IDE skills, use MCP-based loading instead of direct folder access.

## Advanced Usage

### Batch Skill Loading

```javascript
// Load multiple skills at once
const skills = [
  "skills/technical/python-debugging",
  "skills/creative/writing",
  "skills/mathematics/calculus"
];

for (const skillPath of skills) {
  const skill = await adn_skills_reader(skillPath, "structured");
  // Process structured skill data
}
```

### Skill Validation

```javascript
// Validate skill format before loading
const validation = await adn_skills_creator("validate", skill_path="skills/example");
if (validation.success) {
  const skill = await adn_skills_reader("skills/example", "structured");
}
```

## Migration from Manual Copying

If you were manually copying skills between IDEs:

1. **Stop manual copying** - it's unreliable
2. **Configure Advanced Memory MCP** in each IDE
3. **Use `adn_skills_reader`** for structured loading
4. **Remove copied skill files** to avoid confusion

This approach provides better reliability, automatic updates, and proper data formatting.
