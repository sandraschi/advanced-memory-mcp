"""Comprehensive tests for HTML export with combined export and TOC features."""

from unittest.mock import patch

import pytest

from tests.mcp.tool_invoker import mcp_fn

from advanced_memory.mcp.tools.export_html_notes import export_html_notes

# Import internal functions for direct testing


@pytest.fixture
def sample_note():
    """Sample note data for testing."""
    return {
        "title": "Test Note",
        "content": "# Test Note\n\nThis is a test note with some content.",
        "filename": "test-note.md",
        "path": "test/test-note.md",
        "folder": "test",
    }


@pytest.fixture
def multiple_notes():
    """Multiple notes for testing combined export."""
    return [
        {
            "title": "Note 1: Introduction",
            "content": "# Introduction\n\nThis is the first note.\n\n## Section 1\n\nContent here.",
            "filename": "note-1.md",
            "path": "notes/note-1.md",
            "folder": "notes",
        },
        {
            "title": "Note 2: Details",
            "content": "# Details\n\nThis is the second note.\n\n- Item 1\n- Item 2",
            "filename": "note-2.md",
            "path": "notes/note-2.md",
            "folder": "notes",
        },
        {
            "title": "Note 3: Conclusion",
            "content": "# Conclusion\n\nFinal thoughts here.\n\n## Summary\n\nAll done.",
            "filename": "note-3.md",
            "path": "notes/note-3.md",
            "folder": "notes",
        },
    ]


@pytest.fixture
def edge_case_notes():
    """Notes with edge cases for testing."""
    return [
        {
            "title": "Empty Note",
            "content": "",
            "filename": "empty.md",
            "path": "test/empty.md",
            "folder": "test",
        },
        {
            "title": "Special Characters: @#$%^&*()",
            "content": "# Special Characters\n\nTesting: @#$%^&*()\n\nAlso: <>&\"'",
            "filename": "special.md",
            "path": "test/special.md",
            "folder": "test",
        },
        {
            "title": "Unicode Test: 中文 🎉 Émojis",
            "content": "# Unicode Test\n\n中文 content\n\n🎉 Emojis work!",
            "filename": "unicode.md",
            "path": "test/unicode.md",
            "folder": "test",
        },
        {
            "title": "Code Blocks",
            "content": """# Code Blocks

```python
def hello():
    print("Hello!")
```
""",
            "filename": "code.md",
            "path": "test/code.md",
            "folder": "test",
        },
        {
            "title": "Complex Markdown",
            "content": """# Complex

## Headers
### Level 3
#### Level 4

- List item
- Another item

**Bold** and *italic*
""",
            "filename": "complex.md",
            "path": "test/complex.md",
            "folder": "test",
        },
    ]


@pytest.fixture
def export_dir(tmp_path):
    """Create a temporary export directory."""
    export_path = tmp_path / "html_exports"
    export_path.mkdir(parents=True, exist_ok=True)
    return export_path


class TestSlugify:
    """Test slugify function for anchor generation."""

    def test_basic_slugify(self):
        """Test basic text slugification."""
        from advanced_memory.mcp.tools.export_html_notes import _slugify

        assert _slugify("Hello World") == "hello-world"
        assert _slugify("Test-Note") == "test-note"
        assert _slugify("Simple") == "simple"

    def test_special_characters(self):
        """Test slugify with special characters."""
        from advanced_memory.mcp.tools.export_html_notes import _slugify

        assert _slugify("Test@#$%") == "test"
        assert _slugify("Note with spaces") == "note-with-spaces"
        assert _slugify("Multiple---Dashes") == "multiple-dashes"

    def test_unicode(self):
        """Test slugify with unicode characters."""
        from advanced_memory.mcp.tools.export_html_notes import _slugify

        result = _slugify("中文 Test")
        assert "test" in result.lower()
        assert result.replace("test", "").strip("-")  # Should handle unicode gracefully


