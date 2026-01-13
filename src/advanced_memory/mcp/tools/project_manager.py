"""Project Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all project management operations: create, switch, delete, set_default, get_current, and list.
It reduces the number of MCP tools while maintaining full functionality.
"""

from textwrap import dedent
from typing import Literal

from fastmcp import Context
from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import add_project_metadata, session
from advanced_memory.mcp.tools.utils import call_delete, call_get, call_post, call_put
from advanced_memory.schemas import ProjectInfoResponse
from advanced_memory.schemas.project_info import (
    ProjectInfoRequest,
    ProjectList,
    ProjectStatusResponse,
)
from advanced_memory.utils import generate_permalink


@mcp.tool
async def adn_project(
    operation: Literal[
        "create",
        "switch",
        "delete",
        "set_default",
        "get_current",
        "list",
        "sync",
        "status",
        "detect",
    ],
    project_name: str | None = None,
    project_path: str | None = None,
    set_default: bool = False,
    ctx: Context | None = None,
) -> str:
    """
    Comprehensive project management tool for Advanced Memory knowledge base.

    This point-of-entry tool provides a unified interface for project operations,
    context switching, and AI-managed project detection.

    ---------------------------------------------------------------------------
    [PORTMANTEAU PATTERN RATIONALE]
    Consolidates 8 project management operations into one tool to prevent tool explosion while maintaining full functionality.

    ---------------------------------------------------------------------------
    [PARAMETER DESIGN]
    The parameters are categorized by operation type:
    - Lifecycle (create, delete): Handles project creation and removal.
    - Context (switch, detect, get_*): Manages the active project session.
    - Configuration (set_default): Persists preferences across restarts.
    - Sync (sync, status): Manages file system synchronization.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]

    Lifecycle Operations:
    - create: Initialize a new project with specified name and path.
    - delete: Remove a project configuration (files preserved).
    - set_default: Set the project to load automatically on startup.

    Context Management:
    - switch: Activate a different project context.
    - list: Display all available projects with health status.
    - get_current: Get statistics for the active project.
    - detect: AI-powered auto-switching based on conversation context.

    Synchronization:
    - sync: Force synchronization for a specific project.
    - status: Get detailed sync status and file counts.

    ---------------------------------------------------------------------------
    [PROJECT CONTEXT IMPACT]
    - All file operations target the active project.
    - Search operations are scoped to the active project by default.
    - Directory listings show the active project's structure.
    - New notes are created in the active project unless specified otherwise.

    ---------------------------------------------------------------------------
    [PREREQUISITES]
    - 'project_path' must be a valid directory for 'create'.
    - 'project_name' is required for most operations except 'list', 'get_current', 'detect'.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation: The project operation to perform (Required).
    - project_name: Project identifier (Required for create/switch/delete/sync/status).
    - project_path: File system path (Required for create).
    - set_default: Set as default project on creation (Default: False).
    - ctx: MCP context for progress reporting (Optional).

    ---------------------------------------------------------------------------
    [USAGE]
    Use this tool to manage the project lifecycle and active context.
    The 'detect' operation is particularly useful for AI agents to auto-switch contexts.

    ---------------------------------------------------------------------------
    [EXAMPLES]

    - Create a new research project:
      adn_project("create", project_name="quantum-research", project_path="~/research/quantum")

    - Switch to work context:
      adn_project("switch", project_name="work")

    - List all projects:
      adn_project("list")

    - Auto-detect context from conversation:
      adn_project("detect")

    ---------------------------------------------------------------------------
    [ERRORS]
    - "Project not found": The specified project does not exist.
    - "Path invalid": The provided project path is not accessible.
    - "Project already exists": Attempted to create a duplicate project.
    """
    logger.info(f"MCP tool call tool=adn_project operation={operation} project_name={project_name}")

    # Route to appropriate operation
    if operation == "create":
        return await _create_operation(project_name, project_path, set_default, ctx)
    elif operation == "switch":
        return await _switch_operation(project_name, ctx)
    elif operation == "delete":
        return await _delete_operation(project_name, ctx)
    elif operation == "set_default":
        return await _set_default_operation(project_name, ctx)
    elif operation == "get_current":
        return await _get_current_operation(ctx)
    elif operation == "list":
        return await _list_operation(ctx)
    elif operation == "sync":
        return await _sync_operation(project_name, ctx)
    elif operation == "status":
        return await _status_operation(project_name, ctx)
    elif operation == "detect":
        return await _detect_operation(ctx)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: create, switch, delete, set_default, get_current, list, sync, status, detect"


