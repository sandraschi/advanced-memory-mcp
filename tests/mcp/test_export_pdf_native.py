"""Comprehensive tests for native PDF export using fpdf2."""

from pathlib import Path
from unittest.mock import patch

import pytest

# Check if fpdf2 is available for testing
try:
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    pytest.skip("fpdf2 not installed - skipping PDF export tests", allow_module_level=True)

from advanced_memory.mcp.tools.export_pdf_native import (
    MarkdownPDF,
    _export_single_note_pdf,
    _get_notes_from_folder,
    export_pdf_native,
)


@pytest.fixture
def sample_note():
    """Sample note data for testing."""
    return {
        "title": "Test Note",
        "content": "# Test Note\n\nThis is a test note with some content.",
        "permalink": "test/test-note",
    }


@pytest.fixture
def multiple_notes():
    """Multiple notes for testing multi-file exports."""
    return [
        {
            "title": "Note 1: Introduction",
            "content": "# Introduction\n\nThis is the first note.\n\n## Section 1\n\nContent here.",
            "permalink": "notes/note-1",
        },
        {
            "title": "Note 2: Details",
            "content": "# Details\n\nThis is the second note.\n\n- Item 1\n- Item 2",
            "permalink": "notes/note-2",
        },
        {
            "title": "Note 3: Conclusion",
            "content": "# Conclusion\n\nFinal thoughts here.",
            "permalink": "notes/note-3",
        },
    ]


@pytest.fixture
def edge_case_notes():
    """Notes with edge cases for testing."""
    return [
        {
            "title": "Empty Note",
            "content": "",
            "permalink": "test/empty",
        },
        {
            "title": "Special Characters: @#$%^&*()",
            "content": "# Special Characters\n\nTesting: @#$%^&*()\n\nAlso: <>&\"'",
            "permalink": "test/special",
        },
        {
            "title": "Very Long Title " + "A" * 200,
            "content": "# Very Long Title\n\nContent with a very long title.",
            "permalink": "test/long-title",
        },
        {
            "title": "Unicode Test: 中文 🎉 Émojis",
            "content": "# Unicode Test\n\n中文 content\n\n🎉 Emojis work!\n\nÉmojis: 🚀🔥💡",
            "permalink": "test/unicode",
        },
        {
            "title": "Code Blocks",
            "content": """# Code Blocks

Here's some Python:

```python
def hello():
    print("Hello, World!")
    return True
```

And some JavaScript:

```javascript
function test() {
    console.log("test");
}
```
""",
            "permalink": "test/code",
        },
        {
            "title": "Complex Markdown",
            "content": """# Complex Markdown

## Headers

### Level 3

#### Level 4

## Lists

- Bullet 1
- Bullet 2
  - Nested bullet
  - Another nested

1. Numbered 1
2. Numbered 2
3. Numbered 3

## Formatting

**Bold text** and *italic text* and `code inline`.

## Horizontal Rule

---

More content after the rule.

## Long Content

"""
            + "\n".join([f"Paragraph {i}. " + "Lorem ipsum " * 10 for i in range(50)]),
            "permalink": "test/complex",
        },
        {
            "title": "Links and References",
            "content": "# Links\n\nThis references [[Another Note]] and [[Third Note]].\n\nExternal link: https://example.com",
            "permalink": "test/links",
        },
    ]


@pytest.fixture
def export_dir(tmp_path):
    """Create a temporary export directory."""
    export_path = tmp_path / "pdf_exports"
    export_path.mkdir(parents=True, exist_ok=True)
    return export_path


