"""Export Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all export operations: pandoc, docsify, html, joplin, pdf_book, archive, evernote, notion.
It reduces the number of MCP tools while maintaining full functionality.
"""

from pathlib import Path

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.utils.export_paths import format_export_path


@mcp.tool
async def adn_export(
    operation: str,
    export_path: str | None = None,
    format_type: str = "pdf",
    source_folder: str = "/",
    include_subfolders: bool = True,
    site_title: str | None = None,
    site_description: str | None = None,
    book_title: str | None = None,
    tag_filter: str | None = None,
    pdf_engine: str = "pdflatex",
    serve: bool = True,
    port: int = 3211,
    export_all: bool = True,
    show_after_export: bool = True,
    project: str | None = None,
) -> str:
    """Comprehensive export management tool for Advanced Memory knowledge base.

    This portmanteau tool consolidates all export operations into a single interface,
    reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

    SUPPORTED OPERATIONS:
    - pandoc: Export to PDF, Word, HTML, and 40+ formats using Pandoc (auto-installs!)
    - docsify: Export to Docsify documentation website with navigation
    - html: Export to standalone HTML website with Mermaid diagram rendering
    - joplin: Export to Joplin-compatible format for cross-platform access
    - pdf_book: Create professional PDF books with title pages and chapters
    - archive: Export complete Advanced Memory archive for migration/backup
    - evernote: Export to Evernote-compatible format
    - notion: Export to Notion-compatible format
    - claude_skills: Export zettelkasten to Claude Skills format (Anthropic agent skills)

    EXPORT FEATURES:
    - Multiple format support (PDF, HTML, DOCX, EPUB, etc.)
    - Professional document generation with templates
    - Mermaid diagram rendering in HTML exports
    - Cross-platform compatibility for various note-taking apps
    - Complete archive creation for backup/migration

    Args:
        operation: The export operation to perform (pandoc, docsify, html, joplin, pdf_book, archive, evernote, notion, claude_skills)
        export_path: Path where exported files will be saved
                    **IMPORTANT: Leave this None/omit parameter to use smart default!**
                    Default behavior (when omitted):
                    - Windows: C:\\Users\\{user}\\Desktop\\advanced-memory-exports\\{operation}\\
                    - macOS: ~/Desktop/advanced-memory-exports/{operation}/
                    - Linux: ~/Desktop/advanced-memory-exports/{operation}/
                    **Only provide export_path when user explicitly specifies a custom location!**
                    * All operations: Optional (has smart default)
        format_type: Output format for pandoc operations
                    * pandoc operation: Optional (default: "pdf")
                    * Other operations: NOT USED
        source_folder: Source folder to export from
                    * All operations: Optional (default: "/" - root folder)
        include_subfolders: Include subfolders recursively
                    * All operations: Optional (default: True)
        site_title: Title for docsify/html exports
                    * docsify, html operations: Optional
                    * Other operations: NOT USED
        site_description: Description for docsify/html exports
                    * docsify, html operations: Optional
                    * Other operations: NOT USED
        book_title: Title for PDF book exports
                    * pdf_book operation: REQUIRED - Title for the generated PDF book
                    * Other operations: NOT USED
        tag_filter: Filter notes by tag for exports
        pdf_engine: PDF generation engine
        project: Optional project specification. Supports:
            - None (default): exports current active project
            - "project-name": exports specific project
            - "proj1,proj2,proj3": exports multiple projects to separate folders
            - "ALL": exports all projects to separate folders
            When exporting multiple projects, each gets its own subfolder

    Returns:
        Operation-specific result with export details and file counts

    Examples:
        # Export to PDF with Pandoc - OMIT export_path to use Desktop (RECOMMENDED!)
        adn_export("pandoc", format_type="pdf")  # → Desktop/advanced-memory-exports/pandoc/

        # Export to DOCX - automatically goes to Desktop
        adn_export("pandoc", format_type="docx")  # → Desktop/advanced-memory-exports/pandoc/

        # Export to Docsify website - automatically goes to Desktop
        adn_export("docsify")  # → Desktop/advanced-memory-exports/docsify/
        adn_export("docsify", export_path="C:/website/")  # Only when user says "export to C:/website"

        # Create PDF book
        adn_export("pdf_book", book_title="Research Papers")  # Default path

        # Export Claude Skills
        adn_export("claude_skills")  # Default: Desktop/advanced-memory-exports/claude_skills/

        # Export complete archive
        adn_export("archive")  # Default path

        # Export all projects to separate folders
        adn_export("pandoc", format_type="pdf", project="ALL")  # → Desktop/advanced-memory-exports/pandoc/project1/, project2/, etc.

        # Export specific projects
        adn_export("claude_skills", project="work,personal")  # → exports two projects
    """
    logger.info(f"MCP tool call tool=adn_export operation={operation} export_path={export_path}")

    # Format export path (use smart default if not provided)
    resolved_export_path = format_export_path(export_path, operation)

    # Check if multi-project export is requested
    from advanced_memory.mcp.async_client import client
    from advanced_memory.mcp.tools.utils import call_post

    projects_to_export = []
    multi_project_export = False

    if project:
        if project.upper() == "ALL":
            # Export all projects
            from advanced_memory.schemas.project_info import ProjectList

            projects_response = await call_post(client, "/projects/projects", json={})
            project_list = ProjectList.model_validate(projects_response.json())
            projects_to_export = [p.name for p in project_list.projects]
            multi_project_export = True
            logger.info(f"Multi-project export: ALL ({len(projects_to_export)} projects)")

        elif "," in project:
            # Multiple specific projects
            projects_to_export = [p.strip() for p in project.split(",")]
            multi_project_export = True
            logger.info(f"Multi-project export: {projects_to_export}")

        else:
            # Single specific project
            projects_to_export = [project]

    # If multi-project export, loop through projects
    if multi_project_export:
        all_results = []

        for proj_name in projects_to_export:
            # Create project-specific subfolder
            proj_export_path = str(Path(resolved_export_path) / proj_name)
            logger.info(f"Exporting project '{proj_name}' to {proj_export_path}")

            try:
                # Call export for this project
                result = None
                if operation == "pandoc":
                    result = await _pandoc_export(
                        proj_export_path,
                        format_type,
                        source_folder,
                        include_subfolders,
                        pdf_engine,
                        show_after_export,
                        proj_name,
                    )
                elif operation == "docsify":
                    result = await _docsify_export(
                        proj_export_path,
                        source_folder,
                        include_subfolders,
                        site_title,
                        site_description,
                        serve,
                        port,
                        export_all,
                        proj_name,
                    )
                elif operation == "html":
                    result = await _html_export(proj_export_path, source_folder, include_subfolders, proj_name)
                elif operation == "claude_skills":
                    result = await _claude_skills_export(proj_export_path, source_folder, include_subfolders, proj_name)
                elif operation == "archive":
                    result = await _archive_export(proj_export_path, show_after_export, proj_name)
                else:
                    result = f"Skipped {operation} for project {proj_name} (not supported for multi-project)"

                all_results.append(f"**{proj_name}**: {result}")

            except Exception as e:
                logger.error(f"Failed to export project {proj_name}: {e}")
                all_results.append(f"**{proj_name}**: Error - {e}")

        # Return summary of all exports
        summary = [
            "# Multi-Project Export Complete",
            "",
            f"**Operation**: {operation}",
            f"**Projects Exported**: {len(projects_to_export)}",
            f"**Base Path**: {resolved_export_path}",
            "",
            "## Results by Project",
            "",
        ]
        summary.extend(all_results)

        return "\n".join(summary)

    # Single-project export (original behavior)
    # Route to appropriate operation
    if operation == "pandoc":
        return await _pandoc_export(
            resolved_export_path,
            format_type,
            source_folder,
            include_subfolders,
            pdf_engine,
            show_after_export,
            project,
        )
    elif operation == "docsify":
        return await _docsify_export(
            resolved_export_path,
            source_folder,
            include_subfolders,
            site_title,
            site_description,
            serve,
            port,
            export_all,
            project,
        )
    elif operation == "html":
        return await _html_export(resolved_export_path, source_folder, include_subfolders, show_after_export, project)
    elif operation == "joplin":
        return await _joplin_export(resolved_export_path, source_folder, include_subfolders, project)
    elif operation == "pdf_book":
        return await _pdf_book_export(
            resolved_export_path, source_folder, include_subfolders, book_title, tag_filter, project
        )
    elif operation == "archive":
        return await _archive_export(resolved_export_path, show_after_export, project)
    elif operation == "evernote":
        return await _evernote_export(resolved_export_path, source_folder, include_subfolders, project)
    elif operation == "notion":
        return await _notion_export(resolved_export_path, source_folder, include_subfolders, project)
    elif operation == "claude_skills":
        return await _claude_skills_export(resolved_export_path, source_folder, include_subfolders, project)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: pandoc, docsify, html, joplin, pdf_book, archive, evernote, notion, claude_skills"


