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
        ],
        Field(description="System operation to perform"),
    ],
    level: Annotated[str | None, Field(description="Status detail level")] = None,
    focus: Annotated[str | None, Field(description="Status focus area")] = None,
    server_name: Annotated[str | None, Field(description="External server name")] = None,
    tool_name: Annotated[str | None, Field(description="External tool name")] = None,
    parameters: Annotated[dict | None, Field(description="Tool parameters")] = None,
    topic: Annotated[str | None, Field(description="Topic for operations")] = None,
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
                available_tools=["full"],
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
                    "Topic required for batch processing",
                )

            from advanced_memory.mcp.tools.inter_server_tools import (
                intelligent_batch_processor as _ibp,
            )

            result = await _ibp(
                items=[{"title": topic}],
                processing_goal=topic,
                available_operations=["full"],
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

        else:
            return build_error_response(
                "VALIDATION_ERROR",
                "VALIDATION_ERROR",
                f"Unknown system operation: {operation}",
            )

    except Exception as e:
        logger.error(f"System operation '{operation}' failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {e!s}"
        )
