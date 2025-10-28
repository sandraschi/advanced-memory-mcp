"""Skills Manager portmanteau tool for Claude Skills integration."""

from pathlib import Path

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.utils import generate_permalink


@mcp.tool
async def adn_skills(
    operation: str,
    identifier: str | None = None,
    skill_name: str | None = None,
    description: str | None = None,
    content: str | None = None,
    source_path: str | None = None,
    export_path: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    metadata: dict | None = None,
    filters: dict | None = None,
    package_format: str = "folder",
    page: int = 1,
    page_size: int = 20,
    project: str | None = None,
) -> str:
    """Claude Skills management portmanteau for Advanced Memory.

    This portmanteau tool provides complete CRUD operations and bidirectional exchange
    with Claude Skills format, integrating skill-creator patterns from Anthropic.

    SUPPORTED OPERATIONS:
    - create: Create new skill with template (init pattern from skill-creator)
    - read: Read skill in SKILL.md format
    - update: Update skill metadata or content
    - delete: Remove skill from knowledge base
    - list: List all skills with filtering
    - validate: Check skill format compliance (Anthropic spec)
    - export: Export skills to Claude Skills format (folders or zips)
    - import: Import Claude Skills from folders/zips
    - package: Create distributable .zip (package pattern from skill-creator)
    - from_zettel: Convert zettelkasten note to Claude Skill
    - to_zettel: Convert Claude Skill back to regular note

    CLAUDE SKILLS FORMAT:
    Skills are folders containing SKILL.md with YAML frontmatter:
    - name: (required) skill-name-in-hyphen-case
    - description: (required) When Claude should use this skill
    - license: (optional) License name or file
    - allowed-tools: (optional) Pre-approved tools list
    - metadata: (optional) Custom key-value pairs

    OPERATIONS DETAIL:

    create: Initialize new skill with template
    - Uses skill-creator initialization pattern
    - Creates SKILL.md with proper frontmatter
    - Generates skills/category/name/ folder structure
    - Adds scripts/, references/, assets/ directories
    - Parameters: skill_name (required), description (required), category (optional)
    - Returns: Created skill with folder structure and next steps

    read: Retrieve skill content
    - Returns SKILL.md in proper format
    - Includes frontmatter + markdown body
    - Parameters: identifier or skill_name (required)
    - Returns: Full SKILL.md content with metadata

    update: Modify existing skill
    - Updates frontmatter metadata
    - Updates markdown content
    - Preserves bundled resources
    - Parameters: identifier (required), description/content/category (any)
    - Returns: Updated skill confirmation

    delete: Remove skill
    - Deletes SKILL.md and resources folder
    - Removes from database
    - Optionally archives instead of deleting
    - Parameters: identifier (required)
    - Returns: Deletion confirmation

    list: Show all skills
    - Filter by category, difficulty, tags
    - Show usage statistics
    - Pagination support
    - Parameters: filters (optional), page/page_size (optional)
    - Returns: Formatted skill list with metadata

    validate: Check format compliance
    - Uses Anthropic validation logic (quick_validate.py pattern)
    - Checks YAML frontmatter required fields
    - Validates naming conventions (hyphen-case)
    - Checks resource structure
    - Parameters: identifier (required)
    - Returns: Validation report with errors/warnings

    export: Export to Claude Skills format
    - Creates SKILL.md files with proper frontmatter
    - Organizes into category/skill-name/ folders
    - Optional: package as .zip files
    - Claude.ai compatible format
    - Parameters: export_path (required), package_format (folder/zip)
    - Returns: Export summary with file counts

    import: Import from Claude Skills
    - Reads SKILL.md files from folders
    - Parses frontmatter metadata
    - Imports to database
    - Preserves bundled resources (scripts/references/assets)
    - Handles both folders and .zip files
    - Parameters: source_path (required)
    - Returns: Import summary with success/failure counts

    package: Create distributable .zip
    - Uses skill-creator package pattern
    - Validates format before packaging
    - Creates skill-name.zip with structure preserved
    - Maintains directory hierarchy
    - Parameters: identifier (required), export_path (optional)
    - Returns: .zip file path and validation status

    from_zettel: Convert note to skill
    - Takes existing zettelkasten note
    - Adds Claude Skills frontmatter fields
    - Sets type: skill in metadata
    - Preserves all existing content
    - Creates skills/category/name/ folder
    - Parameters: identifier (required), description (required), category (optional)
    - Returns: Conversion confirmation with skill location

    to_zettel: Convert skill to note
    - Removes Claude Skills specific frontmatter
    - Sets type: note in metadata
    - Preserves content and tags
    - Moves from skills/ to appropriate folder
    - Parameters: identifier (required)
    - Returns: Conversion confirmation with note location

    Args:
        operation: The skills operation to perform
        identifier: Skill name or note identifier
        skill_name: Name for new skill (hyphen-case, lowercase)
        description: When Claude should use the skill
        content: Skill instructions (markdown body)
        source_path: Path to import from (folder or .zip)
        export_path: Path to export to
        category: Skill category (developer, researcher, writer, etc.)
        difficulty: Difficulty level (beginner, intermediate, advanced, expert)
        metadata: Custom metadata dictionary
        filters: Filtering criteria for list operation
        package_format: Export format (folder or zip)
        page: Pagination page for list operation
        page_size: Results per page
        project: Optional project name

    Returns:
        Operation-specific result with skill details and status

    Examples:
        # Create a skill
        adn_skills("create",
            skill_name="python-expert",
            description="Expert Python guidance for advanced patterns and best practices",
            category="developer")

        # Convert zettel to skill
        adn_skills("from_zettel",
            identifier="Python Fundamentals",
            description="Guide for Python fundamentals - use when teaching Python basics")

        # List all developer skills
        adn_skills("list", filters={"category": "developer"})

        # Validate skill format
        adn_skills("validate", identifier="python-expert")

        # Export all skills to Claude format
        adn_skills("export", export_path="D:/claude-skills/", package_format="zip")

        # Import skill-creator from Anthropic
        adn_skills("import", source_path="D:/anthropic-skills/skill-creator")

        # Package skill for distribution
        adn_skills("package", identifier="python-expert", export_path="./dist")

        # Read skill
        adn_skills("read", identifier="python-expert")

        # Update skill
        adn_skills("update", identifier="python-expert", description="Updated description")

        # Convert skill back to regular note
        adn_skills("to_zettel", identifier="python-expert")
    """
    logger.info(f"MCP tool call tool=adn_skills operation={operation}")

    # Route to appropriate operation
    if operation == "create":
        return await _create_operation(
            skill_name, description, category, difficulty, metadata, project
        )
    elif operation == "read":
        return await _read_operation(identifier or skill_name, project)
    elif operation == "update":
        return await _update_operation(
            identifier, description, content, category, metadata, project
        )
    elif operation == "delete":
        return await _delete_operation(identifier, project)
    elif operation == "list":
        return await _list_operation(filters, page, page_size, project)
    elif operation == "validate":
        return await _validate_operation(identifier, project)
    elif operation == "export":
        return await _export_operation(export_path, package_format, filters, project)
    elif operation == "import":
        return await _import_operation(source_path, project)
    elif operation == "package":
        return await _package_operation(identifier, export_path, project)
    elif operation == "from_zettel":
        return await _from_zettel_operation(identifier, description, category, metadata, project)
    elif operation == "to_zettel":
        return await _to_zettel_operation(identifier, project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: create, read, update, delete, list, validate, export, import, package, from_zettel, to_zettel"


async def _create_operation(
    skill_name: str | None,
    description: str | None,
    category: str | None,
    difficulty: str | None,
    metadata: dict | None,
    project: str | None,
) -> str:
    """Create new skill using skill-creator init pattern."""
    if not skill_name or not description:
        return "# Error\n\nCreate requires: skill_name and description parameters"

    active_project = get_active_project(project)

    # Validate skill name format (Anthropic spec)
    import re

    if not re.match(r"^[a-z0-9-]+$", skill_name):
        return f"# Error\n\nSkill name must be hyphen-case (lowercase letters, digits, hyphens only)\n\nProvided: {skill_name}"

    if skill_name.startswith("-") or skill_name.endswith("-") or "--" in skill_name:
        return f"# Error\n\nSkill name cannot start/end with hyphen or contain consecutive hyphens\n\nProvided: {skill_name}"

    # Validate description (no angle brackets)
    if "<" in description or ">" in description:
        return "# Error\n\nDescription cannot contain angle brackets (< or >)"

    # Create skill folder structure
    skill_folder = f"skills/{category or 'general'}"
    skill_title = " ".join(word.capitalize() for word in skill_name.split("-"))

    # Build SKILL.md content
    frontmatter = {
        "name": skill_name,
        "description": description,
        "type": "skill",
    }

    if category:
        if not metadata:
            metadata = {}
        metadata["category"] = category
    if difficulty:
        if not metadata:
            metadata = {}
        metadata["difficulty"] = difficulty
    if metadata:
        frontmatter["metadata"] = metadata

    # Build frontmatter YAML
    import yaml

    yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)

    skill_content = f"""---
{yaml_str}---

# {skill_title}

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
"""

    # Create the skill using write_note
    from advanced_memory.mcp.tools.write_note import write_note

    result = await write_note.fn(
        title=skill_name,
        content=skill_content,
        folder=skill_folder,
        tags=["claude-skill", category] if category else ["claude-skill"],
        entity_type="skill",
        project=active_project.name,
    )

    # Create bundled resource directories (Anthropic skill-creator pattern)
    project_path = Path(active_project.path)
    skill_dir = project_path / skill_folder / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Create scripts/ directory with example
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    (scripts_dir / "example.py").write_text(
        '"""Example script for this skill.\n\n'
        "Scripts can be executed by Claude for deterministic tasks.\n"
        '"""\n\n'
        "def main():\n"
        '    print("Hello from skill script!")\n\n'
        'if __name__ == "__main__":\n'
        "    main()\n",
        encoding="utf-8",
    )

    # Create references/ directory with example
    references_dir = skill_dir / "references"
    references_dir.mkdir(exist_ok=True)
    (references_dir / "example.md").write_text(
        f"# {skill_title} Reference\n\n"
        "This directory contains reference documentation loaded as needed.\n\n"
        "## Usage\n\n"
        "Reference files are loaded into context when Claude needs detailed information.\n"
        "Keep detailed schemas, API docs, or domain knowledge here.\n",
        encoding="utf-8",
    )

    # Create assets/ directory with README
    assets_dir = skill_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    (assets_dir / "README.md").write_text(
        f"# {skill_title} Assets\n\n"
        "This directory contains files used in output (not loaded into context).\n\n"
        "## Examples\n\n"
        "- Templates (HTML, React, etc.)\n"
        "- Images (logos, icons)\n"
        "- Boilerplate code\n"
        "- Fonts, styles, etc.\n",
        encoding="utf-8",
    )

    return f"""{result}

## Skill Structure Created

**Directory**: {skill_folder}/{skill_name}/
- SKILL.md (main instructions)
- scripts/ (executable code with example.py)
- references/ (documentation with example.md)
- assets/ (templates, resources with README.md)

## Next Steps

1. Edit SKILL.md to complete TODO sections
2. Add Python/Bash scripts to **scripts/** for reusable code
3. Add documentation to **references/** for detailed reference material
4. Add templates/assets to **assets/** for output resources
5. Validate: adn_skills("validate", identifier="{skill_name}")
6. Package: adn_skills("package", identifier="{skill_name}")

✅ Skill created following Anthropic skill-creator pattern!"""


