"""Content Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all content operations: write, read, view, edit, edit_tags, move, and delete.
It reduces the number of MCP tools while maintaining full functionality.
"""

import re
from typing import Literal

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get, call_put
from advanced_memory.schemas import EntityResponse
from advanced_memory.schemas.base import Entity
from advanced_memory.schemas.memory import GraphContext
from advanced_memory.utils import parse_tags, validate_project_path

# Define TagType as a Union that can accept either a string or a list of strings or None
TagType = list[str] | str | None


@mcp.tool
async def adn_content(
    operation: Literal[
        "write",
        "read",
        "read_latest",
        "view",
        "view_rendered",
        "edit",
        "edit_tags",
        "quick",
        "daily",
        "move",
        "delete",
    ],
    identifier: str | None = None,
    content: str | None = None,
    folder: str | None = None,
    tags: TagType | None = None,
    entity_type: str = "note",
    destination_path: str | None = None,
    edit_operation: Literal[
        "append",
        "prepend",
        "find_replace",
        "replace_section",
        "insert_mermaid",
        "insert_ascii_art",
        "insert_kilroy",
        "insert_kanban",
        "insert_changelog",
    ]
    | None = None,
    tag_operation: Literal["add", "remove", "replace", "clear"] | None = None,
    find_text: str | None = None,
    expected_replacements: int = 1,
    use_regex: bool = False,
    section: str | None = None,
    page: int = 1,
    page_size: int = 10,
    results_per_page: int | None = None,  # Alias for page_size (compatibility with standalone search_notes)
    project: str | None = None,
) -> str:
    """Comprehensive content management tool for Advanced Memory knowledge base.

    This portmanteau tool consolidates all content operations into a single interface,
    reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

    WHY PORTMANTEAU TOOLS?
    Claude Desktop has a limit on the number of available tools. Portmanteau tools like adn_content
    combine multiple related operations (write, read, edit, delete, etc.) into a single tool interface,
    dramatically reducing the tool count while maintaining full functionality.

    PARAMETER DESIGN:
    The 'identifier' parameter is intentionally flexible:
    - For write operations: Pass the note title (e.g., "My Meeting Notes")
      Advanced Memory will automatically generate the permalink from the title.
    - For read/view operations: Can pass title, permalink, or memory:// URL
      This flexibility allows reading notes in multiple ways.

    TIP FOR CLAUDE:
    When using this tool, always specify the operation first (write, read, edit, etc.),
    then provide the required parameters. The documentation below shows what each operation needs.

    SUPPORTED OPERATIONS:
    - write: Create new notes or update existing ones with semantic processing
    - read: Retrieve complete note content with intelligent lookup strategies
    - view: Display notes as formatted artifacts for better readability
    - view_rendered: Display notes as HTML artifacts with rendered Mermaid diagrams
    - edit: Perform targeted edits (append, prepend, find_replace, replace_section)
    - edit_tags: Edit tags (add, remove, replace, clear) without full note edits
    - quick: Ultra-fast note creation with smart defaults (auto-folder, auto-title)
    - daily: Create or append to today's daily journal note
    - move: Relocate notes while preserving relationships and updating references
    - delete: Remove notes from knowledge base with relationship cleanup

    NOTE: Audio operations (dictate, speak) moved to adn_audio tool

    SKILL SUPPORT (AUTO-DETECTION):
    When writing to skills/ folder, adn_content automatically:
    - Detects missing Claude Skills frontmatter
    - Auto-generates YAML frontmatter with name, description, metadata
    - Extracts category from folder path (skills/developer -> category: developer)
    - Sets entity_type to 'skill' automatically
    - Validates frontmatter format against Anthropic spec

    This means you can write skills like regular notes, and frontmatter is added automatically!

    Example skill creation:
        adn_content("write",
            identifier="Python Expert",
            content="# Python Expert\\n\\nAdvanced Python guidance...",
            folder="skills/developer")
        # Auto-generates frontmatter with name: python-expert

    CONTENT PROCESSING:
    - Automatic entity recognition and linking ([[Entity Name]] syntax)
    - Relationship extraction and graph building
    - Tag processing and categorization
    - Folder organization and hierarchy
    - Markdown rendering and syntax validation
    - Claude Skills frontmatter generation (when writing to skills/)

    Args:
        operation: Operation type (write, read, view, view_rendered, edit, edit_tags, quick, daily, move, delete)
        identifier: Note identifier - REQUIRED for most operations. What you pass depends on the operation:
                    * Write operations: REQUIRED - The note title as a string (e.g., "My Meeting Notes")
                      Advanced Memory will automatically create the permalink from the title.
                    * Read/View operations: REQUIRED - Can be any of:
                      - Note title (e.g., "My Meeting Notes")
                      - Permalink (e.g., "meetings/my-meeting-notes")
                      - Memory URL (e.g., "memory://meetings/my-meeting-notes")
                    * Edit/Move/Delete/Edit_tags operations: REQUIRED - Can be any of:
                      - Note title (e.g., "My Meeting Notes")
                      - Permalink (e.g., "meetings/my-meeting-notes")
                      - Memory URL (e.g., "memory://meetings/my-meeting-notes")
                    * Quick/Daily operations: NOT USED - These operations don't require identifier
        content: Markdown content
                    * Write operations: REQUIRED - Full note content
                    * Edit operations: REQUIRED - Content to add/replace (depends on edit_operation)
                      - For find_replace: REPLACEMENT text (find_text is what to find)
                      - For append: Content to add at the end of the note
                      - For prepend: Content to add at the beginning of the note
                      - For replace_section: New content to replace the entire section
                      - For insert_mermaid: Diagram type ("flowchart", "sequence", "gantt", "mindmap", "er") OR custom Mermaid code
                      - For insert_kanban: Comma-separated column names (e.g., "To Do,In Progress,Done")
                      - For insert_changelog: Version string (e.g., "1.0.0" or "Unreleased")
                      - For insert_ascii_art: Art type ("cat", "dog", "robot", "heart", "star", "tree")
                      - For insert_kilroy: Optional custom message (or leave empty for default)
                    * Quick/Daily operations: REQUIRED - Content to capture
                    * Other operations: NOT USED
        folder: Target folder path
                    * Write operations: Optional - Destination folder for new note (defaults to "inbox" if not specified)
                    * Move operations: NOT USED - Use destination_path instead
                    * Other operations: NOT USED
        destination_path: New path for move operations
                    * Move operations: REQUIRED - Full destination path
                    * Other operations: NOT USED
        edit_operation: Edit type for edit operations
                    * Edit operations: REQUIRED - One of: "append", "prepend", "find_replace", "replace_section", "insert_mermaid", "insert_ascii_art", "insert_kilroy", "insert_kanban", "insert_changelog"
                    * For insert_mermaid: content can be diagram type ("flowchart", "sequence", "gantt", "mindmap", "er") OR custom Mermaid code
                    * For insert_kanban: content is comma-separated column names (e.g., "To Do,In Progress,Done"), section is optional title
                    * For insert_changelog: content is version (e.g., "1.0.0" or "Unreleased"), section is optional project name
                    * See edit_note tool documentation for comprehensive Mermaid syntax guide
                    * Other operations: NOT USED
        tag_operation: Tag operation for edit_tags
                    * Edit_tags operations: REQUIRED - One of: "add", "remove", "replace", "clear"
                    * Other operations: NOT USED
        tags: Tags for categorization (string, list, or None)
                    * Write operations: Optional - Tags for categorization
                    * Edit_tags operations:
                      - For "add": REQUIRED - Tags to add to existing tags
                      - For "remove": REQUIRED - Tags to remove from existing tags
                      - For "replace": REQUIRED - Tags to replace all existing tags with
                      - For "clear": NOT USED (tags parameter ignored, all tags cleared)
                    * Quick/Daily operations: Optional - Additional tags to include
                    * Other operations: NOT USED
        entity_type: Content type (default: "note")
                    * Write operations: Optional (default: "note")
                    * Other operations: NOT USED
        find_text: Text to find for find_replace operation
                    * Edit with find_replace: REQUIRED - The exact text to search for
                    * Other operations: NOT USED
        expected_replacements: Expected replacement count for find_replace validation (default: 1)
                    * Edit with find_replace: Optional - Validates that exactly this many replacements occurred
                    * Other operations: NOT USED
        use_regex: Enable regex pattern matching for find_replace (default: False)
                    * Edit with find_replace: Optional - When True, find_text is treated as a regex pattern
                      - Content can use backreferences like \\1, \\2 for captured groups
                      - Includes security safeguards (pattern length limits, ReDoS protection)
                    * Other operations: NOT USED
        section: Section header or title for various edit operations
                    * Edit with replace_section: REQUIRED - Section header to replace (e.g., "## Summary")
                    * Edit with insert_mermaid: Optional - Title for the diagram section
                    * Edit with insert_kanban: Optional - Title for the Kanban board section
                    * Edit with insert_changelog: Optional - Project name for the changelog entry
                    * Other operations: NOT USED
        page: Pagination page number (default: 1)
                    * Read/View/View_rendered operations: Optional - Page number for paginated results
                    * Other operations: NOT USED
        page_size: Items per page for paginated content (default: 10)
                    * Read/View/View_rendered operations: Optional - Number of items per page
                    * Other operations: NOT USED
        results_per_page: Alias for page_size (compatibility with standalone search_notes tool)
                    * Read/View/View_rendered operations: Optional - Same as page_size
                    * Other operations: NOT USED
        project: Optional project name. Supports:
            - None (default): uses current active project
            - "project-name": uses specific project
            Note: Multi-project operations not supported for write/edit/delete (safety)

    Returns:
        Operation-specific result with semantic content summary and project context

    Examples:
        # Write a new note - identifier is REQUIRED and must be the note title
        # Advanced Memory will auto-generate the permalink from the title
        adn_content("write", identifier="Project Plan", content="# Project Overview...", folder="projects")

        # Read a note - can use title, permalink, or URL
        adn_content("read", identifier="Project Plan")  # By title
        adn_content("read", identifier="projects/project-plan")  # By permalink
        adn_content("read", identifier="memory://projects/project-plan")  # By URL

        # Edit a note (append content)
        adn_content("edit", identifier="Project Plan", edit_operation="append", content="\\n## Updates...")

        # Edit tags (add tags)
        adn_content("edit_tags", identifier="Meeting Notes", tag_operation="add", tags="urgent, follow-up")

        # Edit tags (remove tags)
        adn_content("edit_tags", identifier="Draft", tag_operation="remove", tags=["draft", "wip"])

        # Edit tags (replace all)
        adn_content("edit_tags", identifier="Project Plan", tag_operation="replace", tags="final, approved")

        # Find and replace text
        adn_content("edit", identifier="My Note", edit_operation="find_replace",
                    find_text="old text", content="new text", expected_replacements=1)

        # Quick capture (ultra-fast note creation)
        adn_content("quick", content="Great insight: use AI for code reviews")

        # Daily journal entry
        adn_content("daily", content="## Meeting Notes\\n\\nDiscussed Q4 roadmap with team")

        # Move a note
        adn_content("move", identifier="Project Plan", destination_path="archive/completed/project-plan.md")

        # Delete a note
        adn_content("delete", identifier="Project Plan")

        # View note with rendered Mermaid diagrams
        adn_content("view_rendered", identifier="System Architecture")
    """
    # Parameter aliasing for compatibility with standalone tools
    # results_per_page → page_size (for compatibility with search_notes tool)
    if results_per_page is not None and page_size == 10:  # Only if default value
        page_size = results_per_page
        logger.debug(f"Using 'results_per_page' alias as page_size: {page_size}")

    logger.info(f"MCP tool call tool=adn_content operation={operation} identifier={identifier}")

    original_operation = operation
    normalized_operation = re.sub(r"(?<!^)(?=[A-Z])", "_", operation)
    normalized_operation = normalized_operation.replace("-", "_").replace(" ", "_").lower()
    alias_map: dict[
        str,
        Literal[
            "write",
            "read",
            "read_latest",
            "view",
            "view_rendered",
            "edit",
            "edit_tags",
            "quick",
            "daily",
            "move",
            "delete",
        ],
    ] = {
        "createnote": "write",
        "newnote": "write",
        "appendnote": "edit",
        "modifytags": "edit_tags",
        "readnote": "read",
        "readlatest": "read_latest",
        "latest": "read_latest",
        "last": "read_latest",
        "lastnote": "read_latest",
        "latestnote": "read_latest",
        "showlatest": "read_latest",
        "viewnote": "view",
        "previewnote": "view",
        "viewlatest": "view",
        "previewlatest": "view",
    }
    # Type-safe operation mapping with fallback to original
    mapped_operation = alias_map.get(normalized_operation)
    if mapped_operation:
        operation = mapped_operation  # type: ignore[assignment]

    # Get the active project
    active_project = get_active_project(project)
    if not active_project:
        return "# Error\n\nNo active project found. Please switch to a project first."

    # Route to appropriate operation handler
    if operation == "write":
        missing = []
        if not identifier:
            missing.append("identifier (note title)")
        if not content:
            missing.append("content")
        if not folder:
            missing.append("folder")
        if missing:
            return f'# Error\n\nWrite operation requires the following parameters:\n- {", ".join(missing)}\n\n**Example:**\n```python\nadn_content("write",\n    identifier="My Note Title",\n    content="# My Note\\n\\nContent here...",\n    folder="notes")\n```'
        # Type narrowing: we've validated these are not None above
        assert identifier is not None
        assert content is not None
        assert folder is not None
        return await _write_operation(active_project, identifier, content, folder, tags, entity_type)

    elif operation == "read":
        latest_aliases = {"", "latest", "last", "__latest__", "latest_note", "last_note"}
        identifier_key = (identifier or "").strip().lower().replace(" ", "_")

        if not identifier or identifier_key in latest_aliases:
            logger.info(
                "adn_content_auto_read_latest",
                original_operation=original_operation,
                identifier=identifier,
            )
            return await _read_latest_operation(active_project)

        return await _read_operation(active_project, identifier, page, page_size)

    elif operation == "read_latest":
        # Get and read the single most recent note (regardless of date)
        return await _read_latest_operation(active_project)

    elif operation == "view":
        latest_aliases = {"", "latest", "last", "__latest__", "latest_note", "last_note"}
        identifier_key = (identifier or "").strip().lower().replace(" ", "_")

        if not identifier or identifier_key in latest_aliases:
            latest_identifier, error_message = await _get_latest_identifier(active_project)
            if not latest_identifier:
                return error_message or "# No Recent Activity\n\nNo notes found to display."
            identifier = latest_identifier

        return await _view_operation(active_project, identifier)

    elif operation == "view_rendered":
        latest_aliases = {"", "latest", "last", "__latest__", "latest_note", "last_note"}
        identifier_key = (identifier or "").strip().lower().replace(" ", "_")

        if not identifier or identifier_key in latest_aliases:
            latest_identifier, error_message = await _get_latest_identifier(active_project)
            if not latest_identifier:
                return error_message or "# No Recent Activity\n\nNo notes found to display."
            identifier = latest_identifier

        return await _view_rendered_operation(active_project, identifier)

    elif operation == "edit":
        if identifier is None:
            return '# Error\n\nEdit operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content("edit",\n    identifier="My Note",\n    edit_operation="append",\n    content="\\n## New Section")\n```'
        if not edit_operation:
            return '# Error\n\nEdit operation requires: edit_operation parameter\n\n**Valid operations:** append, prepend, find_replace, replace_section\n\n**Example:**\n```python\nadn_content("edit",\n    identifier="My Note",\n    edit_operation="append",\n    content="New content")\n```'
        if not content and edit_operation in ["append", "prepend", "replace_section"]:
            return f'# Error\n\nEdit operation \'{edit_operation}\' requires: content parameter\n\n**Example:**\n```python\nadn_content("edit",\n    identifier="My Note",\n    edit_operation="{edit_operation}",\n    content="Content to {edit_operation}")\n```'
        return await _edit_operation(
            active_project,
            identifier,
            edit_operation,
            content,
            section,
            find_text,
            expected_replacements,
            use_regex,
        )

    elif operation == "edit_tags":
        if identifier is None:
            return '# Error\n\nEdit_tags operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content("edit_tags",\n    identifier="My Note",\n    tag_operation="add",\n    tags="tag1, tag2")\n```'
        if not tag_operation:
            return '# Error\n\nEdit_tags operation requires: tag_operation parameter\n\n**Valid operations:** add, remove, replace, clear\n\n**Example:**\n```python\nadn_content("edit_tags",\n    identifier="My Note",\n    tag_operation="add",\n    tags="important")\n```'
        return await _edit_tags_operation(active_project, identifier, tag_operation, tags)

    elif operation == "quick":
        if not content:
            return "# Error\n\nQuick capture requires: content parameter"
        return await _quick_capture_operation(active_project, content, tags)

    elif operation == "daily":
        if not content:
            return "# Error\n\nDaily note operation requires: content parameter"
        return await _daily_note_operation(active_project, content, tags)

    elif operation == "dictate" or operation == "speak":
        return f"""# Audio Operations Moved

The '{operation}' operation has been moved to the adn_audio tool for better separation of concerns.

**New Usage**:
- For dictate: adn_audio("dictate", audio_path="recording.mp3", tags=["voice"])
- For speak: adn_audio("speak", identifier="Note Title", speed=1.5)

**Why the change**:
Audio operations require heavy optional dependencies (Whisper, pyttsx3) and are better
separated from core content operations.

**Install voice dependencies** (if needed):
pip install advanced-memory[voice]
"""

    elif operation == "move":
        if identifier is None or destination_path is None:
            return "# Error\n\nMove operation requires: identifier, destination_path"
        return await _move_operation(active_project, identifier, destination_path)
    elif operation == "delete":
        if identifier is None:
            return "# Error\n\nDelete operation requires: identifier"
        return await _delete_operation(active_project, identifier)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: write, read, view, view_rendered, edit, edit_tags, quick, daily, move, delete\n\nNote: Audio operations (dictate, speak) are now in adn_audio tool"