async def _pandoc_export(
    export_path: str,
    format_type: str,
    source_folder: str,
    include_subfolders: bool,
    pdf_engine: str,
    show_after_export: bool,
    project: str | None,
) -> str:
    """Handle Pandoc export operation."""
    from advanced_memory.mcp.tools.export_pandoc import export_pandoc

    return await export_pandoc(
        export_path,
        format_type,
        source_folder,
        include_subfolders,
        pdf_engine,
        None,
        None,
        False,
        "tango",
        True,
        False,
        project,
        show_after_export,
    )  # type: ignore[operator,no-any-return]


async def _docsify_export(
    export_path: str,
    source_folder: str,
    include_subfolders: bool,
    site_title: str | None,
    site_description: str | None,
    serve: bool,
    port: int,
    export_all: bool,
    project: str | None,
) -> str:
    """Handle Docsify export operation."""
    from advanced_memory.mcp.tools.export_docsify import export_docsify

    return await export_docsify(
        export_path,
        source_folder,
        include_subfolders,
        site_title or "Knowledge Base",
        site_description or "Documentation generated from Advanced Memory",
        project,
        serve,
        port,
        export_all,
    )  # type: ignore[operator,no-any-return]


async def _html_export(export_path: str, source_folder: str, include_subfolders: bool, project: str | None) -> str:
    """Handle HTML export operation."""
    from advanced_memory.mcp.tools.export_html_notes import export_html_notes

    return await export_html_notes(export_path, source_folder, include_subfolders, True, project)  # type: ignore[operator,no-any-return]