class TestExtractHeadings:
    """Test heading extraction for TOC."""

    def test_extract_simple_headings(self):
        """Test extracting simple headings."""
        from advanced_memory.mcp.tools.export_html_notes import _extract_headings

        content = "# Title\n\n## Section 1\n\n### Subsection"
        headings = _extract_headings(content, "note")

        assert len(headings) == 3
        assert headings[0]["level"] == 2  # Level incremented (was H1)
        assert headings[0]["title"] == "Title"
        assert headings[1]["level"] == 3  # Level incremented (was H2)
        assert headings[1]["title"] == "Section 1"

    def test_extract_nested_headings(self):
        """Test extracting nested headings."""
        from advanced_memory.mcp.tools.export_html_notes import _extract_headings

        content = """# Main
## Section A
### Subsection A1
## Section B
### Subsection B1
"""
        headings = _extract_headings(content, "test")

        assert len(headings) == 5
        assert headings[0]["level"] == 2  # Main (H1 -> level 2)
        assert headings[1]["level"] == 3  # Section A (H2 -> level 3)
        assert headings[2]["level"] == 4  # Subsection A1 (H3 -> level 4)

    def test_no_headings(self):
        """Test with no headings."""
        from advanced_memory.mcp.tools.export_html_notes import _extract_headings

        content = "Just plain text\n\nNo headings here."
        headings = _extract_headings(content, "note")
        assert len(headings) == 0


class TestAddHeadingAnchors:
    """Test adding anchor IDs to HTML headings."""

    def test_add_anchors_to_headings(self):
        """Test adding anchor IDs."""
        from advanced_memory.mcp.tools.export_html_notes import _add_heading_anchors

        html = "<h1>Title</h1><h2>Section</h2>"
        result = _add_heading_anchors(html, "note")

        assert 'id="' in result
        assert "note" in result.lower()

    def test_multiple_headings(self):
        """Test multiple headings get anchors."""
        from advanced_memory.mcp.tools.export_html_notes import _add_heading_anchors

        html = "<h1>First</h1><p>Content</p><h2>Second</h2>"
        result = _add_heading_anchors(html, "test")

        # Count id attributes
        id_count = result.count('id="')
        assert id_count == 2  # Two headings