async def _write_operation(
    active_project, identifier: str, content: str, folder: str, tags: TagType, entity_type: str
) -> str:
    """Handle write operation with auto-skill detection."""
    if not identifier or not content or not folder:
        return "# Error\n\nWrite operation requires: identifier, content, and folder parameters"

    # Validate folder path to prevent path traversal attacks
    project_path = active_project.home
    if folder and not validate_project_path(folder, project_path):
        logger.warning("Attempted path traversal attack blocked", folder=folder, project=active_project.name)
        return f"# Error\n\nFolder path '{folder}' is not allowed - paths must stay within project boundaries"

    # AUTO-DETECT SKILLS: If writing to skills/ folder, ensure proper frontmatter
    from advanced_memory.mcp.tools.skill_helpers import (
        detect_skill_path,
        generate_skill_frontmatter,
        parse_skill_frontmatter,
        title_to_skill_name,
    )

    if detect_skill_path(folder):
        logger.info(f"Detected skills folder: {folder}. Auto-generating skill frontmatter if needed.")

        # Check if content already has frontmatter
        fm, body, errors = parse_skill_frontmatter(content)

        if fm is None:
            # No frontmatter found - auto-generate it
            logger.info("No frontmatter detected. Auto-generating Claude Skills frontmatter.")

            # Extract metadata from tags if present
            tag_list = parse_tags(tags) if tags else []
            category = None
            difficulty = None

            # Try to extract category from folder path (skills/developer -> developer)
            if "/" in folder:
                parts = folder.split("/")
                if len(parts) >= 2:
                    category = parts[1]

            # Generate skill name from title
            skill_name = title_to_skill_name(identifier)

            # Create description (use first paragraph from body if available)
            description = (
                f"Expert guidance for {identifier}. Use when working with {identifier.lower()} or related topics."
            )

            # Generate frontmatter
            try:
                frontmatter_yaml = generate_skill_frontmatter(
                    name=skill_name,
                    description=description,
                    category=category,
                    difficulty=difficulty,
                )

                # Prepend frontmatter to content
                content = frontmatter_yaml + "\n" + content

                logger.info(f"Auto-generated skill frontmatter for '{skill_name}'")

            except Exception as e:
                logger.warning(f"Failed to auto-generate skill frontmatter: {e}")
                # Continue without frontmatter - will be caught by validation later

        # Ensure entity_type is 'skill' when writing to skills/ folder
        if entity_type == "note":
            entity_type = "skill"
            logger.info("Changed entity_type from 'note' to 'skill' for skills folder")

    # Process tags using the helper function
    tag_list = parse_tags(tags)

    # Create the entity request
    metadata = {"tags": tag_list} if tag_list else None
    entity = Entity(
        title=identifier,
        folder=folder,
        entity_type=entity_type,
        content_type="text/markdown",
        content=content,
        entity_metadata=metadata,
    )
    project_url = active_project.project_url

    # Create or update via knowledge API
    logger.debug(f"Creating entity via API permalink={entity.permalink}")
    url = f"{project_url}/knowledge/entities/{entity.permalink}"
    response = await call_put(client, url, json=entity.model_dump())
    result = EntityResponse.model_validate(response.json())

    # Format semantic summary based on status code
    action = "Created" if response.status_code == 201 else "Updated"
    summary = [
        f"# {action} note",
        f"project: {active_project.name}",
        f"file_path: {result.file_path}",
        f"permalink: {result.permalink}",
        f"checksum: {result.checksum[:8] if result.checksum else 'unknown'}",
    ]

    # Count observations by category
    categories: dict[str, int] = {}
    if result.observations:
        for obs in result.observations:
            if obs.category:  # Only count observations with categories
                categories[obs.category] = categories.get(obs.category, 0) + 1

        summary.append("\n## Observations")
        for category, count in sorted(categories.items()):
            summary.append(f"- {category}: {count}")

    # Count resolved/unresolved relations
    unresolved = 0
    resolved = 0
    if result.relations:
        unresolved = sum(1 for r in result.relations if not r.to_id)
        resolved = len(result.relations) - unresolved

        summary.append("\n## Relations")
        summary.append(f"- Resolved: {resolved}")
        if unresolved:
            summary.append(f"- Unresolved: {unresolved}")
            summary.append("\nNote: Unresolved relations point to entities that don't exist yet.")
            summary.append(
                "They will be automatically resolved when target entities are created or during sync operations."
            )

    if tag_list:
        summary.append(f"\n## Tags\n- {', '.join(tag_list)}")

    logger.info(
        f"MCP tool response: tool=content_manager operation=write action={action} permalink={result.permalink} observations_count={len(result.observations)} relations_count={len(result.relations)} resolved_relations={resolved} unresolved_relations={unresolved} status_code={response.status_code}"
    )
    return "\n".join(summary)


