"""Automation Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates agentic and batch operations: workflow, batch, sampling status.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import AutomationOperation


@mcp.tool(name="adn_automation")
async def adn_automation(op: AutomationOperation, ctx: Any = None) -> Any:
    """
    Autonomous orchestration and batch intelligence for Advanced Memory.

    This tool enables high-level agentic workflows and intelligent batch
    processing, allowing the system to achieve complex multi-step goals via
    automated tool orchestration and LLM sampling.

    ---------------------------------------------------------------------------
    [RATIONALE]
    Complex tasks often require multiple tool calls and intermediate reasoning.
    By providing an 'Automation' entry point, we allow the AI to trigger
    autonomous sub-agents (Workflows) that can handle research, consolidation,
    and cross-server coordination without constant user intervention.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - workflow: Autonomous execution of complex goals via multi-step orchestration.
    - batch: Intelligent processing of multiple items (e.g., 'Tag all these notes').
    - status: Reports on the health and capabilities of the sampling engine.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The automation task (workflow, batch, status).
    - goal (str, optional): The high-level objective or processing prompt.
    - items (list, optional): List of note identifiers or URLs for batch processing.
    - tools (list, optional): Subset of tools allowed for the autonomous agent.
    - iterations (int, optional): Maximum steps for a workflow (default 5).

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Process a batch of notes for a specific goal
    adn_automation(
        operation="batch",
        items=["Note A", "Note B", "Note C"],
        goal="Extract key dates and add them to the 'Timeline' note."
    )

    # Trigger a 10-step autonomous research workflow
    adn_automation(
        operation="workflow",
        goal="Find all references to 'Quantum' and build a skills matrix.",
        iterations=10
    )
    ```
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_automation operation={operation}")

    from advanced_memory.mcp.tools.inter_server_tools import (
        agentic_content_workflow,
        intelligent_batch_processor,
        sampling_capabilities_status,
    )

    if operation == "workflow":
        return await agentic_content_workflow(
            workflow_prompt=op.goal,
            available_tools=op.tools or ["full"],
            max_iterations=op.iterations or 5,
            ctx=ctx
        )
    elif operation == "batch":
        return await intelligent_batch_processor(
            items=op.items,
            processing_goal=op.goal,
            available_operations=op.tools or ["full"],
            ctx=ctx
        )
    elif operation == "status":
        return await sampling_capabilities_status(ctx=ctx)
    else:
        return f"Error: Unsupported operation {operation}"