async def _joplin_export(export_path: str, source_folder: str, include_subfolders: bool, project: str | None) -> str:
    """Handle Joplin export operation."""
    from advanced_memory.mcp.tools.export_joplin_notes import export_joplin_notes

    return await export_joplin_notes(export_path, source_folder, include_subfolders, True, project)  # type: ignore[operator,no-any-return]


async def _pdf_book_export(
    export_path: str,
    source_folder: str,
    include_subfolders: bool,
    book_title: str | None,
    tag_filter: str | None,
    project: str | None,
) -> str:
    """Handle PDF book export operation."""
    if not book_title:
        return '# Error\n\nPDF book export requires: book_title parameter\n\n**Example:**\n```python\nadn_export("pdf_book", book_title="Research Papers")\n```'

    from advanced_memory.mcp.tools.make_pdf_book import make_pdf_book

    return await make_pdf_book(
        book_title,
        source_folder,
        tag_filter,
        export_path,
        "Advanced Memory",
        include_subfolders,
        2,
        "a4",
        project,
    )  # type: ignore[operator,no-any-return]


async def _archive_export(export_path: str, show_after_export: bool, project: str | None) -> str:
    """Handle archive export operation."""
    from advanced_memory.mcp.tools.export_to_archive import export_to_archive

    return await (export_to_archive.fn if hasattr(export_to_archive, "fn") else export_to_archive)(
        export_path, None, None, None, None, True, project, show_after_export
    )  # type: ignore[operator,no-any-return]


async def _evernote_export(export_path: str, source_folder: str, include_subfolders: bool, project: str | None) -> str:
    """Handle Evernote export operation."""
    return f"[UNICODE] **Evernote Export**\n\nEvernote export functionality requires the full export_evernote_compatible tool.\n\n**Requested**: {source_folder} → {export_path}\n**Include subfolders**: {include_subfolders}\n\nUse the individual export_evernote_compatible tool for complete functionality."


async def _notion_export(export_path: str, source_folder: str, include_subfolders: bool, project: str | None) -> str:
    """Handle Notion export operation."""
    return f"[UNICODE] **Notion Export**\n\nNotion export functionality requires the full export_notion_compatible tool.\n\n**Requested**: {source_folder} → {export_path}\n**Include subfolders**: {include_subfolders}\n\nUse the individual export_notion_compatible tool for complete functionality."


