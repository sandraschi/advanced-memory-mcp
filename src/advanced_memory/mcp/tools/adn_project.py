"""
Advanced Memory project management tools - FastMCP 2.12 compliant.

Complete CRUD toolset for managing multiple Advanced Memory projects.
"""

from mcp.server.fastmcp import Context

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.project_session import session
from advanced_memory.mcp.server import mcp
from advanced_memory.mcp.tools.utils import call_delete, call_get, call_post, call_put


@mcp.tool()
async def adn_project_create(
    name: str,
    path: str,
    set_as_default: bool = False,
    ctx: Context | None = None,
) -> str:
    '''
    Create a new Advanced Memory project.

    Creates a new project with the specified name and path. The project directory
    will be created if it doesn't exist. Optionally sets the new project as default.

    Args:
        name: Name for the new project (must be unique)
        path: File system path where the project will be stored
        set_as_default: Whether to set this project as the default (optional, defaults to False)

    Returns:
        Confirmation message with project details

    Example:
        adn_project_create("my-research", "~/Documents/research")
        adn_project_create("work-notes", "/home/user/work", set_as_default=True)
    '''

    try:
        data = {"name": name, "path": path, "set_default": set_as_default}
        await call_post(client, "/projects/projects", json=data)

        result = f"✅ Project '{name}' created successfully\n\n"
        result += f"📁 Path: {path}\n"

        if set_as_default:
            result += "⭐ Set as default project\n"

        result += "\n## Usage:\n"
        result += "```bash\n"
        result += "# Sync this project\n"
        result += f"advanced-memory --project={name} sync\n\n"
        result += "# Or set as default\n"
        result += f"adn_project_set_default(\"{name}\")\n"
        result += "```\n"

        result += f"\n\n<!-- Project: {session.get_current_project()} -->"
        return result

    except Exception as e:
        return f"❌ Error creating project: {str(e)}\n\n<!-- Project: {session.get_current_project()} -->"


@mcp.tool()
async def adn_project_list(ctx: Context | None = None) -> str:
    '''
    List all configured Advanced Memory projects.

    Shows all projects with their paths, default status, and entity counts.

    Returns:
        Formatted list of all projects with status indicators

    Example:
        adn_project_list()
    '''

    try:
        response = await call_get(client, "/projects/projects")
        projects = response.json()

        if not projects.get("projects"):
            return f"No projects configured.\n\n<!-- Project: {session.get_current_project()} -->"

        result = "# Advanced Memory Projects\n\n"
        result += "| Project | Path | Default | Entities |\n"
        result += "|---------|------|---------|----------|\n"

        for proj in projects["projects"]:
            name = proj["name"]
            path = proj["path"]
            is_default = "⭐" if proj.get("is_default") else ""
            # Would need API call to get entity count - skip for now or add later
            result += f"| {name} | {path} | {is_default} | - |\n"

        result += f"\n\n<!-- Project: {session.get_current_project()} -->"
        return result

    except Exception as e:
        return f"❌ Error listing projects: {str(e)}\n\n<!-- Project: {session.get_current_project()} -->"


@mcp.tool()
async def adn_project_sync(
    project_name: str,
    ctx: Context | None = None,
) -> str:
    '''
    Sync a specific project without changing the default.

    Indexes all markdown files in the project directory into the database.
    This operation does not change which project is set as default.

    Args:
        project_name: Name of the project to sync

    Returns:
        Sync results with file counts

    Example:
        adn_project_sync("myai")
        adn_project_sync("work-notes")
    '''

    try:
        # Call sync endpoint for specific project
        response = await call_post(client, f"/projects/{project_name}/sync")
        data = response.json()

        result = f"✅ Project '{project_name}' synced successfully\n\n"
        result += "📊 Results:\n"
        result += f"  - New files: {data.get('new', 0)}\n"
        result += f"  - Modified files: {data.get('modified', 0)}\n"
        result += f"  - Deleted files: {data.get('deleted', 0)}\n"
        result += f"  - Total changes: {data.get('total', 0)}\n"

        result += f"\n\n<!-- Project: {session.get_current_project()} -->"
        return result

    except Exception as e:
        result = f"❌ Error syncing project '{project_name}': {str(e)}\n\n"
        result += "Make sure the project exists. Use adn_project_list() to see all projects.\n"
        result += f"\n<!-- Project: {session.get_current_project()} -->"
        return result


@mcp.tool()
async def adn_project_set_default(
    project_name: str,
    ctx: Context | None = None,
) -> str:
    '''
    Set a project as the default.

    Changes which project loads by default when Advanced Memory starts.
    This affects all new sessions and connections.

    Args:
        project_name: Name of the project to set as default

    Returns:
        Confirmation message

    Example:
        adn_project_set_default("work-notes")
        adn_project_set_default("my-research")
    '''

    try:
        await call_put(client, f"/projects/{project_name}/default")

        result = f"✅ Project '{project_name}' set as default\n\n"
        result += "This project will now load automatically on startup.\n"

        result += f"\n\n<!-- Project: {session.get_current_project()} -->"
        return result

    except Exception as e:
        return f"❌ Error setting default project: {str(e)}\n\n<!-- Project: {session.get_current_project()} -->"


@mcp.tool()
async def adn_project_delete(
    project_name: str,
    ctx: Context | None = None,
) -> str:
    '''
    Delete a project from configuration and database.

    Removes a project from Advanced Memory management while preserving
    all files on disk. Cannot delete the currently active default project.

    Args:
        project_name: Name of the project to remove

    Returns:
        Confirmation message with file preservation notice

    Example:
        adn_project_delete("old-research")
        adn_project_delete("archived-project")
    '''

    try:
        await call_delete(client, f"/projects/{project_name}")

        result = f"✅ Project '{project_name}' removed from configuration\n\n"
        result += "📁 All markdown files remain on disk (not deleted)\n"
        result += "🗄️ Database records for this project have been removed\n\n"
        result += "To re-add this project later:\n"
        result += "```\n"
        result += f"adn_project_create(\"{project_name}\", \"<path>\")\n"
        result += "```\n"

        result += f"\n\n<!-- Project: {session.get_current_project()} -->"
        return result

    except Exception as e:
        return f"❌ Error deleting project: {str(e)}\n\n<!-- Project: {session.get_current_project()} -->"


@mcp.tool()
async def adn_project_status(
    project_name: str | None = None,
    ctx: Context | None = None,
) -> str:
    '''
    Get detailed status and statistics for a project.

    Shows entity count, file count, recent activity, and configuration
    for the specified project or current project if not specified.

    Args:
        project_name: Name of project (optional, uses current if not specified)

    Returns:
        Detailed project statistics and status

    Example:
        adn_project_status()
        adn_project_status("myai")
    '''

    try:
        if project_name:
            response = await call_get(client, f"/projects/{project_name}/status")
        else:
            response = await call_get(client, "/projects/current/status")

        data = response.json()

        result = f"# Project Status: {data.get('name', 'Unknown')}\n\n"
        result += f"📁 Path: {data.get('path', 'Unknown')}\n"
        result += f"📊 Entities: {data.get('entity_count', 0):,}\n"
        result += f"🔗 Relations: {data.get('relation_count', 0):,}\n"
        result += f"📝 Observations: {data.get('observation_count', 0):,}\n"

        if data.get('is_default'):
            result += "\n⭐ This is the default project\n"

        result += f"\n\n<!-- Project: {session.get_current_project()} -->"
        return result

    except Exception as e:
        return f"❌ Error getting project status: {str(e)}\n\n<!-- Project: {session.get_current_project()} -->"

