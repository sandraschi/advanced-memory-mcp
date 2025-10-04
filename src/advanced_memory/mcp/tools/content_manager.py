"""Content Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all content operations: write, read, view, edit, move, and delete.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import List, Union, Optional, Dict, Any

from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.utils import call_put, call_get, call_patch, call_delete
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.schemas import EntityResponse
from advanced_memory.schemas.base import Entity
from advanced_memory.utils import parse_tags, validate_project_path, sanitize_filename
from advanced_memory.mcp.tools.search import search_notes

# Define TagType as a Union that can accept either a string or a list of strings or None
TagType = Union[List[str], str, None]


@mcp.tool(
    description="""Comprehensive content management tool for Advanced Memory knowledge base.

This portmanteau tool consolidates all content operations into a single interface,
reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

SUPPORTED OPERATIONS:
- **write**: Create new notes or update existing ones with semantic processing
- **read**: Retrieve complete note content with intelligent lookup strategies
- **view**: Display notes as formatted artifacts for better readability
- **edit**: Perform targeted edits (append, prepend, find_replace, replace_section)
- **move**: Relocate notes while preserving relationships and updating references
- **delete**: Remove notes from knowledge base with relationship cleanup

CONTENT PROCESSING:
- Automatic entity recognition and linking ([[Entity Name]] syntax)
- Relationship extraction and graph building
- Tag processing and categorization
- Folder organization and hierarchy
- Markdown rendering and syntax validation

PARAMETERS:
- operation (str, REQUIRED): Operation type (write, read, view, edit, move, delete)
- identifier (str): Note title, permalink, or memory:// URL
- content (str): Full markdown content for write/edit operations
- folder (str): Target folder path for write/move operations
- tags (optional): Tags as string, list of strings, or None for categorization
- entity_type (str, default="note"): Content type (note, entity, observation, etc.)
- destination_path (str): New path for move operations
- edit_operation (str): Edit type (append, prepend, find_replace, replace_section)
- find_text (str): Text to find for find_replace operations
- expected_replacements (int, default=1): Expected replacement count for validation
- section (str): Target section for replace_section operations
- page (int, default=1): Pagination page for read operations
- page_size (int, default=10): Items per page for paginated content
- project (str, optional): Specific project to operate on (defaults to active project)

USAGE EXAMPLES:
Write note: adn_content("write", identifier="Meeting Notes", content="# Meeting Summary...", folder="meetings")
Read note: adn_content("read", identifier="Meeting Notes")
Edit note: adn_content("edit", identifier="Meeting Notes", edit_operation="append", content="\\n## New Section...")
Move note: adn_content("move", identifier="Meeting Notes", destination_path="archive/old-meetings.md")
Delete note: adn_content("delete", identifier="Meeting Notes")

RETURNS:
Operation-specific results with semantic content summaries, file paths, and processing details.