async def _read_operation(active_project, identifier: str, page: int, page_size: int) -> str:
    """Handle read operation."""
    if not identifier:
        return "# Error\n\nRead operation requires identifier parameter"

    # Delegate to read_note tool
    from advanced_memory.mcp.tools.read_note import read_note

    return await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=identifier, page=page, page_size=page_size, project=active_project.name
    )


async def _get_latest_identifier(active_project) -> tuple[str | None, str | None]:
    from loguru import logger

    try:
        from advanced_memory.mcp.tools.recent_activity import recent_activity

        raw_context = await (recent_activity.fn if hasattr(recent_activity, "fn") else recent_activity)(
            type_filter=["entity", "observation"],
            depth=1,
            timeframe="365d",
            page=1,
            page_size=1,
            max_related=0,
            project=active_project.name,
        )

        if isinstance(raw_context, GraphContext):
            result = raw_context
        else:
            result = GraphContext.model_validate(raw_context)

    except Exception as exc:  # pragma: no cover
        logger.error("adn_content_latest_identifier_error", exc_info=True)
        return None, (f"# Error\n\nUnable to load recent activity to determine the latest note.\nDetails: {exc}")

    context_results = getattr(result, "results", [])
    if not context_results:
        return None, "# No Recent Activity\n\nNo notes found in the past year."

    ctx_result = context_results[0]
    if getattr(ctx_result, "primary_result", None):
        item = ctx_result.primary_result
    elif getattr(ctx_result, "observations", None):
        item = ctx_result.observations[0]
    else:
        item = ctx_result

    identifier = getattr(item, "permalink", None) or getattr(item, "file_path", None)
    if not identifier:
        return None, (f"# Error\n\nCould not determine identifier for most recent note.\nItem attributes: {dir(item)}")

    logger.debug(f"Extracted latest identifier: {identifier}")
    return identifier, None


