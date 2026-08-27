"""Vector repository for semantic search using LanceDB."""

import base64
import os
import shutil
from pathlib import Path
from typing import Any

import lancedb
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from loguru import logger


def _get_fastembed_cache_dir() -> Path:
    """Return the fastembed cache directory (local to repo root by default)."""
    # fastembed uses FASTEMBED_CACHE_PATH env var
    env_path = os.environ.get("FASTEMBED_CACHE_PATH")
    if env_path:
        return Path(env_path)

    # Use a persistent local cache in the repository's 'data' folder
    # This file is at src/advanced_memory/repository/vector_repository.py
    # Repo root is 4 levels up from this file's position in a typical install,
    # but we can try common paths or just use 'data/fastembed_cache' relative to cwd
    # or the repo root if we can identify it.
    try:
        # Search for .git or pyproject.toml up from current file
        curr = Path(__file__).resolve().parent
        for _ in range(5):
            if (curr / ".git").exists() or (curr / "pyproject.toml").exists():
                cache_dir = curr / "data" / "fastembed_cache"
                cache_dir.mkdir(parents=True, exist_ok=True)
                return cache_dir
            curr = curr.parent
    except Exception:
        pass

    # Fallback to current directory or system temp
    local_data = Path.cwd() / "data" / "fastembed_cache"
    if local_data.parent.exists():
        local_data.mkdir(parents=True, exist_ok=True)
        return local_data

    return Path(os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))) / "fastembed_cache"


def _purge_fastembed_model_cache(model_slug: str) -> None:
    """Delete the cached files for a specific model slug so fastembed re-downloads it.

    model_slug example: 'models--qdrant--bge-small-en-v1.5-onnx-q'
    """
    cache_dir = _get_fastembed_cache_dir() / model_slug
    if cache_dir.exists():
        logger.warning("Purging corrupt fastembed cache at: %s", cache_dir)
        shutil.rmtree(cache_dir, ignore_errors=True)
        logger.info("Cache purged, model will be re-downloaded on next use.")
    else:
        logger.info("No cache dir found at %s, nothing to purge.", cache_dir)


