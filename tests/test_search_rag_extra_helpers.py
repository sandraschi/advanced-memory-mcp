"""Unit tests for LanceDB extra-root chunk helpers."""

from advanced_memory.services.search_service import (
    _chunk_text_by_paragraphs,
    _external_chunk_entity_id,
    _is_rag_extra_metadata,
)


def test_chunk_paragraphs_single_and_split() -> None:
    assert _chunk_text_by_paragraphs("hello", 500) == ["hello"]
    # max_chars below 200 is raised to 200 inside the helper
    para = "w" * 200
    body = f"{para}\n\n{para}\n\n{para}"
    chunks = _chunk_text_by_paragraphs(body, max_chars=250)
    assert len(chunks) >= 3


def test_external_entity_id_negative_and_distinct() -> None:
    a = _external_chunk_entity_id(r"D:\x\doc.md", 0)
    b = _external_chunk_entity_id(r"D:\x\doc.md", 1)
    assert a < 0 and b < 0
    assert a != b


def test_is_rag_extra_metadata() -> None:
    assert _is_rag_extra_metadata({"rag_extra_root": True}) is True
    assert _is_rag_extra_metadata({"rag_extra_root": 1}) is True
    assert _is_rag_extra_metadata({"rag_extra_root": "true"}) is True
    assert _is_rag_extra_metadata({}) is False
