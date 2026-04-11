"""Skills Manager portmanteau tool for Claude Skills integration."""

from pathlib import Path
from typing import Literal

import frontmatter
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.adn_skills_operations_new import (
    _distill_from_arxiv_operation,
    _distill_from_expert_operation,
    _distill_from_text_operation,
    _distill_from_textbook_operation,
    _distill_from_wikipedia_operation,
    _import_from_github_operation,
)
from advanced_memory.utils import generate_permalink


@mcp.tool
async def adn_skills(
    operation: Literal[
        "create",
        "read",
        "update",
        "delete",
        "list",
        "validate",
        "export",
        "import",
        "package",
        "from_zettel",
        "to_zettel",
        "import_from_github",
        "distill_from_wikipedia",
        "distill_from_arxiv",
        "distill_from_textbook",
        "distill_from_text",
        "distill_from_expert",
    ],
    identifier: str | None = None,
    skill_name: str | None = None,
    description: str | None = None,
    content: str | None = None,
    source_path: str | None = None,
    export_path: str | None = None,
    category: str | None = None,
    difficulty: Literal["beginner", "intermediate", "advanced", "expert"] | None = None,
    metadata: dict | None = None,
    filters: dict | None = None,
    package_format: Literal["folder", "zip"] | None = "folder",
    page: int = 1,
    page_size: int = 20,
    project: str | None = None,
    # GitHub import parameters
    repository: str | None = None,
    branch: str = "main",
    # Distillation parameters
    topic: str | None = None,
    query: str | None = None,
    max_papers: int = 5,
    chapters: list[int] | None = None,
    pdf_path: str | None = None,
    text_path: str | None = None,
    expert_name: str | None = None,
    focus_area: str | None = None,
    source_types: list[str] | None = None,
    depth: int = 0,
    include_related: bool = False,
    quality: Literal["basic", "comprehensive", "expert"] | None = None,
    synthesis_level: Literal["summary", "synthesis", "comprehensive"] | None = None,
    level: Literal["beginner", "intermediate", "advanced"] | None = None,
    focus: Literal["principles", "examples", "methodology", "all"] | None = None,
    context_level: Literal["basic", "comprehensive", "detailed"] | None = None,
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
    - import_from_github: Import skill from GitHub repository (SkillsMP compatible)
    - distill_from_wikipedia: Create skill from Wikipedia article
    - distill_from_arxiv: Create skill from arXiv research papers
    - distill_from_textbook: Create skill from textbook PDF
    - distill_from_text: Create skill from famous text/document
    - distill_from_expert: Create skill from SOTA thinker's work

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
        operation: The skills operation to perform. MUST be one of:
            - "create": Create new skill with template
            - "read": Read skill in SKILL.md format
            - "update": Update skill metadata or content
            - "delete": Remove skill from knowledge base
            - "list": List all skills with filtering
            - "validate": Check skill format compliance (Anthropic spec)
            - "export": Export skills to Claude Skills format
            - "import": Import Claude Skills from folders/zips
            - "package": Create distributable .zip
            - "from_zettel": Convert zettelkasten note to Claude Skill
            - "to_zettel": Convert Claude Skill back to regular note
        identifier: Skill name or note identifier (required for read/update/delete/validate/package/from_zettel/to_zettel)
        skill_name: Name for new skill - must be hyphen-case, lowercase (required for create operation)
        description: When Claude should use the skill (required for create/from_zettel operations)
        content: Skill instructions (markdown body)
        source_path: Path to import from - folder or .zip (required for import operation)
        export_path: Path to export to (optional, defaults to Desktop)
        category: Skill category (e.g., developer, researcher, writer, creative)
        difficulty: Difficulty level. MUST be one of:
            - "beginner": Basic concepts
            - "intermediate": Standard usage
            - "advanced": Complex scenarios
            - "expert": Deep expertise
            Default: None (not specified)
        metadata: Custom metadata dictionary
        filters: Filtering criteria for list operation
        package_format: Export/package format. MUST be one of:
            - "folder": Export as folder structure (default)
            - "zip": Export as .zip archive
            Default: "folder"
        page: Pagination page for list operation (default: 1)
        page_size: Results per page (default: 20)
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
        return await _create_operation(skill_name, description, category, difficulty, metadata, project)
    elif operation == "read":
        return await _read_operation(identifier or skill_name, project)
    elif operation == "update":
        return await _update_operation(identifier, description, content, category, metadata, project)
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
    elif operation == "import_from_github":
        return await _import_from_github_operation(repository, source_path, branch, category, project)
    elif operation == "distill_from_wikipedia":
        return await _distill_from_wikipedia_operation(topic, depth, include_related, quality, category, project)
    elif operation == "distill_from_arxiv":
        return await _distill_from_arxiv_operation(query, max_papers, synthesis_level, category, project)
    elif operation == "distill_from_textbook":
        return await _distill_from_textbook_operation(pdf_path, chapters, level, category, project)
    elif operation == "distill_from_text":
        return await _distill_from_text_operation(text_path, focus, context_level, category, project)
    elif operation == "distill_from_expert":
        return await _distill_from_expert_operation(expert_name, source_types, focus_area, category, project)
    else:
        return f"""# Error: Invalid Skills Operation

**You provided:** operation="{operation}"

**Valid skills operations are:**
- "create" - Create new skill with template (requires: skill_name, description)
- "read" - Read skill in SKILL.md format (requires: identifier)
- "update" - Update skill metadata or content (requires: identifier, content)
- "delete" - Remove skill from knowledge base (requires: identifier)
- "list" - List all skills with filtering (optional: filters)
- "validate" - Check skill format compliance (requires: identifier)
- "export" - Export skills to Claude Skills format (requires: export_path)
- "import" - Import Claude Skills from folders/zips (requires: source_path)
- "package" - Create distributable .zip (requires: identifier)
- "from_zettel" - Convert note to Claude Skill (requires: identifier, description)
- "to_zettel" - Convert skill back to regular note (requires: identifier)
- "import_from_github" - Import skill from GitHub repository (requires: repository)
- "distill_from_wikipedia" - Create skill from Wikipedia article (requires: topic)
- "distill_from_arxiv" - Create skill from arXiv papers (requires: query)
- "distill_from_textbook" - Create skill from textbook PDF (requires: pdf_path)
- "distill_from_text" - Create skill from famous text (requires: text_path)
- "distill_from_expert" - Create skill from SOTA thinker (requires: expert_name)

**Example for creating a skill:**
```
adn_skills(
    operation="create",
    skill_name="my-skill",
    description="When to use this skill",
    category="developer"
)
```

**Check your operation parameter spelling and required parameters.**"""


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
        return """# Error: Missing Required Parameters

**Operation:** create

**Missing:** skill_name and/or description

The create operation requires both:
- **skill_name**: Hyphen-case name (e.g., "python-expert", "my-skill")
- **description**: When Claude should use this skill

**Example:**
```
adn_skills(
    operation="create",
    skill_name="python-expert",
    description="Expert Python guidance for advanced patterns and best practices",
    category="developer"
)
```

**Provide both required parameters and try again.**"""

    active_project = get_active_project(project)

    # Validate skill name format (Anthropic spec)
    import re

    if not re.match(r"^[a-z0-9-]+$", skill_name):
        return f"# Error\n\nSkill name must be hyphen-case (lowercase letters, digits, hyphens only)\n\nProvided: {skill_name}"

    if skill_name.startswith("-") or skill_name.endswith("-") or "--" in skill_name:
        return f"# Error\n\nSkill name cannot start/end with hyphen or contain consecutive hyphens\n\nProvided: {skill_name}"

    # Validate description (no angle brackets)
    if "<" in description or ">" in description:
        return f"""# Error: Invalid Description Format

**Problem:** Description contains angle brackets (< or >)

**Your description:** {description[:100]}...

Angle brackets are not allowed in Claude Skills descriptions as they can cause parsing issues.

**How to fix:** Remove < and > characters from your description.

**Example of valid description:**
"Expert Python guidance for advanced patterns and best practices"

**Try again with a description without angle brackets.**"""

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

    result = await (write_note.fn if hasattr(write_note, "fn") else write_note)(
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
        return """# Error: Missing Required Parameter

**Operation:** read

**Missing:** identifier parameter

The read operation requires the skill's name or identifier.

**Example:**
```
adn_skills(
    operation="read",
    identifier="python-expert"
)
```

**Provide the skill identifier and try again.**"""

    # Read note content
    from advanced_memory.mcp.tools.read_note import read_note

    return await (read_note.fn if hasattr(read_note, "fn") else read_note)(identifier=identifier, project=project)


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
        return """# Error: Missing Required Parameter

**Operation:** update

**Missing:** identifier parameter

The update operation requires the skill's name or identifier.

**Example:**
```
adn_skills(
    operation="update",
    identifier="python-expert",
    content="# Updated skill content..."
)
```

**Provide the skill identifier and try again.**"""

    # Update using edit_note
    from advanced_memory.mcp.tools.edit_note import edit_note

    if content:
        return await (edit_note.fn if hasattr(edit_note, "fn") else edit_note)(
            identifier=identifier, operation="replace", content=content, project=project
        )
    else:
        return f"""# Error: Missing Required Parameter

**Operation:** update

**Missing:** content parameter

The update operation requires new content for the skill.

**Example:**
```
adn_skills(
    operation="update",
    identifier="{identifier}",
    content="# Updated skill instructions\\n\\n..."
)
```

**Provide the content parameter and try again.**"""


async def _delete_operation(identifier: str | None, project: str | None) -> str:
    """Delete skill."""
    if not identifier:
        return """# Error: Missing Required Parameter

**Operation:** delete

**Missing:** identifier parameter

The delete operation requires the skill's name or identifier.

**Example:**
```
adn_skills(
    operation="delete",
    identifier="python-expert"
)
```

**Provide the skill identifier and try again.**"""

    from advanced_memory.mcp.tools.delete_note import delete_note

    result = await (delete_note.fn if hasattr(delete_note, "fn") else delete_note)(
        identifier=identifier, project=project
    )
    return f"# Skill Deleted\n\n{result}\n\n✅ Skill removed from knowledge base"


async def _list_operation(filters: dict | None, page: int, page_size: int, project: str | None) -> str:
    """List all skills with optional filtering."""

    skills_root = Path("skills")
    if not skills_root.exists():
        return """# Skills List

No `skills/` directory found.

Create your first skill with:
```
adn_skills("create", skill_name="my-skill", description="My first skill")
```
"""

    def _matches_filters(record: dict[str, str | list[str]]) -> bool:
        if not filters:
            return True

        category_filter = filters.get("category")
        if category_filter:
            categories = (
                {category_filter.lower()}
                if isinstance(category_filter, str)
                else {str(cat).lower() for cat in category_filter}
            )
            if record["category"].lower() not in categories:
                return False

        confidence_filter = filters.get("confidence")
        if confidence_filter and record["confidence"].lower() != str(confidence_filter).lower():
            return False

        difficulty_filter = filters.get("difficulty")
        if difficulty_filter and record["difficulty"].lower() != str(difficulty_filter).lower():
            return False

        tag_filter = filters.get("tags")
        if tag_filter:
            requested_tags = (
                {tag.lower() for tag in tag_filter}
                if isinstance(tag_filter, list | tuple | set)
                else {str(tag_filter).lower()}
            )
            record_tags = {tag.lower() for tag in record["tags"]}
            if not record_tags.intersection(requested_tags):
                return False

        return True

    skill_records: list[dict[str, str | list[str]]] = []
    for skill_file in sorted(skills_root.glob("**/SKILL.md")):
        try:
            post = frontmatter.loads(skill_file.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning(f"Failed to parse {skill_file}: {exc}")
            skill_records.append(
                {
                    "title": skill_file.parent.name,
                    "category": "unknown",
                    "confidence": "unknown",
                    "difficulty": "unassigned",
                    "status": "Parse error",
                    "license": "unknown",
                    "allowed_tools": [],
                    "tags": [],
                    "rel_path": skill_file.parent.relative_to(skills_root).as_posix(),
                    "issues": f"Failed to parse frontmatter: {exc}",
                }
            )
            continue

        fm = post.metadata
        meta_block = fm.get("metadata")
        if not isinstance(meta_block, dict):
            meta_block = {}

        category = meta_block.get("category", "general")
        confidence = meta_block.get("confidence", "low")
        difficulty = meta_block.get("difficulty", "unassigned")
        status = meta_block.get("status", "Draft scaffold – complete research checklist before use")
        license_value = fm.get("license", "Proprietary")
        allowed_tools = fm.get("allowed-tools") or []
        if not isinstance(allowed_tools, list):
            allowed_tools = [str(allowed_tools)]
        tags = meta_block.get("tags", [])
        if not isinstance(tags, list):
            tags = [str(tags)]

        record = {
            "title": fm.get("name", skill_file.parent.name),
            "category": str(category),
            "confidence": str(confidence),
            "difficulty": str(difficulty),
            "status": str(status),
            "license": str(license_value),
            "allowed_tools": [str(tool) for tool in allowed_tools],
            "tags": [str(tag) for tag in tags],
            "rel_path": skill_file.parent.relative_to(skills_root).as_posix(),
        }

        if _matches_filters(record):
            skill_records.append(record)

    total = len(skill_records)
    if total == 0:
        return """# Skills List

No skills matched the requested filters.

Create a new skill:
```
adn_skills("create", skill_name="my-skill", description="My first skill")
```
"""

    start = max((page - 1) * page_size, 0)
    end = start + page_size
    page_entries = skill_records[start:end]

    if not page_entries:
        return f"# Skills List\n\nRequested page {page} is out of range for {total} skill(s)."

    lines = [
        "# Skills List",
        "",
        f"Found {total} skill(s). Showing page {page} (items {start + 1}–{start + len(page_entries)}).",
        "",
    ]

    for idx, record in enumerate(page_entries, start=start + 1):
        allowed = ", ".join(record["allowed_tools"]) if record["allowed_tools"] else "None"
        tags = ", ".join(record["tags"]) if record["tags"] else "None"
        lines.append(f"## {idx}. {record['title']}")
        lines.append(f"**Directory:** `skills/{record['rel_path']}`")
        lines.append(f"**Category:** {record['category']}")
        lines.append(f"**Confidence:** {record['confidence']}")
        lines.append(f"**Difficulty:** {record['difficulty']}")
        lines.append(f"**Status:** {record['status']}")
        lines.append(f"**License:** {record['license']}")
        lines.append(f"**Allowed tools:** {allowed}")
        lines.append(f"**Tags:** {tags}")
        if record.get("issues"):
            lines.append(f"**Warnings:** {record['issues']}")
        lines.append("")

    return "\n".join(lines)


async def _validate_operation(identifier: str | None, project: str | None) -> str:
    """Validate skill format compliance with repair suggestions."""
    if not identifier:
        return """# Error: Missing Required Parameter

**Operation:** validate

**Missing:** identifier parameter

The validate operation requires the skill's name or identifier to check.

**Example:**
```
adn_skills(
    operation="validate",
    identifier="python-expert"
)
```

**Provide the skill identifier and try again.**"""

    # Read the skill
    from advanced_memory.mcp.tools.read_note import read_note

    content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(identifier=identifier, project=project)

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
        return """# Error: Missing Required Parameter

**Operation:** export

**Missing:** export_path parameter

The export operation requires a destination path for exported skills.

**Example:**
```
adn_skills(
    operation="export",
    export_path="D:/my-skills/",
    package_format="zip"
)
```

**Tip:** Omit export_path to use default Desktop location.

**Provide export_path or use adn_export('claude_skills') for default location.**"""

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
        return """# Error: Missing Required Parameter

**Operation:** import

**Missing:** source_path parameter

The import operation requires the path to a Claude Skills folder or .zip file.

**Example:**
```
adn_skills(
    operation="import",
    source_path="D:/anthropic-skills/skill-creator"
)
```

**Provide the source_path parameter and try again.**"""

    source = Path(source_path)
    if not source.exists():
        return f"""# Error: Source Path Not Found

**Operation:** import

**Path you provided:** {source_path}

**Problem:** This path does not exist on your file system.

**How to fix:**
1. Check the path spelling
2. Verify the directory/file exists
3. Use absolute paths (e.g., "D:/skills/" not "~/skills/")
4. On Windows, use forward slashes or double backslashes

**Try again with a valid path.**"""

    # Check for SKILL.md
    skill_md = source / "SKILL.md"
    if not skill_md.exists():
        return f"""# Error: Invalid Skill Structure

**Operation:** import

**Path you provided:** {source_path}

**Problem:** No SKILL.md file found in this directory

**Expected structure:**
```
skill-name/
  └── SKILL.md (required entrypoint file)
  └── scripts/ (optional)
  └── references/ (optional)
  └── assets/ (optional)
```

**How to fix:**
1. Verify you're pointing to a skill folder (not a parent directory)
2. Check that SKILL.md exists in the folder
3. Make sure the file is named exactly "SKILL.md" (case-sensitive)

**Try again with a valid skill folder path.**"""

    # Read and parse SKILL.md
    import yaml

    content = skill_md.read_text(encoding="utf-8")

    # Parse frontmatter
    import re

    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        return f"""# Error: Invalid SKILL.md Format

**Operation:** import

**Path:** {source_path}

**Problem:** SKILL.md is missing YAML frontmatter

Claude Skills must start with YAML frontmatter:
```
---
name: skill-name
description: When to use this skill
---

# Skill content here
```

**Check the SKILL.md file format and try again.**"""

    try:
        frontmatter = yaml.safe_load(match.group(1))
        match.group(2)
    except Exception as e:
        return f"""# Error: Invalid YAML Frontmatter

**Operation:** import

**Path:** {source_path}

**Problem:** Could not parse YAML frontmatter

**Error details:** {e!s}

**Common issues:**
- Indentation errors (use spaces, not tabs)
- Unquoted special characters in values
- Missing colons after field names

**Example of valid frontmatter:**
```yaml
---
name: my-skill
description: When to use this skill
---
```

**Fix the YAML syntax and try again.**"""

    skill_name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not skill_name or not description:
        return f"""# Error: Missing Required Fields

**Operation:** import

**Path:** {source_path}

**Problem:** SKILL.md frontmatter missing required fields

**Required fields:**
- **name**: skill-name-in-hyphen-case
- **description**: When Claude should use this skill

**Your frontmatter has:**
- name: {"✅ " + skill_name if skill_name else "❌ MISSING"}
- description: {"✅ " + description[:50] + "..." if description else "❌ MISSING"}

**Add the missing fields to SKILL.md and try again.**"""

    # Determine category from metadata or path
    skill_metadata = frontmatter.get("metadata", {})
    category = skill_metadata.get("category", "general")

    # Create skill in Advanced Memory
    folder = f"skills/{category}"

    from advanced_memory.mcp.tools.write_note import write_note

    result = await (write_note.fn if hasattr(write_note, "fn") else write_note)(
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


async def _package_operation(identifier: str | None, export_path: str | None, project: str | None) -> str:
    """Package skill as distributable .zip."""
    if not identifier:
        return """# Error: Missing Required Parameter

**Operation:** package

**Missing:** identifier parameter

The package operation requires the skill's name or identifier.

**Example:**
```
adn_skills(
    operation="package",
    identifier="python-expert",
    export_path="D:/my-skills/"
)
```

**Provide the skill identifier and try again.**"""

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
        return """# Error: Missing Required Parameters

**Operation:** from_zettel

**Missing:** identifier and/or description

Converting a note to a Claude Skill requires:
- **identifier**: The note's title or permalink
- **description**: When Claude should use this skill

**Example:**
```
adn_skills(
    operation="from_zettel",
    identifier="Python Fundamentals",
    description="Guide for Python fundamentals - use when teaching Python basics",
    category="developer"
)
```

**Provide both required parameters and try again.**"""

    # Read the note
    from advanced_memory.mcp.tools.read_note import read_note

    note_content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=identifier, project=project
    )

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

    result = await (edit_note.fn if hasattr(edit_note, "fn") else edit_note)(
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
        return """# Error: Missing Required Parameter

**Operation:** to_zettel

**Missing:** identifier parameter

The to_zettel operation requires the skill's name or identifier.

**Example:**
```
adn_skills(
    operation="to_zettel",
    identifier="python-expert"
)
```

**Provide the skill identifier and try again.**"""

    # Read the skill
    from advanced_memory.mcp.tools.read_note import read_note

    skill_content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=identifier, project=project
    )

    if "# Note Not Found:" in skill_content:
        return skill_content

    # Parse frontmatter and remove Claude Skills fields
    import re

    import yaml

    match = re.match(r"^---\n(.*?)\n---\n(.*)$", skill_content, re.DOTALL)

    if not match:
        return f"""# Error: Not a Claude Skill

**Operation:** to_zettel

**Identifier:** {identifier}

**Problem:** This note doesn't have Claude Skills frontmatter

This note may already be a regular zettelkasten note (not a skill).

**Claude Skills have:**
```markdown
---
name: skill-name
description: When to use
---
```

**Regular notes have simpler frontmatter or none.**

**This note is probably already a regular note - no conversion needed.**"""

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

    result = await (edit_note.fn if hasattr(edit_note, "fn") else edit_note)(
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

    content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(identifier=identifier, project=project)

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
        return f"# Validation Failed\n\n❌ Invalid YAML frontmatter\n\nError: {e!s}"

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
