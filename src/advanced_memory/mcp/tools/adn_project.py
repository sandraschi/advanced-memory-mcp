"""Project Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all project management operations: create, switch, delete, list, status, detect.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import ProjectOperation
from advanced_memory.mcp.tools.utils import build_error_response


@mcp.tool(name="adn_project")
async def adn_project(op: ProjectOperation) -> Any:
    """
    Comprehensive project and environment management for Advanced Memory.

    This tool manages the lifecycle and active context of projects, enabling
    seamless switching between different knowledge silos and repositories.

    ---------------------------------------------------------------------------
    [RATIONALE]
    Advanced Memory operates within a 'Project Context' that scopes all search,
    note, and audio operations. By consolidating these management tasks, we
    provide a stable control plane for the environment, ensuring that the AI
    is always grounded in the correct directory and metadata schema.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - ls: Lists all registered projects with their health and session status.
    - create: Initializes a new project and links it to a filesystem directory.
    - switch: Activates a different project context for all subsequent tools.
    - rm: Removes a project configuration (files on disk are preserved).
    - status: Displays detailed statistics and synchronization health.
    - detect: Automatically identifies and switches to the most relevant project.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The management task (ls, create, switch, rm, status, detect).
    - name (str, optional): Unique hyphen-case identifier for the project.
    - path (str, optional): Absolute filesystem path to the project root.
    - set_default (bool, optional): If true, loads this project on startup.

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Initialize a new repository as a project
    adn_project(operation="create", name="chrono-glenn", path="C:/Users/sandr/dev/chrono-glenn")

    # Switch context to an existing project
    adn_project(operation="switch", name="antigravity-fleet")
    ```
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_project operation={operation}")

    # Import internal operation handlers from project_manager
    from advanced_memory.mcp.tools.project_manager import (
        _create_operation,
        _delete_operation,
        _detect_operation,
        _list_operation,
        _status_operation,
        _switch_operation,
    )

    if operation == "ls":
        return await _list_operation(None)
    elif operation == "create":
        return await _create_operation(op.name, op.path, op.set_default, None)
    elif operation == "switch":
        return await _switch_operation(op.name, None)
    elif operation == "rm":
        return await _delete_operation(op.name, None)
    elif operation == "status":
        return await _status_operation(op.name, None)
    elif operation == "detect":
        return await _detect_operation(None)
    else:
        return build_error_response(
            error="Unsupported operation",
            error_code="INVALID_OPERATION",
            message=f"Operation {operation} is not supported.",
        )