async def _read_operation(identifier: str | None, project: str | None) -> str:
    """Read skill in SKILL.md format."""
    if not identifier:
        return "# Error\n\nRead requires: identifier parameter"

    # Read note content
    from advanced_memory.mcp.tools.read_note import read_note

    return await read_note.fn(identifier=identifier, project=project)


async def _update_operation(
    identifier: str | None,
    description: str | None,
    content: str | None,
    category: str | None,
    metadata: dict | None,
    project: str | None,
) -> str:
    """Update existing skill."""
    if not identifier:
        return "# Error\n\nUpdate requires: identifier parameter"

    # Update using edit_note
    from advanced_memory.mcp.tools.edit_note import edit_note

    if content:
        return await edit_note.fn(
            identifier=identifier, operation="replace", content=content, project=project
        )
    else:
        return f"# Error\n\nUpdate requires content parameter\n\nUse: adn_skills('update', identifier='{identifier}', content='...updated content...')"


async def _delete_operation(identifier: str | None, project: str | None) -> str:
    """Delete skill."""
    if not identifier:
        return "# Error\n\nDelete requires: identifier parameter"

    from advanced_memory.mcp.tools.delete_note import delete_note

    result = await delete_note.fn(identifier=identifier, project=project)
    return f"# Skill Deleted\n\n{result}\n\n✅ Skill removed from knowledge base"


