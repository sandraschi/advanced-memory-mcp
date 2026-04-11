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
from advanced_memory.mcp.project_session import session
from advanced_memory.mcp.tools.utils import (
    build_error_response,
    build_success_response,
    call_delete,
    call_get,
    call_post,
    call_put,
)
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
) -> dict:
    """
    Comprehensive project management tool for Advanced Memory knowledge base.

    This point-of-entry tool provides a unified interface for project operations,
    context switching, and AI-managed project detection.

    RESPONSES:
    Success: {"success": true, "operation": "...", "summary": "...", "result": {...}}
    Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

    For errors, check recovery_options for next steps.

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
        return build_error_response(
            error="Invalid operation",
            error_code="INVALID_OPERATION",
            message=f"Operation '{operation}' is not supported",
            recovery_options=[
                "Use one of: create, switch, delete, set_default, get_current, list, sync, status, detect",
                "Check operation spelling and try again",
                "Use adn_project('list') to see available operations",
            ],
            supported_operations=[
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
            urgency="medium",
        )


async def _create_operation(
    project_name: str | None,
    project_path: str | None,
    set_default: bool,
    ctx: Context | None,
) -> dict:
    """Handle create operation."""
    missing = []
    if not project_name:
        missing.append("project_name")
    if not project_path:
        missing.append("project_path")
    if missing:
        return build_error_response(
            error="Missing required parameters",
            error_code="MISSING_PARAMETERS",
            message=f"Create operation requires: {', '.join(missing)}",
            recovery_options=[
                "Provide all required parameters",
                "Check parameter names and values",
                "Use absolute paths for project_path",
            ],
            required_parameters=["project_name", "project_path"],
            example={
                "operation": "create",
                "project_name": "my-research",
                "project_path": "~/Documents/research",
            },
            urgency="medium",
        )

    if ctx:  # pragma: no cover
        await ctx.info(f"Creating project: {project_name} at {project_path}")

    # Create the project request
    project_request = ProjectInfoRequest(
        name=project_name, path=project_path, set_default=set_default
    )

    # Call API to create project
    response = await call_post(client, "/projects/projects", json=project_request.model_dump())
    status_response = ProjectStatusResponse.model_validate(response.json())

    # If project was set as default, update session
    if set_default:
        session.set_current_project(project_name)

    project_details = None
    if status_response.new_project:
        project_details = {
            "name": status_response.new_project.name,
            "path": status_response.new_project.path,
            "set_as_default": set_default,
        }

    return build_success_response(
        operation="create",
        summary=status_response.message,
        result={
            "project_created": bool(status_response.new_project),
            "project_details": project_details,
            "set_as_default": set_default,
            "message": status_response.message,
        },
        next_steps=[
            f"Switch to the new project: adn_project('switch', project_name='{project_name}')",
            "Start adding content to your project",
            "Configure project settings if needed",
        ],
    )


async def _switch_operation(project_name: str | None, ctx: Context | None) -> dict:
    """Handle switch operation."""
    if not project_name:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_PROJECT_NAME",
            message="Switch operation requires project_name parameter",
            recovery_options=[
                "Provide project_name parameter",
                "Use adn_project('list') to see available projects",
                "Check project name spelling",
            ],
            example={"operation": "switch", "project_name": "work-project"},
            urgency="medium",
        )

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
            return build_error_response(
                error="Project not found",
                error_code="PROJECT_NOT_FOUND",
                message=f"Project '{project_name}' does not exist",
                recovery_options=[
                    "Use adn_project('list') to see available projects",
                    "Check project name spelling",
                    "Create the project first with adn_project('create', ...)",
                ],
                available_projects=available_projects,
                urgency="medium",
            )

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

            return build_success_response(
                operation="switch",
                summary=f"Successfully switched to project '{canonical_name}'",
                result={
                    "project_name": canonical_name,
                    "project_permalink": target_project.permalink,
                    "statistics": {
                        "total_entities": project_info.statistics.total_entities,
                        "total_observations": project_info.statistics.total_observations,
                        "total_relations": project_info.statistics.total_relations,
                    },
                },
                next_steps=[
                    "Start working with content in this project",
                    "Use adn_content() to add or search for notes",
                    "Use other tools with this project's context",
                ],
            )

        except Exception as e:
            # If we can't get project info, still confirm the switch
            logger.warning(f"Could not get project info for {canonical_name}: {e}")
            return build_success_response(
                operation="switch",
                summary=f"Successfully switched to project '{canonical_name}'",
                result={
                    "project_name": canonical_name,
                    "project_permalink": target_project.permalink,
                    "statistics": None,  # Could not retrieve
                },
                next_steps=[
                    "Project switched successfully",
                    "Statistics temporarily unavailable",
                    "Try adn_project('get_current') for project details",
                ],
            )

    except Exception as e:
        logger.error(f"Error switching to project {project_name}: {e}")
        # Revert to previous project on error
        session.set_current_project(current_project)

        # Return user-friendly error message instead of raising exception
        return dedent(f"""
            # Project Switch Failed

            Could not switch to project '{project_name}': {e!s}

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


