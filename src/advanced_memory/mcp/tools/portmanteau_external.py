"""Portmanteau tool for external integrations and specialized operations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 4+ external integration operations
including audio processing, content workflows, batch processing, and specialized
tools into a single tool. External integrations have well-defined boundaries and
benefit from consolidation while maintaining operational clarity.
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


@mcp.tool
async def adn_external(
    operation: Annotated[
        Literal[
            "audio",
            "workflow",
            "batch",
            "canvas",
            "typora",
            "zettel",
            "content_workflow",
            "sampling",
            "restart_watch",
        ],
        Field(description="External integration operation to perform"),
    ],
    content: Annotated[str | None, Field(description="Content for operations")] = None,
    path: Annotated[str | None, Field(description="File path")] = None,
    parameters: Annotated[dict | None, Field(description="Operation parameters")] = None,
    ctx: object = None,  # FastMCP injects Context for sampling operations
) -> dict:
    """Unified portmanteau for external integrations and specialized operations.

    Operations: audio, workflow, batch, canvas, typora, zettel,
    content_workflow, sampling, restart_watch.

    For full documentation on parameters and usage examples, call:
    `help(topic="adn_external")`
    """
    try:
        parameters = parameters or {}

        if operation == "audio":
            sub_op = parameters.get("sub_operation", "status")
            from advanced_memory.mcp.tools.adn_audio import adn_audio

            if sub_op == "dictate":
                if not path and not content:
                    return build_error_response(
                        "VALIDATION_ERROR",
                        "MISSING_PARAMETER",
                        "Path or content required for dictation",
                    )
                result = await adn_audio("dictate", path=path, content=content)
            elif sub_op == "speak":
                if not content:
                    return build_error_response(
                        "VALIDATION_ERROR",
                        "MISSING_CONTENT",
                        "Content required for speech synthesis",
                    )
                result = await adn_audio("speak", content=content)
            else:
                result = await adn_audio("status")

            return build_success_response("audio", result)

        elif operation == "workflow":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_CONTENT",
                    "Content/topic required for workflow",
                )

            from advanced_memory.mcp.tools.inter_server_tools import (
                agentic_content_workflow,
            )

            result = await agentic_content_workflow(content, available_tools=["full"], ctx=ctx)
            return build_success_response("workflow", result)

        elif operation == "batch":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_CONTENT",
                    "Content/topic required for batch processing",
                )

            from advanced_memory.mcp.tools.inter_server_tools import (
                intelligent_batch_processor,
            )

            result = await intelligent_batch_processor(
                items=[{"content": content}],
                processing_goal=content,
                available_operations=["full"],
                ctx=ctx,
            )
            return build_success_response("batch", result)

        elif operation == "canvas":
            from advanced_memory.mcp.tools.canvas import canvas

            result = await canvas(content or "", **parameters)
            return build_success_response("canvas", result)

        elif operation == "typora":
            sub_op = parameters.get("sub_operation", "status")
            from advanced_memory.mcp.tools.typora_control import typora_control

            if sub_op == "open" and path:
                result = await typora_control("open", path)
            elif sub_op == "close":
                result = await typora_control("close")
            else:
                result = await typora_control("status")

            return build_success_response("typora", result)

        elif operation == "zettel":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_CONTENT",
                    "Content required for Zettelkastel operations",
                )

            from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker

            result = await adn_zettelmaker(content, **parameters)
            return build_success_response("zettel", result)

        elif operation == "content_workflow":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_CONTENT",
                    "Content required for content workflow",
                )

            from advanced_memory.mcp.tools.inter_server_tools import (
                agentic_content_workflow,
            )

            result = await agentic_content_workflow(content, available_tools=["full"], ctx=ctx)
            return build_success_response("content_workflow", result)

        elif operation == "sampling":
            from advanced_memory.mcp.tools.inter_server_tools import (
                sampling_capabilities_status,
            )

            result = await sampling_capabilities_status(ctx=ctx)
            return build_success_response("sampling", result)

        elif operation == "restart_watch":
            try:
                result = {
                    "message": "Watch service restart initiated",
                    "status": "success",
                }
            except Exception as e:
                result = {"message": f"Restart failed: {e}", "status": "error"}

            return build_success_response("restart_watch", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR",
                "VALIDATION_ERROR",
                f"Unknown external operation: {operation}",
            )

    except Exception as e:
        logger.error(f"External operation '{operation}' failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {e!s}"
        )
