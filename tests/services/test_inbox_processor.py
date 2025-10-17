"""Tests for inbox processor service"""

from unittest.mock import AsyncMock, patch

import pytest

from advanced_memory.services.inbox_processor import InboxProcessor, get_inbox_processor


@pytest.fixture
def inbox_dir(tmp_path):
    """Create temporary inbox directory"""
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    return inbox


@pytest.fixture
def converted_dir(tmp_path):
    """Create temporary converted directory"""
    converted = tmp_path / "converted"
    converted.mkdir()
    return converted


@pytest.fixture
def processor(inbox_dir, converted_dir):
    """Create inbox processor with temp directories"""
    return InboxProcessor(inbox_dir=inbox_dir, converted_dir=converted_dir)


@pytest.mark.asyncio
async def test_process_markdown_file(processor, inbox_dir):
    """Test processing markdown file"""
    # Create test markdown file
    md_file = inbox_dir / "test-note.md"
    md_file.write_text("# Test Note\n\nContent here.")

    with patch.object(processor, "_trigger_sync", new=AsyncMock()):
        result = await processor.process_file(md_file)

    assert result["status"] == "success"
    assert result["action"] == "moved"
    assert "test-note.md" in result["target"]

    # File should be moved (no longer in inbox)
    assert not md_file.exists()


@pytest.mark.asyncio
async def test_process_text_file(processor, inbox_dir):
    """Test processing plain text file"""
    txt_file = inbox_dir / "notes.txt"
    txt_file.write_text("Some text content here.")

    with patch.object(processor, "_trigger_sync", new=AsyncMock()):
        result = await processor.process_file(txt_file)

    assert result["status"] == "success"
    assert result["action"] == "converted"

    # Original should be removed
    assert not txt_file.exists()


@pytest.mark.asyncio
async def test_skip_readme(processor, inbox_dir):
    """Test that README.md is skipped"""
    readme = inbox_dir / "README.md"
    readme.write_text("# Readme")

    result = await processor.process_file(readme)

    assert result["status"] == "skipped"
    assert readme.exists()  # Should not be processed


@pytest.mark.asyncio
async def test_skip_gitkeep(processor, inbox_dir):
    """Test that .gitkeep is skipped"""
    gitkeep = inbox_dir / ".gitkeep"
    gitkeep.write_text("")

    result = await processor.process_file(gitkeep)

    assert result["status"] == "skipped"
    assert gitkeep.exists()


@pytest.mark.asyncio
async def test_skip_hidden_files(processor, inbox_dir):
    """Test that hidden files are skipped"""
    hidden = inbox_dir / ".hidden.txt"
    hidden.write_text("hidden content")

    result = await processor.process_file(hidden)

    assert result["status"] == "skipped"
    assert hidden.exists()


@pytest.mark.asyncio
async def test_unsupported_file_type(processor, inbox_dir):
    """Test handling of unsupported file types"""
    unsupported = inbox_dir / "file.xyz"
    unsupported.write_text("content")

    result = await processor.process_file(unsupported)

    assert result["status"] == "unsupported"
    assert "supported_types" in result


@pytest.mark.asyncio
async def test_process_inbox_empty(processor):
    """Test processing empty inbox"""
    results = await processor.process_inbox()

    assert results == []


@pytest.mark.asyncio
async def test_process_inbox_multiple_files(processor, inbox_dir):
    """Test processing multiple files"""
    # Create several files
    (inbox_dir / "note1.md").write_text("# Note 1")
    (inbox_dir / "note2.txt").write_text("Note 2 content")
    (inbox_dir / "note3.md").write_text("# Note 3")

    with patch.object(processor, "_trigger_sync", new=AsyncMock()):
        results = await processor.process_inbox()

    assert len(results) == 3
    successful = sum(1 for r in results if r["status"] == "success")
    assert successful == 3


@pytest.mark.asyncio
async def test_process_file_not_found(processor, inbox_dir):
    """Test handling of non-existent file"""
    nonexistent = inbox_dir / "does-not-exist.md"

    result = await processor.process_file(nonexistent)

    assert result["status"] == "error"
    assert "not found" in result["message"].lower()


@pytest.mark.asyncio
async def test_avoid_filename_collision(processor, inbox_dir):
    """Test that filename collisions are avoided"""
    # Create file in inbox
    md_file = inbox_dir / "duplicate.md"
    md_file.write_text("# Original")

    # Create file with same name in project (simulate existing note)
    with patch.object(processor, "_trigger_sync", new=AsyncMock()):
        # First call should use base name
        result1 = await processor.process_file(md_file)
        assert "duplicate" in result1["target"]

        # Create another file with same name
        md_file2 = inbox_dir / "duplicate.md"
        md_file2.write_text("# Another")

        # Second call should append _1
        result2 = await processor.process_file(md_file2)
        assert "duplicate_1" in result2["target"] or "duplicate.md" in result2["target"]


@pytest.mark.asyncio
async def test_singleton_inbox_processor():
    """Test that get_inbox_processor returns same instance"""
    processor1 = get_inbox_processor()
    processor2 = get_inbox_processor()

    assert processor1 is processor2


@pytest.mark.asyncio
async def test_process_document_with_converter_mock(processor, inbox_dir):
    """Test document processing with mocked converter"""
    docx_file = inbox_dir / "document.docx"
    docx_file.write_text("fake docx content")

    # Mock the converter to return markdown
    with patch.object(
        processor.converter,
        "convert",
        new=AsyncMock(return_value="# Converted Document\n\nContent here."),
    ):
        with patch.object(processor, "_trigger_sync", new=AsyncMock()):
            result = await processor.process_file(docx_file)

    assert result["status"] == "success"
    assert result["action"] == "converted"

    # Original should be moved to converted dir
    assert not docx_file.exists()
