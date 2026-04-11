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
    operation: Literal[
        "ingest_document",
        "query_knowledge",
        "list_documents",
        "get_document_info",
        "delete_document",
        "search_similar",
    ],
    document_path: str | None = None,
    query: str | None = None,
    document_id: str | None = None,
    chunk_method: Literal["fixed", "semantic", "sentence"] = "fixed",
    max_results: int = 5,
    document_filter: list[str] | None = None,
) -> dict[str, Any]:
    """
    RAG (Retrieval Augmented Generation) system for deep document analysis and knowledge retrieval.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates document chunking, vector storage, and semantic retrieval into one tool
    for comprehensive RAG capabilities that enhance skill generation with primary sources.

    SUPPORTED OPERATIONS:

    ingest_document: Process and store a document in the vector database
    - Chunks documents intelligently and creates vector embeddings
    - Enables semantic search across large documents
    - Required: document_path

    query_knowledge: Search for relevant information across all documents
    - Performs semantic similarity search using vector embeddings
    - Returns most relevant chunks with similarity scores
    - Required: query

    list_documents: Show all documents in the knowledge base
    - Lists stored documents with metadata and chunk counts

    get_document_info: Get detailed information about a specific document
    - Shows document metadata, summary, and processing statistics
    - Required: document_id

    delete_document: Remove a document and all its chunks
    - Cleans up vector database and frees storage
    - Required: document_id

    search_similar: Find documents similar to query or example text
    - Uses embeddings to find semantically similar content
    - Useful for discovering related information

    RAG ENHANCEMENT:
    This tool enables processing documents larger than LLM context windows,
    providing persistent knowledge storage and intelligent retrieval for:
    - Academic papers and research
    - Historical texts and primary sources
    - Technical documentation
    - Books and lengthy manuscripts

    Args:
        operation: The RAG operation to perform
        document_path: Path to document file (for ingest_document)
        query: Search query (for query_knowledge, search_similar)
        document_id: Document identifier (for get_document_info, delete_document)
        chunk_method: Chunking strategy (fixed, semantic, sentence)
        max_results: Maximum results to return
        document_filter: Limit search to specific documents

    Returns:
        Operation-specific results with document/chunk data and metadata

    Examples:
        # Ingest Schreber's memoirs for deep psychological analysis
        await adn_rag("ingest_document", document_path="/books/schreber-memoirs.pdf")

        # Query for delusional content across all documents
        await adn_rag("query_knowledge", query="divine mission delusions")

        # Find Transformer architecture details in the original paper
        await adn_rag("query_knowledge", query="attention mechanism equations")

        # Search within specific documents
        await adn_rag(
            "query_knowledge",
            query="witchcraft theology",
            document_filter=["malleus-maleficarum"]
        )

        # Get document processing statistics
        await adn_rag("get_document_info", document_id="attention-is-all-you-need")
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
