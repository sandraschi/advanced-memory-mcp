"""
Integration tests for adn_nav ls operation (migrated from list_directory MCP tool).

Tests the complete list directory workflow: MCP client -> MCP server -> FastAPI -> database -> file system

NOTE: The new adn_nav ls surface (NavLsOp) exposes only ``path`` - the old
``depth`` and ``file_name_glob`` parameters are not part of the new wire
schema. Tests that relied on server-side depth recursion or glob filtering are
adapted: deep structure is verified by navigating level by level, and glob
filtering is applied client-side to the (depth-1) listing.
"""

import pytest
from fastmcp import Client


async def write_note(client: Client, title: str, folder: str, content: str, tags: str | None = None):
    """Helper: write a note through the adn_notes portmanteau."""
    op = {"operation": "write", "title": title, "folder": folder, "content": content}
    if tags is not None:
        op["tags"] = tags
    await client.call_tool("adn_notes", {"op": op})


async def list_directory(client: Client, path: str = "/") -> str:
    """List a directory through the adn_nav ls operation."""
    result = await client.call_tool(
        "adn_nav",
        {"op": {"operation": "ls", "path": path}},
    )
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    return result.content[0].text


def doc_lines(list_text: str) -> list[str]:
    """Extract [DOC] file lines from a listing."""
    return [line for line in list_text.split("\n") if "[DOC]" in line]


@pytest.mark.asyncio
async def test_list_directory_basic_operation(mcp_server, app):
    """Test basic ls operation showing root contents."""

    async with Client(mcp_server) as client:
        # Create some test files and directories first.
        # NOTE: The new adn_notes write surface defaults folder="" to "inbox",
        # so the "root" note lands in the inbox folder.
        await write_note(
            client,
            "Root Note",
            "",  # Root folder -> defaults to inbox on the new surface
            "# Root Note\n\nThis is in the root directory.",
            "test,root",
        )

        await write_note(
            client,
            "Project Planning",
            "projects",
            "# Project Planning\n\nPlanning document for projects.",
            "planning,project",
        )

        await write_note(
            client,
            "Meeting Notes",
            "meetings",
            "# Meeting Notes\n\nNotes from the meeting.",
            "meeting,notes",
        )

        # List root directory
        list_text = await list_directory(client, "/")

        # Should show the structure
        assert "Contents of '/' (depth 1)" in list_text
        assert "[FOLDER] meetings" in list_text
        assert "[FOLDER] projects" in list_text
        assert "[FOLDER] inbox" in list_text  # folder="" defaults to inbox
        assert "Pagination:" in list_text
        assert "directories" in list_text or "folder" in list_text.lower()

        # The root note lives in the inbox folder - verify file + title there
        list_inbox = await list_directory(client, "/inbox")
        assert "[DOC] Root_Note.md" in list_inbox
        assert "Root Note" in list_inbox  # Title should be shown
        assert "file" in list_inbox


@pytest.mark.asyncio
async def test_list_directory_specific_folder(mcp_server, app):
    """Test listing contents of a specific folder."""

    async with Client(mcp_server) as client:
        # Create nested structure
        await write_note(
            client,
            "Task List",
            "work",
            "# Task List\n\nWork tasks for today.",
            "work,tasks",
        )

        await write_note(
            client,
            "Project Alpha",
            "work/projects",
            "# Project Alpha\n\nAlpha project documentation.",
            "project,alpha",
        )

        await write_note(
            client,
            "Daily Standup",
            "work/meetings",
            "# Daily Standup\n\nStandup meeting notes.",
            "meeting,standup",
        )

        # List specific folder
        list_text = await list_directory(client, "/work")

        # Should show work folder contents
        assert "Contents of '/work' (depth 1)" in list_text
        assert "[FOLDER] meetings" in list_text or "📁 meetings" in list_text
        assert "[FOLDER] projects" in list_text or "📁 projects" in list_text
        assert "[DOC] Task_List.md" in list_text or "📄 Task_List.md" in list_text
        assert "work/Task_List.md" in list_text  # Path should be shown without leading slash


