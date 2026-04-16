"""Write note tool for Advanced Memory MCP server."""

from typing import Annotated

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_put
from advanced_memory.schemas import EntityResponse
from advanced_memory.schemas.base import Entity
from advanced_memory.utils import parse_tags, validate_project_path

# Define TagType for better readability
TagType = list[str] | str | None


@mcp.tool
async def write_note(
    title: Annotated[str, Field(description="The title of the note")],
    content: Annotated[str, Field(description="Markdown content with observations/relations")],
    folder: Annotated[
        str, Field(description="Folder path relative to project root (e.g. 'notes')")
    ],
    tags: Annotated[
        str | list[str] | None,
        Field(description="Tags as list or comma-separated string"),
    ] = None,
    entity_type: Annotated[
        str, Field(description="Type of entity to create (default: 'note')")
    ] = "note",
    project: Annotated[str | None, Field(description="Optional project name")] = None,
) -> str:
    """Write a markdown note with semantic observations and relations.

    Observations: `- [category] Observation text #tag1 #tag2 (optional context)`
    Relations: `- relation_type [[Entity]] (optional context)`
    """
    logger.info(f"MCP tool call tool=write_note folder={folder}, title={title}, tags={tags}")

    # Get the active project first to check project-specific sync status
    active_project = get_active_project(project)

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
        title=title,
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

    # Log the response with structured data
    logger.info(
        f"MCP tool response: tool=write_note action={action} permalink={result.permalink} observations_count={len(result.observations)} relations_count={len(result.relations)} resolved_relations={resolved} unresolved_relations={unresolved} status_code={response.status_code}"
    )
    return "\n".join(summary)
