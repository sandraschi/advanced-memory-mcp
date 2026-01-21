"""Export Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all export operations: pdf, pandoc, docsify, html, joplin, pdf_book, archive, evernote, notion.
It reduces the number of MCP tools while maintaining full functionality.
"""

from pathlib import Path

from loguru import logger  # pyright: ignore[reportMissingImports]

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response
from advanced_memory.utils.export_paths import format_export_path


@mcp.tool
async def adn_export(
    operation: str,
    export_path: str | None = None,
    format_type: str = "pdf",
    skills_format: str = "anthropic",  # New parameter for skills export format
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
    search_query: str | None = None,
    combine_into_one: bool = False,
    make_toc: bool = True,
) -> dict:
    """Comprehensive export management tool for Advanced Memory knowledge base.

    This point-of-entry tool provides a unified interface for exporting content
    from the Advanced Memory ecosystem to various external formats and services.

    RESPONSES:
    Success: {"success": true, "operation": "...", "summary": "...", "result": {...}}
    Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

    For errors, check recovery_options for next steps.

    ---------------------------------------------------------------------------
    [PORTMANTEAU PATTERN RATIONALE]
    Consolidates 10+ export operations into one tool to prevent tool explosion while maintaining full functionality.

    ---------------------------------------------------------------------------
    [PARAMETER DESIGN]
    The parameters are categorized by export type and requirements:
    - Operation: The specific export task (pdf, pandoc, docsify, html, etc.).
    - Destination (export_path): Where the files go (Defaults to Desktop).
    - Content (source_folder, project, search_query, tag_filter): What to export.
    - Formatting (format_type, book_title, site_title, pdf_engine): How it looks.
    - Behavior (combine_into_one, make_toc, serve, open_after): Functional switches.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]

    Document Formats:
    - pdf: Native PDF with fpdf2 (No LaTeX required).
    - pandoc: Universal converter (DOCX, HTML, EPUB, etc.).
    - pdf_book: Professional book generation with cover/TOC.

    Web Publishing:
    - docsify: Static documentation site generator.
    - html: Standalone HTML with Mermaid support.

    External Systems:
    - joplin: Joplin-compatible Markdown export.
    - evernote: Evernote ENEX compatible export.
    - notion: Notion-compatible Markdown/CSV export.
    - skills: Anthropic agent skills export (format: "anthropic" or "antigravity").

    System & Data:
    - archive: Full system backup.
    - repo: Git repository export (ZIP with .gitignore support).

    ---------------------------------------------------------------------------
    [PREREQUISITES]
    - 'pandoc' must be installed for pandoc operations.
    - 'pathspec' required for repo export.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The export type to perform (Required).
    - export_path (str): Destination path (Optional - Defaults to Desktop).
    - format_type (str): Target format for Pandoc (Default: 'pdf').
    - source_folder (str): Base directory for export (Default: '/').
    - project (str): Project context for filtering (Optional).
    - search_query (str): Filter content by keyword (Optional).
    - tag_filter (str): Filter content by tags (Optional).
    - book_title (str): Title for PDF books (Required for pdf_book).
    - combine_into_one (bool): Merge multiple notes into one file (Default: False).

    ---------------------------------------------------------------------------
    [USAGE]
    Use this tool to publish content, migrate data, or create backups.
    It automatically handles path resolution and format conversion.

    ---------------------------------------------------------------------------
    [EXAMPLES]

    - Export project to PDF:
      adn_export(operation="pdf", project="research", combine_into_one=True)

    - Export to Docsify site:
      adn_export(operation="docsify", site_title="My Knowledge Base")

    - Create a repo archive:
      adn_export(operation="repo", source_folder="/path/to/repo")

    ---------------------------------------------------------------------------
    [ERRORS]
    - Export failed: General failure in the export process.
    - Missing dependency: Required tools (like pandoc) not found.
    - Invalid path: Source or destination path is invalid.
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
                    result = await _html_export(
                        proj_export_path,
                        source_folder,
                        include_subfolders,
                        show_after_export,
                        proj_name,
                    )
                elif operation == "skills":
                    result = await _skills_export(
                        proj_export_path,
                        source_folder,
                        include_subfolders,
                        proj_name,
                        skills_format,
                    )
                elif operation == "archive":
                    result = await _archive_export(proj_export_path, show_after_export, proj_name)
                elif operation == "repo":
                    result = await _repo_export(proj_export_path, source_folder, show_after_export)
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
    if operation == "pdf":
        return await _pdf_export(
            resolved_export_path,
            source_folder,
            include_subfolders,
            project,
            search_query=search_query,
            combine_into_one=combine_into_one,
            book_title=book_title,
            make_toc=make_toc,
        )
    elif operation == "pandoc":
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
        return await _html_export(
            resolved_export_path,
            source_folder,
            include_subfolders,
            show_after_export,
            project,
            search_query=search_query,
            combine_into_one=combine_into_one,
            html_title=site_title,
            make_toc=make_toc,
        )
    elif operation == "joplin":
        return await _joplin_export(
            resolved_export_path, source_folder, include_subfolders, project
        )
    elif operation == "pdf_book":
        return await _pdf_book_export(
            resolved_export_path,
            source_folder,
            include_subfolders,
            book_title,
            tag_filter,
            project,
        )
    elif operation == "archive":
        return await _archive_export(resolved_export_path, show_after_export, project)
    elif operation == "repo":
        return await _repo_export(resolved_export_path, source_folder, show_after_export)
    elif operation == "evernote":
        return await _evernote_export(
            resolved_export_path, source_folder, include_subfolders, project
        )
    elif operation == "notion":
        return await _notion_export(
            resolved_export_path, source_folder, include_subfolders, project
        )
    elif operation == "skills":
        return await _skills_export(
            resolved_export_path, source_folder, include_subfolders, project, skills_format
        )
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: pdf, pandoc, docsify, html, joplin, pdf_book, archive, evernote, notion, skills"


async def _pdf_export(
    export_path: str,
    source_folder: str,
    include_subfolders: bool,
    project: str | None,
    search_query: str | None = None,
    combine_into_one: bool = False,
    book_title: str | None = None,
    make_toc: bool = True,
) -> str:
    """Handle native PDF export using fpdf2 (no LaTeX, no weasyprint!)."""
    from advanced_memory.mcp.tools.export_pdf_native import export_pdf_native

    return await export_pdf_native(
        export_path,
        source_folder,
        include_subfolders,
        project,
        search_query=search_query,
        combine_into_one=combine_into_one,
        pdf_title=book_title,
        make_toc=make_toc,
    )


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
    # Reject PDF format - use native PDF export instead
    if format_type == "pdf":
        return build_error_response(
            error="pandoc_pdf_deprecated",
            error_code="PDF_FORMAT_DEPRECATED",
            message="PDF format in pandoc operation is deprecated - use native PDF export instead",
            recovery_options=[
                "Use operation='pdf' for native PDF export (no LaTeX required)",
                "For other formats with pandoc, use: docx, html, epub, odt, rtf",
                "Native PDF export uses fpdf2 for better performance",
            ],
            alternative_operations=["pdf"],
            supported_pandoc_formats=["docx", "html", "epub", "odt", "rtf"],
            urgency="medium",
        )

    from advanced_memory.mcp.tools.export_pandoc import export_pandoc

    return await export_pandoc.fn(
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

    return await export_docsify.fn(
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


async def _html_export(
    export_path: str,
    source_folder: str,
    include_subfolders: bool,
    show_after_export: bool,
    project: str | None,
    search_query: str | None = None,
    combine_into_one: bool = False,
    html_title: str | None = None,
    make_toc: bool = True,
) -> str:
    """Handle HTML export operation."""
    from advanced_memory.mcp.tools.export_html_notes import export_html_notes

    return await export_html_notes.fn(
        export_path=export_path,
        source_folder=source_folder,
        include_subfolders=include_subfolders,
        include_index=True,
        show_after_export=show_after_export,
        project=project,
        search_query=search_query,
        combine_into_one=combine_into_one,
        html_title=html_title,
        make_toc=make_toc,
    )  # type: ignore[operator,no-any-return]


async def _joplin_export(
    export_path: str, source_folder: str, include_subfolders: bool, project: str | None
) -> str:
    """Handle Joplin export operation."""
    from advanced_memory.mcp.tools.export_joplin_notes import export_joplin_notes

    return await export_joplin_notes.fn(
        export_path, source_folder, include_subfolders, True, project
    )  # type: ignore[operator,no-any-return]


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
        return build_error_response(
            error="missing_book_title",
            error_code="BOOK_TITLE_REQUIRED",
            message="PDF book export requires book_title parameter",
            recovery_options=[
                "Provide book_title parameter with your desired book title",
                "Book title will be used as the PDF filename and title page",
                "Example: book_title='My Research Notes'",
            ],
            example={"operation": "pdf_book", "book_title": "Research Papers"},
            urgency="medium",
        )

    from advanced_memory.mcp.tools.make_pdf_book import make_pdf_book

    return await make_pdf_book.fn(
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

    return await export_to_archive.fn(
        export_path, None, None, None, None, True, project, show_after_export
    )  # type: ignore[operator,no-any-return]


async def _repo_export(export_path: str, repo_path: str | None, show_after_export: bool) -> str:
    """Export repository folder tree as ZIP, respecting .gitignore patterns.

    Args:
        export_path: Path where ZIP archive will be saved
        repo_path: Path to repository root directory (default: current working directory)
        show_after_export: Whether to open file explorer after export

    Returns:
        Export summary with file counts and archive location
    """
    import os
    import zipfile
    from pathlib import Path

    try:
        from pathspec import PathSpec  # pyright: ignore[reportMissingImports]
        from pathspec.patterns import GitWildMatchPattern  # pyright: ignore[reportMissingImports]
    except ImportError:
        return build_error_response(
            error="missing_dependency",
            error_code="PATHSPEC_NOT_INSTALLED",
            message="Repository export requires the pathspec package for .gitignore support",
            recovery_options=[
                "Install pathspec: pip install pathspec>=0.12.0",
                "Install all dependencies: pip install advanced-memory[all]",
                "Use alternative export methods without repository features",
            ],
            required_package="pathspec>=0.12.0",
            urgency="medium",
        )

    # Determine repository root
    if repo_path and repo_path != "/":
        repo_root = Path(repo_path).resolve()
    else:
        repo_root = Path.cwd()

    if not repo_root.exists():
        return f"[UNICODE] **Error: Repository path not found**\n\nPath: {repo_root}"

    if not repo_root.is_dir():
        return f"[UNICODE] **Error: Repository path is not a directory**\n\nPath: {repo_root}"

    logger.info(f"Exporting repository: {repo_root} → {export_path}")

    # Ensure export path is a ZIP file
    export_path_obj = Path(export_path)
    if export_path_obj.suffix.lower() != ".zip":
        export_path_obj = export_path_obj.with_suffix(".zip")

    # Collect all .gitignore files (including nested ones)
    gitignore_files = []
    for gitignore_path in repo_root.rglob(".gitignore"):
        gitignore_files.append(gitignore_path)

    # Build a map of directory -> patterns for nested .gitignore files
    # Root .gitignore patterns apply to entire repo
    # Nested .gitignore patterns apply only to their directory and subdirectories
    ignore_specs = {}  # Maps directory (relative to repo_root) -> PathSpec

    # First, parse root .gitignore (applies to entire repo)
    root_gitignore = repo_root / ".gitignore"
    root_patterns = []
    if root_gitignore.exists():
        try:
            with open(root_gitignore, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        root_patterns.append(line)
        except Exception as e:
            logger.warning(f"Failed to read root .gitignore: {e}")

    if root_patterns:
        ignore_specs[Path(".")] = PathSpec.from_lines(GitWildMatchPattern, root_patterns)
        logger.debug(f"Loaded {len(root_patterns)} patterns from root .gitignore")

    # Then parse nested .gitignore files (patterns apply only within their directory)
    for gitignore_file in gitignore_files:
        if gitignore_file == root_gitignore:
            continue  # Already processed

        # Get directory relative to repo root
        gitignore_dir = gitignore_file.parent.relative_to(repo_root)

        try:
            with open(gitignore_file, encoding="utf-8") as f:
                patterns = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
                if patterns:
                    ignore_specs[gitignore_dir] = PathSpec.from_lines(GitWildMatchPattern, patterns)
                    logger.debug(
                        f"Loaded {len(patterns)} patterns from nested .gitignore at {gitignore_dir}"
                    )
        except Exception as e:
            logger.warning(f"Failed to read .gitignore at {gitignore_file}: {e}")

    # Check if ZIP64 is needed
    needs_zip64 = False
    total_size_check = 0
    files_to_include = []

    # Walk repository and collect files (respecting .gitignore)
    for file_path in repo_root.rglob("*"):
        if not file_path.is_file():
            continue

        # Calculate relative path from repo root
        rel_path = file_path.relative_to(repo_root)
        rel_path_str = str(rel_path).replace("\\", "/")
        rel_path_obj = Path(rel_path_str)

        # Check if file matches any .gitignore pattern
        # Check root patterns first, then check nested patterns for each parent directory
        should_ignore = False

        # Check root .gitignore patterns (apply to entire repo)
        if Path(".") in ignore_specs:
            if ignore_specs[Path(".")].match_file(rel_path_str):
                should_ignore = True
                logger.debug(f"Ignoring (root .gitignore): {rel_path_str}")

        # Check nested .gitignore patterns (check each parent directory up to repo root)
        # Nested .gitignore files only apply to files within their directory tree
        if not should_ignore:
            # Check if file is within any directory that has a nested .gitignore
            for gitignore_dir, spec in ignore_specs.items():
                if gitignore_dir == Path("."):
                    continue  # Already checked root

                # Check if file is within this .gitignore's directory
                try:
                    # Check if rel_path is within gitignore_dir
                    if (
                        rel_path_obj.is_relative_to(gitignore_dir)
                        or gitignore_dir in rel_path_obj.parents
                    ):
                        # Get path relative to the .gitignore directory
                        rel_to_gitignore = rel_path_obj.relative_to(gitignore_dir)
                        rel_to_gitignore_str = str(rel_to_gitignore).replace("\\", "/")
                        if spec.match_file(rel_to_gitignore_str):
                            should_ignore = True
                            logger.debug(
                                f"Ignoring (nested .gitignore in {gitignore_dir}): {rel_path_str}"
                            )
                            break
                except ValueError:
                    # File is not within this directory, skip
                    continue

        if should_ignore:
            continue

        # Check file size for ZIP64 determination
        file_size = file_path.stat().st_size
        total_size_check += file_size
        if file_size > 4 * 1024 * 1024 * 1024:
            needs_zip64 = True

        files_to_include.append((file_path, rel_path_str))

    # Check if total size exceeds ZIP32 limit
    if not needs_zip64 and total_size_check > 4 * 1024 * 1024 * 1024:
        needs_zip64 = True

    if needs_zip64:
        logger.warning(
            f"Archive requires ZIP64 format (total: {total_size_check / (1024**3):.2f} GB). "
            "Windows Explorer may have issues opening this archive."
        )

    # Create ZIP archive
    file_count = 0
    total_size = 0

    export_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Create ZIP file with explicit Windows Explorer compatibility settings
    # Use explicit open/close instead of context manager to ensure proper finalization
    zipf = zipfile.ZipFile(
        export_path_obj,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
        allowZip64=needs_zip64,
    )

    try:
        for file_path, rel_path_str in files_to_include:
            try:
                zipf.write(file_path, rel_path_str)
                file_count += 1
                total_size += file_path.stat().st_size
                logger.debug(f"Added to ZIP: {rel_path_str}")
            except Exception as e:
                logger.warning(f"Failed to add {rel_path_str} to ZIP: {e}")
    finally:
        # Explicitly close and finalize the ZIP file
        # This ensures proper ZIP structure that Windows Explorer expects
        zipf.close()

    # Verify the ZIP file is valid
    try:
        test_zip = zipfile.ZipFile(export_path_obj, "r")
        test_zip.close()
        logger.info(f"ZIP archive created and verified: {export_path_obj} (ZIP64: {needs_zip64})")
    except zipfile.BadZipFile as e:
        logger.error(f"Created ZIP file is invalid: {e}")
        raise

    final_size = export_path_obj.stat().st_size

    # Format results
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    result = f"""[UNICODE][UNICODE] **Repository Export Complete!**