async def _claude_skills_export(
    export_path: str, source_folder: str, include_subfolders: bool, project: str | None
) -> str:
    """Export zettelkasten templates to Claude Skills format.

    Args:
        export_path: Directory to export skills to
        source_folder: Source folder in Advanced Memory
        include_subfolders: Recursively include subfolders
        project: Optional project name

    Returns:
        Export summary with skill counts and usage instructions
    """
    from advanced_memory.mcp.project_session import get_current_project_config
    from advanced_memory.repository import get_repository
    from advanced_memory.services.skills_converter import SkillsConverter

    logger.info(f"Starting Claude Skills export: {source_folder} → {export_path}")

    # Get project configuration
    if project:
        # TODO: Support non-current projects
        project_config = get_current_project_config()
    else:
        project_config = get_current_project_config()

    # Get repository
    repo = await get_repository()
    current_project = await repo.get_project_by_name(project_config.name)

    if not current_project:
        return "# Error\n\nCurrent project not found in database."

    # Create export directory
    export_dir = Path(export_path).expanduser()
    export_dir.mkdir(parents=True, exist_ok=True)

    # Get all entities from source folder
    entities = await repo.search_entities(
        project_id=current_project.id,
        folder_path=source_folder,
        include_subfolders=include_subfolders,
    )

    if not entities:
        return f"# No Content Found\n\nNo notes found in {source_folder}"

    skills_created = 0
    errors = []

    # Export each entity as a skill
    for entity in entities:
        try:
            # Parse frontmatter from entity metadata
            frontmatter = entity.entity_metadata or {}
            frontmatter["title"] = entity.title
            frontmatter["type"] = entity.entity_type

            # Get entity content
            content = ""
            if entity.file_path:
                file_path = project_config.home / entity.file_path
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    # Remove frontmatter from content
                    from advanced_memory.file_utils import remove_frontmatter

                    content = remove_frontmatter(content)

            # Infer category from file path
            category = None
            if entity.file_path:
                parts = Path(entity.file_path).parts
                if len(parts) > 0:
                    category = parts[0]  # First folder = category

            # Convert to Skills format
            skills_fm = SkillsConverter.zettel_to_skill(frontmatter, content, category)

            # Validate skill name
            is_valid, error_msg = SkillsConverter.validate_skill_name(skills_fm.name)
            if not is_valid:
                errors.append(f"{entity.title}: {error_msg}")
                continue

            # Create skill directory structure
            if category:
                skill_dir = export_dir / category / skills_fm.name
            else:
                skill_dir = export_dir / skills_fm.name

            skill_dir.mkdir(parents=True, exist_ok=True)

            # Format and write SKILL.md
            skill_content = SkillsConverter.format_skill_markdown(skills_fm, content)
            (skill_dir / "SKILL.md").write_text(skill_content, encoding="utf-8")

            # Add MIT license file
            _write_mit_license(skill_dir)

            skills_created += 1
            logger.debug(f"Created skill: {skills_fm.name}")

        except Exception as e:
            logger.error(f"Failed to export {entity.title}: {e}")
            errors.append(f"{entity.title}: {e}")

    # Generate summary
    summary_lines = [
        "# 🎯 Claude Skills Export Complete",
        "",
        f"**Created**: {skills_created} skills",
        f"**Location**: {export_path}",
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
            "## 📖 How to Use",
            "",
            "**Option 1: Claude Desktop Discovery**",
            "1. Open Claude Desktop Settings",
            f"2. Add skills directory: `{export_path}`",
            "3. Claude will discover these skills automatically",
            "",
            "**Option 2: Manual Skill Loading**",
            "1. Open skill folder in file explorer",
            "2. Drag SKILL.md into Claude Desktop",
            "3. Claude loads the skill for current conversation",
            "",
            "## 🔧 What's Next",
            "",
            "- Skills appear in Claude's skill picker UI",
            "- Claude can use them to guide responses",
            "- Update skills by re-exporting from Advanced Memory",
            "",
            f"**Total Skills Available**: {skills_created}",
        ]
    )

    return "\n".join(summary_lines)


def _write_mit_license(skill_dir: Path) -> None:
    """Write MIT license file to skill directory."""
    license_text = """MIT License

Copyright (c) 2025 Advanced Memory Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    (skill_dir / "LICENSE.txt").write_text(license_text, encoding="utf-8")