def _load_text_embedding(model_name: str, max_retries: int = 2) -> tuple[Any, str, int]:
    """Load fastembed TextEmbedding with automatic cache-repair on ONNX errors."""
    from advanced_memory.rag.fastembed_gpu import create_text_embedding, repo_root_from_here

    MODEL_SLUG_MAP = {
        "BAAI/bge-small-en-v1.5": "models--qdrant--bge-small-en-v1.5-onnx-q",
    }

    for attempt in range(max_retries):
        try:
            model, device, batch = create_text_embedding(
                model_name,
                str(_get_fastembed_cache_dir()),
                repo_root=repo_root_from_here(),
            )
            list(model.embed(["warmup"]))
            logger.info("TextEmbedding model loaded and verified: %s", model_name)
            return model, device, batch
        except Exception as e:
            err_str = str(e)
            is_onnx_error = (
                "ONNXRuntimeError" in err_str
                or "Load model" in err_str
                or "File doesn't exist" in err_str
                or "model_optimized.onnx" in err_str
                or "NoSuchKey" in err_str
                or "Size does not match" in err_str
                or "corrupt" in err_str.lower()
            )
            if is_onnx_error and attempt < max_retries - 1:
                logger.warning(
                    "ONNX model load failed (attempt %d/%d): %s â€” purging cache and retrying.",
                    attempt + 1,
                    max_retries,
                    e,
                )
                slug = MODEL_SLUG_MAP.get(model_name)
                if slug:
                    _purge_fastembed_model_cache(slug)
                else:
                    # Unknown model: wipe the whole cache as fallback
                    logger.warning("Unknown model slug for '%s', wiping entire fastembed cache.", model_name)
                    cache_dir = _get_fastembed_cache_dir()
                    if cache_dir.exists():
                        shutil.rmtree(cache_dir, ignore_errors=True)
            else:
                raise


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
        self._embed_batch_size = 64
        self._reranker_model = None
        self.encryptor = MetadataEncryptor(passphrase)

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            model, device, batch = _load_text_embedding("BAAI/bge-small-en-v1.5")
            self._embedding_model = model
            self._embed_batch_size = batch
            logger.info("Vector embed device: %s (batch %s)", device, batch)
        return self._embedding_model

    def get_reranker(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        attn_implementation: str = "flash_attention_2",
    ):
        """Get or initialize the reranker model. Returns None if deps missing."""
        if self._reranker_model is None:
            try:
                import torch
                from sentence_transformers import CrossEncoder

                logger.info(
                    "Loading reranker model: %s with %s",
                    model_name,
                    attn_implementation,
                )
                model_kwargs = {}
                if attn_implementation == "flash_attention_2" and torch.cuda.is_available():
                    model_kwargs["attn_implementation"] = "flash_attention_2"
                    model_kwargs["torch_dtype"] = torch.float16
                self._reranker_model = CrossEncoder(model_name, automodel_args=model_kwargs)
            except Exception as e:
                logger.warning(
                    "Reranker unavailable (install sentence-transformers, torch): %s",
                    e,
                )
                return None
        return self._reranker_model

    async def connect(self):
        """Connect to the LanceDB database."""
        if self.db is None:
            os.makedirs(self.db_path, exist_ok=True)
            self.db = lancedb.connect(self.db_path)

        # list_tables() is the current API; table_names() was deprecated in lancedb 0.20+.
        # NOTE: in lancedb 0.29+ list_tables() returns a ListTablesResponse object
        # with a `.tables` attribute, not a plain list. Normalize to a list of names.
        raw_tables = self.db.list_tables()
        table_list = list(getattr(raw_tables, "tables", [])) if not isinstance(raw_tables, list) else raw_tables

        if self.table_name not in table_list:
            # Table is created lazily in add_documents(); avoid INFO spam on every search.
            logger.debug(
                "Vector table {} not present yet (created on first index)",
                self.table_name,
            )
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

        # Generate embeddings (batched)
        texts = [doc["text"] for doc in documents]
        batch = self._embed_batch_size
        all_embeddings: list[Any] = []
        for start in range(0, len(texts), batch):
            chunk = texts[start : start + batch]
            all_embeddings.extend(list(self.embedding_model.embed(chunk)))

        data = []
        for doc, emb in zip(documents, all_embeddings, strict=False):
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
            self.table = self.db.create_table(self.table_name, data=data, mode="overwrite")
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

        # Native LanceDB hybrid search requires an embedding function registered on
        # the table, but this store is populated with pre-computed vectors. So hybrid
        # is implemented manually as a union of semantic (vector) and keyword (FTS) hits.
        if query_type == "hybrid":
            query_vector = next(iter(self.embedding_model.embed([query])))
            vec_search = self.table.search(query_vector)
            fts_search = self.table.search(query, query_type="fts")
            if filter:
                vec_search = vec_search.where(filter)
                fts_search = fts_search.where(filter)
            vec_rows = vec_search.limit(limit).to_list()
            fts_rows = fts_search.limit(limit).to_list()
            seen: set[str] = set()
            results: list[dict[str, Any]] = []
            for row in vec_rows + fts_rows:
                row_id = row.get("id")
                if row_id in seen:
                    continue
                seen.add(row_id)
                results.append(row)
        else:
            search_obj = None
            if query_type == "fts":
                search_obj = self.table.search(query, query_type="fts")
            else:
                query_vector = next(iter(self.embedding_model.embed([query])))
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
        """Rerank search results using a Cross-Encoder. Returns docs unchanged if reranker unavailable."""
        if not documents:
            return []
        reranker = self.get_reranker(model_name, attn_implementation)
        if reranker is None:
            for doc in documents:
                doc["rerank_score"] = doc.get("_score", 0.0)
            return documents
        pairs = [[query, doc["text"]] for doc in documents]
        scores = reranker.predict(pairs)
        for doc, score in zip(documents, scores, strict=False):
            doc["rerank_score"] = float(score)
        return sorted(documents, key=lambda x: x["rerank_score"], reverse=True)

    async def delete_by_id(self, doc_id: str):
        """Delete a document by its ID."""
        await self.connect()
        if self.table:
            self.table.delete(f"id = '{doc_id}'")

    async def drop_table(self) -> None:
        """Drop the vector table entirely — used before a full reindex to prevent stale chunks."""
        await self.connect()
        raw_tables = self.db.list_tables()
        table_list = list(getattr(raw_tables, "tables", [])) if not isinstance(raw_tables, list) else raw_tables
        if self.table_name in table_list:
            self.db.drop_table(self.table_name)
            self.table = None
            logger.info(f"Dropped vector table: {self.table_name}")
        else:
            logger.debug(f"drop_table: {self.table_name} does not exist, nothing to drop")

    async def delete_by_entity_id(self, entity_id: int):
        """Delete all chunks for a specific entity."""
        await self.connect()
        if self.table:
            self.table.delete(f"metadata.entity_id = {entity_id}")