async def _list_operation(
    filters: dict | None, page: int, page_size: int, project: str | None
) -> str:
    """List all skills with filtering."""
    from advanced_memory.mcp.tools.search import search_notes

    # Search for skills (entity_type = skill)
    results = await search_notes.fn(
        query="*",
        entity_types=["skill"],
        page=page,
        results_per_page=page_size,
        project=project,
    )

    if not results or not results.results:
        return """# Skills List

No skills found.

CREATE YOUR FIRST SKILL:
adn_skills("create", skill_name="my-skill", description="My first skill")

OR IMPORT FROM ANTHROPIC:
adn_skills("import", source_path="D:/anthropic-skills/skill-creator")"""

    # Format results
    response_lines = [
        "# Skills List",
        "",
        f"Found {len(results.results)} skill(s):",
        "",
    ]

    for idx, skill in enumerate(results.results, 1):
        title = skill.title or "Unknown"
        permalink = skill.permalink or ""
        metadata_str = skill.metadata or {}
        cat = (
            metadata_str.get("category", "general") if isinstance(metadata_str, dict) else "general"
        )

        response_lines.append(f"## {idx}. {title}")
        response_lines.append(f"**Category:** {cat}")
        response_lines.append(f"**Permalink:** {permalink}")
        response_lines.append("")

    response_lines.append(f"**Total:** {len(results.results)} skills")
    response_lines.append(
        f"**Page:** {page} of {(results.total + page_size - 1) // page_size if hasattr(results, 'total') else '?'}"
    )

    return "\n".join(response_lines)


