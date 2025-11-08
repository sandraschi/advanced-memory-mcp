"""Content Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all content operations: write, read, view, edit, edit_tags, move, and delete.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Literal

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get, call_put
from advanced_memory.schemas import EntityResponse
from advanced_memory.schemas.base import Entity
from advanced_memory.utils import parse_tags, validate_project_path

# Define TagType as a Union that can accept either a string or a list of strings or None
TagType = list[str] | str | None


@mcp.tool
async def adn_content(
    operation: Literal["write", "read", "read_latest", "view", "view_rendered", "edit", "edit_tags", "quick", "daily", "move", "delete"],
    identifier: str | None = None,
    content: str | None = None,
    folder: str | None = None,
    tags: TagType | None = None,
    entity_type: str = "note",
    destination_path: str | None = None,
    edit_operation: Literal["append", "prepend", "find_replace", "replace_section"] | None = None,
    tag_operation: Literal["add", "remove", "replace", "clear"] | None = None,
    find_text: str | None = None,
    expected_replacements: int = 1,
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
                    * Quick/Daily operations: REQUIRED - Content to capture
                    * Other operations: NOT USED
        folder: Target folder path
                    * Write operations: REQUIRED - Destination folder for new note
                    * Move operations: NOT USED - Use destination_path instead
                    * Other operations: NOT USED
        destination_path: New path for move operations
                    * Move operations: REQUIRED - Full destination path
                    * Other operations: NOT USED
        edit_operation: Edit type for edit operations
                    * Edit operations: REQUIRED - One of: "append", "prepend", "find_replace", "replace_section"
                    * Other operations: NOT USED
        tag_operation: Tag operation for edit_tags
                    * Edit_tags operations: REQUIRED - One of: "add", "remove", "replace", "clear"
                    * Other operations: NOT USED
        tags: Tags for categorization (string, list, or None)
                    * Write operations: Optional - Tags for categorization
                    * Edit_tags operations: Optional - Tags to add/remove/replace (depends on tag_operation)
                    * Other operations: NOT USED
        entity_type: Content type (default: "note")
                    * Write operations: Optional (default: "note")
                    * Other operations: NOT USED
        expected_replacements: Expected replacement count for find_replace validation (default: 1)
        section: Section header for replace_section operations
                    * Edit with replace_section: REQUIRED - Section header to replace (e.g., "## Summary")
                    * Other operations: NOT USED
        page: Pagination page for read operations
        page_size: Items per page for paginated content
        results_per_page: Alias for page_size (compatibility with standalone search_notes tool)
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
            return f"# Error\n\nWrite operation requires the following parameters:\n- {', '.join(missing)}\n\n**Example:**\n```python\nadn_content(\"write\",\n    identifier=\"My Note Title\",\n    content=\"# My Note\\n\\nContent here...\",\n    folder=\"notes\")\n```"
        return await _write_operation(
            active_project, identifier, content, folder, tags, entity_type
        )

    elif operation == "read":
        if identifier is None:
            return "# Error\n\nRead operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content(\"read\", identifier=\"My Note Title\")\n# or\nadn_content(\"read\", identifier=\"notes/my-note-title\")\n```"
        return await _read_operation(active_project, identifier, page, page_size)

    elif operation == "read_latest":
        # Get and read the single most recent note (regardless of date)
        return await _read_latest_operation(active_project)

    elif operation == "view":
        if identifier is None:
            return "# Error\n\nView operation requires: identifier"
        return await _view_operation(active_project, identifier)

    elif operation == "view_rendered":
        if identifier is None:
            return "# Error\n\nView rendered operation requires: identifier"
        return await _view_rendered_operation(active_project, identifier)

    elif operation == "edit":
        if identifier is None:
            return "# Error\n\nEdit operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content(\"edit\",\n    identifier=\"My Note\",\n    edit_operation=\"append\",\n    content=\"\\n## New Section\")\n```"
        if not edit_operation:
            return "# Error\n\nEdit operation requires: edit_operation parameter\n\n**Valid operations:** append, prepend, find_replace, replace_section\n\n**Example:**\n```python\nadn_content(\"edit\",\n    identifier=\"My Note\",\n    edit_operation=\"append\",\n    content=\"New content\")\n```"
        if not content and edit_operation in ["append", "prepend", "replace_section"]:
            return f"# Error\n\nEdit operation '{edit_operation}' requires: content parameter\n\n**Example:**\n```python\nadn_content(\"edit\",\n    identifier=\"My Note\",\n    edit_operation=\"{edit_operation}\",\n    content=\"Content to {edit_operation}\")\n```"
        return await _edit_operation(
            active_project,
            identifier,
            edit_operation,
            content,
            section,
            find_text,
            expected_replacements,
        )

    elif operation == "edit_tags":
        if identifier is None:
            return "# Error\n\nEdit_tags operation requires: identifier parameter\n\n**Example:**\n```python\nadn_content(\"edit_tags\",\n    identifier=\"My Note\",\n    tag_operation=\"add\",\n    tags=\"tag1, tag2\")\n```"
        if not tag_operation:
            return "# Error\n\nEdit_tags operation requires: tag_operation parameter\n\n**Valid operations:** add, remove, replace, clear\n\n**Example:**\n```python\nadn_content(\"edit_tags\",\n    identifier=\"My Note\",\n    tag_operation=\"add\",\n    tags=\"important\")\n```"
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
        logger.warning(
            "Attempted path traversal attack blocked", folder=folder, project=active_project.name
        )
        return f"# Error\n\nFolder path '{folder}' is not allowed - paths must stay within project boundaries"

    # AUTO-DETECT SKILLS: If writing to skills/ folder, ensure proper frontmatter
    from advanced_memory.mcp.tools.skill_helpers import (
        detect_skill_path,
        generate_skill_frontmatter,
        parse_skill_frontmatter,
        title_to_skill_name,
    )

    if detect_skill_path(folder):
        logger.info(
            f"Detected skills folder: {folder}. Auto-generating skill frontmatter if needed."
        )

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
            description = f"Expert guidance for {identifier}. Use when working with {identifier.lower()} or related topics."

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

    return await read_note.fn(
        identifier=identifier, page=page, page_size=page_size, project=active_project.name
    )


async def _read_latest_operation(active_project) -> str:
    """Handle read_latest operation - read the single most recent note."""
    from loguru import logger

    from advanced_memory.mcp.tools.recent_activity import recent_activity

    # Get single most recent item (any type, past year)
    result = await recent_activity.fn(
        type="",  # All types
        depth=1,
        timeframe="365d",  # Past year to be safe
        page=1,
        page_size=1,  # Just the most recent one
        max_related=0,
        project=active_project.name
    )

    # Debug: Log the structure
    logger.debug(f"GraphContext structure: hasattr(results)={hasattr(result, 'results')}")
    if hasattr(result, 'results'):
        logger.debug(f"results length={len(result.results)}")
        if result.results:
            logger.debug(f"First result: {result.results[0]}")
            logger.debug(f"First result type: {type(result.results[0])}")

    # Extract the most recent item
    if hasattr(result, 'results') and result.results:
        ctx_result = result.results[0]

        # Get primary result from context result
        if hasattr(ctx_result, 'primary_result') and ctx_result.primary_result:
            item = ctx_result.primary_result
        else:
            # Fallback: try to get the item directly if no primary_result
            item = ctx_result

        # Get identifier (permalink or title)
        identifier = getattr(item, 'permalink', getattr(item, 'title', None))

        logger.debug(f"Extracted identifier: {identifier}")

        if identifier:
            # Read the note content
            from advanced_memory.mcp.tools.read_note import read_note
            return await read_note.fn(identifier=identifier, project=active_project.name)
        else:
            return f"# Error\n\nCould not determine identifier for most recent note. Item attributes: {dir(item)}"
    else:
        return "# No Recent Activity\n\nNo notes found in the past year."


async def _view_operation(active_project, identifier: str) -> str:
    """Handle view operation."""
    from advanced_memory.mcp.tools.view_note import view_note

    return await view_note.fn(identifier=identifier, project=active_project.name)


async def _view_rendered_operation(active_project, identifier: str) -> str:
    """Handle view_rendered operation."""
    from advanced_memory.mcp.tools.view_note_rendered import view_note_rendered

    return await view_note_rendered.fn(identifier=identifier, project=active_project.name)


async def _edit_operation(
    active_project,
    identifier: str,
    edit_operation: str | None,
    content: str | None,
    section: str | None,
    find_text: str | None,
    expected_replacements: int,
) -> str:
    """Handle edit operation."""
    from advanced_memory.mcp.tools.edit_note import edit_note

    return await edit_note.fn(
        identifier=identifier,
        operation=edit_operation or "replace",
        content=content or "",
        section=section,
        find_text=find_text,
        expected_replacements=expected_replacements,
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
    current_tags = (
        current_entity.entity_metadata.get("tags", []) if current_entity.entity_metadata else []
    )

    # Parse input tags (unless clear operation)
    if tag_operation != "clear":
        if tags is None and tag_operation != "clear":
            return f"# Error\n\n'{tag_operation}' operation requires tags parameter.\n\nProvide tags as string or list."

        new_tags = parse_tags(tags)

        if not new_tags and tag_operation != "clear":
            return f"# Error\n\nNo valid tags provided.\n\nTags: {tags}"

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

    update_url = f"{project_url}/knowledge/entities/{current_entity.permalink}"
    update_data = {
        "title": current_entity.title,
        "entity_type": current_entity.entity_type,
        "content_type": current_entity.content_type,
        "content": current_entity.content,
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

    return await move_note.fn(
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
    return await _write_operation(
        active_project, title, formatted_content, folder, tag_list, "note"
    )


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

    existing_note = await read_note.fn(
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
        return await _write_operation(
            active_project, title, formatted_content, folder, tag_list, "note"
        )
    else:
        # Append to existing daily note
        timestamp = today.strftime("%H:%M")
        append_content = f"""

## {timestamp}

{content}

---
"""
        return await edit_note.fn(
            identifier=f"{folder}/{title}",
            operation="append",
            content=append_content,
            project=active_project.name,
        )


async def _delete_operation(active_project, identifier: str) -> str:
    """Handle delete operation."""
    from advanced_memory.mcp.tools.delete_note import delete_note

    return await delete_note.fn(identifier=identifier, project=active_project.name)