async def _delete_operation(project_name: str | None, ctx: Context | None) -> dict:
    """Handle delete operation."""
    if not project_name:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_PROJECT_NAME",
            message="Delete operation requires project_name parameter",
            recovery_options=[
                "Provide project_name parameter",
                "Use adn_project('list') to see available projects",
                "Check project name spelling",
            ],
            example={"operation": "delete", "project_name": "old-project"},
            urgency="medium",
        )

    if ctx:  # pragma: no cover
        await ctx.info(f"Deleting project: {project_name}")

    current_project = session.get_current_project()

    # Check if trying to delete current project
    if project_name == current_project:
        return build_error_response(
            error="Cannot delete active project",
            error_code="CANNOT_DELETE_ACTIVE_PROJECT",
            message=f"Cannot delete the currently active project '{project_name}'",
            recovery_options=[
                "Switch to a different project first",
                "Use adn_project('switch', project_name='other-project')",
                "Then retry the delete operation",
            ],
            current_project=current_project,
            urgency="medium",
        )

    # Get project info before deletion to validate it exists
    response = await call_get(client, "/projects/projects")
    project_list = ProjectList.model_validate(response.json())

    # Check if project exists
    project_exists = any(p.name == project_name for p in project_list.projects)
    if not project_exists:
        available_projects = [p.name for p in project_list.projects]
        return build_error_response(
            error="Project not found",
            error_code="PROJECT_NOT_FOUND",
            message=f"Project '{project_name}' does not exist",
            recovery_options=[
                "Use adn_project('list') to see available projects",
                "Check project name spelling",
                "Create the project first with adn_project('create', ...)",
            ],
            available_projects=available_projects,
            urgency="medium",
        )

    # Call API to delete project
    response = await call_delete(client, f"/projects/{project_name}")
    status_response = ProjectStatusResponse.model_validate(response.json())

    deleted_project = None
    if status_response.old_project:
        deleted_project = {
            "name": status_response.old_project.name,
            "path": getattr(status_response.old_project, "path", None),
        }

    return build_success_response(
        operation="delete",
        summary=status_response.message,
        result={
            "project_deleted": bool(status_response.old_project),
            "deleted_project": deleted_project,
            "message": status_response.message,
            "files_preserved": True,
        },
        next_steps=[
            "Files remain on disk at the original location",
            "Re-create the project if you want to access the content again",
            "Use adn_project('create', ...) to re-add the project",
        ],
    )


async def _set_default_operation(project_name: str | None, ctx: Context | None) -> dict:
    """Handle set_default operation."""
    if not project_name:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_PROJECT_NAME",
            message="Set_default operation requires project_name parameter",
            recovery_options=[
                "Provide project_name parameter",
                "Use adn_project('list') to see available projects",
                "Check project name spelling",
            ],
            example={"operation": "set_default", "project_name": "personal-notes"},
            urgency="medium",
        )

    if ctx:  # pragma: no cover
        await ctx.info(f"Setting default project to: {project_name}")

    # Call API to set default project
    response = await call_put(client, f"/projects/{project_name}/default")
    status_response = ProjectStatusResponse.model_validate(response.json())

    previous_default = None
    if status_response.old_project:
        previous_default = status_response.old_project.name

    return build_success_response(
        operation="set_default",
        summary=status_response.message,
        result={
            "new_default_project": project_name,
            "previous_default_project": previous_default,
            "message": status_response.message,
            "restart_required": True,
        },
        next_steps=[
            "Restart Advanced Memory for changes to take effect",
            "Run: basic-memory mcp",
            "The new default project will be loaded automatically",
        ],
    )


async def _get_current_operation(ctx: Context | None) -> dict:
    """Handle get_current operation."""
    if ctx:  # pragma: no cover
        await ctx.info("Getting current project information")

    current_project = session.get_current_project()

    # get project stats (use permalink in URL path)
    current_project_permalink = generate_permalink(current_project)
    response = await call_get(
        client,
        f"/{current_project_permalink}/project/info",
        params={"project_name": current_project},
    )
    project_info = ProjectInfoResponse.model_validate(response.json())

    default_project = session.get_default_project()

    return build_success_response(
        operation="get_current",
        summary=f"Current project is '{current_project}'",
        result={
            "current_project": current_project,
            "project_permalink": current_project_permalink,
            "statistics": {
                "total_entities": project_info.statistics.total_entities,
                "total_observations": project_info.statistics.total_observations,
                "total_relations": project_info.statistics.total_relations,
            },
            "default_project": default_project,
            "is_default": current_project == default_project,
        },
        next_steps=[
            "Use adn_content() to add or search for notes in this project",
            "Use other tools with this project's context",
            "Switch to a different project if needed",
        ],
    )


