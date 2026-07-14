"""Content CRUD services — write, read, view, edit, move, delete.

Extracted verbatim from content_manager.py (lines 1106-1486, 1697-1707,
1988-2006) during Phase 1 of the 2.0 migration (ARCHITECTURE_2_0.md).
Pure move, no behavior changes. Legacy names carried the pattern
_<name>_operation; the service names drop the underscore prefix and
suffix. In-body imports of standalone tool modules (read_note,
edit_note, delete_note, move_note, view_note, view_note_rendered,
recent_activity, skill_helpers) are retained as-is; those modules are
triaged separately (PHASE1_TRIAGE.md section E).
"""

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.tools.utils import (  # response builders (shared)
    build_error_response,
    build_success_response,
    call_put,
)
from advanced_memory.schemas import EntityResponse
from advanced_memory.schemas.base import Entity
from advanced_memory.schemas.memory import GraphContext
from advanced_memory.utils import parse_tags, validate_project_path

TagType = list[str] | str | None


async def write_note(
    active_project,
    identifier: str,
    content: str,
    folder: str,
    tags: TagType,
    entity_type: str,
) -> str:
    """Handle write operation with auto-skill detection."""
    if not identifier or not content or not folder:
        return build_error_response(
            error="Missing write parameters",
            error_code="MISSING_WRITE_PARAMS",
            message="Write operation requires identifier and content",
            recovery_options=[
                "Provide identifier (note title)",
                "Provide content (markdown text)",
                "Use folder parameter to specify location (optional, defaults to inbox)",
            ],
            urgency="medium",
        )

    # Validate folder path to prevent path traversal attacks
    project_path = active_project.home
    if folder and not validate_project_path(folder, project_path):
        logger.warning(
            "Attempted path traversal attack blocked",
            folder=folder,
            project=active_project.name,
        )
        return build_error_response(
            error="Invalid folder path",
            error_code="INVALID_PATH",
            message=f"Folder path '{folder}' is not allowed",
            recovery_options=[
                "Use relative paths within project boundaries",
                "Avoid '..' or absolute paths",
                "Default folder is 'inbox' if not specified",
            ],
            diagnostic_info={"folder": folder, "project_path": str(project_path)},
            urgency="medium",
        )

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
    try:
        logger.debug(f"Creating entity via API permalink={entity.permalink}")
        url = f"{project_url}/knowledge/entities/{entity.permalink}"
        response = await call_put(client, url, json=entity.model_dump())

        if response.status_code not in (200, 201):
            return f"""# Error: Failed to Create/Update Note

The API request failed with status code {response.status_code}.

**Details:**
- **Title:** {identifier}
- **Folder:** {folder}
- **URL:** {url}

**Possible causes:**
- Project not found or not accessible
- Invalid folder path
- Network connectivity issue
- Server error

**Response:** {response.text[:200] if hasattr(response, "text") else "No response text"}
"""

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
        return build_success_response(
            operation="write",
            summary=f"Note '{identifier}' {'created' if action == 'created' else 'updated'} successfully",
            result={
                "title": identifier,
                "permalink": result.permalink,
                "folder": folder,
                "observations_count": len(result.observations),
                "relations_count": len(result.relations),
                "resolved_relations": resolved,
                "unresolved_relations": unresolved,
                "tags": tag_list,
            },
            next_steps=[
                "Read the note to verify content" if action == "created" else "Review the updated content",
                "Add related notes or concepts",
                "Consider enhancing with AI suggestions",
            ],
        )
    except Exception as e:
        logger.error(f"Error creating/updating note: {e}", exc_info=True)
        return build_error_response(
            error="Failed to create/update note",
            error_code="WRITE_FAILED",
            message=f"Could not create or update note '{identifier}'",
            recovery_options=[
                "Check project is active with adn_project('list')",
                "Verify folder path is valid and within project boundaries",
                "Try again if it was a temporary network issue",
                "Check server logs for detailed error information",
            ],
            diagnostic_info={
                "title": identifier,
                "folder": folder,
                "error_details": str(e),
                "project": active_project.name if active_project else None,
            },
            urgency="medium",
        )


async def read_note(active_project, identifier: str, page: int, page_size: int) -> dict:
    """Handle read operation."""
    if not identifier:
        return build_error_response(
            error="Missing identifier for read",
            error_code="MISSING_IDENTIFIER",
            message="Read operation requires identifier parameter",
            recovery_options=[
                "Provide note title, permalink, or memory:// URL",
                "Use adn_search to find available notes",
                "Use read_latest to get the most recent note",
            ],
            urgency="medium",
        )

    # Delegate to read_note tool
    from advanced_memory.mcp.tools.read_note import read_note

    result = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=identifier,
        page=page,
        page_size=page_size,
        project=active_project.name,
    )

    # If the tool returned a raw string, wrap it in a dict to satisfy
    # the adn_content return type constraint (dict)
    if isinstance(result, str):
        return build_success_response(
            operation="read",
            summary=f"Read note '{identifier}'",
            result={"content": result},
        )

    return result


async def get_latest_identifier(active_project) -> tuple[str | None, str | None]:
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


async def read_latest_note(active_project) -> dict:
    """Handle read_latest operation - read the single most recent note."""
    identifier, error_message = await get_latest_identifier(active_project)
    if not identifier:
        return error_message or "# No Recent Activity\n\nNo notes found in the past year."

    from advanced_memory.mcp.tools.read_note import read_note

    return await (read_note.fn if hasattr(read_note, "fn") else read_note)(
        identifier=identifier, project=active_project.name
    )


async def view_note(active_project, identifier: str) -> dict:
    """Handle view operation."""
    from advanced_memory.mcp.tools.view_note import view_note

    return await (view_note.fn if hasattr(view_note, "fn") else view_note)(
        identifier=identifier, project=active_project.name
    )


async def view_note_rendered(active_project, identifier: str) -> dict:
    """Handle view_rendered operation."""
    from advanced_memory.mcp.tools.view_note_rendered import view_note_rendered

    return await (view_note_rendered.fn if hasattr(view_note_rendered, "fn") else view_note_rendered)(
        identifier=identifier, project=active_project.name
    )


async def edit_note(
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


async def move_note(active_project, identifier: str, destination_path: str) -> dict:
    """Handle move operation."""
    from advanced_memory.mcp.tools.move_note import move_note

    return await (move_note.fn if hasattr(move_note, "fn") else move_note)(
        identifier=identifier,
        destination_path=destination_path,
        project=active_project.name,
    )


async def delete_note(active_project, identifier: str) -> dict:
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