async def _read_latest_operation(active_project) -> str:
    """Handle read_latest operation - read the single most recent note."""
    identifier, error_message = await _get_latest_identifier(active_project)
    if not identifier:
        return error_message or "# No Recent Activity\n\nNo notes found in the past year."

    from advanced_memory.mcp.tools.read_note import read_note

    return await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=identifier, project=active_project.name
    )


async def _view_operation(active_project, identifier: str) -> str:
    """Handle view operation."""
    from advanced_memory.mcp.tools.view_note import view_note

    return await (view_note.fn if hasattr(view_note, "fn") else view_note)(
        identifier=identifier, project=active_project.name
    )


async def _view_rendered_operation(active_project, identifier: str) -> str:
    """Handle view_rendered operation."""
    from advanced_memory.mcp.tools.view_note_rendered import view_note_rendered

    return await (view_note_rendered.fn if hasattr(view_note_rendered, "fn") else view_note_rendered)(
        identifier=identifier, project=active_project.name
    )


async def _edit_operation(
    active_project,
    identifier: str,
    edit_operation: str | None,
    content: str | None,
    section: str | None,
    find_text: str | None,
    expected_replacements: int,
    use_regex: bool,
) -> str:
    """Handle edit operation."""
    from advanced_memory.mcp.tools.edit_note import edit_note

    return await (edit_note.fn if hasattr(edit_note, "fn") else edit_note)(
        identifier=identifier,
        operation=edit_operation or "replace",
        content=content or "",
        section=section,
        find_text=find_text,
        expected_replacements=expected_replacements,
        use_regex=use_regex,
        project=active_project.name,
    )