**Archive Details:**
- [FOLDER] Location: {export_path_obj}
- [CHART] Size: {_format_size(final_size)}
- [DOC] Files: {file_count}
- [UNICODE] Repository: {repo_root}
- [UNICODE] .gitignore files parsed: {len(gitignore_files)}
- [UNICODE] ZIP64 format: {needs_zip64}

**Contents:**
- All files from repository root
- Excluded files matching .gitignore patterns
- Windows Explorer compatible (ZIP32) unless ZIP64 required

**To extract:**
Right-click the ZIP file and select "Extract All" (Windows Explorer)
Or use: `unzip {export_path_obj.name}` (Linux/macOS)
"""

    if show_after_export:
        try:
            import platform

            if platform.system() == "Windows":
                os.startfile(export_path_obj.parent)  # type: ignore[attr-defined]
            elif platform.system() == "Darwin":
                os.system(f'open "{export_path_obj.parent}"')
            else:
                os.system(f'xdg-open "{export_path_obj.parent}"')
        except Exception as e:
            logger.warning(f"Failed to open file explorer: {e}")

    return result


async def _evernote_export(
    export_path: str, source_folder: str, include_subfolders: bool, project: str | None
) -> str:
    """Handle Evernote export operation."""
    return f"[UNICODE] **Evernote Export**\n\nEvernote export functionality requires the full export_evernote_compatible tool.\n\n**Requested**: {source_folder} → {export_path}\n**Include subfolders**: {include_subfolders}\n\nUse the individual export_evernote_compatible tool for complete functionality."


async def _notion_export(
    export_path: str, source_folder: str, include_subfolders: bool, project: str | None
) -> str:
    """Handle Notion export operation."""
    return f"[UNICODE] **Notion Export**\n\nNotion export functionality requires the full export_notion_compatible tool.\n\n**Requested**: {source_folder} → {export_path}\n**Include subfolders**: {include_subfolders}\n\nUse the individual export_notion_compatible tool for complete functionality."


async def _skills_export(
    export_path: str,
    source_folder: str,
    include_subfolders: bool,
    project: str | None,
    skills_format: str = "anthropic",
) -> str:
    """Export zettelkasten templates to Claude Skills format.

    Args:
        export_path: Directory to export skills to
        source_folder: Source folder in Advanced Memory
        include_subfolders: Recursively include subfolders
        project: Optional project name
        skills_format: Format for exported skills ("anthropic" or "antigravity")

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
        return build_error_response(
            error="project_not_found",
            error_code="CURRENT_PROJECT_NOT_FOUND",
            message="Current project not found in database",
            recovery_options=[
                "Use adn_project('list') to see available projects",
                "Use adn_project('switch', project_name='...') to switch to a valid project",
                "Create a new project if needed",
            ],
            urgency="high",
        )

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

            # Create skill directory structure based on format
            if skills_format == "antigravity":
                # Antigravity IDE format: category/name/
                if category:
                    skill_dir = export_dir / category / skills_fm.name
                else:
                    skill_dir = export_dir / skills_fm.name
            else:
                # Anthropic format: name/ (flat structure)
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