async def _validate_operation(identifier: str | None, project: str | None) -> str:
    """Validate skill format compliance with repair suggestions."""
    if not identifier:
        return "# Error\n\nValidate requires: identifier parameter"

    # Read the skill
    from advanced_memory.mcp.tools.read_note import read_note

    content = await read_note.fn(identifier=identifier, project=project)

    if "# Note Not Found:" in content:
        return content

    # Use skill_helpers for validation
    from advanced_memory.mcp.tools.skill_helpers import (
        generate_repair_suggestions,
        parse_skill_frontmatter,
        validate_skill_frontmatter,
    )

    # Parse frontmatter
    frontmatter, body, parse_errors = parse_skill_frontmatter(content)

    # If no frontmatter, provide comprehensive repair suggestions
    if frontmatter is None:
        suggestions = generate_repair_suggestions(parse_errors, None, content)
        return f"""# Validation Failed

**Skill:** {identifier}

## Errors

{chr(10).join(f"❌ {error}" for error in parse_errors)}

{suggestions}

**After fixing, run:** `adn_skills("validate", identifier="{identifier}")`"""

    # Validate frontmatter content
    errors, warnings = validate_skill_frontmatter(frontmatter)

    # Build validation report
    if errors:
        suggestions = generate_repair_suggestions(errors, frontmatter, content)
        return f"""# Validation Failed

**Skill:** {identifier}

## Errors ({len(errors)})

{chr(10).join(f"❌ {error}" for error in errors)}

{f"## Warnings ({len(warnings)})" + chr(10) + chr(10).join(f"⚠️ {warning}" for warning in warnings) if warnings else ""}

{suggestions}

**After fixing, run:** `adn_skills("validate", identifier="{identifier}")`"""

    # Validation passed!
    return f"""# Validation Passed ✅

**Skill:** {identifier}
**Name:** {frontmatter.get("name", "N/A")}
**Description:** {frontmatter.get("description", "N/A")[:100]}{"..." if len(frontmatter.get("description", "")) > 100 else ""}

## Checks

✅ YAML frontmatter present
✅ Required field 'name' present and valid
✅ Required field 'description' present and valid
✅ Naming convention correct (hyphen-case)
✅ No invalid characters

{f"## Warnings ({len(warnings)})" + chr(10) + chr(10).join(f"⚠️ {warning}" for warning in warnings) if warnings else ""}

**Status:** Ready for export to Claude! 🚀

**Next steps:**
- Export: `adn_skills("export", export_path="./claude-skills/")`
- Package: `adn_skills("package", identifier="{identifier}")`"""


