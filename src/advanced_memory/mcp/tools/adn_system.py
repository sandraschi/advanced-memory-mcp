"""System Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates system-level operations: status, help, workflow, external bridge, and sync.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import SystemOperation


@mcp.tool(name="adn_system")
async def adn_system(op: SystemOperation) -> Any:
    """
    Central control plane and orchestration for the Antigravity fleet.

    This tool provides the infrastructure for autonomous workflows, system
    observability, and cross-server communication via the External MCP Bridge.

    ---------------------------------------------------------------------------
    [RATIONALE]
    A SOTA agentic system needs a unified way to monitor its own health, access
    its internal documentation, and orchestrate complex multi-tool goals.
    By consolidating these system tasks, we provide a single 'System' entry point
    that can act as a master controller for both internal and external tools.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - status: Comprehensive report on environment health, DB status, and config.
    - help: Accesses the high-fidelity documentation library and usage guides.
    - workflow: Triggers the autonomous execution engine to solve complex goals.
    - external_bridge: Enables Advanced Memory to call tools on OTHER MCP servers.
    - sync: Reports on the real-time file synchronization and indexing engine.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The system task (status, help, workflow, external_bridge, sync).
    - level (str, optional): Detail depth for status/help ('basic', 'detailed', 'expert').
    - focus (str, optional): Specific area for status reports (e.g., 'db', 'audio').
    - topic (str, optional): Subject for help documentation.
    - goal (str, optional): The high-level objective for an autonomous workflow.
    - server (str, optional): Target external MCP server (e.g., 'speech-mcp').
    - tool (str, optional): Specific tool to call on the external server.
    - args (dict, optional): JSON parameters for the external tool call.

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Trigger an autonomous workflow to consolidate research
    adn_system(operation="workflow", goal="Summarize all notes on 'Chrono-Glenn' and create a skill.")

    # Call a tool on another MCP server via the bridge
    adn_system(
        operation="external_bridge",
        server="browser-mcp",
        tool="search_web",
        args={"query": "FastMCP 3.2 release notes"}
    )
    ```
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_system operation={operation}")

    from advanced_memory.mcp.tools.portmanteau_system import adn_system as _adn_system_impl

    if operation == "status":
        return await _adn_system_impl(operation="status", level=op.level, focus=op.focus)
    elif operation == "help":
        return await _adn_system_impl(operation="help", topic=op.topic, level=op.level)
    elif operation == "workflow":
        return await _adn_system_impl(
            operation="workflow",
            topic=op.goal,
            ctx=None,  # Context injection happens at implementation level if needed
        )
    elif operation == "external_bridge":
        return await _adn_system_impl(
            operation="external_call", server_name=op.server, tool_name=op.tool, parameters=op.args
        )
    elif operation == "sync":
        return await _adn_system_impl(operation="sync_status")
    else:
        return f"Error: Unsupported operation {operation}"