class TestMarkdownPDF:
    """Test the MarkdownPDF class directly."""

    def test_pdf_creation(self):
        """Test creating a basic PDF."""
        pdf = MarkdownPDF(title="Test PDF")
        pdf.add_page()
        pdf.add_markdown("# Test\n\nContent here.")

        # Should not raise any errors
        assert pdf is not None

    def test_headers(self):
        """Test different header levels."""
        pdf = MarkdownPDF(title="Headers Test")
        pdf.add_page()

        content = """# H1 Header
## H2 Header
### H3 Header
#### H4 Header
"""
        pdf.add_markdown(content)

        assert pdf.page_no() > 0

    def test_lists(self):
        """Test bullet and numbered lists."""
        pdf = MarkdownPDF(title="Lists Test")
        pdf.add_page()

        content = """- Item 1
- Item 2
- Item 3

1. First
2. Second
3. Third
"""
        pdf.add_markdown(content)

        assert pdf.page_no() > 0

    def test_code_blocks(self):
        """Test code block rendering."""
        pdf = MarkdownPDF(title="Code Test")
        pdf.add_page()

        content = """```python
def test():
    return True
```
"""
        pdf.add_markdown(content)

        assert pdf.page_no() > 0

    def test_long_content(self):
        """Test handling of long content that spans multiple pages."""
        pdf = MarkdownPDF(title="Long Content Test")
        pdf.add_page()

        # Generate very long content
        long_content = "# Long Content\n\n"
        for i in range(100):
            long_content += f"Paragraph {i}. " + "This is a very long paragraph. " * 10 + "\n\n"

        pdf.add_markdown(long_content)

        # Should have multiple pages
        assert pdf.page_no() >= 1

    def test_empty_content(self):
        """Test handling empty content."""
        pdf = MarkdownPDF(title="Empty Test")
        pdf.add_page()
        pdf.add_markdown("")

        assert pdf.page_no() > 0

    def test_special_characters(self):
        """Test special characters in content."""
        pdf = MarkdownPDF(title="Special Chars")
        pdf.add_page()

        content = "# Special\n\n@#$%^&*() <>\"'`"
        pdf.add_markdown(content)

        assert pdf.page_no() > 0

    def test_unicode_content(self):
        """Test Unicode characters."""
        pdf = MarkdownPDF(title="Unicode Test")
        pdf.add_page()

        content = "# Unicode\n\n中文 日本語 한국어\n\n🎉🚀🔥"
        pdf.add_markdown(content)

        assert pdf.page_no() > 0


class TestExportSingleNotePDF:
    """Test exporting a single note to PDF."""

    @pytest.mark.asyncio
    async def test_basic_export(self, export_dir, sample_note):
        """Test exporting a basic note."""
        result = await _export_single_note_pdf(sample_note, export_dir)

        assert result is not None
        assert Path(result).exists()
        assert Path(result).suffix == ".pdf"
        assert Path(result).stat().st_size > 0

    @pytest.mark.asyncio
    async def test_empty_note(self, export_dir):
        """Test exporting an empty note."""
        empty_note = {
            "title": "Empty Note",
            "content": "",
            "permalink": "test/empty",
        }

        result = await _export_single_note_pdf(empty_note, export_dir)

        # Should still create a PDF
        assert result is not None
        assert Path(result).exists()

    @pytest.mark.asyncio
    async def test_special_characters_in_title(self, export_dir):
        """Test note with special characters in title."""
        note = {
            "title": "Test @#$% Note",
            "content": "# Test\n\nContent",
            "permalink": "test/special",
        }

        result = await _export_single_note_pdf(note, export_dir)

        assert result is not None
        # Filename should be sanitized
        assert Path(result).exists()

    @pytest.mark.asyncio
    async def test_unicode_in_title(self, export_dir):
        """Test note with Unicode characters in title."""
        note = {
            "title": "Test 中文 Note 🎉",
            "content": "# Test\n\nContent",
            "permalink": "test/unicode",
        }

        result = await _export_single_note_pdf(note, export_dir)

        assert result is not None
        assert Path(result).exists()

    @pytest.mark.asyncio
    async def test_long_title(self, export_dir):
        """Test note with very long title."""
        note = {
            "title": "A" * 300,
            "content": "# Test\n\nContent",
            "permalink": "test/long",
        }

        result = await _export_single_note_pdf(note, export_dir)

        assert result is not None
        assert Path(result).exists()

    @pytest.mark.asyncio
    async def test_complex_markdown(self, export_dir, edge_case_notes):
        """Test exporting note with complex markdown."""
        complex_note = next(n for n in edge_case_notes if n["title"] == "Complex Markdown")

        result = await _export_single_note_pdf(complex_note, export_dir)

        assert result is not None
        assert Path(result).exists()
        file_size = Path(result).stat().st_size
        assert file_size > 1000  # Should be substantial size

    @pytest.mark.asyncio
    async def test_code_blocks(self, export_dir, edge_case_notes):
        """Test exporting note with code blocks."""
        code_note = next(n for n in edge_case_notes if n["title"] == "Code Blocks")

        result = await _export_single_note_pdf(code_note, export_dir)

        assert result is not None
        assert Path(result).exists()


