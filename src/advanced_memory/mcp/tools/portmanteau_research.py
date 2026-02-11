"""Portmanteau tool for AI research and RAG operations.

PORTMANTEAU PATTERN RATIONALE: Consolidates 15+ research and AI tools including
web search, academic research, document ingestion, RAG queries, and LLM interactions
into a single tool. This creates a coherent research workflow while reducing tool count.
"""

from typing import Annotated, Literal

from loguru import logger
from pydantic import Field

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


@mcp.tool
async def adn_research(
    operation: Annotated[
        Literal[
            "web_search",
            "arxiv",
            "github",
            "document_ingest",
            "rag_query",
            "llm_config",
            "llm_generate",
            "research_orchestrate",
            "tvtropes",
        ],
        Field(description="Research operation to perform"),
    ],
    query: Annotated[str | None, Field(description="Search query or research topic")] = None,
    provider: Annotated[
        str | None, Field(description="Provider/service (openai, anthropic, google, etc.)")
    ] = None,
    model: Annotated[str | None, Field(description="Model name/version")] = None,
    api_key: Annotated[str | None, Field(description="API key for service")] = None,
    limit: Annotated[int | None, Field(description="Result limit")] = None,
    language: Annotated[str | None, Field(description="Programming language filter")] = None,
    path: Annotated[str | None, Field(description="File path for document ingestion")] = None,
    content: Annotated[str | None, Field(description="Content for LLM generation")] = None,
) -> dict:
    """Unified portmanteau tool for AI research and knowledge discovery.

    This tool consolidates all research-related operations:
    - Web search and academic research
    - GitHub code exploration
    - Document processing and ingestion
    - RAG (Retrieval Augmented Generation) queries
    - LLM configuration and generation
    - Research orchestration

    Args:
        operation: The specific research operation to perform
        query: Search query or research topic
        provider: AI provider (openai, anthropic, google)
        model: Model name/version
        api_key: API key for authentication
        limit: Maximum results to return
        language: Programming language filter for GitHub search
        path: File path for document processing
        content: Content for LLM operations

    Returns:
        Research results or operation confirmation

    Examples:
        # Web search
        adn_research("web_search", query="machine learning transformers")

        # Academic research
        adn_research("arxiv", query="neural networks", limit=10)

        # GitHub code search
        adn_research("github", query="react hooks", language="typescript")

        # Document processing
        adn_research("document_ingest", path="/path/to/document.pdf")

        # RAG query
        adn_research("rag_query", query="explain quantum computing")

        # Configure LLM
        adn_research("llm_config", provider="openai", model="gpt-4", api_key="your-api-key-here")  # pragma: allowlist secret
    """
    try:
        if operation == "web_search":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Query required for web search"
                )
            from advanced_memory.mcp.tools.adn_web_search import adn_web_search

            result = await adn_web_search.fn(query, limit=limit or 10)
            return build_success_response("web_search", result)

        elif operation == "arxiv":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Query required for arXiv search"
                )
            from advanced_memory.mcp.tools.adn_arxiv_research import adn_arxiv_research

            result = await adn_arxiv_research.fn(query, limit=limit or 10)
            return build_success_response("arxiv", result)

        elif operation == "github":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Query required for GitHub search"
                )
            from advanced_memory.mcp.tools.adn_github_research import adn_github_research

            result = await adn_github_research.fn(query, language=language, limit=limit or 10)
            return build_success_response("github", result)

        elif operation == "tvtropes":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Query required for TV Tropes research"
                )
            from advanced_memory.mcp.tools.adn_tvtropes_research import adn_tvtropes_research

            result = await adn_tvtropes_research.fn(query)
            return build_success_response("tvtropes", result)

        elif operation == "document_ingest":
            if not path:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Path required for document ingestion"
                )
            from advanced_memory.mcp.tools.adn_document_ingest import adn_document_ingest

            result = await adn_document_ingest.fn(path)
            return build_success_response("document_ingest", result)

        elif operation == "rag_query":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Query required for RAG operation"
                )
            from advanced_memory.mcp.tools.adn_rag import adn_rag

            result = await adn_rag.fn(query)
            return build_success_response("rag_query", result)

        elif operation == "llm_config":
            if not provider or not model:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Provider and model required for LLM config",
                )
            from advanced_memory.mcp.tools.adn_llm import adn_llm

            result = await adn_llm.fn("configure", provider=provider, model=model, api_key=api_key)
            return build_success_response("llm_config", result)

        elif operation == "llm_generate":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR", "MISSING_PARAMETER", "Content required for LLM generation"
                )
            from advanced_memory.mcp.tools.adn_llm import adn_llm

            result = await adn_llm.fn("generate", content=content)
            return build_success_response("llm_generate", result)

        elif operation == "research_orchestrate":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for research orchestration",
                )
            from advanced_memory.mcp.tools.research_orchestrator import research_orchestrator

            result = await research_orchestrator.fn(query)
            return build_success_response("research_orchestrate", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR", "VALIDATION_ERROR", f"Unknown research operation: {operation}"
            )

    except Exception as e:
        logger.error(f"Research operation '{operation}' failed: {e}")
        return build_error_response(
            "VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {str(e)}"
        )
