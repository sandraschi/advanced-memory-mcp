"""RAG (Retrieval Augmented Generation) MCP Tool.

Provides comprehensive RAG capabilities for document ingestion, vector storage,
and semantic retrieval to enhance skill generation with deep document understanding.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.rag.system import get_rag_system


@mcp.tool
async def adn_rag(
    operation: Annotated[
        Literal[
            "ingest_document",
            "query_knowledge",
            "list_documents",
            "get_document_info",
            "delete_document",
            "search_similar",
        ],
        Field(description="RAG action: ingest, query, list, info, delete, or similarity search"),
    ],
    document_path: Annotated[
        str | None, Field(description="Local path to file (PDF, TXT, MD, Code)")
    ] = None,
    query: Annotated[
        str | None, Field(description="Semantic query or example text for vector search")
    ] = None,
    document_id: Annotated[
        str | None, Field(description="Canonical ID of the document (slugified path)")
    ] = None,
    chunk_method: Annotated[
        Literal["fixed", "semantic", "sentence"],
        Field(description="Strategy for breaking text into vector snippets"),
    ] = "fixed",
    max_results: Annotated[
        int, Field(description="Total chunks to retrieve for context injection")
    ] = 5,
    document_filter: Annotated[
        list[str] | None, Field(description="Limit search to these specific document IDs")
    ] = None,
) -> dict[str, Any]:
    """Retrieval Augmented Generation (RAG) system for high-fidelity document grounding.

    Consolidates document chunking, vector storage, and semantic retrieval to enhance
    knowledge generation with primary source grounding.

    ## Return Format
    - JSON dictionary containing operation `success` status.
    - `results`: List of chunks with `content`, `score`, and `metadata`.
    - `info`: Document statistics (chunk count, size, timestamp).

    ## Examples
    ```python
    adn_rag(operation="ingest_document", document_path="./manual.pdf")
    adn_rag(operation="query_knowledge", query="How to configure the reactor?", max_results=3)
    adn_rag(operation="search_similar", query="theology of the machine")
    ```
    """

    try:
        rag_system = get_rag_system()

        if operation == "ingest_document":
            if not document_path:
                return {
                    "error": "document_path required for ingest_document operation",
                    "operation": operation,
                }

            # Read and extract text content from the document file directly
            try:
                import fitz  # PyMuPDF for PDF files

                file_path_obj = Path(document_path)
                if not file_path_obj.exists():
                    return {
                        "success": False,
                        "error": f"Document file not found: {document_path}",
                    }

                # Extract text content based on file type
                if file_path_obj.suffix.lower() == ".pdf":
                    # PDF extraction
                    doc = fitz.open(str(file_path_obj))
                    full_content = ""
                    for page_num in range(min(50, len(doc))):  # Limit to first 50 pages for RAG
                        page = doc.load_page(page_num)
                        full_content += page.get_text() + "\n\n"
                    doc.close()
                elif file_path_obj.suffix.lower() in [".txt", ".md", ".py", ".js", ".html", ".css"]:
                    # Text-based files
                    with open(file_path_obj, encoding="utf-8", errors="ignore") as f:
                        full_content = f.read()
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported file format: {file_path_obj.suffix}. Supported: PDF, TXT, MD, PY, JS, HTML, CSS",
                        "document_path": document_path,
                    }

                if not full_content.strip():
                    return {
                        "success": False,
                        "error": "No text content extracted from document",
                        "document_path": document_path,
                    }

            except ImportError:
                return {
                    "success": False,
                    "error": "Document processing dependencies not available. Install PyMuPDF for PDF support.",
                    "document_path": document_path,
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to read document: {e!s}",
                    "document_path": document_path,
                }

            # Generate document ID from path
            doc_id = str(document_path).replace("/", "_").replace("\\", "_").replace(".", "_")

            # Add to RAG system
            rag_result = rag_system.add_document(
                document_id=doc_id,
                content=full_content,
                metadata={
                    "source_path": str(document_path),
                    "file_size": Path(document_path).stat().st_size
                    if Path(document_path).exists()
                    else 0,
                    "ingested_at": "2025-12-02",
                    "chunk_method": chunk_method,
                },
                chunk_method=chunk_method,
            )

            return {
                "operation": operation,
                "document_path": document_path,
                "document_id": doc_id,
                "rag_result": rag_result,
                "chunks_processed": rag_result.get("chunks_added", 0),
                "total_characters": len(full_content),
            }

        elif operation == "query_knowledge":
            if not query:
                return {
                    "error": "query required for query_knowledge operation",
                    "operation": operation,
                }

            rag_result = rag_system.query(
                query=query,
                n_results=max_results,
                document_filter=document_filter,
                include_metadata=True,
            )

            return {
                "operation": operation,
                "query": query,
                "results": rag_result,
                "max_results": max_results,
                "document_filter": document_filter,
            }

        elif operation == "list_documents":
            rag_result = rag_system.list_documents()

            return {
                "operation": operation,
                "documents": rag_result,
            }

        elif operation == "get_document_info":
            if not document_id:
                return {
                    "error": "document_id required for get_document_info operation",
                    "operation": operation,
                }

            rag_result = rag_system.get_document_info(document_id)

            return {
                "operation": operation,
                "document_id": document_id,
                "info": rag_result,
            }

        elif operation == "delete_document":
            if not document_id:
                return {
                    "error": "document_id required for delete_document operation",
                    "operation": operation,
                }

            rag_result = rag_system.delete_document(document_id)

            return {
                "operation": operation,
                "document_id": document_id,
                "result": rag_result,
            }

        elif operation == "search_similar":
            if not query:
                return {
                    "error": "query required for search_similar operation",
                    "operation": operation,
                }

            # For similarity search, we can use the same query method
            rag_result = rag_system.query(
                query=query,
                n_results=max_results,
                document_filter=document_filter,
                include_metadata=True,
            )

            return {
                "operation": operation,
                "query": query,
                "similar_documents": rag_result,
                "max_results": max_results,
            }

        else:
            return {
                "error": f"Unsupported operation: {operation}",
                "supported_operations": [
                    "ingest_document",
                    "query_knowledge",
                    "list_documents",
                    "get_document_info",
                    "delete_document",
                    "search_similar",
                ],
            }

    except Exception as exc:
        logger.error("adn_rag_error: %s", exc, exc_info=True)
        return {
            "success": False,
            "error": str(exc),
            "operation": operation,
            "suggestions": [
                "Check RAG system initialization",
                "Verify document paths exist",
                "Ensure ChromaDB dependencies are installed",
                "Check embedding model availability",
            ],
        }