async def _edit_tags_operation(
    active_project,
    identifier: str,
    tag_operation: str | None,
    tags: TagType,
) -> str:
    """Handle edit_tags operation."""
    if not tag_operation:
        return "# Error\n\nEdit tags operation requires tag_operation parameter (add, remove, replace, clear)"

    # Get current note to read existing tags
    project_url = active_project.project_url
    url = f"{project_url}/knowledge/entities/{identifier}"

    response = await call_get(client, url)
    if response.status_code == 404:
        return f"# Error\n\nNote not found: {identifier}\n\nPlease provide exact note title or permalink."

    current_entity = EntityResponse.model_validate(response.json())

    # Normalize current tags to a list[str]
    existing_tags_raw = current_entity.entity_metadata.get("tags", []) if current_entity.entity_metadata else []
    if isinstance(existing_tags_raw, str):
        # Try to parse string representation of list (e.g., "['tag1', 'tag2']")
        import ast

        try:
            parsed = ast.literal_eval(existing_tags_raw)
            if isinstance(parsed, list):
                current_tags = [str(tag) for tag in parsed]
            else:
                current_tags = [existing_tags_raw]
        except (ValueError, SyntaxError):
            # Not a list representation, treat as single tag
            current_tags = [existing_tags_raw]
    elif isinstance(existing_tags_raw, list):
        current_tags = [str(tag) for tag in existing_tags_raw]
    else:
        current_tags = []

    # Parse input tags (unless clear operation)
    if tag_operation != "clear":
        if tags is None and tag_operation != "clear":
            return f"# Error\n\n'{tag_operation}' operation requires tags parameter.\n\nProvide tags as string or list."

        new_tags = parse_tags(tags)

        if not new_tags and tag_operation != "clear":
            return f"# Error\n\nNo valid tags provided.\n\nTags: {tags}"
    else:
        new_tags = []

    # Perform the operation
    if tag_operation == "add":
        # Add tags (preserve existing, no duplicates)
        updated_tags = list(set(current_tags + new_tags))
        added_tags = [tag for tag in new_tags if tag not in current_tags]
        operation_summary = (
            f"Added {len(added_tags)} tag(s): {', '.join(added_tags)}"
            if added_tags
            else "No new tags added (all tags already exist)"
        )

    elif tag_operation == "remove":
        # Remove specific tags
        updated_tags = [tag for tag in current_tags if tag not in new_tags]
        removed_tags = [tag for tag in new_tags if tag in current_tags]
        operation_summary = (
            f"Removed {len(removed_tags)} tag(s): {', '.join(removed_tags)}"
            if removed_tags
            else "No tags removed (specified tags not found)"
        )

    elif tag_operation == "replace":
        # Replace all tags
        updated_tags = new_tags
        operation_summary = f"Replaced all tags with {len(new_tags)} new tag(s)"

    elif tag_operation == "clear":
        # Clear all tags
        updated_tags = []
        operation_summary = f"Cleared all {len(current_tags)} tag(s)"

    else:
        return f"# Error\n\nInvalid tag_operation: {tag_operation}\n\nSupported: add, remove, replace, clear"

    # Update the entity with new tags
    metadata = current_entity.entity_metadata or {}
    metadata["tags"] = updated_tags

    # Fetch the existing note content so we don't overwrite it with None
    resource_url = f"{project_url}/resource/{current_entity.permalink}"
    resource_response = await call_get(client, resource_url)
    if resource_response.status_code != 200:
        return (
            "# Error\n\n"
            f"Failed to retrieve current note content for '{identifier}'.\n"
            "Tag update aborted to avoid overwriting content.\n"
            f"Details: HTTP {resource_response.status_code}"
        )

    current_content = resource_response.text

    # Validate permalink exists
    if not current_entity.permalink:
        return (
            "# Error\n\n"
            f"Entity '{identifier}' has no permalink.\n"
            "Cannot update tags without a valid permalink.\n"
            "This may indicate a corrupted entity in the database."
        )

    # Extract folder from permalink (everything except the last part)
    permalink_parts = current_entity.permalink.split("/")
    folder = "/".join(permalink_parts[:-1]) if len(permalink_parts) > 1 else ""

    update_url = f"{project_url}/knowledge/entities/{current_entity.permalink}"
    update_data = {
        "title": current_entity.title,
        "entity_type": current_entity.entity_type,
        "content_type": current_entity.content_type,
        "content": current_content,
        "folder": folder,
        "entity_metadata": metadata,
    }

    update_response = await call_put(client, update_url, json=update_data)
    result = EntityResponse.model_validate(update_response.json())

    # Format response
    response_lines = [
        "# Tag Edit Complete",
        "",
        f"**Project:** {active_project.name}",
        f"**Note:** {result.title}",
        f"**Permalink:** {result.permalink}",
        "",
        "## Operation",
        f"**Action:** {tag_operation}",
        f"**Summary:** {operation_summary}",
        "",
        "## Tags",
        f"**Before:** {', '.join(current_tags) if current_tags else '(no tags)'}",
        f"**After:** {', '.join(updated_tags) if updated_tags else '(no tags)'}",
        f"**Total tags:** {len(updated_tags)}",
    ]

    logger.info(
        f"MCP tool response: tool=adn_content operation=edit_tags tag_operation={tag_operation} identifier={identifier} tags_before={len(current_tags)} tags_after={len(updated_tags)}"
    )

    return "\n".join(response_lines)


