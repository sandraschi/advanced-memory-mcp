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
        return await _rag_query(op.prompt, op.limit, op.project)
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


async def _rag_query(prompt: str | None, limit: int, project: str | None) -> Any:
    """Semantic RAG over the LanceDB vector store.

    Builds the SearchService the same way ``deps.get_search_service`` does for a
    FastAPI request, but callable directly from the MCP tool context (the FastAPI
    dependency function requires request-injected args and cannot be invoked bare).
    """
    from pathlib import Path

    from advanced_memory import db
    from advanced_memory.config import ConfigManager
    from advanced_memory.markdown import EntityParser
    from advanced_memory.markdown.markdown_processor import MarkdownProcessor
    from advanced_memory.repository import EntityRepository, ProjectRepository
    from advanced_memory.repository.search_repository import SearchRepository
    from advanced_memory.repository.vector_repository import VectorRepository
    from advanced_memory.services.file_service import FileService
    from advanced_memory.services.search_service import SearchService

    app_config = ConfigManager().load_config()

    project_name = project
    if not project_name:
        try:
            from advanced_memory.mcp.project_session import session

            project_name = session.get_current_project()
        except Exception:
            project_name = app_config.default_project or "main"

    _, session_maker = await db.get_or_create_db(app_config.database_path)
    project_repo = ProjectRepository(session_maker)
    proj = await project_repo.get_by_name(project_name) or await project_repo.get_by_permalink(project_name)
    if proj is None:
        return build_error_response(
            error="Project not found",
            error_code="PROJECT_NOT_FOUND",
            message=f"Project '{project_name}' not found for RAG search.",
        )

    project_path = Path(proj.path)
    entity_parser = EntityParser(project_path)
    markdown_processor = MarkdownProcessor(entity_parser)
    file_service = FileService(project_path, markdown_processor)

    entity_repository = EntityRepository(session_maker, project_id=proj.id)
    search_repository = SearchRepository(session_maker, project_id=proj.id)
    vector_db_path = str(app_config.app_database_path.parent / "vectors")
    vector_repository = VectorRepository(vector_db_path, passphrase=app_config.rag_storage_passphrase)

    search_service = SearchService(
        search_repository,
        entity_repository,
        vector_repository,
        file_service,
        app_config,
    )

    results = await search_service.knowledge_rag(query=prompt or "", limit=limit)
    return {
        "operation": "rag",
        "prompt": prompt,
        "results": results,
        "limit": limit,
    }