async def _create_operation(
    project_name: str | None,
    project_path: str | None,
    set_default: bool,
    ctx: Context | None,
) -> str:
    """Handle create operation."""
    missing = []
    if not project_name:
        missing.append("project_name")
    if not project_path:
        missing.append("project_path")
    if missing:
        return f'# Error\n\nCreate operation requires the following parameters:\n- {", ".join(missing)}\n\n**Example:**\n```python\nadn_project("create",\n    project_name="my-research",\n    project_path="~/Documents/research")\n```'

    if ctx:  # pragma: no cover
        await ctx.info(f"Creating project: {project_name} at {project_path}")

    # Create the project request
    project_request = ProjectInfoRequest(
        name=project_name, path=project_path, set_default=set_default
    )

    # Call API to create project
    response = await call_post(client, "/projects/projects", json=project_request.model_dump())
    status_response = ProjectStatusResponse.model_validate(response.json())

    result = f"✓ {status_response.message}\n\n"

    if status_response.new_project:
        result += "Project Details:\n"
        result += f"📁 Name: {status_response.new_project.name}\n"
        result += f"📁 Path: {status_response.new_project.path}\n"

        if set_default:
            result += "⭐ Set as default project\n"

    result += "\nProject is now available for use.\n"

    # If project was set as default, update session
    if set_default:
        session.set_current_project(project_name)

    return add_project_metadata(result, session.get_current_project())


async def _switch_operation(project_name: str | None, ctx: Context | None) -> str:
    """Handle switch operation."""
    if not project_name:
        return '# Error\n\nSwitch operation requires: project_name parameter\n\n**Example:**\n```python\nadn_project("switch", project_name="work-project")\n```'

    if ctx:  # pragma: no cover
        await ctx.info(f"Switching to project: {project_name}")

    project_permalink = generate_permalink(project_name)
    current_project = session.get_current_project()

    try:
        # Validate project exists by getting project list
        response = await call_get(client, "/projects/projects")
        project_list = ProjectList.model_validate(response.json())

        # Find the project by name (case-insensitive) or permalink
        target_project = None
        for p in project_list.projects:
            # Match by permalink (handles case-insensitive input)
            if p.permalink == project_permalink:
                target_project = p
                break
            # Also match by name comparison (case-insensitive)
            if p.name.lower() == project_name.lower():
                target_project = p
                break

        if not target_project:
            available_projects = [p.name for p in project_list.projects]
            return f"Error: Project '{project_name}' not found. Available projects: {', '.join(available_projects)}"

        # Switch to the project using the canonical name from database
        canonical_name = target_project.name
        session.set_current_project(canonical_name)
        current_project = session.get_current_project()

        # Get project info to show summary
        try:
            current_project_permalink = generate_permalink(canonical_name)
            response = await call_get(
                client,
                f"/{current_project_permalink}/project/info",
                params={"project_name": canonical_name},
            )
            project_info = ProjectInfoResponse.model_validate(response.json())

            result = f"✓ Switched to {canonical_name} project\n\n"
            result += "Project Summary:\n"
            result += f"📊 {project_info.statistics.total_entities} entities\n"
            result += f"📊 {project_info.statistics.total_observations} observations\n"
            result += f"📊 {project_info.statistics.total_relations} relations\n"

        except Exception as e:
            # If we can't get project info, still confirm the switch
            logger.warning(f"Could not get project info for {canonical_name}: {e}")
            result = f"✓ Switched to {canonical_name} project\n\n"
            result += "Project summary unavailable.\n"

        return add_project_metadata(result, canonical_name)

    except Exception as e:
        logger.error(f"Error switching to project {project_name}: {e}")
        # Revert to previous project on error
        session.set_current_project(current_project)

        # Return user-friendly error message instead of raising exception
        return dedent(f"""
            # Project Switch Failed

            Could not switch to project '{project_name}': {str(e)}

            ## Current project: {current_project}
            Your session remains on the previous project.

            ## Troubleshooting:
            1. **Check available projects**: Use `project_manager("list")` to see valid project names
            2. **Verify spelling**: Ensure the project name is spelled correctly
            3. **Check permissions**: Verify you have access to the requested project
            4. **Try again**: The error might be temporary

            ## Available options:
            - See all projects: `project_manager("list")`
            - Stay on current project: `project_manager("get_current")`
            - Try different project: `project_manager("switch", project_name="correct-project-name")`

            If the project should exist but isn't listed, send a message to support@basicmachines.co.
            """).strip()


