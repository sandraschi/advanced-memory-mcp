"""Integration test for project state synchronization between MCP session and CLI config.

This test validates the fix for GitHub issue #148 where MCP session and CLI commands
had inconsistent project state, causing "Project not found" errors and edit failures.

The test simulates the exact workflow reported in the issue:
1. MCP server starts with a default project
2. Default project is changed
3. MCP tools should immediately use the new project (no restart needed)
4. All operations should work consistently in the new project context

NOTE ON MAPPING: The old set_default_project tool no longer exists on the wire
surface. The only way to change the default project is adn_project op=create
with set_default=True (creating an existing project is rejected as a
duplicate). The tests below exercise the same session/config sync behavior
through that path.
"""

import json

import pytest
from fastmcp import Client


def parse_text(result) -> dict:
    """Parse a JSON text response."""
    assert len(result.content) == 1
    assert result.content[0].type == "text"
    return json.loads(result.content[0].text)


async def project_op(client: Client, operation: str, **kwargs):
    """Helper: call adn_project with an operation dict."""
    op = {"operation": operation, **kwargs}
    return await client.call_tool("adn_project", {"op": op})


@pytest.mark.asyncio
async def test_project_state_sync_after_default_change(mcp_server, app, config_manager):
    """Test that MCP session stays in sync when default project is changed."""

    async with Client(mcp_server) as client:
        # Step 1: Verify initial state - MCP should show test-project as current
        initial_result = parse_text(await project_op(client, "status", name="test-project"))
        assert initial_result["success"] is True
        assert initial_result["result"]["project"]["name"] == "test-project"

        # Step 2: Create a second project AND set it as the default in one step.
        # (The old two-step create-then-set_default flow has no equivalent on
        # the new surface - create with set_default=True is the only path.)
        create_result = parse_text(
            await project_op(
                client,
                "create",
                name="minerva",
                path="/tmp/minerva-test-project",
                set_default=True,
            )
        )
        assert create_result["success"] is True
        assert create_result["result"]["project_created"] is True
        assert "minerva" in create_result["technical_summary"]
        assert create_result["result"]["set_as_default"] is True

        # Step 3: Verify MCP session immediately reflects the change (no restart needed)
        # This tests the fix - the session should switch to the new default
        updated_result = parse_text(await project_op(client, "status", name="minerva"))
        assert updated_result["result"]["project"]["name"] == "minerva"

        # The session current project is minerva (canonical via ls)
        list_result = parse_text(await project_op(client, "ls"))
        assert list_result["result"]["current_project"] == "minerva"

        # Step 4: Verify config manager also shows the new default
        assert config_manager.default_project == "minerva"

        # Step 5: Test that note operations work in the new project context
        # This validates that the identifier resolution works correctly
        write_result = await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Test Consistency Note",
                    "folder": "test",
                    "content": "# Test Note\n\nThis note tests project state consistency.\n\n- [test] Project state sync working",
                    "tags": "test,consistency",
                }
            },
        )
        write_parsed = parse_text(write_result)
        assert write_parsed["success"] is True
        assert write_parsed["result"]["title"] == "Test Consistency Note"

        # Step 6: Test that we can read the note we just created
        read_result = parse_text(
            await client.call_tool("adn_notes", {"op": {"operation": "read", "identifier": "Test Consistency Note"}})
        )
        content = read_result["result"]["content"]
        assert "Test Consistency Note" in content
        assert "project state sync working" in content.lower()

        # Step 7: Test that edit operations work (this was failing in the original issue)
        edit_result = parse_text(
            await client.call_tool(
                "adn_notes",
                {
                    "op": {
                        "operation": "edit",
                        "identifier": "Test Consistency Note",
                        "mode": "append",
                        "content": "\n\n## Update\n\nEdit operation successful after project switch!",
                    }
                },
            )
        )
        assert edit_result["success"] is True
        assert "Edited note (append)" in edit_result["summary"]

        # Step 8: Verify the edit was applied
        final_read_result = parse_text(
            await client.call_tool("adn_notes", {"op": {"operation": "read", "identifier": "Test Consistency Note"}})
        )
        assert "Edit operation successful" in final_read_result["result"]["content"]

        # Clean up - switch back to test-project.
        # NOTE: minerva remains the config default (the API blocks deleting the
        # default project); the fixture is function-scoped so this is harmless.
        await project_op(client, "switch", name="test-project")


@pytest.mark.asyncio
async def test_multiple_project_switches_maintain_consistency(mcp_server, app, config_manager):
    """Test that multiple project switches maintain consistent state."""

    async with Client(mcp_server) as client:
        # Create multiple test projects, each time making the newest the default
        # (the old set_default_project call is expressed as set_default=True here)
        for project_name in ["project-a", "project-b", "project-c"]:
            create_result = parse_text(
                await project_op(
                    client,
                    "create",
                    name=project_name,
                    path=f"/tmp/{project_name}",
                    set_default=True,
                )
            )
            assert create_result["success"] is True
            assert create_result["result"]["set_as_default"] is True

            # Verify MCP session immediately reflects the change
            current_result = parse_text(await project_op(client, "status", name=project_name))
            assert current_result["result"]["project"]["name"] == project_name

            # Verify config is also updated
            assert config_manager.default_project == project_name

            # Test that operations work in this project
            note_title = f"Note in {project_name}"
            write_result = parse_text(
                await client.call_tool(
                    "adn_notes",
                    {
                        "op": {
                            "operation": "write",
                            "title": note_title,
                            "folder": "test",
                            "content": f"# {note_title}\n\nTesting operations in {project_name}.",
                            "tags": "test",
                        }
                    },
                )
            )
            assert write_result["success"] is True
            assert write_result["result"]["title"] == note_title

        # Switch to test-project - the active default is project-c, but a switch
        # must still work and the session must follow
        switch_result = parse_text(await project_op(client, "switch", name="test-project"))
        assert switch_result["success"] is True
        assert switch_result["result"]["project_name"] == "test-project"

        # Clean up - delete the created projects (project-c is the config default,
        # which the API refuses to delete; it is left in place, and the fixture is
        # function-scoped so this is harmless).
        for project_name in ["project-a", "project-b"]:
            delete_result = parse_text(await project_op(client, "rm", name=project_name))
            assert delete_result["success"] is True


@pytest.mark.asyncio
async def test_session_handles_nonexistent_project_gracefully(mcp_server, app):
    """Test that session handles attempts to switch to nonexistent projects gracefully."""

    async with Client(mcp_server) as client:
        # Try to switch to a project that doesn't exist
        switch_result = parse_text(await project_op(client, "switch", name="nonexistent-project"))

        # Should show an error message
        assert switch_result["success"] is False
        assert "not exist" in switch_result["message"].lower()
        assert "test-project" in switch_result.get("available_projects", [])  # Should list available projects

        # Verify the session stays on the original project
        current_result = parse_text(await project_op(client, "status", name="test-project"))
        assert current_result["result"]["project"]["name"] == "test-project"
