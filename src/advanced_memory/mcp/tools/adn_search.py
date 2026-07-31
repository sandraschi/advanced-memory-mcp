"""Search Manager portmanteau tool for Advanced Memory MCP server.

This tool consolidates all search operations: Boolean query, Semantic RAG, and External vault searches.
It reduces the number of MCP tools while maintaining full functionality.
"""

import time as _time
from typing import Any

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.models.portmanteau import SearchOperation
from advanced_memory.mcp.tools.utils import build_error_response


@mcp.tool(name="adn_search")
async def adn_search(op: SearchOperation) -> Any:
    """
    Comprehensive search and semantic discovery for Advanced Memory.

    This tool consolidates Boolean full-text search, Vector-based RAG, and
    cross-platform external vault discovery into a single intelligence interface.

    ---------------------------------------------------------------------------
    [RATIONALE]
    High-performance retrieval requires switching between exact-match Boolean
    logic and fuzzy semantic meaning. By unifying these into 'adn_search', we
    allow the LLM to choose the best strategy (Query vs RAG) based on the user's
    intent, while maintaining a consistent response format for internal and
    external knowledge silos.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - query: High-speed full-text search with Boolean logic (AND, OR, NOT).
    - rag: Semantic retrieval using Vector Embeddings and LanceDB.
    - external: Search across Obsidian, Notion, Joplin, and Evernote vaults.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The search strategy (query, rag, external).
    - text (str, optional): Search term or Boolean query (used in 'query').
    - prompt (str, optional): Natural language prompt for semantic discovery (used in 'rag').
    - query (str, optional): Search term for external vaults.
    - source (str, optional): External platform ('obsidian', 'notion', 'joplin', 'evernote').
    - path (str, optional): Absolute path to the external vault or export folder.
    - search_type (str, optional): Focus for 'query' (text, title, tag, permalink).
    - limit (int, optional): Maximum results for RAG (default 5).
    - max_results (int, optional): Maximum results for external searches.
    - project (str, optional): Override the current active project context.

    ---------------------------------------------------------------------------
    [EXAMPLES]
    ```python
    # Semantic Search (RAG) for conceptual topics
    adn_search(operation="rag", prompt="How do we handle async error recovery in the MCP layer?")

    # Boolean Search for specific tags or titles
    adn_search(operation="query", search_type="tag", text="work AND finance")
    ```
    """
    _st = _time.time()
    logger.info(f"[TIMED] enter adn_search op={getattr(op, 'operation', op)} at +0.0s")
    operation = op.operation
    logger.info(f"MCP tool call tool=adn_search operation={operation}")

    if operation == "query":
        from advanced_memory.mcp.tools.search import search_notes

        return await (search_notes.fn if hasattr(search_notes, "fn") else search_notes)(
            op.text,
            op.page,
            op.page_size,
            op.search_type,
            project=op.project,
        )

    elif operation == "rag":
        from advanced_memory.rag.system import get_rag_system

        rag_system = get_rag_system()
        rag_result = rag_system.query(
            query=op.prompt,
            n_results=op.limit,
            include_metadata=True,
        )
        return {
            "operation": "rag",
            "prompt": op.prompt,
            "results": rag_result,
            "limit": op.limit,
        }

    elif operation == "external":
        if op.source == "obsidian":
            from advanced_memory.mcp.tools.search_obsidian_vault import search_obsidian_vault

            return await (search_obsidian_vault.fn if hasattr(search_obsidian_vault, "fn") else search_obsidian_vault)(
                op.path, op.query, "text", op.max_results, False
            )
        elif op.source == "joplin":
            from advanced_memory.mcp.tools.search_joplin_vault import search_joplin_vault

            return await (search_joplin_vault.fn if hasattr(search_joplin_vault, "fn") else search_joplin_vault)(
                op.path, op.query, "text", op.max_results, False
            )
        elif op.source == "notion":
            from advanced_memory.mcp.tools.search_notion_vault import search_notion_vault

            return await (search_notion_vault.fn if hasattr(search_notion_vault, "fn") else search_notion_vault)(
                op.path, op.query, False, None, op.max_results
            )
        elif op.source == "evernote":
            from advanced_memory.mcp.tools.search_evernote_vault import search_evernote_vault

            return await (search_evernote_vault.fn if hasattr(search_evernote_vault, "fn") else search_evernote_vault)(
                op.path, op.query, False, None, None, None, op.max_results
            )
        else:
            return build_error_response(
                error="Unsupported external source",
                error_code="INVALID_SOURCE",
                message=f"Source {op.source} is not supported.",
            )

    else:
        return build_error_response(
            error="Unsupported operation",
            error_code="INVALID_OPERATION",
            message=f"Operation {operation} is not supported.",
        )