@pytest.mark.asyncio
async def test_list_directory_with_depth(mcp_server, app):
    """Test recursive directory listing with depth control.

    NOTE: NavLsOp has no depth field (always lists depth 1). The deep nested
    structure is verified by navigating level by level instead.
    """

    async with Client(mcp_server) as client:
        # Create deep nested structure
        await write_note(
            client,
            "Deep Note",
            "research/ml/algorithms/neural-networks",
            "# Deep Note\n\nDeep learning research.",
            "research,ml,deep",
        )

        await write_note(
            client,
            "ML Overview",
            "research/ml",
            "# ML Overview\n\nMachine learning overview.",
            "research,ml,overview",
        )

        await write_note(
            client,
            "Research Index",
            "research",
            "# Research Index\n\nIndex of research topics.",
            "research,index",
        )

        # Level 1: /research should show ml folder + Research Index
        list_text = await list_directory(client, "/research")
        assert "Contents of '/research' (depth 1)" in list_text
        assert "[FOLDER] ml" in list_text or "📁 ml" in list_text
        assert "[DOC] Research_Index.md" in list_text or "📄 Research_Index.md" in list_text

        # Level 2: /research/ml should show the nested algorithms folder
        list_text = await list_directory(client, "/research/ml")
        assert "[FOLDER] algorithms" in list_text or "📁 algorithms" in list_text
        assert "[DOC] ML_Overview.md" in list_text or "📄 ML_Overview.md" in list_text
        assert "ML Overview" in list_text  # ML Overview title should appear

        # Level 3: /research/ml/algorithms should show the deepest note
        list_text = await list_directory(client, "/research/ml/algorithms")
        assert "[FOLDER] neural-networks" in list_text or "📁 neural-networks" in list_text


@pytest.mark.asyncio
async def test_list_directory_with_glob_pattern(mcp_server, app):
    """Test directory listing with glob pattern filtering.

    NOTE: NavLsOp has no file_name_glob field. The filtering intent is
    preserved by filtering the returned (depth-1) listing client-side.
    """

    async with Client(mcp_server) as client:
        # Create files with different patterns
        await write_note(
            client,
            "Meeting 2025-01-15",
            "meetings",
            "# Meeting 2025-01-15\n\nMonday meeting notes.",
            "meeting,january",
        )

        await write_note(
            client,
            "Meeting 2025-01-22",
            "meetings",
            "# Meeting 2025-01-22\n\nMonday meeting notes.",
            "meeting,january",
        )

        await write_note(
            client,
            "Project Status",
            "meetings",
            "# Project Status\n\nProject status update.",
            "meeting,project",
        )

        # List the meetings folder
        list_text = await list_directory(client, "/meetings")

        # Simulate the 'Meeting*' glob filter on the listing
        meeting_docs = [line for line in doc_lines(list_text) if "Meeting_2025" in line]

        # Should show only matching files
        assert len(meeting_docs) == 2
        assert "Meeting_2025-01-15.md" in meeting_docs[0]
        assert "Meeting_2025-01-22.md" in meeting_docs[1]
        # The non-matching file is excluded by the filter
        assert not any("Project_Status" in line for line in meeting_docs)


@pytest.mark.asyncio
async def test_list_directory_empty_directory(mcp_server, app):
    """Test listing an empty directory."""

    async with Client(mcp_server) as client:
        # List non-existent/empty directory
        list_text = await list_directory(client, "/empty")

        # Should indicate no files found
        assert "No files found in directory '/empty'" in list_text


@pytest.mark.asyncio
async def test_list_directory_glob_no_matches(mcp_server, app):
    """Test glob pattern that matches no files.

    NOTE: NavLsOp has no file_name_glob field. The '*.py' glob intent is
    preserved by verifying no Python files exist in the returned listing.
    """

    async with Client(mcp_server) as client:
        # Create some files
        await write_note(
            client,
            "Document One",
            "docs",
            "# Document One\n\nFirst document.",
            "doc",
        )

        # List the docs folder
        list_text = await list_directory(client, "/docs")

        # The listing contains the markdown file...
        assert "Document_One.md" in list_text

        # ...but no Python files match the '*.py' pattern
        assert not any(line.strip().endswith(".py") for line in doc_lines(list_text))


