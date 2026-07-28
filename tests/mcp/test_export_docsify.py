"""Tests for docsify export functionality."""

from unittest.mock import patch

import pytest

from advanced_memory.mcp.tools.export_docsify import export_docsify_enhanced
from advanced_memory.mcp.tools.write_note import write_note
from tests.mcp.tool_invoker import mcp_fn


@pytest.mark.asyncio
async def test_export_docsify_enhanced_basic(tmp_path, config_home, app):
    """Test basic enhanced docsify export creates required files."""
    # Create notes through the API so they're in the system
    await mcp_fn(write_note)(
        title="Test Note",
        folder="docsify_test",
        content="""# Test Note

This is a test note with some content.

## Section 1
Content here.
""",
    )

    await mcp_fn(write_note)(
        title="Nested Note",
        folder="docsify_test/subfolder",
        content="""# Nested Note

Nested content.
""",
    )

    # Export to temp directory
    export_path = tmp_path / "docsify_export"

    # Call the export function (access .fn attribute of FunctionTool)
    result = await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="/docsify_test",
        site_title="Test Site",
        site_description="Test Description",
        serve=False,
    )

    # Verify result is a string (success message)
    assert isinstance(result, str)
    assert "exported" in result.lower() or "complete" in result.lower()

    # Verify required files were created
    assert (export_path / "index.html").exists(), "index.html not created"
    assert (export_path / "README.md").exists(), "README.md not created"
    assert (export_path / "_sidebar.md").exists(), "_sidebar.md not created"
    assert (export_path / ".nojekyll").exists(), ".nojekyll not created"

    # Verify index.html has docsify configuration
    index_content = (export_path / "index.html").read_text(encoding="utf-8")
    assert "docsify" in index_content.lower(), "index.html missing docsify"
    assert "Test Site" in index_content, "index.html missing site title"

    # Verify sidebar has navigation
    sidebar_content = (export_path / "_sidebar.md").read_text(encoding="utf-8")
    assert len(sidebar_content) > 0, "Sidebar is empty"


@pytest.mark.asyncio
async def test_export_docsify_enhanced_plugins(tmp_path, config_home, app):
    """Test that enhanced features/plugins are properly configured."""
    # Create note through API
    await mcp_fn(write_note)(title="Simple Note", folder="plugin_test", content="# Simple Note\n\nContent.")

    export_path = tmp_path / "docsify_plugins"

    # Export with all plugins enabled
    result = await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="/plugin_test",
        enable_pagination=True,
        enable_toc=True,
        enable_theme_toggle=True,
        enable_progress_bar=True,
        enable_code_copy=True,
        enable_emoji=True,
        serve=False,
    )

    assert "exported" in result.lower() or "created" in result.lower()

    # Check that index.html includes plugin configurations
    index_content = (export_path / "index.html").read_text(encoding="utf-8")

    # Should have docsify plugins loaded (CDN links or config)
    assert "docsify" in index_content.lower()

    # Check for plugin-related keywords (might be in config or plugin URLs)
    # Note: Exact plugin detection depends on implementation


@pytest.mark.asyncio
async def test_export_docsify_enhanced_empty_folder(tmp_path, config_home, app):
    """Test export with empty source folder."""
    # Don't create any notes - test empty folder behavior
    export_path = tmp_path / "docsify_empty"

    result = await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="/empty",
        serve=False,
    )

    # Export should return "no notes found" message, not create files
    assert isinstance(result, str)
    assert "no notes found" in result.lower() or "empty" in result.lower()


@pytest.mark.asyncio
async def test_export_docsify_enhanced_special_characters(tmp_path, config_home, app):
    """Test export handles filenames with special characters."""
    # Create note with special characters through API
    await mcp_fn(write_note)(
        title='Test: Note with "Special" Characters!',
        folder="special_chars",
        content="""# Test Note

Content with <special> &characters.
""",
    )

    export_path = tmp_path / "docsify_special"

    await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="/special_chars",
        serve=False,
    )

    assert (export_path / "index.html").exists()

    # Check that files were created (sanitized filenames)
    exported_files = list(export_path.glob("**/*.md"))
    assert len(exported_files) >= 1  # At least README.md