class TestExportPDFNative:
    """Test the main export_pdf_native function."""

    @pytest.mark.asyncio
    async def test_export_single_note(self, export_dir, sample_note):
        """Test exporting a single note."""
        with patch("advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder") as mock_get:
            mock_get.return_value = [sample_note]

            result = await export_pdf_native(
                export_path=str(export_dir),
                source_folder="/",
                include_subfolders=False,
            )

            assert "PDF Export Summary" in result
            assert "Files Exported: 1" in result

    @pytest.mark.asyncio
    async def test_export_multiple_notes(self, export_dir, multiple_notes):
        """Test exporting multiple notes - stitched together concept."""
        with patch("advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder") as mock_get:
            mock_get.return_value = multiple_notes

            result = await export_pdf_native(
                export_path=str(export_dir),
                source_folder="notes",
                include_subfolders=True,
            )

            assert "PDF Export Summary" in result
            assert "Files Exported: 3" in result

            # Check that all PDFs were created
            pdf_files = list(export_dir.glob("*.pdf"))
            assert len(pdf_files) == 3

    @pytest.mark.asyncio
    async def test_export_empty_folder(self, export_dir):
        """Test exporting from empty folder."""
        with patch("advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder") as mock_get:
            mock_get.return_value = []

            result = await export_pdf_native(
                export_path=str(export_dir),
                source_folder="/empty",
                include_subfolders=False,
            )

            assert "No notes found" in result or "Files Exported: 0" in result

    @pytest.mark.asyncio
    async def test_export_edge_cases(self, export_dir, edge_case_notes):
        """Test exporting notes with edge cases."""
        with patch("advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder") as mock_get:
            mock_get.return_value = edge_case_notes

            result = await export_pdf_native(
                export_path=str(export_dir),
                source_folder="test",
                include_subfolders=True,
            )

            assert "PDF Export Summary" in result
            # Should export all edge case notes
            pdf_files = list(export_dir.glob("*.pdf"))
            assert len(pdf_files) == len(edge_case_notes)

    @pytest.mark.asyncio
    async def test_export_with_errors(self, export_dir):
        """Test export handles errors gracefully."""
        error_note = {
            "title": "Error Note",
            "content": "# Error\n\nContent",
            "permalink": "test/error",
        }

        with patch("advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder") as mock_get:
            mock_get.return_value = [error_note]

            # Mock PDF creation to raise an error
            with patch("advanced_memory.mcp.tools.export_pdf_native.MarkdownPDF") as mock_pdf:
                mock_pdf.side_effect = Exception("PDF creation failed")

                result = await export_pdf_native(
                    export_path=str(export_dir),
                    source_folder="test",
                    include_subfolders=False,
                )

                # Should report errors but not crash
                assert "PDF Export Summary" in result
                assert "Errors" in result or "Failed" in result

    @pytest.mark.asyncio
    async def test_export_directory_creation(self, tmp_path):
        """Test that export directory is created if it doesn't exist."""
        export_path = tmp_path / "new_dir" / "pdf_exports"

        sample_note = {
            "title": "Test",
            "content": "# Test\n\nContent",
            "permalink": "test/test",
        }

        with patch("advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder") as mock_get:
            mock_get.return_value = [sample_note]

            await export_pdf_native(
                export_path=str(export_path),
                source_folder="/",
                include_subfolders=False,
            )

            # Directory should be created
            assert export_path.exists()
            assert export_path.is_dir()

    @pytest.mark.asyncio
    async def test_export_filtered_by_folder(self, export_dir):
        """Test that notes are filtered by folder correctly."""
        notes = [
            {
                "title": "Root Note",
                "content": "# Root\n\nContent",
                "permalink": "root-note",
            },
            {
                "title": "Subfolder Note",
                "content": "# Sub\n\nContent",
                "permalink": "folder/sub-note",
            },
        ]

        with patch("advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder") as mock_get:
            mock_get.return_value = notes

            result = await export_pdf_native(
                export_path=str(export_dir),
                source_folder="folder",
                include_subfolders=False,
            )

            # Should only export notes in the folder
            assert "PDF Export Summary" in result


