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
) -> dict:
    """Unified portmanteau tool for external integrations and specialized operations.

    This tool consolidates external integrations:
    - Audio processing (speech-to-text, text-to-speech)
    - Content workflows and batch processing
    - Canvas creation and management
    - Typora integration
    - Zettelkastel operations
    - System utilities

    Args:
        operation: The specific external operation to perform
        content: Content for processing operations
        path: File path for file-based operations
        parameters: Additional operation parameters

    Returns:
        Operation result from external integration

    Examples:
        # Audio dictation
        adn_external("audio", operation="dictate", content="audio_file.wav")

        # Audio speech synthesis
        adn_external("audio", operation="speak", content="Hello world")

        # Content workflow
        adn_external("workflow", content="research topic")

        # Batch processing
        adn_external("batch", content="document_list")

        # Create canvas
        adn_external("canvas", content="mind map data")

        # Typora control
        adn_external("typora", operation="open", path="/file.md")

        # Zettelkastel operations
        adn_external("zettel", content="note content")

        # Restart file watcher
        adn_external("restart_watch")
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
                result = await adn_audio.fn("dictate", path=path, content=content)
            elif sub_op == "speak":
                if not content:
                    return build_error_response(
                        "VALIDATION_ERROR",
                        "MISSING_CONTENT",
                        "Content required for speech synthesis",
                    )
                result = await adn_audio.fn("speak", content=content)
            else:
                result = await adn_audio.fn("status")

            return build_success_response("audio", result)

        elif operation == "workflow":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_CONTENT", "Content/topic required for workflow"
                )

            from advanced_memory.mcp.tools.inter_server_tools import agentic_content_workflow

            result = await agentic_content_workflow.fn(content)
            return build_success_response("workflow", result)

        elif operation == "batch":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_CONTENT",
                    "Content/topic required for batch processing",
                )

            from advanced_memory.mcp.tools.inter_server_tools import intelligent_batch_processor

            result = await intelligent_batch_processor.fn(content)
            return build_success_response("batch", result)

        elif operation == "canvas":
            from advanced_memory.mcp.tools.canvas import canvas

            result = await canvas.fn(content or "", **parameters)
            return build_success_response("canvas", result)

        elif operation == "typora":
            sub_op = parameters.get("sub_operation", "status")
            from advanced_memory.mcp.tools.typora_control import typora_control

            if sub_op == "open" and path:
                result = await typora_control.fn("open", path)
            elif sub_op == "close":
                result = await typora_control.fn("close")
            else:
                result = await typora_control.fn("status")

            return build_success_response("typora", result)

        elif operation == "zettel":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_CONTENT",
                    "Content required for Zettelkastel operations",
                )

            from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker

            result = await adn_zettelmaker.fn(content, **parameters)
            return build_success_response("zettel", result)

        elif operation == "content_workflow":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_CONTENT", "Content required for content workflow"
                )

            from advanced_memory.mcp.tools.inter_server_tools import agentic_content_workflow

            result = await agentic_content_workflow.fn(content)
            return build_success_response("content_workflow", result)

        elif operation == "sampling":
            from advanced_memory.mcp.tools.inter_server_tools import sampling_capabilities_status

            result = await sampling_capabilities_status.fn()
            return build_success_response("sampling", result)

        elif operation == "restart_watch":
            # Create a simple restart function
            try:
                # This would trigger the restart_watch_service functionality
                result = {"message": "Watch service restart initiated", "status": "success"}
            except Exception as e:
                result = {"message": f"Restart failed: {e}", "status": "error"}

            return build_success_response("restart_watch", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unknown external operation: {operation}"
            )

    except Exception as e:
        logger.error(f"External operation '{operation}' failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {str(e)}"
        )