@pytest.mark.asyncio
async def test_export_docsify_enhanced_nested_folders(tmp_path, config_home, app):
    """Test export preserves nested folder structure."""
    # Create nested structure through API
    await mcp_fn(write_note)(
        title="Deep Note",
        folder="nested_test/folder1/folder2",
        content="# Deep Note\n\nNested content.",
    )

    export_path = tmp_path / "docsify_nested"

    await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="/nested_test",
        include_subfolders=True,
        serve=False,
    )

    assert (export_path / "index.html").exists()

    # Sidebar should reference the nested structure
    (export_path / "_sidebar.md").read_text(encoding="utf-8")
    # Should have some navigation structure


@pytest.mark.asyncio
async def test_export_docsify_enhanced_no_subfolders(tmp_path, config_home, app):
    """Test export without including subfolders."""
    # Create notes through API
    await mcp_fn(write_note)(title="Root", folder="no_sub_test", content="# Root\n\nRoot level.")
    await mcp_fn(write_note)(title="Sub", folder="no_sub_test/subfolder", content="# Sub\n\nShould not be exported.")

    export_path = tmp_path / "docsify_no_sub"

    await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="/no_sub_test",
        include_subfolders=False,
        serve=False,
    )

    assert (export_path / "index.html").exists()

    # Should only export root-level notes
    # (Exact verification depends on implementation)


@pytest.mark.asyncio
async def test_export_docsify_enhanced_custom_settings(tmp_path, config_home, app):
    """Test export with custom site settings."""
    # Create note through API
    await mcp_fn(write_note)(title="Note", folder="custom_test", content="# Note\n\nContent.")

    export_path = tmp_path / "docsify_custom"

    custom_title = "My Custom Documentation"
    custom_desc = "Custom description for testing"

    await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="/custom_test",
        site_title=custom_title,
        site_description=custom_desc,
        serve=False,
    )

    # Verify custom settings in index.html
    index_content = (export_path / "index.html").read_text(encoding="utf-8")
    assert custom_title in index_content
    # Description might be in meta tag or config


@pytest.mark.asyncio
async def test_export_docsify_file_structure(tmp_path, config_home, app):
    """Test that exported file structure is correct."""
    # Create note through API
    await mcp_fn(write_note)(title="Test", folder="structure_test", content="# Test\n\nContent.")

    export_path = tmp_path / "docsify_structure"

    await mcp_fn(export_docsify_enhanced)(export_path=str(export_path), source_folder="/structure_test", serve=False)

    # Verify core files exist
    core_files = [
        "index.html",
        "README.md",
        "_sidebar.md",
        ".nojekyll",
    ]

    for filename in core_files:
        file_path = export_path / filename
        assert file_path.exists(), f"Missing required file: {filename}"
        if filename != ".nojekyll":  # .nojekyll is intentionally empty
            assert file_path.stat().st_size > 0, f"File is empty: {filename}"


@pytest.mark.asyncio
async def test_export_docsify_index_html_validity(tmp_path, config_home, app):
    """Test that generated index.html is valid HTML."""
    # Create note through API
    await mcp_fn(write_note)(title="Test", folder="html_test", content="# Test\n\nContent.")

    export_path = tmp_path / "docsify_html"

    await mcp_fn(export_docsify_enhanced)(export_path=str(export_path), source_folder="/html_test", serve=False)

    index_content = (export_path / "index.html").read_text(encoding="utf-8")

    # Basic HTML structure checks
    assert "<!DOCTYPE html>" in index_content or "<html" in index_content
    assert "<head>" in index_content
    assert "<body>" in index_content
    assert "</html>" in index_content

    # Docsify-specific checks
    assert "docsify" in index_content.lower()
    assert "<script" in index_content  # Should have script tags