async def _move_operation(active_project, identifier: str, destination_path: str) -> str:
    """Handle move operation."""
    from advanced_memory.mcp.tools.move_note import move_note

    return await (move_note.fn if hasattr(move_note, "fn") else move_note)(
        identifier=identifier, destination_path=destination_path, project=active_project.name
    )


async def _quick_capture_operation(active_project, content: str, tags: TagType) -> str:
    """Handle quick capture operation - ultra-fast note creation with smart defaults."""
    from datetime import datetime

    # Generate smart title from content (first line or timestamp)
    content_lines = content.strip().split("\n")
    first_line = content_lines[0].strip()

    # If first line is a heading, use it as title
    if first_line.startswith("#"):
        title = first_line.lstrip("#").strip()
        # Remove the heading from content since we're using it as title
        content = "\n".join(content_lines[1:]).strip()
    else:
        # Use first few words as title
        words = first_line.split()[:6]
        title = " ".join(words)
        if len(first_line.split()) > 6:
            title += "..."

    # Auto-select folder (inbox or quick-notes)
    folder = "inbox"

    # Auto-add capture tag
    tag_list = parse_tags(tags) if tags else []
    tag_list.append("quick-capture")
    tag_list.append(datetime.now().strftime("%Y-%m-%d"))

    # Add timestamp to content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    formatted_content = f"# {title}\n\n**Captured:** {timestamp}\n\n{content}"

    # Create the note
    return await _write_operation(active_project, title, formatted_content, folder, tag_list, "note")


