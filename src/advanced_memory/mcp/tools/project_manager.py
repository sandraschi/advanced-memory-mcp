"""Project Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all project management operations: create, switch, delete, set_default, get_current, and list.
It reduces the number of MCP tools while maintaining full functionality.
"""

from textwrap import dedent
from typing import Optional

from fastmcp import Context
from loguru import logger

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.project_session import session, add_project_metadata
from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.utils import call_get, call_put, call_post, call_delete
from advanced_memory.schemas import ProjectInfoResponse
from advanced_memory.schemas.project_info import ProjectList, ProjectStatusResponse, ProjectInfoRequest
from advanced_memory.utils import generate_permalink


@mcp.tool(
    description="""Comprehensive project management tool for Advanced Memory knowledge base.

This portmanteau tool consolidates all project operations into a single interface,
reducing MCP tool count while maintaining full functionality for Cursor IDE compatibility.

SUPPORTED OPERATIONS:
- **create**: Create new projects with specified name and path
- **switch**: Change active project context for all subsequent operations
- **delete**: Remove projects from configuration while preserving files on disk
- **set_default**: Configure which project loads by default on startup
- **get_current**: Display currently active project with comprehensive statistics
- **list**: List all available projects with status indicators

PROJECT CONTEXT IMPACT:
- All file operations target the active project
- Search operations are scoped to the active project
- Directory listings show the active project's structure
- New notes are created in the active project
- Sync status reflects the active project's state

PARAMETERS:
- operation (str, REQUIRED): Operation type (create, switch, delete, set_default, get_current, list)
- project_name (str): Name of the project for most operations
- project_path (str): File system path for create operations
- set_default (bool, default=False): Whether to set new project as default for create operations
- ctx (Context, optional): MCP context for progress reporting

VALIDATION:
- Projects must exist in configuration for most operations
- Project paths must be accessible
- Cannot delete currently active project (switch first)
- Automatic project initialization when needed

USAGE EXAMPLES:
Create project: adn_project("create", project_name="my-research", project_path="~/Documents/research")
Switch project: adn_project("switch", project_name="work-project")
List projects: adn_project("list")
Get current: adn_project("get_current")
Set default: adn_project("set_default", project_name="personal-notes")
Delete project: adn_project("delete", project_name="old-project")

RETURNS:
Operation-specific results with project details, statistics, and configuration status.

PROJECT PERSISTENCE:
- Project context persists for the current session
- All tools automatically use the active project
- Default project settings persist across server restarts
- No need to specify project parameter repeatedly in other tools

NOTE: This tool provides all project management functionality in a single interface for better MCP client compatibility.""",
)
async def adn_project(
    operation: str,
    project_name: Optional[str] = None,
    project_path: Optional[str] = None,
    set_default: bool = False,
    ctx: Context | None = None,
) -> str:
    """Comprehensive project management for Advanced Memory knowledge base.

    This portmanteau tool consolidates all project operations:
    - create: Create new projects with specified name and path
    - switch: Change active project context
    - delete: Remove projects from configuration
    - set_default: Configure default project for startup
    - get_current: Display current project with statistics
    - list: List all available projects with status

    Args:
        operation: The operation to perform (create, switch, delete, set_default, get_current, list)
        project_name: Name of the project for most operations
        project_path: File system path for create operations
        set_default: Whether to set new project as default for create operations
        ctx: Optional MCP context for progress reporting

    Returns:
        Operation-specific result with project details and statistics

    Examples:
        # Create a new project
        project_manager("create", project_name="my-research", project_path="~/Documents/research")

        # Switch to a different project
        project_manager("switch", project_name="work-project")

        # List all available projects
        project_manager("list")

        # Get current project information
        project_manager("get_current")

        # Set default project
        project_manager("set_default", project_name="personal-notes")

        # Delete a project
        project_manager("delete", project_name="old-project")
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
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: create, switch, delete, set_default, get_current, list"


async def _create_operation(
    project_name: Optional[str], project_path: Optional[str], set_default: bool, ctx: Context | None
) -> str:
    """Handle create operation."""
    if not project_name or not project_path:
        return "# Error\n\nCreate operation requires: project_name and project_path parameters"

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
        result += f"• Name: {status_response.new_project.name}\n"
        result += f"• Path: {status_response.new_project.path}\n"

        if set_default:
            result += "• Set as default project\n"

    result += "\nProject is now available for use.\n"

    # If project was set as default, update session
    if set_default:
        session.set_current_project(project_name)

    return add_project_metadata(result, session.get_current_project())


async def _switch_operation(project_name: Optional[str], ctx: Context | None) -> str:
    """Handle switch operation."""
    if not project_name:
        return "# Error\n\nSwitch operation requires: project_name parameter"

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
            result += f"• {project_info.statistics.total_entities} entities\n"
            result += f"• {project_info.statistics.total_observations} observations\n"
            result += f"• {project_info.statistics.total_relations} relations\n"

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


async def _delete_operation(project_name: Optional[str], ctx: Context | None) -> str:
    """Handle delete operation."""
    if not project_name:
        return "# Error\n\nDelete operation requires: project_name parameter"

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
        result += f"• Name: {status_response.old_project.name}\n"
        if hasattr(status_response.old_project, "path"):
            result += f"• Path: {status_response.old_project.path}\n"

    result += "Files remain on disk but project is no longer tracked by Advanced Memory.\n"
    result += "Re-add the project to access its content again.\n"

    return add_project_metadata(result, session.get_current_project())


async def _set_default_operation(project_name: Optional[str], ctx: Context | None) -> str:
    """Handle set_default operation."""
    if not project_name:
        return "# Error\n\nSet_default operation requires: project_name parameter"

    if ctx:  # pragma: no cover
        await ctx.info(f"Setting default project to: {project_name}")

    # Call API to set default project
    response = await call_put(client, f"/projects/{project_name}/default")
    status_response = ProjectStatusResponse.model_validate(response.json())

    result = f"✓ {status_response.message}\n\n"
    result += "Restart Advanced Memory for this change to take effect:\n"
    result += "advanced-memory mcp\n"

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

    result += f"• {project_info.statistics.total_entities} entities\n"
    result += f"• {project_info.statistics.total_observations} observations\n"
    result += f"• {project_info.statistics.total_relations} relations\n"

    default_project = session.get_default_project()
    if current_project != default_project:
        result += f"• Default project: {default_project}\n"

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
            result += f"• {project.name} ({', '.join(indicators)})\n"
        else:
            result += f"• {project.name}\n"

    return add_project_metadata(result, current)