async def _delete_operation(project_name: str | None, ctx: Context | None) -> str:
    """Handle delete operation."""
    if not project_name:
        return '# Error\n\nDelete operation requires: project_name parameter\n\n**Example:**\n```python\nadn_project("delete", project_name="old-project")\n```'

    if ctx:  # pragma: no cover
        await ctx.info(f"Deleting project: {project_name}")

    current_project = session.get_current_project()

    # Check if trying to delete current project
    if project_name == current_project:
        return f"# Error\n\nCannot delete the currently active project '{project_name}'. Switch to a different project first using `project_manager('switch', project_name='other-project')`."

    # Get project info before deletion to validate it exists
    response = await call_get(client, "/projects/projects")
    project_list = ProjectList.model_validate(response.json())

    # Check if project exists
    project_exists = any(p.name == project_name for p in project_list.projects)
    if not project_exists:
        available_projects = [p.name for p in project_list.projects]
        return f"# Error\n\nProject '{project_name}' not found. Available projects: {', '.join(available_projects)}"

    # Call API to delete project
    response = await call_delete(client, f"/projects/{project_name}")
    status_response = ProjectStatusResponse.model_validate(response.json())

    result = f"✓ {status_response.message}\n\n"

    if status_response.old_project:
        result += "Removed project details:\n"
        result += f"📁 Name: {status_response.old_project.name}\n"
        if hasattr(status_response.old_project, "path"):
            result += f"📁 Path: {status_response.old_project.path}\n"

    result += "Files remain on disk but project is no longer tracked by Advanced Memory.\n"
    result += "Re-add the project to access its content again.\n"

    return add_project_metadata(result, session.get_current_project())


async def _set_default_operation(project_name: str | None, ctx: Context | None) -> str:
    """Handle set_default operation."""
    if not project_name:
        return '# Error\n\nSet_default operation requires: project_name parameter\n\n**Example:**\n```python\nadn_project("set_default", project_name="personal-notes")\n```'

    if ctx:  # pragma: no cover
        await ctx.info(f"Setting default project to: {project_name}")

    # Call API to set default project
    response = await call_put(client, f"/projects/{project_name}/default")
    status_response = ProjectStatusResponse.model_validate(response.json())

    result = f"✓ {status_response.message}\n\n"
    result += "Restart Advanced Memory for this change to take effect:\n"
    result += "basic-memory mcp\n"

    if status_response.old_project:
        result += f"\nPrevious default: {status_response.old_project.name}\n"

    return add_project_metadata(result, session.get_current_project())


async def _get_current_operation(ctx: Context | None) -> str:
    """Handle get_current operation."""
    if ctx:  # pragma: no cover
        await ctx.info("Getting current project information")

    current_project = session.get_current_project()
    result = f"Current project: {current_project}\n\n"

    # get project stats (use permalink in URL path)
    current_project_permalink = generate_permalink(current_project)
    response = await call_get(
        client,
        f"/{current_project_permalink}/project/info",
        params={"project_name": current_project},
    )
    project_info = ProjectInfoResponse.model_validate(response.json())

    result += f"[UNICODE] {project_info.statistics.total_entities} entities\n"
    result += f"[UNICODE] {project_info.statistics.total_observations} observations\n"
    result += f"[UNICODE] {project_info.statistics.total_relations} relations\n"

    default_project = session.get_default_project()
    if current_project != default_project:
        result += f"[UNICODE] Default project: {default_project}\n"

    return add_project_metadata(result, current_project)


async def _list_operation(ctx: Context | None) -> str:
    """Handle list operation."""
    if ctx:  # pragma: no cover
        await ctx.info("Listing all available projects")

    # Get projects from API
    response = await call_get(client, "/projects/projects")
    project_list = ProjectList.model_validate(response.json())

    current = session.get_current_project()

    result = "Available projects:\n"

    for project in project_list.projects:
        indicators = []
        if project.name == current:
            indicators.append("current")
        if project.is_default:
            indicators.append("default")

        if indicators:
            result += f"[UNICODE] {project.name} ({', '.join(indicators)})\n"
        else:
            result += f"[UNICODE] {project.name}\n"

    return add_project_metadata(result, current)


async def _sync_operation(project_name: str | None, ctx: Context | None) -> str:
    """Handle sync operation - sync a specific project without changing default."""
    if not project_name:
        return '# Error\n\nSync operation requires: project_name parameter\n\n**Example:**\n```python\nadn_project("sync", project_name="my-project")\n```'

    if ctx:  # pragma: no cover
        await ctx.info(f"Syncing project: {project_name}")

    try:
        # Call the new project-specific sync endpoint
        response = await call_post(client, f"/projects/{project_name}/sync")
        sync_response = response.json()

        result = f"✅ Project '{project_name}' synced successfully\n\n"
        result += f"Files processed: {sync_response.get('files_synced', 'N/A')}\n"

        return add_project_metadata(result, session.get_current_project())

    except Exception as e:
        result = f"❌ Error syncing project '{project_name}': {str(e)}\n\n"
        result += "Make sure the project exists. Use adn_project('list') to see all projects.\n"
        return add_project_metadata(result, session.get_current_project())


