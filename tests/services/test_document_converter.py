"""Tests for document converter service"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from advanced_memory.services.document_converter import (
    DocumentConverter,
    get_document_converter,
)


@pytest.fixture
def converter():
    """Create document converter instance"""
    return DocumentConverter()


@pytest.fixture
def test_file(tmp_path):
    """Create test file"""
    file = tmp_path / "test.txt"
    file.write_text("Test content")
    return file


def test_converter_singleton():
    """Test that get_document_converter returns same instance"""
    converter1 = get_document_converter()
    converter2 = get_document_converter()

    assert converter1 is converter2


def test_check_pandoc():
    """Test Pandoc detection"""
    converter = DocumentConverter()

    # Should detect whether pandoc is installed
    assert isinstance(converter.pandoc_available, bool)


@pytest.mark.asyncio
async def test_convert_txt(converter, tmp_path):
    """Test converting plain text file"""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Plain text content\nMultiple lines")

    result = await converter.convert_txt(txt_file)

    assert result is not None
    assert "# Test" in result
    assert "Plain text content" in result
    assert "text file" in result.lower()


@pytest.mark.asyncio
async def test_convert_nonexistent_file(converter, tmp_path):
    """Test converting file that doesn't exist"""
    nonexistent = tmp_path / "doesnt-exist.md"

    result = await converter.convert(nonexistent, "txt")

    assert result is None


@pytest.mark.asyncio
async def test_convert_unsupported_type(converter, test_file):
    """Test converting unsupported document type"""
    result = await converter.convert(test_file, "unsupported")  # type: ignore

    assert result is None


@pytest.mark.asyncio
async def test_convert_docx_without_pandoc(converter, tmp_path):
    """Test docx conversion when Pandoc is not available"""
    docx_file = tmp_path / "test.docx"
    docx_file.write_text("fake docx")

    # Mock pandoc as unavailable
    with patch.object(converter, "pandoc_available", False):
        result = await converter.convert_docx(docx_file)

    # Should return placeholder
    assert result is not None
    assert "Pandoc is not installed" in result


@pytest.mark.asyncio
async def test_convert_html_without_pandoc(converter, tmp_path):
    """Test HTML conversion when Pandoc is not available"""
    html_file = tmp_path / "test.html"
    html_file.write_text("<html><body>Test</body></html>")

    # Mock pandoc as unavailable
    with patch.object(converter, "pandoc_available", False):
        result = await converter.convert_html(html_file)

    # Should return placeholder
    assert result is not None
    assert "Pandoc is not installed" in result


@pytest.mark.asyncio
async def test_convert_pdf_without_tools(converter, tmp_path):
    """Test PDF conversion when no tools available"""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("fake pdf")

    # Mock both pypdf and pdftotext as unavailable
    with patch("advanced_memory.services.document_converter.shutil.which", return_value=None):
        with patch.dict("sys.modules", {"pypdf": None}):
            result = await converter.convert_pdf(pdf_file)

    # Should return placeholder
    assert result is not None
    # Either placeholder or error message
    assert "pdf" in result.lower() or "PDF" in result


@pytest.mark.asyncio
async def test_clean_pdf_text(converter):
    """Test PDF text cleaning"""
    raw_text = """Some   text   with   extra   spaces


Multiple



newlines

Hyphen-
ated words"""

    cleaned = converter._clean_pdf_text(raw_text)

    # Should reduce multiple newlines
    assert "\n\n\n" not in cleaned

    # Should remove excessive spaces
    assert "   " not in cleaned

    # Should fix hyphenated words
    assert "Hyphen-\nated" not in cleaned


@pytest.mark.asyncio
async def test_create_placeholder(converter, tmp_path):
    """Test placeholder creation for failed conversions"""
    file = tmp_path / "failed.pdf"
    file.write_text("fake")

    placeholder = converter._create_placeholder(file, "PDF", "Test error")

    assert "# Failed" in placeholder
    assert "PDF" in placeholder
    assert "Test error" in placeholder
    assert "Error" in placeholder


@pytest.mark.asyncio
async def test_convert_dispatcher(converter, tmp_path):
    """Test that convert dispatches to correct method"""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("content")

    result = await converter.convert(txt_file, "txt")

    assert result is not None
    assert "# Test" in result


@pytest.mark.asyncio
async def test_docx_conversion_with_pandoc(converter, tmp_path):
    """Test docx conversion when Pandoc is available"""
    if not converter.pandoc_available:
        pytest.skip("Pandoc not installed")

    docx_file = tmp_path / "test.docx"

    # Create minimal docx-like file
    docx_file.write_text("content")

    # Mock subprocess to return markdown
    mock_result = MagicMock()
    mock_result.stdout = "# Converted\n\nContent"

    with patch("subprocess.run", return_value=mock_result):
        result = await converter.convert_docx(docx_file)

    assert result is not None
    assert "Converted" in result or "Test" in result


@pytest.mark.asyncio
async def test_html_conversion_with_pandoc(converter, tmp_path):
    """Test HTML conversion when Pandoc is available"""
    if not converter.pandoc_available:
        pytest.skip("Pandoc not installed")

    html_file = tmp_path / "test.html"
    html_file.write_text("<html><body><h1>Test</h1></body></html>")

    # Mock subprocess to return markdown
    mock_result = MagicMock()
    mock_result.stdout = "# Test\n\nContent"

    with patch("subprocess.run", return_value=mock_result):
        result = await converter.convert_html(html_file)

    assert result is not None
    assert "Test" in result or "HTML" in result


@pytest.mark.asyncio
async def test_pandoc_failure_handling(converter, tmp_path):
    """Test handling of Pandoc conversion failures"""
    if not converter.pandoc_available:
        pytest.skip("Pandoc not installed")

    docx_file = tmp_path / "bad.docx"
    docx_file.write_text("invalid content")

    # Mock subprocess to raise error
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "pandoc", stderr="Error")):
        result = await converter.convert_docx(docx_file)

    # Should return placeholder with error
    assert result is not None
    assert "Error" in result or "Conversion failed" in result