NOTE: This tool provides all content management functionality in a single interface for better MCP client compatibility.""",
)
async def adn_content(
    operation: str,
    identifier: Optional[str] = None,
    content: Optional[str] = None,
    folder: Optional[str] = None,
    tags: Optional[TagType] = None,
    entity_type: str = "note",
    destination_path: Optional[str] = None,
    edit_operation: Optional[str] = None,
    find_text: Optional[str] = None,
    expected_replacements: int = 1,
    section: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    project: Optional[str] = None,
) -> str:
    """Comprehensive content management for Advanced Memory knowledge base.

    This portmanteau tool consolidates all content operations:
    - write: Create/update notes with semantic processing
    - read: Retrieve notes with intelligent lookup
    - view: Display formatted note artifacts
    - edit: Targeted content modifications
    - move: Relocate notes with relationship preservation
    - delete: Remove notes with cleanup

    Args:
        operation: The operation to perform (write, read, view, edit, move, delete)
        identifier: Note title, permalink, or memory:// URL
        content: Markdown content for write/edit operations
        folder: Target folder path for write/move operations
        tags: Tags for categorization (string, list, or None)
        entity_type: Content type (default: "note")
        destination_path: New path for move operations
        edit_operation: Edit type for edit operations
        find_text: Text to find for find_replace operations
        expected_replacements: Expected replacement count for validation
        section: Target section for replace_section operations
        page: Pagination page for read operations
        page_size: Items per page for paginated content
        project: Optional project name (defaults to active project)

    Returns:
        Operation-specific result with semantic content summary

    Examples:
        # Write a new note
        adn_content("write", identifier="Project Plan", content="# Project Overview...", folder="projects")

        # Read a note
        adn_content("read", identifier="Project Plan")

        # Edit a note (append content)
        adn_content("edit", identifier="Project Plan", edit_operation="append", content="\\n## Updates...")

        # Move a note
        adn_content("move", identifier="Project Plan", destination_path="archive/completed/project-plan.md")

        # Delete a note
        adn_content("delete", identifier="Project Plan")
    """
    logger.info(f"MCP tool call tool=adn_content operation={operation} identifier={identifier}")

    # Get the active project
    active_project = get_active_project(project)

    # Check migration status and wait briefly if needed
    from advanced_memory.mcp.tools.utils import wait_for_migration_or_return_status

    migration_status = await wait_for_migration_or_return_status(
        timeout=5.0, project_name=active_project.name
    )
    if migration_status:  # pragma: no cover
        return f"# System Status\n\n{migration_status}\n\nPlease wait for migration to complete before content operations."

    # Route to appropriate operation
    if operation == "write":
        return await _write_operation(
            active_project, identifier, content, folder, tags, entity_type
        )
    elif operation == "read":
        return await _read_operation(active_project, identifier, page, page_size)
    elif operation == "view":
        return await _view_operation(active_project, identifier, page, page_size)
    elif operation == "edit":
        return await _edit_operation(
            active_project, identifier, edit_operation, content, find_text, expected_replacements, section
        )
    elif operation == "move":
        return await _move_operation(active_project, identifier, destination_path)
    elif operation == "delete":
        return await _delete_operation(active_project, identifier)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: write, read, view, edit, move, delete"


async def _write_operation(
    active_project, identifier: str, content: str, folder: str, tags: TagType, entity_type: str
) -> str:
    """Handle write operation."""
    if not identifier or not content or not folder:
        return "# Error\n\nWrite operation requires: identifier, content, and folder parameters"

    # Validate folder path to prevent path traversal attacks
    project_path = active_project.home
    if folder and not validate_project_path(folder, project_path):
        logger.warning(
            "Attempted path traversal attack blocked", folder=folder, project=active_project.name
        )
        return f"# Error\n\nFolder path '{folder}' is not allowed - paths must stay within project boundaries"

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
        f"file_path: {result.file_path}",
        f"permalink: {result.permalink}",
        f"checksum: {result.checksum[:8] if result.checksum else 'unknown'}",
    ]

    # Count observations by category
    categories = {}
    if result.observations:
        for obs in result.observations:
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
        return "# Error\n\nRead operation requires: identifier parameter"

    from advanced_memory.mcp.tools.read_note import read_note
    return await read_note(identifier, page, page_size, active_project.name)


async def _view_operation(active_project, identifier: str, page: int, page_size: int) -> str:
    """Handle view operation."""
    if not identifier:
        return "# Error\n\nView operation requires: identifier parameter"

    from advanced_memory.mcp.tools.view_note import view_note
    return await view_note(identifier, page, page_size, active_project.name)


async def _edit_operation(
    active_project, identifier: str, edit_operation: str, content: str, 
    find_text: Optional[str], expected_replacements: int, section: Optional[str]
) -> str:
    """Handle edit operation."""
    if not identifier or not edit_operation or not content:
        return "# Error\n\nEdit operation requires: identifier, edit_operation, and content parameters"

    # Validate edit operation
    valid_operations = ["append", "prepend", "find_replace", "replace_section"]
    if edit_operation not in valid_operations:
        return f"# Error\n\nInvalid edit_operation '{edit_operation}'. Must be one of: {', '.join(valid_operations)}"

    # Validate required parameters for specific operations
    if edit_operation == "find_replace" and not find_text:
        return "# Error\n\nfind_replace operation requires find_text parameter"
    if edit_operation == "replace_section" and not section:
        return "# Error\n\nreplace_section operation requires section parameter"

    project_url = active_project.project_url

    try:
        # Prepare the edit request data
        edit_data = {
            "operation": edit_operation,
            "content": content,
        }

        # Add optional parameters
        if section:
            edit_data["section"] = section
        if find_text:
            edit_data["find_text"] = find_text
        if expected_replacements != 1:
            edit_data["expected_replacements"] = str(expected_replacements)

        # Call the PATCH endpoint
        url = f"{project_url}/knowledge/entities/{identifier}"
        response = await call_patch(client, url, json=edit_data)
        result = EntityResponse.model_validate(response.json())

        # Format summary
        summary = [
            f"# Edited note ({edit_operation})",
            f"project: {active_project.name}",
            f"file_path: {result.file_path}",
            f"permalink: {result.permalink}",
            f"checksum: {result.checksum[:8] if result.checksum else 'unknown'}",
        ]

        # Add operation-specific details
        if edit_operation == "append":
            lines_added = len(content.split("\n"))
            summary.append(f"operation: Added {lines_added} lines to end of note")
        elif edit_operation == "prepend":
            lines_added = len(content.split("\n"))
            summary.append(f"operation: Added {lines_added} lines to beginning of note")
        elif edit_operation == "find_replace":
            summary.append("operation: Find and replace operation completed")
        elif edit_operation == "replace_section":
            summary.append(f"operation: Replaced content under section '{section}'")

        # Count observations by category
        categories = {}
        if result.observations:
            for obs in result.observations:
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

        logger.info(
            "MCP tool response",
            tool="content_manager",
            operation="edit",
            edit_operation=edit_operation,
            permalink=result.permalink,
            observations_count=len(result.observations),
            relations_count=len(result.relations),
            status_code=response.status_code,
        )

        return "\n".join(summary)

    except Exception as e:
        logger.error(f"Error editing note: {e}")
        return f"# Edit Failed\n\nError editing note '{identifier}': {str(e)}\n\n## Troubleshooting:\n1. Verify the note exists: content_manager('read', identifier='{identifier}')\n2. Check your parameters match exactly\n3. Try a simpler operation first"


async def _move_operation(active_project, identifier: str, destination_path: str) -> str:
    """Handle move operation."""
    if not identifier or not destination_path:
        return "# Error\n\nMove operation requires: identifier and destination_path parameters"

    from advanced_memory.mcp.tools.move_note import move_note
    return await move_note(identifier, destination_path, active_project.name)


async def _delete_operation(active_project, identifier: str) -> str:
    """Handle delete operation."""
    if not identifier:
        return "# Error\n\nDelete operation requires: identifier parameter"

    from advanced_memory.mcp.tools.delete_note import delete_note
    return await delete_note(identifier, active_project.name)