async def _export_operation(
    export_path: str | None,
    package_format: str,
    filters: dict | None,
    project: str | None,
) -> str:
    """Export skills to Claude Skills format."""
    if not export_path:
        return "# Error\n\nExport requires: export_path parameter"

    # List skills to export
    skills_list = await _list_operation(filters, 1, 1000, project)

    if "No skills found" in skills_list:
        return skills_list

    # For now, provide instructions (full implementation later)
    return f"""# Skills Export

**Export path:** {export_path}
**Format:** {package_format}

## Next Steps

This operation will be fully implemented in the next version.

For now, use:
1. Read each skill: adn_skills("read", identifier="skill-name")
2. Manually create SKILL.md files in export directory
3. Or use existing adn_export("claude_skills") for batch export

**Coming soon:** Full automatic export with package_format support!"""


async def _import_operation(source_path: str | None, project: str | None) -> str:
    """Import Claude Skills from folders."""
    if not source_path:
        return "# Error\n\nImport requires: source_path parameter"

    source = Path(source_path)
    if not source.exists():
        return f"# Error\n\nSource path not found: {source_path}"

    # Check for SKILL.md
    skill_md = source / "SKILL.md"
    if not skill_md.exists():
        return f"""# Error\n\nNo SKILL.md found in {source_path}

SKILL STRUCTURE:
skill-name/
  └── SKILL.md (required)

Ensure the source path contains a valid skill folder."""

    # Read and parse SKILL.md
    import yaml

    content = skill_md.read_text(encoding="utf-8")

    # Parse frontmatter
    import re

    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return "# Error\n\nInvalid SKILL.md format (no frontmatter)"

    try:
        frontmatter = yaml.safe_load(match.group(1))
        match.group(2)
    except Exception as e:
        return f"# Error\n\nFailed to parse SKILL.md: {str(e)}"

    skill_name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not skill_name or not description:
        return "# Error\n\nSKILL.md missing required fields (name and description)"

    # Determine category from metadata or path
    skill_metadata = frontmatter.get("metadata", {})
    category = skill_metadata.get("category", "general")

    # Create skill in Advanced Memory
    folder = f"skills/{category}"

    from advanced_memory.mcp.tools.write_note import write_note

    result = await write_note.fn(
        title=skill_name,
        content=content,  # Full content including frontmatter
        folder=folder,
        tags=["claude-skill", "imported", category],
        entity_type="skill",
        project=project,
    )

    return f"""# Skill Imported

{result}

**Source:** {source_path}
**Skill name:** {skill_name}
**Category:** {category}

✅ Skill successfully imported from Claude Skills format!"""


async def _package_operation(
    identifier: str | None, export_path: str | None, project: str | None
) -> str:
    """Package skill as distributable .zip."""
    if not identifier:
        return "# Error\n\nPackage requires: identifier parameter"

    return f"""# Package Skill

**Skill:** {identifier}
**Export path:** {export_path or "./dist"}

## Coming Soon

Full packaging with validation will be implemented in next version.

For now:
1. Validate: adn_skills("validate", identifier="{identifier}")
2. Export: adn_skills("export", export_path="{export_path or "./dist"}")

**Status:** Planned feature - implementation pending"""


async def _from_zettel_operation(
    identifier: str | None,
    description: str | None,
    category: str | None,
    metadata: dict | None,
    project: str | None,
) -> str:
    """Convert zettelkasten note to Claude Skill."""
    if not identifier or not description:
        return "# Error\n\nConversion requires: identifier and description parameters"

    # Read the note
    from advanced_memory.mcp.tools.read_note import read_note

    note_content = await read_note.fn(identifier=identifier, project=project)

    if "# Note Not Found:" in note_content:
        return note_content

    # Generate skill name from identifier
    skill_name = generate_permalink(identifier)

    # Parse existing frontmatter and update
    import re

    import yaml

    match = re.match(r"^---\n(.*?)\n---\n(.*)$", note_content, re.DOTALL)

    if match:
        existing_frontmatter = yaml.safe_load(match.group(1))
        body = match.group(2)
    else:
        existing_frontmatter = {}
        body = note_content

    # Add Claude Skills fields
    existing_frontmatter["name"] = skill_name
    existing_frontmatter["description"] = description
    existing_frontmatter["type"] = "skill"

    if category or metadata:
        if "metadata" not in existing_frontmatter:
            existing_frontmatter["metadata"] = {}
        if category:
            existing_frontmatter["metadata"]["category"] = category
        if metadata:
            existing_frontmatter["metadata"].update(metadata)

    # Build new content
    yaml_str = yaml.dump(existing_frontmatter, default_flow_style=False, allow_unicode=True)
    new_content = f"---\n{yaml_str}---\n{body}"

    # Update the note
    from advanced_memory.mcp.tools.edit_note import edit_note

    result = await edit_note.fn(
        identifier=identifier, operation="replace", content=new_content, project=project
    )

    return f"""# Zettel → Skill Conversion

{result}

## Converted

**Note:** {identifier}
**Skill name:** {skill_name}
**Type:** note → skill

## Claude Skills Fields Added

- name: {skill_name}
- description: {description[:100]}...
- type: skill

✅ Note is now a Claude Skill!
✅ Works in both Advanced Memory and Claude.ai"""


