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
) -> dict:
    """Comprehensive import management for Advanced Memory knowledge base.

    This point-of-entry tool provides a unified interface for importing content
    from various external sources into the Advanced Memory ecosystem.

    RESPONSES:
    Success: {"success": true, "operation": "...", "summary": "...", "result": {...}}
    Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

    For errors, check recovery_options for next steps.

    ---------------------------------------------------------------------------
    [PORTMANTEAU PATTERN RATIONALE]
    Consolidates 10+ import operations into one tool to prevent tool explosion while maintaining full functionality.

    ---------------------------------------------------------------------------
    [PARAMETER DESIGN]
    The parameters are categorized by source type and import requirements:
    - Source (source_path): The common input for all operations.
    - Destination (destination_folder, project): Where the content goes.
    - Options (preserve_structure, convert_links, include_attachments): Modification flags.
    - Behavior (skip_existing, create_missing_files, restore_mode): functional switches.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]

    Note-Taking Apps:
    - obsidian: Import complete Obsidian vaults (preserves links/attachments).
    - joplin: Import Joplin export directories.
    - notion: Import Notion export (ZIP or directory).
    - evernote: Import Evernote ENEX files.
    - onenote: Import OneNote pages from HTML JSON.

    AI Assistants:
    - claude_skills: Import Anthropic agent skills (SKILL.md).
    - claude_conversations: Import Claude.ai data export.
    - claude_projects: Import Claude.ai project artifacts.
    - chatgpt: Import ChatGPT data export.
    - gemini: Import Google Gemini data export.

    System:
    - archive: Restore complete system backups.
    - canvas: Import Obsidian Canvas files.

    ---------------------------------------------------------------------------
    [PREREQUISITES]
    - 'source_path' must be a valid file or directory depending on the operation.
    - Valid exports from respective services (e.g., JSON export for Claude).

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The import source/type to process (Required).
    - source_path (str): File system path to import from (Required).
    - destination_folder (str): Target folder in Advanced Memory (Optional).
    - preserve_structure (bool): Maintain folder hierarchy where applicable (Default: True).
    - convert_links (bool): Transform wiki-links to entity references (Default: True).
    - include_attachments (bool): Import media files (Default: True).
    - skip_existing (bool): Prevent overwriting existing notes (Default: True).
    - project (str): Target project context (Optional).

    ---------------------------------------------------------------------------
    [USAGE]
    Use this tool to migrate data from other tools or restore backups.
    It automatically handles format conversion and metadata preservation.

    ---------------------------------------------------------------------------
    [EXAMPLES]

    - Import an Obsidian vault:
      adn_import(operation="obsidian", source_path="/path/to/vault", destination_folder="imported/obsidian")

    - Import Claude conversations:
      adn_import(operation="claude_conversations", source_path="conversations.json")

    - Restore from backup:
      adn_import(operation="archive", source_path="backup.zip", restore_mode="merge")

    ---------------------------------------------------------------------------
    [ERRORS]
    - Source not found: The provided path does not exist.
    - Invalid format: The source file is not in the expected format (e.g., bad JSON).
    - Import failed: General failure during the import process.
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
            source_path,
            destination_folder,
            preserve_structure,
            include_attachments,
            project,
        )
    elif operation == "onenote":
        return await _onenote_import(source_path, destination_folder, project)
    elif operation == "archive":
        return await _archive_import(source_path, restore_mode, backup_existing, project)
    elif operation == "canvas":
        return await _canvas_import(source_path, destination_folder, create_missing_files, project)
    elif operation == "claude_skills":
        return await _claude_skills_import(
            source_path, destination_folder, preserve_structure, project
        )
    elif operation == "claude_conversations":
        return await _claude_conversations_import(source_path, destination_folder, project)
    elif operation == "claude_projects":
        return await _claude_projects_import(source_path, destination_folder, project)
    elif operation == "chatgpt":
        return await _chatgpt_import(source_path, destination_folder, project)
    elif operation == "gemini":
        return await _gemini_import(source_path, destination_folder, project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: obsidian, joplin, notion, evernote, onenote, archive, canvas, claude_skills, claude_conversations, claude_projects, chatgpt, gemini"


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
        source_path,
        destination_folder,
        preserve_structure,
        convert_links,
        skip_existing,
        project,
    )  # type: ignore[operator,no-any-return]


async def _notion_import(
    source_path: str,
    destination_folder: str,
    preserve_structure: bool,
    project: str | None,
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
        source_path,
        destination_folder,
        preserve_structure,
        include_attachments,
        project,
    )  # type: ignore[operator,no-any-return]


async def _onenote_import(
    source_path: str,
    destination_folder: str,
    project: str | None,
) -> str:
    """Handle OneNote import operation."""
    from advanced_memory.mcp.tools.load_onenote_html import load_onenote_html

    return await load_onenote_html(
        source_path=source_path,
        folder=destination_folder,
        project=project,
    )  # type: ignore[operator,no-any-return]


async def _archive_import(
    source_path: str, restore_mode: str, backup_existing: bool, project: str | None
) -> str:
    """Handle archive import operation."""
    from advanced_memory.mcp.tools.import_from_archive import import_from_archive

    return await import_from_archive.fn(source_path, restore_mode, backup_existing, False, project)  # type: ignore[operator,no-any-return]


async def _canvas_import(
    source_path: str,
    destination_folder: str,
    create_missing_files: bool,
    project: str | None,
) -> str:
    """Handle Canvas import operation."""
    return f"[UNICODE] **Canvas Import**\n\nCanvas import functionality requires the full load_canvas tool.\n\n**Requested**: {source_path} → {destination_folder}\n**Create missing files**: {create_missing_files}\n\nUse the individual load_canvas tool for complete functionality."


async def _claude_skills_import(
    source_path: str,
    destination_folder: str,
    preserve_structure: bool,
    project: str | None,
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


async def _claude_conversations_import(
    source_path: str, destination_folder: str, project: str | None
) -> str:
    """Handle Claude conversations import operation.

    Args:
        source_path: Path to Claude conversations.json export file
        destination_folder: Destination folder in Advanced Memory
        project: Optional project name

    Returns:
        Import summary with conversation and message counts
    """
    import json
    from pathlib import Path

    from advanced_memory.config import get_project_config
    from advanced_memory.importers.claude_conversations_importer import (
        ClaudeConversationsImporter,
    )
    from advanced_memory.markdown import EntityParser, MarkdownProcessor

    logger.info(f"Starting Claude conversations import: {source_path} → {destination_folder}")

    # Validate source file
    source_file = Path(source_path).expanduser()
    if not source_file.exists():
        return f"# Error\n\nSource file not found: {source_path}\n\n**How to export from Claude.ai:**\n1. Go to claude.ai → Settings → Privacy → Export Data\n2. Or use Claude Exporter Chrome extension\n3. Download conversations.json file"

    # Get config and markdown processor
    config = get_project_config(project) if project else get_project_config()
    entity_parser = EntityParser(config.home)
    markdown_processor = MarkdownProcessor(entity_parser)

    # Create importer
    importer = ClaudeConversationsImporter(config.home, markdown_processor)

    try:
        # Read JSON file
        with source_file.open("r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Run import
        result = await importer.import_data(json_data, destination_folder)

        if not result.success:
            return f"# Error\n\nImport failed: {result.error_message}"

        # Generate summary
        summary_lines = [
            "# ✅ Claude Conversations Import Complete",
            "",
            f"**Imported**: {result.conversations} conversations",
            f"**Messages**: {result.messages} total messages",
            f"**From**: {source_path}",
            f"**To**: {destination_folder}",
            "",
            "## 📝 Next Steps",
            "",
            "**Sync to index new files**:",
            "  Run sync to add imported conversations to search index",
            "",
            "**Search imported conversations**:",
            f'  adn_search("notes", query="your search", folder="{destination_folder}")',
            "",
            f"**Total conversations in Advanced Memory**: {result.conversations}",
        ]

        return "\n".join(summary_lines)

    except json.JSONDecodeError as e:
        return f"# Error\n\nInvalid JSON file: {source_path}\n\nError: {e}\n\n**Expected format**: Array of conversation objects with 'name', 'chat_messages', 'created_at', 'updated_at' fields"
    except Exception as e:
        logger.exception("Claude conversations import failed")
        return f"# Error\n\nImport failed: {e}"


async def _claude_projects_import(
    source_path: str, destination_folder: str, project: str | None
) -> str:
    """Handle Claude projects import operation.

    Args:
        source_path: Path to Claude projects.json export file
        destination_folder: Destination folder in Advanced Memory
        project: Optional project name

    Returns:
        Import summary with document and prompt counts
    """
    import json
    from pathlib import Path

    from advanced_memory.config import get_project_config
    from advanced_memory.importers.claude_projects_importer import (
        ClaudeProjectsImporter,
    )
    from advanced_memory.markdown import EntityParser, MarkdownProcessor

    logger.info(f"Starting Claude projects import: {source_path} → {destination_folder}")

    # Validate source file
    source_file = Path(source_path).expanduser()
    if not source_file.exists():
        return f"# Error\n\nSource file not found: {source_path}\n\n**How to export from Claude.ai:**\n1. Go to claude.ai → Settings → Privacy → Export Data\n2. Or use Claude Exporter Chrome extension\n3. Download projects.json file"

    # Get config and markdown processor
    config = get_project_config(project) if project else get_project_config()
    entity_parser = EntityParser(config.home)
    markdown_processor = MarkdownProcessor(entity_parser)

    # Create importer
    importer = ClaudeProjectsImporter(config.home, markdown_processor)

    try:
        # Read JSON file
        with source_file.open("r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Run import
        result = await importer.import_data(json_data, destination_folder)

        if not result.success:
            return f"# Error\n\nImport failed: {result.error_message}"

        # Generate summary
        summary_lines = [
            "# ✅ Claude Projects Import Complete",
            "",
            f"**Documents**: {result.documents} project documents",
            f"**Prompts**: {result.prompts} prompt templates",
            f"**From**: {source_path}",
            f"**To**: {destination_folder}",
            "",
            "## 📝 Next Steps",
            "",
            "**Sync to index new files**:",
            "  Run sync to add imported projects to search index",
            "",
            "**Search imported projects**:",
            f'  adn_search("notes", query="project name", folder="{destination_folder}")',
            "",
            f"**Total documents in Advanced Memory**: {result.documents}",
        ]

        return "\n".join(summary_lines)

    except json.JSONDecodeError as e:
        return f"# Error\n\nInvalid JSON file: {source_path}\n\nError: {e}\n\n**Expected format**: Array of project objects with 'name', 'docs', 'prompt_template' fields"
    except Exception as e:
        logger.exception("Claude projects import failed")
        return f"# Error\n\nImport failed: {e}"


async def _chatgpt_import(source_path: str, destination_folder: str, project: str | None) -> str:
    """Handle ChatGPT import operation.

    Args:
        source_path: Path to ChatGPT conversations.json export file
        destination_folder: Destination folder in Advanced Memory
        project: Optional project name

    Returns:
        Import summary with conversation and message counts
    """
    import json
    from pathlib import Path

    from advanced_memory.config import get_project_config
    from advanced_memory.importers.chatgpt_importer import ChatGPTImporter
    from advanced_memory.markdown import EntityParser, MarkdownProcessor

    logger.info(f"Starting ChatGPT import: {source_path} → {destination_folder}")

    # Validate source file
    source_file = Path(source_path).expanduser()
    if not source_file.exists():
        return f"# Error\n\nSource file not found: {source_path}\n\n**How to export from ChatGPT:**\n1. Go to chat.openai.com → Settings → Data Controls\n2. Click 'Export data'\n3. Select 'Conversations'\n4. Download conversations.json file"

    # Get config and markdown processor
    config = get_project_config(project) if project else get_project_config()
    entity_parser = EntityParser(config.home)
    markdown_processor = MarkdownProcessor(entity_parser)

    # Create importer
    importer = ChatGPTImporter(config.home, markdown_processor)

    try:
        # Read JSON file
        with source_file.open("r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Run import
        result = await importer.import_data(json_data, destination_folder)

        if not result.success:
            return f"# Error\n\nImport failed: {result.error_message}"

        # Generate summary
        summary_lines = [
            "# ✅ ChatGPT Import Complete",
            "",
            f"**Imported**: {result.conversations} conversations",
            f"**Messages**: {result.messages} total messages",
            f"**From**: {source_path}",
            f"**To**: {destination_folder}",
            "",
            "## 📝 Next Steps",
            "",
            "**Sync to index new files**:",
            "  Run sync to add imported conversations to search index",
            "",
            "**Search imported conversations**:",
            f'  adn_search("notes", query="your search", folder="{destination_folder}")',
            "",
            f"**Total conversations in Advanced Memory**: {result.conversations}",
        ]

        return "\n".join(summary_lines)

    except json.JSONDecodeError as e:
        return f"# Error\n\nInvalid JSON file: {source_path}\n\nError: {e}\n\n**Expected format**: Array of conversation objects with 'title', 'mapping', 'create_time', 'update_time' fields"
    except Exception as e:
        logger.exception("ChatGPT import failed")
        return f"# Error\n\nImport failed: {e}"


async def _gemini_import(source_path: str, destination_folder: str, project: str | None) -> str:
    """Handle Google Gemini import operation.

    Args:
        source_path: Path to Gemini conversations.json export file
        destination_folder: Destination folder in Advanced Memory
        project: Optional project name

    Returns:
        Import summary with conversation and message counts
    """
    import json
    from pathlib import Path

    from advanced_memory.config import get_project_config
    from advanced_memory.importers.gemini_importer import GeminiImporter
    from advanced_memory.markdown import EntityParser, MarkdownProcessor

    logger.info(f"Starting Gemini import: {source_path} → {destination_folder}")

    # Validate source file
    source_file = Path(source_path).expanduser()
    if not source_file.exists():
        return f"# Error\n\nSource file not found: {source_path}\n\n**How to export from Google Gemini:**\n1. Install 'Simple Exporter for Gemini™' Chrome extension\n2. Go to gemini.google.com and open a conversation\n3. Click the extension icon and select 'JSON' format\n4. Save the exported JSON file"

    # Get config and markdown processor
    config = get_project_config(project) if project else get_project_config()
    entity_parser = EntityParser(config.home)
    markdown_processor = MarkdownProcessor(entity_parser)

    # Create importer
    importer = GeminiImporter(config.home, markdown_processor)

    try:
        # Read JSON file
        with source_file.open("r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Run import
        result = await importer.import_data(json_data, destination_folder)

        if not result.success:
            return f"# Error\n\nImport failed: {result.error_message}"

        # Generate summary
        summary_lines = [
            "# ✅ Google Gemini Import Complete",
            "",
            f"**Imported**: {result.conversations} conversations",
            f"**Messages**: {result.messages} total messages",
            f"**From**: {source_path}",
            f"**To**: {destination_folder}",
            "",
            "## 📝 Next Steps",
            "",
            "**Sync to index new files**:",
            "  Run sync to add imported conversations to search index",
            "",
            "**Search imported conversations**:",
            f'  adn_search("notes", query="your search", folder="{destination_folder}")',
            "",
            f"**Total conversations in Advanced Memory**: {result.conversations}",
        ]

        return "\n".join(summary_lines)

    except json.JSONDecodeError as e:
        return f"# Error\n\nInvalid JSON file: {source_path}\n\nError: {e}\n\n**Expected format**: Array of conversation objects or object with 'conversations' array. Each conversation should have 'title'/'name', 'messages' array, and timestamp fields"
    except Exception as e:
        logger.exception("Gemini import failed")
        return f"# Error\n\nImport failed: {e}"