async def _status_operation(project_name: str | None, ctx: Context | None) -> str:
    """Handle status operation - get detailed statistics for a specific project."""
    if not project_name:
        return '# Error\n\nStatus operation requires: project_name parameter\n\n**Example:**\n```python\nadn_project("status", project_name="my-project")\n```'

    if ctx:  # pragma: no cover
        await ctx.info(f"Getting status for project: {project_name}")

    try:
        # Get project info
        project_permalink = generate_permalink(project_name)
        response = await call_get(
            client,
            f"/{project_permalink}/project/info",
            params={"project_name": project_name},
        )
        project_info = ProjectInfoResponse.model_validate(response.json())

        result = f"📊 Project: {project_info.name}\n\n"
        result += f"📁 Path: {project_info.path}\n"
        result += f"🔗 Permalink: {project_info.permalink}\n\n"

        result += "Statistics:\n"
        result += f"  📄 {project_info.statistics.total_entities} entities\n"
        result += f"  🔍 {project_info.statistics.total_observations} observations\n"
        result += f"  🔗 {project_info.statistics.total_relations} relations\n\n"

        if project_info.is_default:
            result += "⭐ This is the default project\n"

        return add_project_metadata(result, session.get_current_project())

    except Exception as e:
        return add_project_metadata(
            f"❌ Error getting status for project '{project_name}': {str(e)}",
            session.get_current_project(),
        )


async def _detect_operation(ctx: Context | None) -> str:
    """Handle detect operation - AI-managed project detection.

    This operation analyzes conversation context to detect which project
    the user is likely referring to and optionally switches automatically.

    The AI should call this with a user_query parameter extracted from the conversation.
    """
    from advanced_memory.services.project_detector import get_project_detector

    if ctx:  # pragma: no cover
        await ctx.info("Detecting relevant project from context...")

    current_project = session.get_current_project()
    detector = get_project_detector()

    # Try to extract query from context if available
    # In practice, the AI will pass this explicitly
    user_query = ""
    if ctx and hasattr(ctx, "user_query"):
        user_query = ctx.user_query  # type: ignore
    elif ctx and hasattr(ctx, "message"):
        user_query = ctx.message  # type: ignore

    # Detect project from context
    detection = await detector.detect_project_from_context(
        user_query=user_query or "",
        current_project=current_project,
    )

    suggested_project = detection["suggested_project"]
    confidence = detection["confidence"]
    reason = detection["reason"]
    should_switch = detection["should_switch"]

    result_lines = [
        "# 🤖 AI-Managed Project Detection",
        "",
        f"**Current Project**: {current_project}",
        "",
    ]

    if suggested_project:
        result_lines.extend(
            [
                f"**Suggested Project**: {suggested_project}",
                f"**Confidence**: {confidence:.0%}",
                f"**Reason**: {reason}",
                "",
            ]
        )

        if should_switch and suggested_project != current_project:
            # Auto-switch if confidence is high enough
            try:
                switch_result = await _switch_operation(suggested_project, ctx)
                result_lines.extend(
                    [
                        "## ✅ Auto-Switched Project",
                        "",
                        f"I've automatically switched to **{suggested_project}** project based on context.",
                        "",
                        switch_result.split("\n\n")[-1]
                        if "\n\n" in switch_result
                        else switch_result,
                    ]
                )
            except Exception as e:
                result_lines.extend(
                    [
                        "## ⚠️ Auto-Switch Failed",
                        "",
                        f"Could not automatically switch: {e}",
                        "",
                        f"You can manually switch: `adn_project('switch', project_name='{suggested_project}')`",
                    ]
                )
        elif suggested_project == current_project:
            result_lines.extend(
                [
                    "## ✓ Already on Correct Project",
                    "",
                    f"You're already on the **{suggested_project}** project. No switch needed.",
                ]
            )
        else:
            result_lines.extend(
                [
                    "## 💡 Project Suggestion",
                    "",
                    f"Based on context, you might want to switch to **{suggested_project}** project.",
                    "",
                    f"**Confidence**: {confidence:.0%} (threshold: 60% for auto-switch)",
                    "",
                    f"To switch manually: `adn_project('switch', project_name='{suggested_project}')`",
                ]
            )
    else:
        result_lines.extend(
            [
                "## ℹ️ No Clear Project Detected",
                "",
                "Could not detect a specific project from the context.",
                "",
                "**Available projects**:",
            ]
        )
        projects = await detector._get_all_projects()
        for proj in projects:
            marker = "⭐ " if proj["name"] == current_project else "  "
            result_lines.append(f"{marker}- {proj['name']}")

    result_lines.extend(
        [
            "",
            "## How It Works",
            "",
            "The AI analyzes your queries for:",
            "- Explicit project name mentions (e.g., 'work project', 'private notes')",
            "- Folder/path references that match project names",
            "- Search results that contain project metadata",
            "- File paths that belong to specific projects",
            "",
            "**Auto-switch happens when confidence ≥ 60%**",
        ]
    )

    return add_project_metadata("\n".join(result_lines), current_project)
