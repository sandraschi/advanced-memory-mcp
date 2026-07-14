"""Typora Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates Typora editor operations: open, save, insert, get/set content, cursor, analyze, export.
It reduces the number of MCP tools while maintaining full functionality.
"""

from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import TyporaOperation


@mcp.tool(name="adn_typora")
async def adn_typora(op: TyporaOperation) -> Any:
    """
    Bidirectional Typora editor integration and telemetry for Advanced Memory.

    This tool provides deep control over the Typora markdown editor, allowing
    for programmatic content injection, structural analysis, and professional
    document synthesis.

    ---------------------------------------------------------------------------
    [RATIONALE]
    While the AI operates on raw markdown, the user often works in a rich visual
    editor. By bridging these worlds, we enable 'Co-Editing' workflows where the
    AI can observe the user's cursor position (telemetry), insert suggestions at
    the point of focus, and handle final document export without the user
    leaving their preferred writing environment.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - open: Editor Induction - opens a specific markdown file for manual editing.
    - save: Persist current changes in the active Typora instance.
    - insert: Injects text or markdown at the cursor or a specified anchor.
    - get_content: Editor Inspection - reads the full content of the active document.
    - set_content: Editor Modification - replaces the entire document content.
    - cursor: Telemetry - retrieves cursor position and selection metrics.
    - analyze: Intelligence - reports on headings, links, and document health.
    - export: Synthesis - renders the document to PDF, HTML, DOCX, or ODT.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The editor task (open, save, insert, cursor, export, etc.).
    - file_path (str, optional): Absolute path to the file for 'open'.
    - text (str, optional): Content to inject for 'insert'.
    - position (str, optional): Target location anchor (e.g., 'current cursor').
    - format (str, optional): Export target (pdf, html, docx, odt).
    - path (str, optional): Destination path for exported files.

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Open a meeting note and insert a summary at the cursor
    adn_typora(operation="open", file_path="C:/Vault/notes/meeting.md")
    adn_typora(operation="insert", text="## AI Summary\n- Action Item 1", position="current cursor")

    # Export the current document to a professional PDF
    adn_typora(operation="export", format="pdf", path="C:/Exports/report.pdf")
    ```
    """
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_typora operation={operation}")

    from advanced_memory.mcp.tools.typora_control import typora_control

    if operation == "open":
        return await typora_control(operation="open_file", file_path=op.file_path)
    elif operation == "save":
        return await typora_control(operation="save_file")
    elif operation == "insert":
        return await typora_control(operation="insert_text", text=op.text, position=op.position)
    elif operation == "get_content":
        return await typora_control(operation="get_content")
    elif operation == "set_content":
        return await typora_control(operation="set_content", content=op.content)
    elif operation == "cursor":
        return await typora_control(operation="get_cursor")
    elif operation == "analyze":
        return await typora_control(operation="content_analysis")
    elif operation == "export":
        return await typora_control(operation="export", format=op.format, output_path=op.path, options=op.options)
    else:
        return f"Error: Unsupported operation {operation}"