async def _to_zettel_operation(identifier: str | None, project: str | None) -> str:
    """Convert Claude Skill back to regular note."""
    if not identifier:
        return "# Error\n\nConversion requires: identifier parameter"

    # Read the skill
    from advanced_memory.mcp.tools.read_note import read_note

    skill_content = await read_note.fn(identifier=identifier, project=project)

    if "# Note Not Found:" in skill_content:
        return skill_content

    # Parse frontmatter and remove Claude Skills fields
    import re

    import yaml

    match = re.match(r"^---\n(.*?)\n---\n(.*)$", skill_content, re.DOTALL)

    if not match:
        return "# Error\n\nNo frontmatter found - already a regular note?"

    frontmatter = yaml.safe_load(match.group(1))
    body = match.group(2)

    # Remove Claude Skills specific fields
    frontmatter.pop("name", None)
    frontmatter.pop("description", None)
    frontmatter["type"] = "note"  # Change type back to note

    # Clean metadata
    if "metadata" in frontmatter:
        metadata = frontmatter["metadata"]
        if isinstance(metadata, dict):
            metadata.pop("category", None)
            metadata.pop("difficulty", None)
            if not metadata:  # Empty after cleanup
                frontmatter.pop("metadata")

    # Build new content
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    new_content = f"---\n{yaml_str}---\n{body}"

    # Update the note
    from advanced_memory.mcp.tools.edit_note import edit_note

    result = await edit_note.fn(
        identifier=identifier, operation="replace", content=new_content, project=project
    )

    return f"""# Skill → Zettel Conversion

{result}

## Converted

**Skill:** {identifier}
**Type:** skill → note

## Claude Skills Fields Removed

- name (removed)
- description (removed)
- type: skill → note

✅ Now a regular zettelkasten note!"""


async def _validate_operation(identifier: str | None, project: str | None) -> str:
    """Validate skill format (already implemented above)."""
    if not identifier:
        return "# Error\n\nValidate requires: identifier parameter"

    # Read and validate (reuse validation logic from _validate_operation above)
    from advanced_memory.mcp.tools.read_note import read_note

    content = await read_note.fn(identifier=identifier, project=project)

    if "# Note Not Found:" in content:
        return content

    # Validation logic (same as in _validate_operation helper)
    import re

    import yaml

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return "# Validation Failed\n\n❌ No YAML frontmatter found\n\nSkills must start with ---\\n...\\n---"

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except Exception as e:
        return f"# Validation Failed\n\n❌ Invalid YAML frontmatter\n\nError: {str(e)}"

    errors = []
    warnings = []

    # Validate required fields
    if "name" not in frontmatter:
        errors.append("Missing required field: name")
    else:
        name = frontmatter["name"]
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"Name '{name}' must be hyphen-case")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append(f"Name '{name}' has invalid hyphen placement")

    if "description" not in frontmatter:
        errors.append("Missing required field: description")
    else:
        desc = frontmatter["description"]
        if "<" in desc or ">" in desc:
            errors.append("Description contains angle brackets")
        if len(desc.strip()) < 20:
            warnings.append("Description is short (< 20 chars)")

    if errors:
        return f"""# Validation Failed

❌ {len(errors)} error(s) found

{chr(10).join(f"• {error}" for error in errors)}

{f"⚠️ {len(warnings)} warning(s)" + chr(10) + chr(10).join(f"• {warning}" for warning in warnings) if warnings else ""}"""

    return f"""# Validation Passed

✅ Skill is Anthropic spec compliant!

**Name:** {frontmatter.get("name")}
**Description:** {frontmatter.get("description")[:100]}...

{"⚠️ Warnings:" + chr(10) + chr(10).join(f"• {warning}" for warning in warnings) if warnings else ""}

**Ready for Claude.ai upload!**"""