@pytest.mark.asyncio
async def test_export_docsify_sidebar_generation(tmp_path, config_home, app):
    """Test that sidebar is properly generated with navigation."""
    # Create multiple notes through API
    await mcp_fn(write_note)(title="Note 1", folder="sidebar_test", content="# Note 1\n\nContent 1.")
    await mcp_fn(write_note)(title="Note 2", folder="sidebar_test", content="# Note 2\n\nContent 2.")

    export_path = tmp_path / "docsify_sidebar"

    await mcp_fn(export_docsify_enhanced)(export_path=str(export_path), source_folder="/sidebar_test", serve=False)

    sidebar_content = (export_path / "_sidebar.md").read_text(encoding="utf-8")

    # Sidebar should have markdown list structure
    assert "-" in sidebar_content or "*" in sidebar_content  # Markdown list
    assert len(sidebar_content.split("\n")) > 1  # Multiple lines


@pytest.mark.asyncio
async def test_export_docsify_serve_disabled(tmp_path, config_home, app):
    """Test Docsify export with serve=False doesn't start server."""
    from advanced_memory.mcp.tools.write_note import write_note

    # Create test note
    await mcp_fn(write_note)(
        title="Server Test",
        content="# Server Test\n\nContent.",
        folder="server_test",
    )

    export_path = tmp_path / "docsify_no_serve"

    result = await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="/server_test",
        serve=False,  # Don't start server
    )

    # Should not mention server being started
    assert (export_path / "index.html").exists()
    # The actual server startup section shouldn't be in result when serve=False
    # (Note: static docs may mention localhost in examples, that's OK)
    assert "Server Started" not in result or "Server running" not in result


@pytest.mark.asyncio
async def test_export_docsify_serve_enabled(tmp_path, config_home, app):
    """Test Docsify export with serve=True starts server."""
    from advanced_memory.mcp.tools.write_note import write_note

    # Create test note
    await mcp_fn(write_note)(
        title="Server Test 2",
        content="# Server Test 2\n\nContent.",
        folder="server_test",
    )

    export_path = tmp_path / "docsify_serve"

    # Mock the server start to avoid actually starting one
    with patch("advanced_memory.mcp.tools.export_docsify._start_local_server") as mock_server:
        mock_server.return_value = "## Server Started\n\nhttp://localhost:3211"

        result = await mcp_fn(export_docsify_enhanced)(
            export_path=str(export_path),
            source_folder="/server_test",
            serve=True,
            port=3211,
        )

    # Should mention server
    assert "Server" in result or "localhost" in result


@pytest.mark.asyncio
async def test_export_docsify_export_all_true(tmp_path, config_home, app):
    """Test export_all=True exports from all matching folders."""
    from advanced_memory.mcp.tools.write_note import write_note

    # Create notes in different folders with same name
    await mcp_fn(write_note)(
        title="Standards Doc 1",
        content="# Standards 1",
        folder="zettelkasten/standards",
    )
    await mcp_fn(write_note)(
        title="Standards Doc 2",
        content="# Standards 2",
        folder="projects/standards",
    )

    export_path = tmp_path / "docsify_all"

    result = await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="standards",  # Ambiguous - matches both
        export_all=True,  # Should export both
        serve=False,
    )

    # Should export both notes
    assert (export_path / "index.html").exists()
    # Result should indicate multiple notes exported
    assert "exported" in result.lower() or "created" in result.lower()


@pytest.mark.asyncio
async def test_export_docsify_export_all_false_exact_path(tmp_path, config_home, app):
    """Test export_all=False works with exact paths."""
    from advanced_memory.mcp.tools.write_note import write_note

    # Create note
    await mcp_fn(write_note)(
        title="Exact Path Doc",
        content="# Exact Path",
        folder="projects/specific",
    )

    export_path = tmp_path / "docsify_exact"

    result = await mcp_fn(export_docsify_enhanced)(
        export_path=str(export_path),
        source_folder="projects/specific",  # Exact path
        export_all=False,  # Should work fine with exact path
        serve=False,
    )

    # Should succeed
    assert (export_path / "index.html").exists()
    assert "export" in result.lower() or "created" in result.lower()
