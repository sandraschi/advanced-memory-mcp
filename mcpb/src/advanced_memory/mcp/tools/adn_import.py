"""Import Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all import operations: obsidian, joplin, notion, evernote, archive, canvas.
It reduces the number of MCP tools while maintaining full functionality.
"""

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool
async def adn_import(
    operation: str,
    source_path: str,
    destination_folder: str | None = None,
    preserve_structure: bool = True,
    convert_links: bool = True,
    include_attachments: bool = True,
    skip_existing: bool = True,
    create_missing_files: bool = False,
    restore_mode: str = "overwrite",
    backup_existing: bool = True,
    project: str | None = None,
) -> str:
    """Comprehensive import management for Advanced Memory knowledge base.

    This portmanteau tool consolidates all import operations:
    - obsidian: Import complete Obsidian vaults
    - joplin: Import Joplin knowledge bases
    - notion: Import Notion workspaces
    - evernote: Import Evernote ENEX files
    - archive: Import complete system archive
    - canvas: Import Obsidian Canvas files
    - claude_skills: Import Claude Skills (Anthropic agent skills)

    Args:
        operation: The import operation to perform
        source_path: Path to source files
        destination_folder: Advanced Memory folder for imported content
        preserve_structure: Maintain original folder hierarchy
        convert_links: Convert internal links to entity references
        include_attachments: Import images and media files
        skip_existing: Skip notes that already exist
        create_missing_files: Create placeholder notes for missing references
        restore_mode: Archive restore mode (overwrite, merge)
        backup_existing: Backup current data before restore
        project: Optional project name. Supports:
            - None (default): imports to current active project
            - "project-name": imports to specific project
            For archive operations, auto-detects project structure from archive metadata

    Returns:
        Operation-specific result with import details and file counts

    Examples:
        # Import Obsidian vault
        adn_import("obsidian", source_path="/path/to/vault", destination_folder="imported/obsidian")

        # Import Joplin export
        adn_import("joplin", source_path="/path/to/export", destination_folder="imported/joplin")

        # Import Notion workspace
        adn_import("notion", source_path="Notion-Export.zip", destination_folder="imported/notion")

        # Import from archive (auto-detects project structure)
        adn_import("archive", source_path="backup.zip", restore_mode="merge")

        # Import to specific project
        adn_import("obsidian", source_path="/path/to/vault", destination_folder="imported", project="work-notes")
    """
    logger.info(f"MCP tool call tool=adn_import operation={operation} source_path={source_path}")

    # Set default destination folder based on operation
    if not destination_folder:
        destination_folder = f"imported/{operation}"

    # Route to appropriate operation
    if operation == "obsidian":
        return await _obsidian_import(
            source_path,
            destination_folder,
            preserve_structure,
            convert_links,
            include_attachments,
            skip_existing,
            project,
        )
    elif operation == "joplin":
        return await _joplin_import(
            source_path,
            destination_folder,
            preserve_structure,
            convert_links,
            skip_existing,
            project,
        )
    elif operation == "notion":
        return await _notion_import(source_path, destination_folder, preserve_structure, project)
    elif operation == "evernote":
        return await _evernote_import(
            source_path, destination_folder, preserve_structure, include_attachments, project
        )
    elif operation == "archive":
        return await _archive_import(source_path, restore_mode, backup_existing, project)
    elif operation == "canvas":
        return await _canvas_import(source_path, destination_folder, create_missing_files, project)
    elif operation == "claude_skills":
        return await _claude_skills_import(
            source_path, destination_folder, preserve_structure, project
        )
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: obsidian, joplin, notion, evernote, archive, canvas, claude_skills"


async def _obsidian_import(
    source_path: str,
    destination_folder: str,
    preserve_structure: bool,
    convert_links: bool,
    include_attachments: bool,
    skip_existing: bool,
    project: str | None,
) -> str:
    """Handle Obsidian import operation."""
    from advanced_memory.mcp.tools.load_obsidian_vault import load_obsidian_vault

    return await load_obsidian_vault(
        source_path,
        destination_folder,
        preserve_structure,
        convert_links,
        include_attachments,
        skip_existing,
        project,
    )  # type: ignore[operator,no-any-return]


async def _joplin_import(
    source_path: str,
    destination_folder: str,
    preserve_structure: bool,
    convert_links: bool,
    skip_existing: bool,
    project: str | None,
) -> str:
    """Handle Joplin import operation."""
    from advanced_memory.mcp.tools.load_joplin_vault import load_joplin_vault

    return await load_joplin_vault(
        source_path, destination_folder, preserve_structure, convert_links, skip_existing, project
    )  # type: ignore[operator,no-any-return]


async def _notion_import(
    source_path: str, destination_folder: str, preserve_structure: bool, project: str | None
) -> str:
    """Handle Notion import operation."""
    from advanced_memory.mcp.tools.load_notion_export import load_notion_export

    return await load_notion_export(source_path, destination_folder, preserve_structure, project)  # type: ignore[operator,no-any-return]


