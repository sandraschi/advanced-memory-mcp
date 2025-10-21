"""Tag editing tool for Advanced Memory knowledge base."""

from typing import Literal

from loguru import logger

from advanced_memory.config import ConfigManager
from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get, call_put
from advanced_memory.schemas import EntityResponse
from advanced_memory.utils import parse_tags


@mcp.tool
async def edit_tags(
    identifier: str,
    operation: Literal["add", "remove", "replace", "clear"],
    tags: str | list[str] | None = None,
    project: str | None = None,
) -> str:
    """Edit tags on notes with precise control over tag operations.

    This tool provides surgical tag editing capabilities without requiring full note rewrites,
    supporting multiple tag operations for different scenarios while maintaining content integrity.

    SUPPORTED OPERATIONS:
    - add: Add tags to existing tags (preserves current tags)
    - remove: Remove specific tags from existing tags
    - replace: Replace all tags with new set
    - clear: Remove all tags from note

    TAG OPERATIONS:

    add: Append new tags
    - Adds specified tags to existing tags
    - Preserves all current tags
    - No duplicates (existing tags are preserved)
    - Useful for adding categories without removing existing tags

    remove: Delete specific tags
    - Removes only specified tags
    - Preserves other existing tags
    - Fails gracefully if tag doesn't exist
    - Useful for removing categories or cleanup

    replace: Complete tag replacement
    - Replaces entire tag set with new tags
    - Removes all existing tags
    - Sets exactly the specified tags
    - Use for major tag restructuring

    clear: Remove all tags
    - Removes all tags from the note
    - tags parameter is ignored
    - Useful for cleanup or reset
    - Preserves all other note content and metadata

    PARAMETERS:
    - identifier (str, REQUIRED): Exact note title or permalink (no fuzzy matching)
    - operation (str, REQUIRED): Tag operation type (add, remove, replace, clear)
    - tags (str | list[str], optional): Tags to apply (comma-separated string or list)
    - project (str, optional): Specific project to edit in (defaults to active project)

    TAG FORMATS:
    Tags can be provided as:
    - String: "python, fastmcp, mcp-server"
    - List: ["python", "fastmcp", "mcp-server"]
    - Leading # symbols are automatically stripped

    VALIDATION:
    - Exact identifier matching required (safety requirement)
    - Project boundary enforcement
    - Tag format validation
    - Empty tag handling
    - Duplicate prevention

    USAGE EXAMPLES:
    Add tags: edit_tags("Meeting Notes", "add", "urgent, follow-up")
    Remove tags: edit_tags("Draft Document", "remove", ["draft", "wip"])
    Replace all tags: edit_tags("Project Plan", "replace", "final, approved, v2")
    Clear all tags: edit_tags("Old Notes", "clear")
    With project: edit_tags("Important Note", "add", "priority", project="work")

    RETURNS:
    Tag edit confirmation with before/after tag lists, changes made, and any warnings.

    SAFETY FEATURES:
    - Exact identifier matching prevents accidental edits
    - No content modification (only tags)
    - Automatic tag format validation
    - Duplicate tag prevention
    - Error recovery with detailed guidance

    NOTE: Requires exact note identifier. Use read_note() or search_notes() first if unsure
    of the exact title/permalink. Tags are case-sensitive as stored.
    """
    logger.info(f"MCP tool call tool=edit_tags identifier={identifier} operation={operation}")

    try:
        ConfigManager()

        # Get active project
        if project:
            active_project = get_active_project(project)
        else:
            active_project = get_active_project()

        if not active_project:
            return "# Error\n\nNo active project. Please switch to a project first."

        logger.debug(f"Active project: {active_project.name}")

        # Get current note to read existing tags
        project_url = active_project.project_url
        url = f"{project_url}/knowledge/entities/resolve/{identifier}"

        response = await call_get(client, url)
        if response.status_code == 404:
            return f"# Error\n\nNote not found: {identifier}\n\nPlease provide exact note title or permalink."

        current_entity = EntityResponse.model_validate(response.json())
        current_tags = current_entity.entity_metadata.get("tags", []) if current_entity.entity_metadata else []

        # Parse input tags (unless clear operation)
        if operation != "clear":
            if tags is None and operation != "clear":
                return f"# Error\n\n'{operation}' operation requires tags parameter.\n\nProvide tags as string or list."

            new_tags = parse_tags(tags)

            if not new_tags and operation != "clear":
                return f"# Error\n\nNo valid tags provided.\n\nTags: {tags}"

        # Perform the operation
        if operation == "add":
            # Add tags (preserve existing, no duplicates)
            updated_tags = list(set(current_tags + new_tags))
            added_tags = [tag for tag in new_tags if tag not in current_tags]
            operation_summary = f"Added {len(added_tags)} tag(s): {', '.join(added_tags)}" if added_tags else "No new tags added (all tags already exist)"

        elif operation == "remove":
            # Remove specific tags
            updated_tags = [tag for tag in current_tags if tag not in new_tags]
            removed_tags = [tag for tag in new_tags if tag in current_tags]
            operation_summary = f"Removed {len(removed_tags)} tag(s): {', '.join(removed_tags)}" if removed_tags else "No tags removed (specified tags not found)"

        elif operation == "replace":
            # Replace all tags
            updated_tags = new_tags
            operation_summary = f"Replaced all tags with {len(new_tags)} new tag(s)"

        elif operation == "clear":
            # Clear all tags
            updated_tags = []
            operation_summary = f"Cleared all {len(current_tags)} tag(s)"

        else:
            return f"# Error\n\nInvalid operation: {operation}\n\nSupported: add, remove, replace, clear"

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
            f"**Note:** {result.title}",
            f"**Permalink:** {result.permalink}",
            "",
            "## Operation",
            f"**Action:** {operation}",
            f"**Summary:** {operation_summary}",
            "",
            "## Tags",
            f"**Before:** {', '.join(current_tags) if current_tags else '(no tags)'}",
            f"**After:** {', '.join(updated_tags) if updated_tags else '(no tags)'}",
            f"**Total tags:** {len(updated_tags)}",
        ]

        logger.info(
            f"MCP tool response: tool=edit_tags operation={operation} identifier={identifier} tags_before={len(current_tags)} tags_after={len(updated_tags)}"
        )

        return "\n".join(response_lines)

    except Exception as e:
        logger.error(f"Error editing tags: {e}")
        return f"# Error\n\nFailed to edit tags: {str(e)}\n\nPlease verify the note identifier and try again."

