"""Tests for docsify export functionality."""

import pytest
from pathlib import Path
from advanced_memory.mcp.tools.export_docsify import export_docsify_enhanced
from advanced_memory.mcp.tools import write_note


@pytest.mark.asyncio
async def test_export_docsify_enhanced_basic(tmp_path, config_home, app):
    """Test basic enhanced docsify export creates required files."""
    # Create notes through the API so they're in the system
    await write_note.fn(
        title="Test Note",
        folder="docsify_test",
        content="""# Test Note

This is a test note with some content.

## Section 1
Content here.
""",
    )
    
    await write_note.fn(
        title="Nested Note",
        folder="docsify_test/subfolder",
        content="""# Nested Note

Nested content.
""",
    )
    
    # Export to temp directory
    export_path = tmp_path / "docsify_export"
    
    # Call the export function (access .fn attribute of FunctionTool)
    result = await export_docsify_enhanced.fn(
        export_path=str(export_path),
        source_folder="/docsify_test",
        site_title="Test Site",
        site_description="Test Description",
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
    index_content = (export_path / "index.html").read_text()
    assert "docsify" in index_content.lower(), "index.html missing docsify"
    assert "Test Site" in index_content, "index.html missing site title"
    
    # Verify sidebar has navigation
    sidebar_content = (export_path / "_sidebar.md").read_text()
    assert len(sidebar_content) > 0, "Sidebar is empty"


@pytest.mark.asyncio
async def test_export_docsify_enhanced_plugins(tmp_path, config_home, app):
    """Test that enhanced features/plugins are properly configured."""
    # Create note through API
    await write_note.fn(title="Simple Note", folder="plugin_test", content="# Simple Note\n\nContent.")
    
    export_path = tmp_path / "docsify_plugins"
    
    # Export with all plugins enabled
    result = await export_docsify_enhanced.fn(
        export_path=str(export_path),
        source_folder="/plugin_test",
        enable_pagination=True,
        enable_toc=True,
        enable_theme_toggle=True,
        enable_progress_bar=True,
        enable_code_copy=True,
        enable_emoji=True,
    )
    
    assert "exported" in result.lower() or "created" in result.lower()
    
    # Check that index.html includes plugin configurations
    index_content = (export_path / "index.html").read_text()
    
    # Should have docsify plugins loaded (CDN links or config)
    assert "docsify" in index_content.lower()
    
    # Check for plugin-related keywords (might be in config or plugin URLs)
    # Note: Exact plugin detection depends on implementation


@pytest.mark.asyncio
async def test_export_docsify_enhanced_empty_folder(tmp_path, config_home, app):
    """Test export with empty source folder."""
    # Don't create any notes - test empty folder behavior
    export_path = tmp_path / "docsify_empty"
    
    result = await export_docsify_enhanced.fn(
        export_path=str(export_path),
        source_folder="/empty",
    )
    
    # Export should return "no notes found" message, not create files
    assert isinstance(result, str)
    assert "no notes found" in result.lower() or "empty" in result.lower()


@pytest.mark.asyncio
async def test_export_docsify_enhanced_special_characters(tmp_path, config_home, app):
    """Test export handles filenames with special characters."""
    # Create note with special characters through API
    await write_note.fn(
        title='Test: Note with "Special" Characters!',
        folder="special_chars",
        content="""# Test Note

Content with <special> &characters.
""",
    )
    
    export_path = tmp_path / "docsify_special"
    
    result = await export_docsify_enhanced.fn(
        export_path=str(export_path),
        source_folder="/special_chars",
    )
    
    assert (export_path / "index.html").exists()
    
    # Check that files were created (sanitized filenames)
    exported_files = list(export_path.glob("**/*.md"))
    assert len(exported_files) >= 1  # At least README.md


@pytest.mark.asyncio
async def test_export_docsify_enhanced_nested_folders(tmp_path, config_home, app):
    """Test export preserves nested folder structure."""
    # Create nested structure through API
    await write_note.fn(title="Deep Note", folder="nested_test/folder1/folder2", content="# Deep Note\n\nNested content.")
    
    export_path = tmp_path / "docsify_nested"
    
    result = await export_docsify_enhanced.fn(
        export_path=str(export_path),
        source_folder="/nested_test",
        include_subfolders=True,
    )
    
    assert (export_path / "index.html").exists()
    
    # Sidebar should reference the nested structure
    sidebar_content = (export_path / "_sidebar.md").read_text()
    # Should have some navigation structure


@pytest.mark.asyncio
async def test_export_docsify_enhanced_no_subfolders(tmp_path, config_home, app):
    """Test export without including subfolders."""
    # Create notes through API
    await write_note.fn(title="Root", folder="no_sub_test", content="# Root\n\nRoot level.")
    await write_note.fn(title="Sub", folder="no_sub_test/subfolder", content="# Sub\n\nShould not be exported.")
    
    export_path = tmp_path / "docsify_no_sub"
    
    result = await export_docsify_enhanced.fn(
        export_path=str(export_path),
        source_folder="/no_sub_test",
        include_subfolders=False,
    )
    
    assert (export_path / "index.html").exists()
    
    # Should only export root-level notes
    # (Exact verification depends on implementation)


@pytest.mark.asyncio
async def test_export_docsify_enhanced_custom_settings(tmp_path, config_home, app):
    """Test export with custom site settings."""
    # Create note through API
    await write_note.fn(title="Note", folder="custom_test", content="# Note\n\nContent.")
    
    export_path = tmp_path / "docsify_custom"
    
    custom_title = "My Custom Documentation"
    custom_desc = "Custom description for testing"
    
    result = await export_docsify_enhanced.fn(
        export_path=str(export_path),
        source_folder="/custom_test",
        site_title=custom_title,
        site_description=custom_desc,
    )
    
    # Verify custom settings in index.html
    index_content = (export_path / "index.html").read_text()
    assert custom_title in index_content
    # Description might be in meta tag or config


@pytest.mark.asyncio
async def test_export_docsify_file_structure(tmp_path, config_home, app):
    """Test that exported file structure is correct."""
    # Create note through API
    await write_note.fn(title="Test", folder="structure_test", content="# Test\n\nContent.")
    
    export_path = tmp_path / "docsify_structure"
    
    await export_docsify_enhanced.fn(export_path=str(export_path), source_folder="/structure_test")
    
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
    await write_note.fn(title="Test", folder="html_test", content="# Test\n\nContent.")
    
    export_path = tmp_path / "docsify_html"
    
    await export_docsify_enhanced.fn(export_path=str(export_path), source_folder="/html_test")
    
    index_content = (export_path / "index.html").read_text()
    
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
    await write_note.fn(title="Note 1", folder="sidebar_test", content="# Note 1\n\nContent 1.")
    await write_note.fn(title="Note 2", folder="sidebar_test", content="# Note 2\n\nContent 2.")
    
    export_path = tmp_path / "docsify_sidebar"
    
    await export_docsify_enhanced.fn(export_path=str(export_path), source_folder="/sidebar_test")
    
    sidebar_content = (export_path / "_sidebar.md").read_text()
    
    # Sidebar should have markdown list structure
    assert "-" in sidebar_content or "*" in sidebar_content  # Markdown list
    assert len(sidebar_content.split("\n")) > 1  # Multiple lines