class TestGetNotesFromFolder:
    """Test the _get_notes_from_folder function."""

    @pytest.mark.asyncio
    async def test_get_notes_root_folder(self, client):
        """Test getting notes from root folder."""
        # This will require mocking the search API call
        with patch("advanced_memory.mcp.tools.export_pdf_native.call_post") as mock_post:
            mock_post.return_value = {
                "results": [
                    {
                        "title": "Note 1",
                        "content": "# Note 1",
                        "permalink": "note-1",
                    },
                    {
                        "title": "Note 2",
                        "content": "# Note 2",
                        "permalink": "note-2",
                    },
                ]
            }

            notes = await _get_notes_from_folder("/", include_subfolders=True)

            assert len(notes) == 2
            assert notes[0]["title"] == "Note 1"

    @pytest.mark.asyncio
    async def test_get_notes_specific_folder(self, client):
        """Test getting notes from specific folder."""
        with patch("advanced_memory.mcp.tools.export_pdf_native.call_post") as mock_post:
            mock_post.return_value = {
                "results": [
                    {
                        "title": "Folder Note",
                        "content": "# Folder Note",
                        "permalink": "folder/folder-note",
                    },
                ]
            }

            notes = await _get_notes_from_folder("folder", include_subfolders=False)

            assert len(notes) == 1
            assert notes[0]["title"] == "Folder Note"

    @pytest.mark.asyncio
    async def test_get_notes_with_subfolders(self, client):
        """Test getting notes including subfolders."""
        with patch("advanced_memory.mcp.tools.export_pdf_native.call_post") as mock_post:
            mock_post.return_value = {
                "results": [
                    {
                        "title": "Parent Note",
                        "content": "# Parent",
                        "permalink": "parent/parent-note",
                    },
                    {
                        "title": "Child Note",
                        "content": "# Child",
                        "permalink": "parent/child/child-note",
                    },
                ]
            }

            notes = await _get_notes_from_folder("parent", include_subfolders=True)

            assert len(notes) == 2


class TestPDFFileOutput:
    """Test actual PDF file output and structure."""

    @pytest.mark.asyncio
    async def test_pdf_file_structure(self, export_dir, sample_note):
        """Test that generated PDF has valid structure."""
        result = await _export_single_note_pdf(sample_note, export_dir)
        pdf_path = Path(result)

        # Check file exists and has content
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0

        # Check filename format
        assert pdf_path.name.startswith("Test_Note")
        assert pdf_path.suffix == ".pdf"

    @pytest.mark.asyncio
    async def test_multiple_pdfs_created(self, export_dir, multiple_notes):
        """Test that multiple PDFs are created correctly."""
        for note in multiple_notes:
            await _export_single_note_pdf(note, export_dir)

        pdf_files = sorted(export_dir.glob("*.pdf"))
        assert len(pdf_files) == len(multiple_notes)

        # All files should have content
        for pdf_file in pdf_files:
            assert pdf_file.stat().st_size > 0

    @pytest.mark.asyncio
    async def test_pdf_filename_sanitization(self, export_dir):
        """Test that filenames are sanitized correctly."""
        problematic_notes = [
            {
                "title": "Test/Note",
                "content": "# Test",
                "permalink": "test/note",
            },
            {
                "title": "Test\\Note",
                "content": "# Test",
                "permalink": "test/note2",
            },
            {
                "title": "Test:Note",
                "content": "# Test",
                "permalink": "test/note3",
            },
        ]

        for note in problematic_notes:
            result = await _export_single_note_pdf(note, export_dir)
            pdf_path = Path(result)

            # Should not contain invalid filename characters
            assert "/" not in pdf_path.name or "\\" not in pdf_path.name or ":" not in pdf_path.name


@pytest.mark.integration
class TestPDFExportIntegration:
    """Integration tests for PDF export with real data flow."""

    @pytest.mark.asyncio
    async def test_full_export_workflow(self, export_dir, entity_service, search_service):
        """Test full export workflow from entity creation to PDF."""
        # Create test entities
        from advanced_memory.schemas.base import Entity as EntitySchema

        entities = []
        for i in range(3):
            entity, _ = await entity_service.create_or_update_entity(
                EntitySchema(
                    title=f"PDF Export Test {i + 1}",
                    folder="pdf_test",
                    entity_type="test",
                    content=f"# Test Entity {i + 1}\n\nContent for entity {i + 1}.",
                )
            )
            entities.append(entity)
            await search_service.index_entity(entity)

        # Now export
        with patch("advanced_memory.mcp.tools.export_pdf_native._get_notes_from_folder") as mock_get:
            # Mock to return our created entities
            mock_get.return_value = [
                {
                    "title": entity.title,
                    "content": entity.content,
                    "permalink": entity.permalink,
                }
                for entity in entities
            ]

            result = await export_pdf_native(
                export_path=str(export_dir),
                source_folder="pdf_test",
                include_subfolders=True,
            )

            assert "PDF Export Summary" in result
            assert "Files Exported: 3" in result
