"""System Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates system-level operations: status, help, workflow, external bridge, and sync.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from fastmcp import Context
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import SystemOperation


@mcp.tool(name="adn_system")
async def adn_system(op: SystemOperation, ctx: Context | None = None) -> Any:
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
    - inter_server: Agentic multi-tool workflow via FastMCP sampling
      (SEP-1577) - the client's own LLM chooses and chains tool calls to
      satisfy a goal. Requires a sampling-capable client; check
      sampling_status first if unsure.
    - sampling_status: Reports whether the current client session supports
      sampling-with-tools. Call before inter_server/batch_process if unsure.
    - batch_process: Intelligent processing over a list of items - the
      client's LLM picks the right operation per item via sampling.
    - restart: Exits this server process (confirm=true required) so the MCP
      client respawns a fresh one. Use when this instance is stuck as a
      local writer instead of proxying to the HTTP daemon (check status
      first: "Stdio lock: held by this instance" + "Role: writer" on a
      stdio-transport instance is the sign) - a fresh process re-runs its
      startup probe against the daemon. Not a replacement for `sc.exe
      stop`/`start` on an NSSM-managed instance.

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
    - tools (list[str], optional): Tool names available to the sampling agent (inter_server).
    - max_iterations (int, optional): Max sampling loop iterations, default 5 (inter_server).
    - items (list[dict], optional): Items to process, e.g. [{'title': 'Note A'}] (batch_process).
    - operations (list[str], optional): Knowledge operations available (batch_process).
    - strategy (str, optional): 'parallel' or 'sequential', default 'parallel' (batch_process).
    - confirm (bool, optional): Must be true to actually restart (restart).

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

    # Batch-process a set of notes with the client's own LLM choosing the operation per item
    adn_system(
        operation="batch_process",
        items=[{"title": "Note A"}, {"title": "Note B"}],
        goal="Tag each note with its primary topic and add a one-line summary observation.",
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
            ctx=ctx,
        )
    elif operation == "external_bridge":
        return await _adn_system_impl(
            operation="external_call", server_name=op.server, tool_name=op.tool, parameters=op.args
        )
    elif operation == "sync":
        return await _adn_system_impl(operation="sync_status")
    elif operation == "reindex":
        from advanced_memory.mcp.tools.adn_search import _rag_reindex

        return await _rag_reindex(op.project, "full")
    elif operation == "restart":
        return await _adn_system_impl(operation="restart", confirm=op.confirm)
    elif operation == "inter_server":
        return await _adn_system_impl(
            operation="inter_server",
            topic=op.goal,
            tools=op.tools,
            max_iterations=op.max_iterations,
            ctx=ctx,
        )
    elif operation == "sampling_status":
        return await _adn_system_impl(operation="sampling_status", ctx=ctx)
    elif operation == "batch_process":
        return await _adn_system_impl(
            operation="batch_process",
            topic=op.goal,
            items=op.items,
            operations=op.operations,
            strategy=op.strategy,
            ctx=ctx,
        )
    else:
        return f"Error: Unsupported operation {operation}"
