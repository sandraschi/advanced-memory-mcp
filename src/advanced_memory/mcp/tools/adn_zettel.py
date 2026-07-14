"""Zettelkasten Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates Zettelkasten operations: generate, suggest, expand, analyze, connect, collect, customize.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import ZettelOperation


@mcp.tool(name="adn_zettel")
async def adn_zettel(op: ZettelOperation) -> Any:
    """
    Structured Zettelkasten 'Slip-box' management for Advanced Memory.

    This tool implements the Zettelkasten method for atomic knowledge management,
    enabling rapid capture, iterative expansion, and automated semantic linking
    of discrete thoughts.

    ---------------------------------------------------------------------------
    [RATIONALE]
    Effective long-term memory requires breaking complex information into
    'atomic' notes. By providing a dedicated Zettelkasten engine, we allow the
    AI to synthesize new insights, identify structural gaps in the user's
    knowledge (Slip-box analysis), and iteratively grow small ideas into
    comprehensive knowledge clusters.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - generate: Synthesizes atomic notes using structured templates or AI.
    - suggest: Discovery Engine - identifies gaps and proposes next topics.
    - expand: Horizontal Growth - iteratively develops notes into broader clusters.
    - analyze: Graph Analysis - evaluates the maturity and connectivity of the vault.
    - connect: Connection Engine - auto-discovers and links semantic relations.
    - collect: Rapid Capture - low-friction session for off-the-cuff insights.
    - customize: Adjusts the parameters of the generation pipeline.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The Zettel task (generate, suggest, expand, connect, etc.).
    - category (str, optional): Taxonomy category (e.g., 'developer', 'science').
    - topic (str, optional): Specific subject or keyword for new notes.
    - note_identifier (str, optional): Title or permalink of an existing note to develop.
    - depth (int, optional): Iteration depth for expansion (1-5).
    - quality (str, optional): Detail level ('quick', 'standard', 'comprehensive').

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Identify gaps in the 'machine-learning' category
    adn_zettel(operation="suggest", category="machine-learning", count=5)

    # Iteratively expand a core concept note
    adn_zettel(operation="expand", note_identifier="Transformer Architecture", depth=2)
    ```
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_zettel operation={operation}")

    from advanced_memory.mcp.tools.zettelmaker import adn_zettelmaker

    if operation == "generate":
        return await adn_zettelmaker(
            operation="generate",
            category=op.category,
            topic=op.topic,
            ai_generate=op.ai_generate,
            quality=op.quality,
            project=op.project,
        )
    elif operation == "suggest":
        return await adn_zettelmaker(operation="suggest", category=op.category, count=op.count, project=op.project)
    elif operation == "expand":
        return await adn_zettelmaker(
            operation="expand", note_identifier=op.note_identifier, depth=op.depth, project=op.project
        )
    elif operation == "analyze":
        return await adn_zettelmaker(operation="analyze", category=op.category, project=op.project)
    elif operation == "connect":
        return await adn_zettelmaker(operation="connect", note_identifier=op.note_identifier, project=op.project)
    elif operation == "collect":
        return await adn_zettelmaker(operation="collect")
    elif operation == "customize":
        return await adn_zettelmaker(
            operation="customize", category=op.category, topic=op.topic, depth=op.depth, project=op.project
        )
    else:
        return f"Error: Unsupported operation {operation}"
