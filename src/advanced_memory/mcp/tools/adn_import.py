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

    PORTMANTEAU PATTERN: Consolidates 10 import operations into one tool.

    SUPPORTED OPERATIONS:
    - obsidian: Import complete Obsidian vaults
    - joplin: Import Joplin knowledge bases
    - notion: Import Notion workspaces
    - evernote: Import Evernote ENEX files
    - onenote: Import OneNote pages from HTML content (from office-365-mcp or other sources)
    - archive: Import complete system archive
    - canvas: Import Obsidian Canvas files
    - claude_skills: Import Claude Skills (Anthropic agent skills)
    - claude_conversations: Import Claude.ai conversation exports (JSON file)
    - claude_projects: Import Claude.ai project exports (JSON file)
    - chatgpt: Import ChatGPT conversation exports (JSON file)
    - gemini: Import Google Gemini conversation exports (JSON file)

    Args:
        operation: The import operation to perform (obsidian, joplin, notion, evernote, onenote, archive, canvas, claude_skills, claude_conversations, claude_projects, chatgpt, gemini)
        source_path: Path to source files
                    * All operations: REQUIRED - Path to source directory/file
                    * obsidian: Path to Obsidian vault directory
                    * joplin: Path to Joplin export directory
                    * notion: Path to Notion export ZIP file or directory
                    * evernote: Path to Evernote .enex file or directory
                    * onenote: Path to OneNote HTML JSON file
                    * archive: Path to Advanced Memory archive ZIP file
                    * canvas: Path to Obsidian Canvas .canvas file
                    * claude_skills: Path to Claude Skills directory (containing SKILL.md files)
                    * claude_conversations: Path to Claude.ai conversations.json export file
                    * claude_projects: Path to Claude.ai projects.json export file
                    * chatgpt: Path to ChatGPT conversations.json export file
                    * gemini: Path to Google Gemini conversations.json export file
        destination_folder: Advanced Memory folder for imported content
                    * obsidian, joplin, notion, evernote, onenote, canvas, claude_skills, claude_conversations, claude_projects, chatgpt, gemini: Optional - Defaults to "imported/{operation}"
                    * archive operation: NOT USED (archive restores to original locations)
        preserve_structure: Maintain original folder hierarchy
                    * obsidian, joplin, notion, evernote, claude_skills: Optional - If True, preserves folder structure (default: True)
                    * claude_conversations, claude_projects, chatgpt, gemini: NOT USED (flat structure)
                    * onenote, canvas, archive: NOT USED
        convert_links: Convert internal links to entity references
                    * obsidian, joplin: Optional - If True, converts [[wikilinks]] to entity references (default: True)
                    * Other operations: NOT USED
        include_attachments: Import images and media files
                    * obsidian, evernote: Optional - If True, imports images and attachments (default: True)
                    * Other operations: NOT USED
        skip_existing: Skip notes that already exist
                    * obsidian, joplin: Optional - If True, skips notes that already exist (default: True)
                    * Other operations: NOT USED
        create_missing_files: Create placeholder notes for missing references
                    * canvas operation: Optional - If True, creates placeholder notes for missing file references (default: False)
                    * Other operations: NOT USED
        restore_mode: Archive restore mode
                    * archive operation: Optional - "overwrite" (replace existing) or "merge" (combine with existing) (default: "overwrite")
                    * Other operations: NOT USED
        backup_existing: Backup current data before restore
                    * archive operation: Optional - If True, creates backup before restoring (default: True)
                    * Other operations: NOT USED
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

        # Import OneNote pages from HTML (from office-365-mcp)
        adn_import("onenote", source_path="onenote-pages.json", destination_folder="imported/onenote")

        # Import from archive (auto-detects project structure)
        adn_import("archive", source_path="backup.zip", restore_mode="merge")

        # Import Claude conversations (requires exported JSON file)
        adn_import("claude_conversations", source_path="conversations.json", destination_folder="imported/claude")

        # Import Claude projects (requires exported JSON file)
        adn_import("claude_projects", source_path="projects.json", destination_folder="imported/claude-projects")

        # Import ChatGPT conversations (requires exported JSON file)
        adn_import("chatgpt", source_path="chatgpt_conversations.json", destination_folder="imported/chatgpt")

        # Import Google Gemini conversations (requires exported JSON file)
        adn_import("gemini", source_path="gemini_conversations.json", destination_folder="imported/gemini")

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
    from advanced_memory.importers.claude_projects_importer import ClaudeProjectsImporter
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
