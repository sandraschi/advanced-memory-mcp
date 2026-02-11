# Skill Parsing Architecture

## Overview

Advanced Memory MCP includes a comprehensive skill discovery and parsing system that scans multiple IDE directories for Claude Skills. This system allows users to access and manage skills created in different IDE environments (Cursor, Windsurf, Antigravity) as well as ADN-generated skills.

## Skill Directory Structure

### IDE Skill Locations

**CRITICAL: These paths are in user home directories, NOT in the repository:**

- **Cursor Skills**: `C:\Users\[username]\.cursor\skills-cursor`
- **Windsurf Skills**: `C:\Users\[username]\.codeium\windsurf\skills`
- **Antigravity Skills**: `C:\Users\[username]\.gemini\antigravity\skills`
- **ADN Skills**: `D:\Dev\repos\advanced-memory-mcp\skills`

### Skill Directory Layout

Each skill is stored in its own subdirectory containing:

```
skill-directory/
├── SKILL.md          # Main skill file with YAML frontmatter and content
├── modules/          # Optional submodules (core-guidance.md, etc.)
├── assets/           # Optional assets (examples, images)
├── references/       # Optional references
└── scripts/          # Optional scripts
```

## Skill File Format

### SKILL.md Structure

Skills use a YAML frontmatter format followed by markdown content:

```markdown
---
name: "Skill Title"
description: "Brief description of what this skill does"
tags: "tag1, tag2, tag3"
created: "2026-01-21T10:00:00.000Z"
modified: "2026-01-21T10:00:00.000Z"
---

# Skill Content

Detailed instructions and guidance for the skill...

## Usage Examples

## Best Practices
```

### Frontmatter Fields

- **name/title**: Skill title (name takes precedence)
- **description**: Brief description
- **tags**: Comma-separated list of tags
- **created**: ISO 8601 timestamp
- **modified**: ISO 8601 timestamp

## Parsing Process

### 1. Directory Discovery

The system resolves skill roots as absolute paths via `path.resolve`. User-based dirs (Cursor, WindSurf, Antigravity) require `USERPROFILE` or `HOME`; if missing, `getSkillDirectory` returns `null` for those folders.

```javascript
function getSkillDirectory(folderName) {
  const userHome = process.env.USERPROFILE || process.env.HOME || '';
  if (!userHome && ['cursor-skills','windsurf-skills','antigravity-skills'].includes(folderName))
    return null;
  let dir;
  switch (folderName) {
    case 'cursor-skills':   dir = path.join(userHome, '.cursor', 'skills-cursor'); break;
    case 'windsurf-skills': dir = path.join(userHome, '.codeium', 'windsurf', 'skills'); break;
    case 'adn-skills':      dir = path.join(__dirname, 'skills'); break;
    case 'antigravity-skills': dir = path.join(userHome, '.gemini', 'antigravity', 'skills'); break;
    default: return null;
  }
  return path.resolve(dir);
}
```

### 2. Directory Scanning

Scanning is **recursive** so both flat layouts (e.g. WindSurf/Antigravity `skills/<skill-name>/SKILL.md`) and nested layouts (e.g. ADN `skills/<category>/<skill-name>/SKILL.md`) are supported.

For each configured directory:

