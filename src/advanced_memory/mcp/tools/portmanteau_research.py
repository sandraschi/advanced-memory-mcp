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


@mcp.tool()
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
        str | None,
        Field(description="Provider/service (openai, anthropic, google, etc.)"),
    ] = None,
    model: Annotated[str | None, Field(description="Model name/version")] = None,
    api_key: Annotated[str | None, Field(description="API key for service")] = None,
    limit: Annotated[int | None, Field(description="Result limit")] = None,
    language: Annotated[str | None, Field(description="Programming language filter")] = None,
    path: Annotated[str | None, Field(description="File path for document ingestion")] = None,
    content: Annotated[str | None, Field(description="Content for LLM generation")] = None,
) -> dict:
    """Unified portmanteau for AI research and knowledge discovery.

    Operations: web_search, arxiv, github, document_ingest, rag_query,
    llm_config, llm_generate, research_orchestrate, tvtropes.

    For full documentation on parameters and usage examples, call:
    `help(topic="adn_research")`
    """
    try:
        if operation == "web_search":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for web search",
                )
            from advanced_memory.mcp.beta.adn_web_search import adn_web_search

            result = await adn_web_search(query, max_results=limit or 10)
            return build_success_response("web_search", result)

        elif operation == "arxiv":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for arXiv search",
                )
            from advanced_memory.mcp.beta.adn_arxiv_research import adn_arxiv_research

            result = await adn_arxiv_research(operation="search_papers", query=query, max_results=limit or 10)
            return build_success_response("arxiv", result)

        elif operation == "github":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for GitHub search",
                )
            from advanced_memory.mcp.beta.adn_github_research import (
                adn_github_research,
            )

            result = await adn_github_research(
                operation="search_repositories",
                query=query,
                language=language,
                max_results=limit or 10,
            )
            return build_success_response("github", result)

        elif operation == "tvtropes":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for TV Tropes research",
                )
            from advanced_memory.mcp.beta.adn_tvtropes_research import (
                adn_tvtropes_research,
            )

            # NOTE (2026-09-19): operation is required — positional query
            # used to land in `operation` and every call failed.
            result = await adn_tvtropes_research(operation="search_tropes", query=query, max_results=limit or 5)
            return build_success_response("tvtropes", result)

        elif operation == "document_ingest":
            if not path:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Path required for document ingestion",
                )
            from advanced_memory.mcp.tools.adn_document_ingest import (
                adn_document_ingest,
            )

            result = await adn_document_ingest(path)
            return build_success_response("document_ingest", result)

        elif operation == "rag_query":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for RAG operation",
                )
            from advanced_memory.mcp.tools.adn_rag import adn_rag

            # NOTE (2026-09-19): operation is required — positional query
            # used to land in `operation` and every call failed.
            result = await adn_rag(operation="query_knowledge", query=query)
            return build_success_response("rag_query", result)

        elif operation == "llm_config":
            if not provider or not model:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Provider and model required for LLM config",
                )
            # NOTE (2026-09-19): this used to call adn_llm("configure", ...),
            # an operation that never existed — every call failed with
            # "Invalid operation", wrapped as success. Rewired to the real op.
            # api_key is accepted for compatibility but not forwarded:
            # hosted keys come from the environment (OPENAI_API_KEY).
            from advanced_memory.mcp.tools.adn_llm import adn_llm

            # .fn when @mcp.tool decorated, direct when plain (mirrors tests/mcp/tool_invoker).
            select = getattr(adn_llm, "fn", adn_llm)
            inner = await select(operation="select_model", provider=provider, model=model)
            if not isinstance(inner, dict) or not inner.get("success"):
                return inner
            summary = inner.get("technical_summary") or inner.get("message") or "Model selected"
            return build_success_response(
                "llm_config",
                summary,
                result=inner.get("result", {}),
            )

        elif operation == "llm_generate":
            if not content:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Content required for LLM generation",
                )
            # NOTE (2026-09-19): this used to call adn_llm("generate", ...),
            # an operation that never existed. Generation lives in
            # services.llm_client, which honors the adn_llm selection
            # (explicit provider/model here override it for this call only).
            from advanced_memory.services.llm_client import get_llm_client

            try:
                client = get_llm_client(provider=provider, model=model)
                text = await client.generate(content)
            except Exception as e:
                return build_error_response(
                    "LLM_GENERATION_FAILED",
                    "GENERATION_ERROR",
                    f"LLM generation failed: {e!s}",
                    recovery_options=[
                        "Check the provider is reachable (adn_llm health)",
                        "Pick an installed model (adn_llm list_models)",
                    ],
                )
            return build_success_response(
                "llm_generate",
                f"Generated {len(text)} chars via {client.provider}/{client.model}",
                result={"provider": client.provider, "model": client.model, "text": text},
            )

        elif operation == "research_orchestrate":
            if not query:
                return build_error_response(
                    "VALIDATION_ERROR",
                    "MISSING_PARAMETER",
                    "Query required for research orchestration",
                )
            from advanced_memory.mcp.tools.research_orchestrator import (
                research_orchestrator,
            )

            # NOTE (2026-09-19): operation+topic are required — positional
            # query used to land in `operation` and every call failed.
            # research_plan needs only a topic, hence the default.
            result = await research_orchestrator(operation="research_plan", topic=query)
            return build_success_response("research_orchestrate", result)

        else:
            return build_error_response(
                "VALIDATION_ERROR",
                "VALIDATION_ERROR",
                f"Unknown research operation: {operation}",
            )

    except Exception as e:
        logger.error(f"Research operation '{operation}' failed: {e}")
        return build_error_response("VALIDATION_ERROR", "VALIDATION_ERROR", f"Operation failed: {e!s}")


# Registered live via @mcp.tool + server.py import (2026-09-19).
# The register_portmanteau_tool helper referenced here never existed.