async def _evernote_import(
    source_path: str,
    destination_folder: str,
    preserve_structure: bool,
    include_attachments: bool,
    project: str | None,
) -> str:
    """Handle Evernote import operation."""
    from advanced_memory.mcp.tools.load_evernote_export import load_evernote_export

    return await load_evernote_export(
        source_path, destination_folder, preserve_structure, include_attachments, project
    )  # type: ignore[operator,no-any-return]


async def _archive_import(
    source_path: str, restore_mode: str, backup_existing: bool, project: str | None
) -> str:
    """Handle archive import operation."""
    from advanced_memory.mcp.tools.import_from_archive import import_from_archive

    return await import_from_archive.fn(source_path, restore_mode, backup_existing, False, project)  # type: ignore[operator,no-any-return]


async def _canvas_import(
    source_path: str, destination_folder: str, create_missing_files: bool, project: str | None
) -> str:
    """Handle Canvas import operation."""
    return f"[UNICODE] **Canvas Import**\n\nCanvas import functionality requires the full load_canvas tool.\n\n**Requested**: {source_path} → {destination_folder}\n**Create missing files**: {create_missing_files}\n\nUse the individual load_canvas tool for complete functionality."


async def _claude_skills_import(
    source_path: str, destination_folder: str, preserve_structure: bool, project: str | None
) -> str:
    """Import Claude Skills into Advanced Memory.

    Args:
        source_path: Path to Claude Skills directory (containing SKILL.md files)
        destination_folder: Destination folder in Advanced Memory
        preserve_structure: Maintain folder hierarchy
        project: Optional project name

    Returns:
        Import summary with skill counts and details
    """
    from pathlib import Path

    from advanced_memory.mcp.tools.content_manager import adn_content
    from advanced_memory.services.skills_converter import SkillsConverter

    logger.info(f"Starting Claude Skills import: {source_path} → {destination_folder}")

    source_dir = Path(source_path).expanduser()
    if not source_dir.exists():
        return f"# Error\n\nSource path not found: {source_path}"

    # Find all SKILL.md files
    skill_files = list(source_dir.rglob("SKILL.md"))

    if not skill_files:
        return f"# No Skills Found\n\nNo SKILL.md files found in {source_path}"

    skills_imported = 0
    errors = []

    for skill_file in skill_files:
        try:
            # Read SKILL.md
            content = skill_file.read_text(encoding="utf-8")

            # Parse Skills frontmatter
            skills_fm, skills_content = SkillsConverter.parse_skill_frontmatter(content)

            # Convert to zettel format
            zettel_fm = SkillsConverter.skill_to_zettel(skills_fm)

            # Determine folder
            if preserve_structure:
                # Preserve relative path from source
                rel_path = skill_file.parent.relative_to(source_dir)
                folder = (
                    f"{destination_folder}/{rel_path}"
                    if rel_path != Path(".")
                    else destination_folder
                )
            else:
                folder = destination_folder

            # Create note in Advanced Memory
            await adn_content(
                operation="write",
                identifier=zettel_fm["title"],
                content=skills_content,
                folder=folder,
                tags=zettel_fm.get("tags", []),
                entity_type=zettel_fm.get("type", "skill"),
                project=project,
            )

            skills_imported += 1
            logger.debug(f"Imported skill: {skills_fm.name} → {zettel_fm['title']}")

        except Exception as e:
            logger.error(f"Failed to import {skill_file}: {e}")
            errors.append(f"{skill_file.name}: {e}")

    # Generate summary
    summary_lines = [
        "# 📚 Claude Skills Import Complete",
        "",
        f"**Imported**: {skills_imported} skills",
        f"**From**: {source_path}",
        f"**To**: {destination_folder}",
        "",
    ]

    if errors:
        summary_lines.append(f"⚠️ **Errors**: {len(errors)}")
        summary_lines.append("")
        for error in errors[:10]:  # Show first 10
            summary_lines.append(f"  - {error}")
        summary_lines.append("")

    summary_lines.extend(
        [
            "## ✅ What's Imported",
            "",
            f"- {skills_imported} skills converted to Advanced Memory notes",
            "- Skills metadata preserved in frontmatter",
            "- Tagged with `claude-skill` for filtering",
            "- Searchable via Advanced Memory search",
            "",
            "## 🔍 Next Steps",
            "",
            "**Search Imported Skills**:",
            f'  search_notes("skill topic", folder="{destination_folder}")',
            "",
            "**Link to Skills in Your Notes**:",
            "  [[Skill Name]] - creates entity relationships",
            "",
            "**Export Enhanced Skills**:",
            f'  adn_export("claude_skills", export_path="~/my-skills/", source_folder="{destination_folder}")',
            "",
            f"**Total Skills in Advanced Memory**: {skills_imported}",
        ]
    )

    return "\n".join(summary_lines)