1. **Existence Check**: Verify directory exists
2. **Recursive Walk**: For each subdirectory, look for `SKILL.md` in that directory; if not found, recurse into its children
3. **File Reading**: Read content of each `SKILL.md` found
4. **filePath**: Use `path.relative` to repo root when same drive; on Windows cross-drive (e.g. skills under `C:\` vs repo on `D:\`), use fallback `folderName/dirName/SKILL.md` via `safeFilePath`

### 3. Frontmatter Parsing

The system uses a relaxed regex to extract YAML frontmatter (`^\s*---\s*\n...\n---\s*\n`). Content is trimmed before parsing. Only **top-level** key/value lines are parsed; indented lines (e.g. `allowed-tools:`, `metadata:` blocks) are skipped to avoid malformed metadata.

If **no frontmatter** is found, a skill is still created: `title` is derived from the directory name (`dirName`), `description` is empty, and the full file content is used as `content`. The parser accepts an optional third argument `dirName` for this fallback.

```javascript
// Simplified logic; see bridge-server.js for full implementation
function parseSkillFrontmatter(content, folderName, dirName) {
  const frontmatterMatch = content.match(/^\s*---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);
  let title = dirName ? dirName.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'Untitled Skill';
  let description = '', tags = [], body = content;

  if (frontmatterMatch) {
    const frontmatter = frontmatterMatch[1], lines = frontmatter.split('\n');
    const metadata = {};
    for (const line of lines) {
      if (line.match(/^\s+/)) continue; // skip indented YAML
      const colonIndex = line.indexOf(':');
      if (colonIndex > 0) {
        const key = line.substring(0, colonIndex).trim();
        const value = line.substring(colonIndex + 1).trim().replace(/^["']|["']$/g, '');
        metadata[key] = value;
      }
    }
    title = metadata.name || metadata.title || title;
    description = metadata.description || '';
    tags = metadata.tags ? metadata.tags.split(',').map(t => t.trim()) : [];
    body = frontmatterMatch[2].trim();
  }

  return { id: Date.now() + Math.random(), title, description, folder: folderName, tags,
           created: new Date().toISOString(), modified: new Date().toISOString(), content: body };
}
```

## API Integration

### Skills Endpoint

The webapp accesses skills through the `/api/v1/skills` endpoint:

```javascript
// Get all skills
GET /api/v1/skills

// Get skills from specific folder
GET /api/v1/skills?folder=cursor-skills
```

### Response Format

```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "id": "1642780800000.123456",
        "title": "Skill Title",
        "description": "Skill description",
        "folder": "cursor-skills",
        "tags": ["tag1", "tag2"],
        "created": "2026-01-21T10:00:00.000Z",
        "modified": "2026-01-21T10:00:00.000Z",
        "content": "Full markdown content...",
        "filePath": "relative/path/to/SKILL.md"
      }
    ],
    "folders": ["cursor-skills", "windsurf-skills", "adn-skills", "antigravity-skills"]
  }
}
```

## Error Handling

### Directory Access Issues

- **Directory Not Found**: Logs error, returns empty skill list
- **Permission Denied**: Logs error, returns empty skill list
- **Invalid SKILL.md**: Skips file, continues with others

### Frontmatter Parsing Issues

- **Missing Frontmatter**: A skill is still emitted; `title` from directory name, `description` empty, full file as `content`
- **Malformed YAML**: Top-level key/value parsing only; indented blocks skipped
- **Missing Fields**: Uses defaults (dirName-derived title, empty description, etc.)

## Integration with Webapp

### Skills Page

The React webapp displays skills in a searchable, filterable interface:

- **Folder Selection**: Dropdown to select skill source; **All collections** shows Cursor, WindSurf, Antigravity, and ADN together
- **Search**: Filter by title, description, or tags
- **Skill Cards**: Display skill metadata and preview content
- **Skill Creation**: Modal for creating new skills

### Auto-Discovery

- Skills are automatically discovered on page load
- Real-time updates when switching folders
- Error states show appropriate user feedback

## Future Enhancements

### Planned Features

- **Skill Validation**: Schema validation for skill files
- **Skill Import/Export**: JSON/YAML export formats
- **Skill Dependencies**: Reference management between skills
- **Skill Categories**: Automatic categorization based on content
- **Skill Search**: Full-text search across all skill content

### Performance Optimizations

- **Caching**: Cache parsed skills to reduce file I/O
- **Incremental Updates**: Watch directories for changes
- **Lazy Loading**: Load skill content on demand
- **Background Scanning**: Non-blocking directory scanning

## Troubleshooting

### Common Issues

1. **Skills Not Showing**
   - Ensure `USERPROFILE` / `HOME` are set when bridge runs (user-based dirs)
   - Check directory paths exist (e.g. `~/.codeium/windsurf/skills`, `~/.gemini/antigravity/skills`)
   - Verify `SKILL.md` exists in each skill subdir; use **All collections** to include every folder
   - Check browser console for errors

2. **Parsing Errors**
   - Ensure YAML frontmatter is properly formatted
   - Check for special characters in metadata values
   - Verify markdown content is valid

3. **Performance Issues**
   - Large number of skills may slow initial load
   - Consider pagination for skill lists
   - Implement caching for frequently accessed skills

### Debug Information

Enable verbose logging in `bridge-server.js` to see:

- Directory access attempts
- File parsing results
- Frontmatter extraction details
- API response structures

## Conclusion

The skill parsing architecture provides a robust, extensible system for discovering and managing Claude Skills across multiple IDE environments. By maintaining consistent directory structures and parsing logic, users can seamlessly work with skills created in different tools while maintaining a unified experience in the Advanced Memory MCP webapp.
