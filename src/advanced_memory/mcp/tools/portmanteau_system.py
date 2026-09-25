"""Portmanteau tool for system management and external integrations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 8+ system-level operations including
status monitoring, external MCP server communication, inter-server tools, and
system utilities into a single tool. System operations have well-defined boundaries
and benefit from consolidation while maintaining operational clarity.
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


# @mcp.tool  # Decommissioned in favor of namespaced system app (FastMCP 3.2 GA)
async def adn_system(
    operation: Annotated[
        Literal[
            "status",
            "sync_status",
            "external_call",
            "inter_server",
            "sampling_status",
            "batch_process",
            "workflow",
            "help",
            "restart",
        ],
        Field(description="System operation to perform"),
    ],
    level: Annotated[str | None, Field(description="Status detail level")] = None,
    focus: Annotated[str | None, Field(description="Status focus area")] = None,
    server_name: Annotated[str | None, Field(description="External server name")] = None,
    tool_name: Annotated[str | None, Field(description="External tool name")] = None,
    parameters: Annotated[dict | None, Field(description="Tool parameters")] = None,
    topic: Annotated[str | None, Field(description="Topic for operations")] = None,
    confirm: Annotated[bool, Field(description="Must be true to actually restart")] = False,
    tools: Annotated[
        list[str] | None, Field(description="Tool names available to the sampling agent (inter_server)")
    ] = None,
    max_iterations: Annotated[int, Field(description="Max sampling loop iterations (inter_server)")] = 5,
    items: Annotated[
        list[dict] | None, Field(description="Items to process, e.g. [{'title': '...'}] (batch_process)")
    ] = None,
    operations: Annotated[
        list[str] | None, Field(description="Knowledge operations available for batch processing")
    ] = None,
    strategy: Annotated[str, Field(description="'parallel' or 'sequential' (batch_process)")] = "parallel",
    ctx: object = None,  # FastMCP injects Context here for sampling operations
) -> dict:
    """Unified portmanteau for system management and external integrations.

    Operations: status, sync_status, external_call, inter_server,
    sampling_status, batch_process, workflow, help.

    For full documentation on parameters and usage examples, call:
    `help(topic="adn_system")`
    """
    try:
        if operation == "status":
            from advanced_memory.mcp.tools.status import status as _status_fn

            result = await _status_fn(level or "basic", focus)
            return build_success_response("status", result)

        elif operation == "sync_status":
            from advanced_memory.mcp.tools.sync_status import sync_status as _ss_fn

            result = await _ss_fn()
            return build_success_response("sync_status", result)

        elif operation == "external_call":
            if not server_name or not tool_name:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Server name and tool name required for external calls",
                )

            from advanced_memory.mcp.tools.external_mcp_clients import (
                external_mcp_clients as _emc,
            )

            result = await _emc(
                operation="call",
                server_name=server_name,
                tool_name=tool_name,
                parameters=parameters or {},
            )
            return build_success_response("external_call", result)

        elif operation == "inter_server":
            if not topic:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Topic required for inter-server operations",
                )

            from advanced_memory.mcp.tools.inter_server_tools import (
                agentic_content_workflow as _acw,
            )

            # _acw is the raw async coroutine function — call it directly
            result = await _acw(
                workflow_prompt=topic,
                available_tools=tools or ["full"],
                max_iterations=max_iterations,
                ctx=ctx,
            )
            return build_success_response("inter_server", result)

        elif operation == "sampling_status":
            from advanced_memory.mcp.tools.inter_server_tools import (
                sampling_capabilities_status as _scs,
            )

            result = await _scs(ctx=ctx)
            return build_success_response("sampling_status", result)

        elif operation == "batch_process":
            if not topic:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Processing goal (topic) required for batch processing",
                )
            if not items:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "items required for batch processing, e.g. [{'title': 'Note A'}, {'title': 'Note B'}]",
                )

            from advanced_memory.mcp.tools.inter_server_tools import (
                intelligent_batch_processor as _ibp,
            )

            result = await _ibp(
                items=items,
                processing_goal=topic,
                available_operations=operations or ["full"],
                batch_strategy=strategy,
                ctx=ctx,
            )
            return build_success_response("batch_process", result)

        elif operation == "workflow":
            if not topic:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Topic required for workflow operations",
                )

            from advanced_memory.mcp.tools.inter_server_tools import (
                agentic_content_workflow as _acw2,
            )

            result = await _acw2(
                workflow_prompt=topic,
                available_tools=["full"],
                ctx=ctx,
            )
            return build_success_response("workflow", result)

        elif operation == "help":
            from advanced_memory.mcp.tools.help import help as _help_fn

            result = await _help_fn(level or "basic", topic)
            return build_success_response("help", result)

        elif operation == "restart":
            if not confirm:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "CONFIRM_REQUIRED",
                    "restart requires confirm=true - this exits the current server process",
                )

            import os
            import threading

            pid = os.getpid()
            logger.warning(f"Restart requested via adn_system(restart) - process {pid} will exit shortly")

            # For an ordinary stdio instance (the common case this exists for:
            # a process that latched onto local-writer mode because its one-
            # shot startup probe to the HTTP daemon hit a bad moment, e.g. the
            # daemon mid-restart), exiting lets the MCP client respawn a fresh
            # process that re-probes and, if the daemon is healthy now,
            # correctly becomes a proxy instead of a second local writer.
            #
            # For an NSSM-managed instance, os._exit() is a clean process exit
            # (unlike an external taskkill), which NSSM's AppExit Default
            # Restart will respawn - but it bypasses the service control
            # manager's own stop protocol. Prefer `sc.exe stop`/`sc.exe start`
            # for those; this tool exists for the stdio-instance case, not as
            # a replacement for it.
            #
            # Delayed exit on a background thread so this response has a
            # chance to actually reach the caller before the process dies -
            # an immediate os._exit() here could kill the process before the
            # MCP response is flushed.
            threading.Timer(0.5, os._exit, args=(0,)).start()

            return build_success_response(
                "restart",
                {
                    "pid": pid,
                    "message": f"Process {pid} exiting in ~0.5s. The MCP client should respawn a fresh instance on its next tool call.",
                },
            )

        else:
            return build_error_response(
                "VALIDATION_ERROR",
                "VALIDATION_ERROR",
                f"Unknown system operation: {operation}",
            )

    except Exception as e:
        logger.error(f"System operation '{operation}' failed: {e}")
        return build_error_response("VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {e!s}")