class TestCombinedHTMLExport:
    """Test combined HTML export functionality."""

    @pytest.mark.asyncio
    async def test_export_single_note_combined(self, export_dir, sample_note):
        """Test exporting a single note as combined HTML."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "combined.html"

        notes_data = [sample_note]
        result = await _export_combined_html(notes_data, export_path, "Test Export", make_toc=True)

        assert "Combined HTML Export Complete" in result
        html_file = export_path.with_suffix(".html")
        assert html_file.exists()

        # Check file content
        content = html_file.read_text(encoding="utf-8")
        assert "Test Export" in content
        assert sample_note["title"] in content

    @pytest.mark.asyncio
    async def test_export_multiple_notes_combined(self, export_dir, multiple_notes):
        """Test exporting multiple notes as combined HTML."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "combined.html"

        result = await _export_combined_html(multiple_notes, export_path, "Multiple Notes", make_toc=True)

        assert "Combined HTML Export Complete" in result
        assert "Notes Combined: 3" in result
        html_file = export_path.with_suffix(".html")
        assert html_file.exists()

        # Check all notes are in the HTML
        content = html_file.read_text(encoding="utf-8")
        for note in multiple_notes:
            assert note["title"] in content

    @pytest.mark.asyncio
    async def test_toc_generation(self, export_dir, multiple_notes):
        """Test TOC is generated in combined HTML."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "with-toc.html"

        await _export_combined_html(multiple_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        assert "Table of Contents" in content
        assert "toc-nav" in content
        assert "toc-list" in content

        # Check note titles are in TOC
        for note in multiple_notes:
            assert note["title"] in content

    @pytest.mark.asyncio
    async def test_no_toc_when_disabled(self, export_dir, multiple_notes):
        """Test TOC is not generated when make_toc=False."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "no-toc.html"

        await _export_combined_html(multiple_notes, export_path, "Test", make_toc=False)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        assert "toc-nav" not in content
        assert "Table of Contents" not in content

    @pytest.mark.asyncio
    async def test_heading_anchors_in_toc(self, export_dir, multiple_notes):
        """Test that headings get anchor IDs and appear in TOC."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "anchors.html"

        await _export_combined_html(multiple_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        # Check for anchor links in TOC
        assert 'href="#' in content
        # Check for id attributes on headings
        assert 'id="' in content

    @pytest.mark.asyncio
    async def test_edge_cases_combined(self, export_dir, edge_case_notes):
        """Test combined export with edge case notes."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "edge-cases.html"

        result = await _export_combined_html(edge_case_notes, export_path, "Edge Cases", make_toc=True)

        assert "Combined HTML Export Complete" in result
        html_file = export_path.with_suffix(".html")
        assert html_file.exists()

        content = html_file.read_text(encoding="utf-8")
        # Check all notes are present
        for note in edge_case_notes:
            assert note["title"] in content

    @pytest.mark.asyncio
    async def test_mermaid_support(self, export_dir):
        """Test Mermaid diagrams are supported in combined HTML."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        notes_with_mermaid = [
            {
                "title": "Mermaid Note",
                "content": "# Test\n\n```mermaid\ngraph TD\nA-->B\n```",
                "filename": "mermaid.md",
                "path": "test/mermaid.md",
                "folder": "test",
            }
        ]

        export_path = export_dir / "mermaid.html"
        await _export_combined_html(notes_with_mermaid, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        assert "mermaid" in content.lower()

    @pytest.mark.asyncio
    async def test_html_file_extension(self, export_dir, sample_note):
        """Test that .html extension is added if missing."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "no-extension"

        await _export_combined_html([sample_note], export_path, "Test", make_toc=True)

        # Should create file with .html extension
        html_file = export_path.with_suffix(".html")
        assert html_file.exists()

    @pytest.mark.asyncio
    async def test_empty_notes_combined(self, export_dir):
        """Test combined export with empty notes."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        empty_notes = [
            {
                "title": "Empty",
                "content": "",
                "filename": "empty.md",
                "path": "test/empty.md",
                "folder": "test",
            }
        ]

        export_path = export_dir / "empty.html"
        await _export_combined_html(empty_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "Empty" in content


class TestSearchQuery:
    """Test search query functionality."""

    @pytest.mark.asyncio
    async def test_search_notes_by_query_integration(self, tmp_path):
        """Test searching notes by query through full export."""
        mock_notes = [
            {
                "title": "Docker Basics",
                "content": "# Docker Basics\n\nContent here.",
                "filename": "docker-basics.md",
                "path": "docker/basics.md",
                "folder": "docker",
            },
            {
                "title": "Docker Advanced",
                "content": "# Docker Advanced\n\nAdvanced content.",
                "filename": "docker-advanced.md",
                "path": "docker/advanced.md",
                "folder": "docker",
            },
        ]

        export_path = tmp_path / "search.html"

        with patch("advanced_memory.mcp.tools.export_html_notes._search_notes") as mock_search:
            mock_search.return_value = mock_notes

            result = await mcp_fn(export_html_notes)(
                export_path=str(export_path),
                search_query="docker",
                combine_into_one=True,
                make_toc=True,
                show_after_export=False,
            )

        assert "Combined HTML Export Complete" in result
        html_file = export_path.with_suffix(".html")
        assert html_file.exists()

        content = html_file.read_text(encoding="utf-8")
        assert "Docker Basics" in content
        assert "Docker Advanced" in content


class TestExportHTMLNotesIntegration:
    """Integration tests for export_html_notes with new features."""

    @pytest.mark.asyncio
    async def test_combined_export_with_search(self, tmp_path):
        """Test combined HTML export with search query."""
        export_path = tmp_path / "combined.html"

        mock_notes = [
            {
                "title": "Docker Note 1",
                "content": "# Docker Note 1\n\nContent about docker.",
                "filename": "docker-1.md",
                "path": "docker/docker-1.md",
                "folder": "docker",
            },
            {
                "title": "Docker Note 2",
                "content": "# Docker Note 2\n\nMore docker content.",
                "filename": "docker-2.md",
                "path": "docker/docker-2.md",
                "folder": "docker",
            },
        ]

        with patch("advanced_memory.mcp.tools.export_html_notes._search_notes") as mock_search:
            mock_search.return_value = mock_notes

            result = await mcp_fn(export_html_notes)(
                export_path=str(export_path),
                search_query="docker",
                combine_into_one=True,
                make_toc=True,
                html_title="Docker Collection",
                show_after_export=False,
            )

        assert "Combined HTML Export Complete" in result
        html_file = export_path.with_suffix(".html")
        assert html_file.exists()

        content = html_file.read_text(encoding="utf-8")
        assert "Docker Collection" in content
        assert "Docker Note 1" in content
        assert "Docker Note 2" in content
        assert "Table of Contents" in content

    @pytest.mark.asyncio
    async def test_combined_export_with_folder(self, tmp_path):
        """Test combined HTML export from folder."""
        export_path = tmp_path / "folder-export.html"

        mock_notes = [
            {
                "title": "Folder Note",
                "content": "# Folder Note\n\nContent.",
                "filename": "note.md",
                "path": "folder/note.md",
                "folder": "folder",
            }
        ]

        with patch("advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder") as mock_get:
            mock_get.return_value = mock_notes

            result = await mcp_fn(export_html_notes)(
                export_path=str(export_path),
                source_folder="folder",
                combine_into_one=True,
                make_toc=True,
                show_after_export=False,
            )

        assert "Combined HTML Export Complete" in result
        html_file = export_path.with_suffix(".html")
        assert html_file.exists()

    @pytest.mark.asyncio
    async def test_toc_includes_note_titles(self, tmp_path, multiple_notes):
        """Test that TOC includes note titles as top-level items."""
        export_path = tmp_path / "toc-test.html"

        with patch("advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder") as mock_get:
            mock_get.return_value = multiple_notes

            await mcp_fn(export_html_notes)(
                export_path=str(export_path),
                combine_into_one=True,
                make_toc=True,
                show_after_export=False,
            )

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")

        # Check all note titles appear in TOC
        for note in multiple_notes:
            assert note["title"] in content

    @pytest.mark.asyncio
    async def test_toc_hierarchical_structure(self, tmp_path):
        """Test TOC has proper hierarchical structure."""
        notes_with_headings = [
            {
                "title": "Main Note",
                "content": "# Main\n\n## Section A\n\n### Sub A1\n\n## Section B",
                "filename": "main.md",
                "path": "main.md",
                "folder": "",
            }
        ]

        export_path = tmp_path / "hierarchy.html"

        with patch("advanced_memory.mcp.tools.export_html_notes._get_notes_from_folder") as mock_get:
            mock_get.return_value = notes_with_headings

            from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

            await _export_combined_html(notes_with_headings, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")

        # Check TOC has different levels
        assert "toc-level-1" in content
        assert "toc-level-2" in content or "toc-level-3" in content


class TestCombinedHTMLStructure:
    """Test the structure of combined HTML files."""

    @pytest.mark.asyncio
    async def test_html_structure(self, export_dir, multiple_notes):
        """Test combined HTML has proper structure."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "structure.html"

        await _export_combined_html(multiple_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")

        # Check basic HTML structure
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "</html>" in content

        # Check combined structure
        assert "combined-header" in content
        assert "combined-content" in content
        assert "note-section" in content

    @pytest.mark.asyncio
    async def test_css_included(self, export_dir, sample_note):
        """Test CSS styles are included in combined HTML."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "css-test.html"

        await _export_combined_html([sample_note], export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        assert "<style>" in content
        assert "combined-header" in content  # CSS class reference

    @pytest.mark.asyncio
    async def test_responsive_design(self, export_dir, sample_note):
        """Test responsive CSS is included."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "responsive.html"

        await _export_combined_html([sample_note], export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        assert "@media" in content


class TestCombinedHTMLTOC:
    """Test TOC functionality in combined HTML."""

    @pytest.mark.asyncio
    async def test_toc_sticky_sidebar(self, export_dir, multiple_notes):
        """Test TOC sidebar is sticky."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "sticky-toc.html"

        await _export_combined_html(multiple_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        assert "position: sticky" in content or "sticky" in content.lower()

    @pytest.mark.asyncio
    async def test_toc_clickable_links(self, export_dir, multiple_notes):
        """Test TOC links are clickable."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html, _slugify

        export_path = export_dir / "toc-links.html"

        await _export_combined_html(multiple_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        # Check for anchor links
        assert 'href="#' in content
        # Check links reference note anchors
        for note in multiple_notes:
            anchor = _slugify(note["title"])
            assert anchor in content

    @pytest.mark.asyncio
    async def test_toc_note_title_entries(self, export_dir, multiple_notes):
        """Test note titles appear as TOC entries."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        export_path = export_dir / "toc-entries.html"

        await _export_combined_html(multiple_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        # All note titles should be in TOC
        for note in multiple_notes:
            assert note["title"] in content


class TestExportEdgeCases:
    """Test edge cases for HTML export."""

    @pytest.mark.asyncio
    async def test_empty_search_results(self, tmp_path):
        """Test export with no search results."""
        export_path = tmp_path / "empty.html"

        with patch("advanced_memory.mcp.tools.export_html_notes._search_notes") as mock_search:
            mock_search.return_value = []

            result = await mcp_fn(export_html_notes)(
                export_path=str(export_path),
                search_query="nonexistent",
                combine_into_one=True,
                show_after_export=False,
            )

        assert "No notes found" in result

    @pytest.mark.asyncio
    async def test_special_characters_in_titles(self, export_dir):
        """Test handling special characters in note titles."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        special_notes = [
            {
                "title": "Note with @#$% Special",
                "content": "# Special\n\nContent",
                "filename": "special.md",
                "path": "special.md",
                "folder": "",
            }
        ]

        export_path = export_dir / "special.html"
        await _export_combined_html(special_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        assert "Note with" in content  # Should handle special chars

    @pytest.mark.asyncio
    async def test_very_long_titles(self, export_dir):
        """Test handling very long note titles."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        long_title = "A" * 300
        long_note = [
            {
                "title": long_title,
                "content": "# Long\n\nContent",
                "filename": "long.md",
                "path": "long.md",
                "folder": "",
            }
        ]

        export_path = export_dir / "long.html"
        await _export_combined_html(long_note, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        assert html_file.exists()

    @pytest.mark.asyncio
    async def test_unicode_in_content(self, export_dir):
        """Test Unicode content in combined HTML."""
        from advanced_memory.mcp.tools.export_html_notes import _export_combined_html

        unicode_notes = [
            {
                "title": "Unicode Test",
                "content": "# Unicode\n\n中文 content\n\n🎉 Emojis!",
                "filename": "unicode.md",
                "path": "unicode.md",
                "folder": "",
            }
        ]

        export_path = export_dir / "unicode.html"
        await _export_combined_html(unicode_notes, export_path, "Test", make_toc=True)

        html_file = export_path.with_suffix(".html")
        content = html_file.read_text(encoding="utf-8")
        assert "Unicode" in content