@pytest.mark.asyncio
async def test_list_directory_various_file_types(mcp_server, app):
    """Test listing directories with various file types and metadata display."""

    async with Client(mcp_server) as client:
        # Create files with different characteristics
        await write_note(
            client,
            "Simple Note",
            "mixed",
            "# Simple Note\n\nA simple note.",
            "simple",
        )

        await write_note(
            client,
            "Complex Document with Long Title",
            "mixed",
            "# Complex Document with Long Title\n\nA more complex document.",
            "complex,long",
        )

        # List the mixed directory
        list_text = await list_directory(client, "/mixed")

        # Should show file names, paths, and titles
        assert "Simple_Note.md" in list_text
        assert "mixed/Simple_Note.md" in list_text
        assert "Complex_Document_with_Long_Title.md" in list_text
        assert "mixed/Complex_Document_with_Long_Title.md" in list_text
        assert "This page: 2 items (2 files)" in list_text


@pytest.mark.asyncio
async def test_list_directory_default_parameters(mcp_server, app):
    """Test ls with default parameters (root, depth=1)."""

    async with Client(mcp_server) as client:
        # Create some content
        await write_note(
            client,
            "Default Test",
            "default-test",
            "# Default Test\n\nTesting default parameters.",
            "default",
        )

        # List with minimal parameters (should use defaults)
        list_text = await list_directory(client)

        # Should show root directory with depth 1
        assert "Contents of '/' (depth 1)" in list_text
        assert "[FOLDER] default-test" in list_text or "📁 default-test" in list_text
        assert "Pagination:" in list_text


@pytest.mark.asyncio
async def test_list_directory_deep_recursion(mcp_server, app):
    """Test directory listing with maximum depth.

    NOTE: NavLsOp has no depth field (always lists depth 1). The deep structure
    is verified by walking down the tree level by level.
    """

    async with Client(mcp_server) as client:
        # Create very deep structure
        await write_note(
            client,
            "Level 5 Note",
            "level1/level2/level3/level4/level5",
            "# Level 5 Note\n\nVery deep note.",
            "deep,level5",
        )

        await write_note(
            client,
            "Level 3 Note",
            "level1/level2/level3",
            "# Level 3 Note\n\nMid-level note.",
            "medium,level3",
        )

        # Walk down the tree level by level
        current_path = "/level1"
        list_text = await list_directory(client, current_path)
        assert "[FOLDER] level2" in list_text or "📁 level2" in list_text

        current_path = "/level1/level2"
        list_text = await list_directory(client, current_path)
        assert "[FOLDER] level3" in list_text or "📁 level3" in list_text

        current_path = "/level1/level2/level3"
        list_text = await list_directory(client, current_path)
        assert "Level_3_Note.md" in list_text

        current_path = "/level1/level2/level3/level4"
        list_text = await list_directory(client, current_path)
        assert "[FOLDER] level5" in list_text or "📁 level5" in list_text

        current_path = "/level1/level2/level3/level4/level5"
        list_text = await list_directory(client, current_path)
        assert "Level_5_Note.md" in list_text


@pytest.mark.asyncio
async def test_list_directory_complex_glob_patterns(mcp_server, app):
    """Test various glob patterns for file filtering.

    NOTE: NavLsOp has no file_name_glob field. The 'Project*' glob intent is
    preserved by filtering the returned (depth-1) listing client-side.
    """

    async with Client(mcp_server) as client:
        # Create files with different naming patterns
        await write_note(
            client,
            "Project Alpha Plan",
            "patterns",
            "# Project Alpha Plan\n\nAlpha planning.",
            "project,alpha",
        )

        await write_note(
            client,
            "Project Beta Plan",
            "patterns",
            "# Project Beta Plan\n\nBeta planning.",
            "project,beta",
        )

        await write_note(
            client,
            "Meeting Minutes",
            "patterns",
            "# Meeting Minutes\n\nMeeting notes.",
            "meeting",
        )

        # List the patterns folder
        list_text = await list_directory(client, "/patterns")

        # Simulate the 'Project*' glob filter on the listing
        project_docs = [line for line in doc_lines(list_text) if "Project_" in line]

        # Should show only Project files
        assert len(project_docs) == 2
        assert any("Project_Alpha_Plan.md" in line for line in project_docs)
        assert any("Project_Beta_Plan.md" in line for line in project_docs)
        # The non-matching file is excluded by the filter
        assert not any("Meeting" in line for line in project_docs)
