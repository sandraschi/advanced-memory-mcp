"""Vector repository for semantic search using LanceDB."""

import os
import base64
from typing import Any
import lancedb
from fastembed import TextEmbedding
from loguru import logger
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class MetadataEncryptor:
    """Handles encryption and decryption of metadata fields."""

    def __init__(self, passphrase: str | None = None):
        self.fernet = None
        if passphrase:
            salt = b"advanced-memory-salt"  # In production, this should be consistent
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
            self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        if not self.fernet:
            return data
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        if not self.fernet:
            return data
        try:
            return self.fernet.decrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return data


class VectorRepository:
    """Repository for managing semantic embeddings and vector search."""

    def __init__(
        self,
        db_path: str,
        table_name: str = "knowledge_vectors",
        passphrase: str | None = None,
    ):
        self.db_path = db_path
        self.table_name = table_name
        self.db = None
        self.table = None
        self._embedding_model = None
        self._reranker_model = None
        self.encryptor = MetadataEncryptor(passphrase)

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            # Using a lightweight but effective model
            # For 4090 we could use larger ones, but bge-small is good for speed
            self._embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        return self._embedding_model

    def get_reranker(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        attn_implementation: str = "flash_attention_2",
    ):
        """Get or initialize the reranker model."""
        if self._reranker_model is None:
            from sentence_transformers import CrossEncoder
            import torch

            logger.info(
                f"Loading reranker model: {model_name} with {attn_implementation}"
            )

            # FA2 requires specific setup often passed via model_kwargs in newer versions
            # Here we follow the standard approach for sentence-transformers/transformers
            model_kwargs = {}
            if attn_implementation == "flash_attention_2" and torch.cuda.is_available():
                model_kwargs["attn_implementation"] = "flash_attention_2"
                model_kwargs["torch_dtype"] = torch.float16

            self._reranker_model = CrossEncoder(model_name, automodel_args=model_kwargs)
        return self._reranker_model

    async def connect(self):
        """Connect to the LanceDB database."""
        if self.db is None:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.db = lancedb.connect(self.db_path)

        if self.table_name not in self.db.table_names():
            # Initial schema definition will happen on first add if not explicitly created
            logger.info(f"Creating vector table: {self.table_name}")
        else:
            self.table = self.db.open_table(self.table_name)

    async def add_documents(self, documents: list[dict[str, Any]]):
        """Add documents to the vector store.

        Expected document format:
        {
            "id": str,
            "text": str,
            "metadata": dict
        }
        """
        if not documents:
            return

        await self.connect()

        # Generate embeddings
        texts = [doc["text"] for doc in documents]
        embeddings = list(self.embedding_model.embed(texts))

        data = []
        for doc, emb in zip(documents, embeddings):
            # Encrypt sensitive chunks
            encrypted_text = self.encryptor.encrypt(doc["text"])

            data.append(
                {
                    "id": doc["id"],
                    "vector": emb,
                    "text": encrypted_text,
                    "metadata": doc["metadata"],
                }
            )

        if self.table is None:
            self.table = self.db.create_table(
                self.table_name, data=data, mode="overwrite"
            )
            # Create FTS index for hybrid search
            self.table.create_fts_index("text", replace=True)
        else:
            self.table.add(data, mode="append")

    async def search(
        self,
        query: str,
        limit: int = 10,
        query_type: str = "vector",
        filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Perform search (vector, fts, or hybrid)."""
        await self.connect()
        if self.table is None:
            return []

        search_obj = None
        if query_type == "fts":
            search_obj = self.table.search(query, query_type="fts")
        elif query_type == "hybrid":
            search_obj = self.table.search(query, query_type="hybrid")
        else:
            query_vector = list(self.embedding_model.embed([query]))[0]
            search_obj = self.table.search(query_vector)

        if filter:
            search_obj = search_obj.where(filter)

        results = search_obj.limit(limit).to_list()

        # Decrypt results
        for res in results:
            if "text" in res:
                res["text"] = self.encryptor.decrypt(res["text"])

        return results

    async def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        model_name: str,
        attn_implementation: str = "flash_attention_2",
    ) -> list[dict[str, Any]]:
        """Rerank search results using a Cross-Encoder."""
        if not documents:
            return []

        reranker = self.get_reranker(model_name, attn_implementation)

        # Prepare pairs for reranking
        pairs = [[query, doc["text"]] for doc in documents]

        # Get scores
        scores = reranker.predict(pairs)

        # Attach scores and sort
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        # Sort by rerank score descending
        sorted_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)

        return sorted_docs

    async def delete_by_id(self, doc_id: str):
        """Delete a document by its ID."""
        await self.connect()
        if self.table:
            self.table.delete(f"id = '{doc_id}'")

    async def delete_by_entity_id(self, entity_id: int):
        """Delete all chunks for a specific entity."""
        await self.connect()
        if self.table:
            self.table.delete(f"metadata.entity_id = {entity_id}")
