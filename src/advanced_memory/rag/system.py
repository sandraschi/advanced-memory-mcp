"""RAG (Retrieval Augmented Generation) System for Advanced Memory.

This module provides comprehensive RAG capabilities including:
- Intelligent document chunking
- Vector embeddings with ChromaDB
- Semantic retrieval
- Context-aware knowledge synthesis
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import chromadb
from loguru import logger
from sentence_transformers import SentenceTransformer


class DocumentChunk:
    """A chunk of document content with metadata."""

    def __init__(
        self,
        content: str,
        document_id: str,
        chunk_id: str,
        start_pos: int,
        end_pos: int,
        metadata: dict[str, Any] | None = None,
    ):
        self.content = content
        self.document_id = document_id
        self.chunk_id = chunk_id
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert chunk to dictionary for storage."""
        return {
            "content": self.content,
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "metadata": self.metadata,
        }


class RAGSystem:
    """RAG system with ChromaDB vector storage and retrieval."""

    def __init__(
        self,
        persist_directory: str | Path = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """Initialize RAG system.

        Args:
            persist_directory: Directory to store ChromaDB data
            embedding_model: Sentence transformer model name
            chunk_size: Size of text chunks (characters)
            chunk_overlap: Overlap between chunks (characters)
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=str(self.persist_directory))

        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model {embedding_model}: {e}")
            # Fallback to a smaller model
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded fallback embedding model: all-MiniLM-L6-v2")

        # Get or create collections
        self.documents_collection = self.chroma_client.get_or_create_collection(
            name="documents", metadata={"description": "Document metadata and summaries"}
        )

        self.chunks_collection = self.chroma_client.get_or_create_collection(
            name="chunks", metadata={"description": "Document chunks with vector embeddings"}
        )

        logger.info("RAG system initialized successfully")

    def add_document(
        self,
        document_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        chunk_method: Literal["fixed", "semantic", "sentence"] = "fixed",
    ) -> dict[str, Any]:
        """Add a document to the RAG system.

        Args:
            document_id: Unique identifier for the document
            content: Full text content of the document
            metadata: Additional metadata about the document
            chunk_method: Method to use for chunking

        Returns:
            Dict with processing results
        """
        try:
            # Create chunks
            chunks = self._chunk_document(content, document_id, chunk_method)

            if not chunks:
                return {
                    "success": False,
                    "error": "No chunks generated from document",
                    "document_id": document_id,
                }

            # Generate embeddings for chunks
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_model.encode(chunk_texts, convert_to_numpy=True)

            # Prepare data for ChromaDB
            chunk_ids = [chunk.chunk_id for chunk in chunks]
            chunk_metadatas = []

            for chunk in chunks:
                chunk_metadata = {
                    "document_id": chunk.document_id,
                    "start_pos": chunk.start_pos,
                    "end_pos": chunk.end_pos,
                    **chunk.metadata,
                }
                chunk_metadatas.append(chunk_metadata)

            # Store chunks in ChromaDB
            self.chunks_collection.add(
                ids=chunk_ids,
                embeddings=embeddings.tolist(),
                documents=chunk_texts,
                metadatas=chunk_metadatas,
            )

            # Store document metadata
            doc_metadata = {
                "document_id": document_id,
                "total_chunks": len(chunks),
                "word_count": len(content.split()),
                "char_count": len(content),
                **(metadata or {}),
            }

            # Create a document summary for retrieval
            doc_summary = self._generate_document_summary(content, document_id)

            self.documents_collection.add(
                ids=[document_id],
                embeddings=[self.embedding_model.encode([doc_summary])[0].tolist()],
                documents=[doc_summary],
                metadatas=[doc_metadata],
            )

            logger.info(f"Added document {document_id} with {len(chunks)} chunks")

            return {
                "success": True,
                "document_id": document_id,
                "chunks_added": len(chunks),
                "total_characters": len(content),
                "embedding_model": self.embedding_model.get_sentence_embedding_dimension(),
            }

        except Exception as e:
            logger.error(f"Failed to add document {document_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id,
            }

    def query(
        self,
        query: str,
        n_results: int = 5,
        document_filter: list[str] | None = None,
        include_metadata: bool = True,
    ) -> dict[str, Any]:
        """Query the RAG system for relevant document chunks.

        Args:
            query: Search query
            n_results: Number of results to return
            document_filter: Optional list of document IDs to search within
            include_metadata: Whether to include chunk metadata in results

        Returns:
            Dict with query results
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()

            # Build filter for document-specific queries
            where_clause = None
            if document_filter:
                where_clause = {"document_id": {"$in": document_filter}}

            # Search chunks collection
            results = self.chunks_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"],
            )

            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    result = {
                        "content": doc,
                        "score": 1.0 - results["distances"][0][i],  # Convert distance to similarity
                        "document_id": results["metadatas"][0][i]["document_id"],
                    }

                    if include_metadata:
                        result["metadata"] = results["metadatas"][0][i]

                    formatted_results.append(result)

            return {
                "success": True,
                "query": query,
                "total_results": len(formatted_results),
                "results": formatted_results,
                "document_filter": document_filter,
            }

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
            }

    def get_document_info(self, document_id: str) -> dict[str, Any]:
        """Get information about a stored document."""

        try:
            results = self.documents_collection.get(
                ids=[document_id], include=["metadatas", "documents"]
            )

            if results["metadatas"]:
                metadata = results["metadatas"][0]
                summary = results["documents"][0] if results["documents"] else ""

                # Get chunk count
                chunk_results = self.chunks_collection.get(where={"document_id": document_id})
                chunk_count = len(chunk_results["ids"]) if chunk_results["ids"] else 0

                return {
                    "success": True,
                    "document_id": document_id,
                    "metadata": metadata,
                    "summary": summary,
                    "chunk_count": chunk_count,
                }
            else:
                return {
                    "success": False,
                    "error": "Document not found",
                    "document_id": document_id,
                }

        except Exception as e:
            logger.error(f"Failed to get document info for {document_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id,
            }

    def list_documents(self) -> dict[str, Any]:
        """List all documents in the RAG system."""

        try:
            results = self.documents_collection.get(include=["metadatas"])

            documents = []
            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    documents.append(
                        {
                            "document_id": metadata["document_id"],
                            "chunk_count": metadata.get("total_chunks", 0),
                            "word_count": metadata.get("word_count", 0),
                            "metadata": metadata,
                        }
                    )

            return {
                "success": True,
                "total_documents": len(documents),
                "documents": documents,
            }

        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def delete_document(self, document_id: str) -> dict[str, Any]:
        """Delete a document and all its chunks from the RAG system."""

        try:
            # Delete chunks
            self.chunks_collection.delete(where={"document_id": document_id})

            # Delete document metadata
            self.documents_collection.delete(ids=[document_id])

            logger.info(f"Deleted document {document_id}")

            return {
                "success": True,
                "document_id": document_id,
                "message": "Document and all chunks deleted successfully",
            }

        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id,
            }

    def _chunk_document(
        self, content: str, document_id: str, method: Literal["fixed", "semantic", "sentence"]
    ) -> list[DocumentChunk]:
        """Chunk a document using the specified method."""

        if method == "sentence":
            return self._chunk_by_sentences(content, document_id)
        elif method == "semantic":
            return self._chunk_semantically(content, document_id)
        else:  # fixed
            return self._chunk_fixed_size(content, document_id)

    def _chunk_fixed_size(self, content: str, document_id: str) -> list[DocumentChunk]:
        """Chunk document using fixed-size overlapping windows."""

        chunks = []
        content_length = len(content)
        start_pos = 0
        chunk_index = 0

        while start_pos < content_length:
            end_pos = min(start_pos + self.chunk_size, content_length)

            # If we're not at the end, try to break at a sentence boundary
            if end_pos < content_length:
                # Look for sentence endings within the last 100 characters
                search_start = max(end_pos - 100, start_pos)
                sentence_endings = [". ", "! ", "? ", "\n\n"]

                best_break = end_pos
                for ending in sentence_endings:
                    last_ending = content.rfind(ending, search_start, end_pos)
                    if last_ending != -1 and last_ending > best_break - 50:
                        best_break = last_ending + len(ending)

                end_pos = best_break

            chunk_content = content[start_pos:end_pos].strip()
            if chunk_content:
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                chunk = DocumentChunk(
                    content=chunk_content,
                    document_id=document_id,
                    chunk_id=chunk_id,
                    start_pos=start_pos,
                    end_pos=end_pos,
                )
                chunks.append(chunk)
                chunk_index += 1

            # Move start position with overlap
            start_pos = end_pos - self.chunk_overlap
            if start_pos >= content_length:
                break

        return chunks

    def _chunk_by_sentences(self, content: str, document_id: str) -> list[DocumentChunk]:
        """Chunk document by grouping sentences."""

        import re

        # Split into sentences
        sentence_pattern = r"(?<=[.!?])\s+"
        sentences = re.split(sentence_pattern, content)

        chunks = []
        current_chunk = ""
        chunk_index = 0
        start_pos = 0

        for sentence in sentences:
            if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                # Create chunk
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                chunk = DocumentChunk(
                    content=current_chunk.strip(),
                    document_id=document_id,
                    chunk_id=chunk_id,
                    start_pos=start_pos,
                    end_pos=start_pos + len(current_chunk),
                )
                chunks.append(chunk)
                chunk_index += 1

                # Start new chunk with overlap
                overlap_size = min(self.chunk_overlap, len(current_chunk))
                current_chunk = current_chunk[-overlap_size:] + sentence
                start_pos += len(current_chunk) - len(sentence) - overlap_size
            else:
                current_chunk += sentence

        # Add final chunk
        if current_chunk.strip():
            chunk_id = f"{document_id}_chunk_{chunk_index}"
            chunk = DocumentChunk(
                content=current_chunk.strip(),
                document_id=document_id,
                chunk_id=chunk_id,
                start_pos=start_pos,
                end_pos=start_pos + len(current_chunk),
            )
            chunks.append(chunk)

        return chunks

    def _chunk_semantically(self, content: str, document_id: str) -> list[DocumentChunk]:
        """Chunk document using semantic similarity (simplified version)."""

        # For now, use sentence-based chunking as semantic chunking
        # requires more complex NLP processing
        return self._chunk_by_sentences(content, document_id)

    def _generate_document_summary(self, content: str, document_id: str) -> str:
        """Generate a summary of the document for retrieval."""

        # Simple extractive summary - take first and last parts
        words = content.split()
        if len(words) <= 100:
            return content

        # Take first 50 words and last 50 words
        first_part = " ".join(words[:50])
        last_part = " ".join(words[-50:])

        return f"{first_part} ... {last_part}"


# Global RAG system instance
_rag_system: RAGSystem | None = None


def get_rag_system() -> RAGSystem:
    """Get or create the global RAG system instance."""

    global _rag_system

    if _rag_system is None:
        # Configure from environment
        persist_dir = os.getenv("RAG_PERSIST_DIR", "./chroma_db")
        embedding_model = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        chunk_size = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
        chunk_overlap = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))

        _rag_system = RAGSystem(
            persist_directory=persist_dir,
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    return _rag_system


async def initialize_rag_system() -> bool:
    """Initialize the global RAG system."""

    try:
        # system = get_rag_system()  # Initialize RAG system
        get_rag_system()  # Initialize RAG system
        logger.info("RAG system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        return False