async def _daily_note_operation(active_project, content: str, tags: TagType) -> str:
    """Handle daily note operation - create or append to today's journal."""
    from datetime import datetime

    from advanced_memory.mcp.tools.edit_note import edit_note

    # Generate today's date-based title and folder
    today = datetime.now()
    title = today.strftime("%Y-%m-%d")
    folder = "journal"

    # Auto-add daily tag
    tag_list = parse_tags(tags) if tags else []
    tag_list.extend(["daily", "journal", today.strftime("%Y"), today.strftime("%Y-%m")])

    # Try to read existing daily note
    from advanced_memory.mcp.tools.read_note import read_note

    existing_note = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=f"{folder}/{title}", page=1, page_size=1000, project=active_project.name
    )

    # Check if note exists (not an error message)
    if "# Note Not Found:" in existing_note:
        # Create new daily note
        timestamp = today.strftime("%H:%M")
        formatted_content = f"""# Daily Note: {title}

## {timestamp}

{content}

---

"""
        return await _write_operation(active_project, title, formatted_content, folder, tag_list, "note")
    else:
        # Append to existing daily note
        timestamp = today.strftime("%H:%M")
        append_content = f"""

## {timestamp}

{content}

---
"""
        return await (edit_note.fn if hasattr(edit_note, "fn") else edit_note)(
            identifier=f"{folder}/{title}",
            operation="append",
            content=append_content,
            project=active_project.name,
        )


async def _delete_operation(active_project, identifier: str) -> str:
    """Handle delete operation."""
    from advanced_memory.mcp.tools.delete_note import delete_note

    result = await (delete_note.fn if hasattr(delete_note, "fn") else delete_note)(
        identifier=identifier, project=active_project.name
    )

    # delete_note returns bool | str, convert to string for consistency
    if isinstance(result, bool):
        if result:
            return f"# Delete Complete\n\n**Note deleted:** {identifier}\n\nSuccessfully removed from project '{active_project.name}'."
        else:
            return f"# Delete Failed\n\n**Note not deleted:** {identifier}\n\nThe delete operation completed but the note was not removed."
    else:
        # Already a formatted error string
        return result