async def _list_operation(ctx: Context | None) -> dict:
    """Handle list operation."""
    if ctx:  # pragma: no cover
        await ctx.info("Listing all available projects")

    # Get projects from API
    response = await call_get(client, "/projects/projects")
    project_list = ProjectList.model_validate(response.json())

    current = session.get_current_project()

    projects = []
    for project in project_list.projects:
        indicators = []
        if project.name == current:
            indicators.append("current")
        if project.is_default:
            indicators.append("default")

        projects.append(
            {
                "name": project.name,
                "permalink": project.permalink,
                "indicators": indicators,
                "is_current": project.name == current,
                "is_default": project.is_default,
            }
        )

    return build_success_response(
        operation="list",
        summary=f"Found {len(projects)} available projects",
        result={"projects": projects, "current_project": current, "total_projects": len(projects)},
        next_steps=[
            "Use adn_project('switch', project_name='name') to switch to a project",
            "Use adn_project('get_current') to see details of current project",
        ],
    )


async def _sync_operation(project_name: str | None, ctx: Context | None) -> dict:
    """Handle sync operation - sync a specific project without changing default."""
    if not project_name:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_PROJECT_NAME",
            message="Sync operation requires project_name parameter",
            recovery_options=[
                "Provide project_name parameter",
                "Use adn_project('list') to see available projects",
                "Check project name spelling",
            ],
            example={"operation": "sync", "project_name": "my-project"},
            urgency="medium",
        )

    if ctx:  # pragma: no cover
        await ctx.info(f"Syncing project: {project_name}")

    try:
        # Call the new project-specific sync endpoint
        response = await call_post(client, f"/projects/{project_name}/sync")
        sync_response = response.json()

        return build_success_response(
            operation="sync",
            summary=f"Project '{project_name}' synced successfully",
            result={
                "project_synced": project_name,
                "files_processed": sync_response.get("files_synced", 0),
                "sync_details": sync_response,
            },
            next_steps=[
                "Project content is now up to date",
                "Use adn_content() to work with synced content",
                "Check sync status if needed",
            ],
        )

    except Exception as e:
        return build_error_response(
            error="Sync failed",
            error_code="SYNC_ERROR",
            message=f"Failed to sync project '{project_name}': {e!s}",
            recovery_options=[
                "Verify the project exists",
                "Use adn_project('list') to see available projects",
                "Check project path and permissions",
                "Try syncing again",
            ],
            diagnostic_info={"project_name": project_name, "error_details": str(e)},
            urgency="medium",
        )


async def _status_operation(project_name: str | None, ctx: Context | None) -> dict:
    """Handle status operation - get detailed statistics for a specific project."""
    if not project_name:
        return build_error_response(
            error="Missing required parameter",
            error_code="MISSING_PROJECT_NAME",
            message="Status operation requires project_name parameter",
            recovery_options=[
                "Provide project_name parameter",
                "Use adn_project('list') to see available projects",
                "Check project name spelling",
            ],
            example={"operation": "status", "project_name": "my-project"},
            urgency="medium",
        )

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

        return build_success_response(
            operation="status",
            summary=f"Project '{project_name}' status retrieved",
            result={
                "project": {
                    "name": project_info.name,
                    "path": project_info.path,
                    "permalink": project_info.permalink,
                    "is_default": project_info.is_default,
                },
                "statistics": {
                    "total_entities": project_info.statistics.total_entities,
                    "total_observations": project_info.statistics.total_observations,
                    "total_relations": project_info.statistics.total_relations,
                },
            },
            next_steps=[
                "Use adn_content() to work with project content",
                "Use adn_project('switch') to switch to this project",
                "Check sync status if needed",
            ],
        )

    except Exception as e:
        return build_error_response(
            error="Status retrieval failed",
            error_code="STATUS_ERROR",
            message=f"Failed to get status for project '{project_name}': {e!s}",
            recovery_options=[
                "Verify the project exists",
                "Use adn_project('list') to see available projects",
                "Check project permissions",
                "Try again later",
            ],
            diagnostic_info={"project_name": project_name, "error_details": str(e)},
            urgency="medium",
        )


async def _detect_operation(ctx: Context | None) -> dict:
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

    detection_result = {
        "current_project": current_project,
        "suggested_project": suggested_project,
        "confidence": confidence,
        "reason": reason,
        "should_switch": should_switch,
        "auto_switched": False,
        "switch_error": None,
    }

    if suggested_project:
        if should_switch and suggested_project != current_project:
            # Auto-switch if confidence is high enough
            try:
                switch_result = await _switch_operation(suggested_project, ctx)
                detection_result["auto_switched"] = True
                detection_result["switch_result"] = switch_result
            except Exception as e:
                detection_result["switch_error"] = str(e)
        elif suggested_project == current_project:
            detection_result["already_on_project"] = True
    else:
        # No clear project detected, provide available projects
        projects = await detector._get_all_projects()
        detection_result["available_projects"] = projects

    return build_success_response(
        operation="detect",
        summary="AI-managed project detection completed",
        result=detection_result,
        next_steps=[
            "Continue working in the detected/suggested project",
            "Use adn_project('switch') if you want to change projects manually",
            "The AI will continue to detect project context from your queries",
        ],
    )
