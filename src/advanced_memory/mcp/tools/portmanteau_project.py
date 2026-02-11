"""Portmanteau tool for project management operations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 8+ project management operations
including creation, deletion, switching, listing, and project-specific operations
into a single tool. Project management has clear boundaries and benefits from
consolidation while maintaining operational clarity.
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


@mcp.tool
async def adn_project(
    operation: Annotated[
        Literal[
            "create",
            "delete",
            "list",
            "switch",
            "current",
            "set_default",
            "sync",
            "status",
            "inbox",
        ],
        Field(description="Project management operation to perform"),
    ],
    name: Annotated[str | None, Field(description="Project name")] = None,
    path: Annotated[str | None, Field(description="Project filesystem path")] = None,
    set_default: Annotated[bool | None, Field(description="Set as default project")] = None,
    description: Annotated[str | None, Field(description="Project description")] = None,
) -> dict:
    """Unified portmanteau tool for all project management operations.

    This tool consolidates project lifecycle management:
    - Project creation, deletion, and configuration
    - Project switching and default management
    - Project listing and status monitoring
    - Project-specific inbox management

    Args:
        operation: The specific project operation to perform
        name: Project name for targeted operations
        path: Filesystem path for project creation
        set_default: Whether to set project as default
        description: Project description for creation

    Returns:
        Operation result with project information

    Examples:
        # Create new project
        adn_project("create", name="research", path="/path/to/research", description="Research notes")

        # List all projects
        adn_project("list")

        # Switch to different project
        adn_project("switch", name="research")

        # Get current project
        adn_project("current")

        # Set default project
        adn_project("set_default", name="main")

        # Delete project
        adn_project("delete", name="old-project")
    """
    try:
        if operation == "create":
            if not name or not path:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Name and path required for project creation",
                )

            from advanced_memory.mcp.tools.project_management import create_memory_project

            result = await create_memory_project.fn(
                name, path, description or "", set_default or False
            )
            return build_success_response("create", result)

        elif operation == "delete":
            if not name:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Project name required for deletion"
                )

            from advanced_memory.mcp.tools.project_management import delete_project

            result = await delete_project.fn(name)
            return build_success_response("delete", result)

        elif operation == "list":
            from advanced_memory.mcp.tools.project_management import list_memory_projects

            result = await list_memory_projects.fn()
            return build_success_response("list", result)

        elif operation == "switch":
            if not name:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Project name required for switching"
                )

            from advanced_memory.mcp.tools.project_management import switch_project

            result = await switch_project.fn(name)
            return build_success_response("switch", result)

        elif operation == "current":
            from advanced_memory.mcp.tools.project_management import get_current_project

            result = await get_current_project.fn()
            return build_success_response("current", result)

        elif operation == "set_default":
            if not name:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Project name required for setting default",
                )

            from advanced_memory.mcp.tools.project_management import set_default_project

            result = await set_default_project.fn(name)
            return build_success_response("set_default", result)

        elif operation == "sync":
            from advanced_memory.mcp.tools.sync_status import sync_status

            result = await sync_status.fn()
            return build_success_response("sync", result)

        elif operation == "status":
            from advanced_memory.mcp.tools.status import status

            result = await status.fn("intermediate", "projects")
            return build_success_response("status", result)

        elif operation == "inbox":
            from advanced_memory.mcp.tools.adn_inbox import adn_inbox

            result = await adn_inbox.fn("status")
            return build_success_response("inbox", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unknown project operation: {operation}"
            )

    except Exception as e:
        logger.error(f"Project operation '{operation}' failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {str(e)}"
        )
