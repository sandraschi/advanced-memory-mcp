"""
Integration tests for adn_project (migrated from project_management MCP tools).

Tests the complete project management workflow: MCP client -> MCP server -> FastAPI -> project service

NOTE ON MAPPING (old tool -> new op):
- list_memory_projects()            -> adn_project op=ls
- get_current_project()             -> adn_project op=status (name of the active project)
- switch_project(name)              -> adn_project op=switch (name)
- set_default_project(name)         -> adn_project op=create with set_default=True (the only way to
                                       set a default project on the new surface; create on an
                                       existing project is rejected as a duplicate)
- create_memory_project(name, path) -> adn_project op=create (name, path, set_default)
- delete_project(name)              -> adn_project op=rm (name)

All responses are JSON dicts: {"success": bool, "operation": str, "summary": str, "result": {...}}.
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


async def list_projects(client: Client) -> dict:
    return parse_text(await project_op(client, "ls"))


async def current_project(client: Client, name: str = "test-project") -> dict:
    """adn_project status requires an explicit name; defaults to the active test project."""
    return parse_text(await project_op(client, "status", name=name))


async def write_note(client: Client, title: str, folder: str, content: str, tags: str | None = None):
    """Helper: write a note through the adn_notes portmanteau."""
    op = {"operation": "write", "title": title, "folder": folder, "content": content}
    if tags is not None:
        op["tags"] = tags
    await client.call_tool("adn_notes", {"op": op})


@pytest.mark.asyncio
async def test_list_projects_basic_operation(mcp_server, app):
    """Test basic ls operation showing available projects."""

    async with Client(mcp_server) as client:
        # List all available projects
        parsed = await list_projects(client)

        # Should show available projects with status indicators
        assert parsed["success"] is True
        assert parsed["operation"] == "list"
        assert "available projects" in parsed["technical_summary"]

        project_names = [p["name"] for p in parsed["result"]["projects"]]
        assert "test-project" in project_names  # Our default test project

        # test-project should be marked as current and default
        test_project = next(p for p in parsed["result"]["projects"] if p["name"] == "test-project")
        assert "current" in test_project["indicators"]
        assert "default" in test_project["indicators"]


@pytest.mark.asyncio
async def test_get_current_project_operation(mcp_server, app):
    """Test current project status showing project info."""

    async with Client(mcp_server) as client:
        # Create some test content first to have stats
        await write_note(
            client,
            "Test Note",
            "test",
            "# Test Note\n\nTest content.\n\n- [feature] Test observation",
            "test",
        )

        # Get current project info
        parsed = await current_project(client)

        assert parsed["success"] is True
        assert parsed["result"]["project"]["name"] == "test-project"
        # Should show current project stats
        assert "total_entities" in parsed["result"]["statistics"]
        assert "total_observations" in parsed["result"]["statistics"]
        assert "total_relations" in parsed["result"]["statistics"]


@pytest.mark.asyncio
async def test_project_info_with_entities(mcp_server, app):
    """Test that project info shows correct entity counts."""

    async with Client(mcp_server) as client:
        # Create multiple entities with observations and relations
        await write_note(
            client,
            "Entity One",
            "stats",
            """# Entity One

This is the first entity.

## Observations
- [type] First entity type
- [status] Active entity

## Relations
- relates_to [[Entity Two]]
- implements [[Some System]]""",
            "entity,test",
        )

        await write_note(
            client,
            "Entity Two",
            "stats",
            """# Entity Two

This is the second entity.

## Observations
- [type] Second entity type
- [priority] High priority

## Relations
- depends_on [[Entity One]]""",
            "entity,test",
        )

        # Get current project info to see updated stats
        parsed = await current_project(client)

        assert parsed["success"] is True
        stats = parsed["result"]["statistics"]

        # Should show at least the entities we created
        assert stats["total_entities"] >= 2
        # Should show observations from our entities (4 + possibly more from setup)
        assert stats["total_observations"] >= 4


@pytest.mark.asyncio
async def test_switch_project_not_found(mcp_server, app):
    """Test switch_project with non-existent project shows error."""

    async with Client(mcp_server) as client:
        # Try to switch to non-existent project
        parsed = parse_text(await project_op(client, "switch", name="non-existent-project"))

        # Should show error message with available projects
        assert parsed["success"] is False
        assert "does not exist" in parsed["message"]
        assert "test-project" in parsed.get("available_projects", [])


@pytest.mark.asyncio
async def test_switch_project_to_test_project(mcp_server, app):
    """Test switching to the currently active project."""

    async with Client(mcp_server) as client:
        # Switch to the same project (test-project)
        parsed = parse_text(await project_op(client, "switch", name="test-project"))

        # Should show successful switch
        assert parsed["success"] is True
        assert "Successfully switched to project 'test-project'" in parsed["technical_summary"]
        assert parsed["result"]["project_name"] == "test-project"
        # Project summary/statistics may be present
        assert "statistics" in parsed["result"]


@pytest.mark.asyncio
async def test_set_default_project_operation(mcp_server, app):
    """Test setting a default project.

    NOTE: The new surface has no standalone set_default op. The only way to
    set a project as default is create with set_default=True. Setting the
    existing test-project as default again is therefore rejected as a
    duplicate; this test verifies the create-with-set_default flow and that
    the session switches to the new default.
    """

    async with Client(mcp_server) as client:
        # Set a fresh project as default via create + set_default
        create_result = await project_op(
            client,
            "create",
            name="default-target-project",
            path="/tmp/default-target-project",
            set_default=True,
        )
        parsed = parse_text(create_result)

        # Should show success and default flag
        assert parsed["success"] is True
        assert parsed["result"]["project_created"] is True
        assert parsed["result"]["set_as_default"] is True

        # Verify the session switched to the new default project
        current = await current_project(client, name="default-target-project")
        assert current["result"]["project"]["name"] == "default-target-project"

        # NOTE: the API refuses to delete the *default* project, so no rm cleanup
        # is possible here; the fixture is function-scoped, so this is harmless.
        await project_op(client, "switch", name="test-project")


@pytest.mark.asyncio
async def test_set_default_project_not_found(mcp_server, app):
    """Test default-setting operation behavior for a non-existent project.

    NOTE: The old set_default_project error path (non-existent project) is gone
    from the new surface: create with set_default=True simply creates the
    project and sets it as default. This test verifies that behavior.
    """

    async with Client(mcp_server) as client:
        # Create a new project and set it as default
        create_result = await project_op(
            client,
            "create",
            name="non-existent-project",
            path="/tmp/non-existent-project",
            set_default=True,
        )
        parsed = parse_text(create_result)

        # The project is created (not an error) and set as default
        assert parsed["success"] is True
        assert parsed["result"]["project_created"] is True
        assert parsed["result"]["set_as_default"] is True

        # NOTE: the API refuses to delete the *default* project, so no rm cleanup
        # is possible here; the fixture is function-scoped, so this is harmless.
        await project_op(client, "switch", name="test-project")


@pytest.mark.asyncio
async def test_project_management_workflow(mcp_server, app):
    """Test complete project management workflow."""

    async with Client(mcp_server) as client:
        # 1. Check current project
        parsed = await current_project(client)
        assert parsed["result"]["project"]["name"] == "test-project"

        # 2. List all projects
        parsed = await list_projects(client)
        assert "available projects" in parsed["technical_summary"]
        assert "test-project" in [p["name"] for p in parsed["result"]["projects"]]

        # 3. Switch to same project (should work)
        parsed = parse_text(await project_op(client, "switch", name="test-project"))
        assert parsed["success"] is True
        assert parsed["result"]["project_name"] == "test-project"

        # 4. Verify we're still on the same project
        parsed = await current_project(client)
        assert parsed["result"]["project"]["name"] == "test-project"


@pytest.mark.asyncio
async def test_project_metadata_consistency(mcp_server, app):
    """Test that all project management tools include consistent project metadata."""

    async with Client(mcp_server) as client:
        # ls
        parsed = await list_projects(client)
        assert "test-project" in [p["name"] for p in parsed["result"]["projects"]]

        # status (current project)
        parsed = await current_project(client)
        assert parsed["result"]["project"]["name"] == "test-project"

        # switch
        parsed = parse_text(await project_op(client, "switch", name="test-project"))
        assert parsed["success"] is True
        assert parsed["result"]["project_name"] == "test-project"


@pytest.mark.asyncio
async def test_project_statistics_accuracy(mcp_server, app):
    """Test that project statistics reflect actual content."""

    async with Client(mcp_server) as client:
        # Get initial stats
        initial = await current_project(client)
        assert initial["success"] is True

        # Create a new entity
        await write_note(
            client,
            "Stats Test Note",
            "stats-test",
            """# Stats Test Note

Testing statistics accuracy.

## Observations
- [test] This is a test observation
- [accuracy] Testing stats accuracy

## Relations
- validates [[Project Statistics]]""",
            "stats,test",
        )

        # Get updated stats
        updated = await current_project(client)
        assert updated["success"] is True
        stats = updated["result"]["statistics"]

        # Stats should be reasonable (at least 1 entity, some observations)
        assert stats["total_entities"] >= 1, f"Should have at least 1 entity, got {stats['total_entities']}"
        assert stats["total_observations"] >= 2, (
            f"Should have at least 2 observations, got {stats['total_observations']}"
        )


@pytest.mark.asyncio
async def test_create_project_basic_operation(mcp_server, app):
    """Test creating a new project with basic parameters."""

    async with Client(mcp_server) as client:
        # Create a new project
        parsed = parse_text(await project_op(client, "create", name="test-new-project", path="/tmp/test-new-project"))

        # Should show success message and project details
        assert parsed["success"] is True
        assert parsed["result"]["project_created"] is True
        assert parsed["result"]["project_details"]["name"] == "test-new-project"
        assert parsed["result"]["project_details"]["path"] == "/tmp/test-new-project"
        assert parsed["result"]["set_as_default"] is False

        # The session should still be on the default project
        current = await current_project(client)
        assert current["result"]["project"]["name"] == "test-project"

        # Verify project appears in project list
        parsed_list = await list_projects(client)
        assert "test-new-project" in [p["name"] for p in parsed_list["result"]["projects"]]


@pytest.mark.asyncio
async def test_create_project_with_default_flag(mcp_server, app):
    """Test creating a project and setting it as default."""

    async with Client(mcp_server) as client:
        # Create a new project and set as default
        parsed = parse_text(
            await project_op(
                client, "create", name="test-default-project", path="/tmp/test-default-project", set_default=True
            )
        )

        # Should show success and default flag
        assert parsed["success"] is True
        assert parsed["result"]["project_created"] is True
        assert parsed["result"]["set_as_default"] is True

        # Verify we switched to the new project
        current = await current_project(client, name="test-default-project")
        assert current["result"]["project"]["name"] == "test-default-project"


@pytest.mark.asyncio
async def test_create_project_duplicate_name(mcp_server, app):
    """Test creating a project with duplicate name shows error."""

    async with Client(mcp_server) as client:
        # First create a project
        parsed = parse_text(await project_op(client, "create", name="duplicate-test", path="/tmp/duplicate-test-1"))
        assert parsed["success"] is True

        # Try to create another project with same name - should raise a ToolError
        with pytest.raises(Exception) as exc_info:
            await project_op(client, "create", name="duplicate-test", path="/tmp/duplicate-test-2")

        # Should show error about duplicate name
        error_message = str(exc_info.value)
        assert "duplicate-test" in error_message or "already exists" in error_message


@pytest.mark.asyncio
async def test_delete_project_basic_operation(mcp_server, app):
    """Test deleting a project that exists."""

    async with Client(mcp_server) as client:
        # First create a project to delete
        parsed = parse_text(await project_op(client, "create", name="to-be-deleted", path="/tmp/to-be-deleted"))
        assert parsed["success"] is True

        # Verify it exists
        parsed_list = await list_projects(client)
        assert "to-be-deleted" in [p["name"] for p in parsed_list["result"]["projects"]]

        # Delete the project
        parsed = parse_text(await project_op(client, "rm", name="to-be-deleted"))

        # Should show success message
        assert parsed["success"] is True
        assert "removed successfully" in parsed["technical_summary"]
        assert parsed["result"]["project_deleted"] is True
        assert parsed["result"]["deleted_project"]["name"] == "to-be-deleted"
        # Files remain on disk but project is no longer tracked
        assert parsed["result"]["files_preserved"] is True

        # Verify project no longer appears in list
        parsed_list = await list_projects(client)
        assert "to-be-deleted" not in [p["name"] for p in parsed_list["result"]["projects"]]


@pytest.mark.asyncio
async def test_delete_project_not_found(mcp_server, app):
    """Test deleting a non-existent project shows error.

    NOTE: The old surface raised an exception; the new surface returns a
    structured error dict.
    """

    async with Client(mcp_server) as client:
        # Try to delete non-existent project
        parsed = parse_text(await project_op(client, "rm", name="non-existent-project"))

        # Should show error about non-existent project
        assert parsed["success"] is False
        assert "does not exist" in parsed["message"]


@pytest.mark.asyncio
async def test_delete_current_project_protection(mcp_server, app):
    """Test that deleting the current project is prevented.

    NOTE: The old surface raised an exception; the new surface returns a
    structured error dict.
    """

    async with Client(mcp_server) as client:
        # Try to delete the current project (test-project)
        parsed = parse_text(await project_op(client, "rm", name="test-project"))

        # Should show error about deleting current project
        assert parsed["success"] is False
        assert "currently active" in parsed["message"]
        assert "test-project" in parsed["message"]


@pytest.mark.asyncio
async def test_project_lifecycle_workflow(mcp_server, app):
    """Test complete project lifecycle: create, switch, use, delete."""

    async with Client(mcp_server) as client:
        project_name = "lifecycle-test"
        project_path = "/tmp/lifecycle-test"

        # 1. Create new project
        parsed = parse_text(await project_op(client, "create", name=project_name, path=project_path))
        assert parsed["success"] is True
        assert project_name in parsed["technical_summary"]

        # 2. Switch to the new project
        parsed = parse_text(await project_op(client, "switch", name=project_name))
        assert parsed["success"] is True
        assert parsed["result"]["project_name"] == project_name

        # 3. Create content in the new project
        await write_note(
            client,
            "Lifecycle Test Note",
            "test",
            "# Lifecycle Test\n\nThis note tests the project lifecycle.\n\n- [test] Lifecycle testing",
            "lifecycle,test",
        )

        # 4. Verify project stats show our content
        parsed = await current_project(client, name=project_name)
        assert parsed["result"]["project"]["name"] == project_name
        assert parsed["result"]["statistics"]["total_entities"] >= 1

        # 5. Switch back to original project
        parsed = parse_text(await project_op(client, "switch", name="test-project"))
        assert parsed["success"] is True

        # 6. Delete the lifecycle test project
        parsed = parse_text(await project_op(client, "rm", name=project_name))
        assert parsed["success"] is True
        assert "removed successfully" in parsed["technical_summary"]
        assert parsed["result"]["deleted_project"]["name"] == project_name

        # 7. Verify project is gone from list
        parsed_list = await list_projects(client)
        assert project_name not in [p["name"] for p in parsed_list["result"]["projects"]]


@pytest.mark.asyncio
async def test_create_delete_project_edge_cases(mcp_server, app):
    """Test edge cases for create and delete project operations."""

    async with Client(mcp_server) as client:
        # Test with special characters in project name (should be handled gracefully)
        special_name = "test-project-with-dashes"

        # Create project with special characters
        parsed = parse_text(await project_op(client, "create", name=special_name, path=f"/tmp/{special_name}"))
        assert parsed["success"] is True
        assert parsed["result"]["project_details"]["name"] == special_name

        # Verify it appears in list
        parsed_list = await list_projects(client)
        assert special_name in [p["name"] for p in parsed_list["result"]["projects"]]

        # Delete it
        parsed = parse_text(await project_op(client, "rm", name=special_name))
        assert parsed["success"] is True
        assert parsed["result"]["deleted_project"]["name"] == special_name

        # Verify it's gone
        parsed_list = await list_projects(client)
        assert special_name not in [p["name"] for p in parsed_list["result"]["projects"]]


@pytest.mark.asyncio
async def test_case_insensitive_project_switching(mcp_server, app):
    """Test case-insensitive project switching with proper database lookup."""

    async with Client(mcp_server) as client:
        # Create a project with mixed case name
        project_name = "Personal-Project"
        parsed = parse_text(await project_op(client, "create", name=project_name, path=f"/tmp/{project_name}"))
        assert parsed["success"] is True
        assert parsed["result"]["project_details"]["name"] == project_name

        # Verify project was created with canonical name
        parsed_list = await list_projects(client)
        assert project_name in [p["name"] for p in parsed_list["result"]["projects"]]

        # Test switching with different case variations
        test_cases = [
            "personal-project",  # all lowercase
            "PERSONAL-PROJECT",  # all uppercase
            "Personal-project",  # mixed case 1
            "personal-Project",  # mixed case 2
        ]

        for test_input in test_cases:
            # Switch using case-insensitive input
            parsed = parse_text(await project_op(client, "switch", name=test_input))

            # Should succeed and show canonical name in response
            assert parsed["success"] is True
            assert parsed["result"]["project_name"] == project_name  # Canonical name should appear
            # Project summary may be unavailable in test environment
            assert "statistics" in parsed["result"]

            # Verify the session is on the canonical project (via ls current_project;
            # NOTE: adn_project status echoes the URL permalink, not the canonical name)
            parsed_list = await list_projects(client)
            assert parsed_list["result"]["current_project"] == project_name

            # Verify current project stats are available
            current = await current_project(client, name=project_name)
            assert "statistics" in current["result"]

        # Clean up - switch back to test project and delete the test project
        await project_op(client, "switch", name="test-project")
        await project_op(client, "rm", name=project_name)


@pytest.mark.asyncio
async def test_case_insensitive_project_operations(mcp_server, app):
    """Test that all project operations work correctly after case-insensitive switching."""

    async with Client(mcp_server) as client:
        # Create a project with capital letters
        project_name = "CamelCase-Project"
        parsed = parse_text(await project_op(client, "create", name=project_name, path=f"/tmp/{project_name}"))
        assert parsed["success"] is True

        # Switch to project using different-case input.
        # NOTE: the old test used "camel-case-project"; the new surface matches
        # by permalink/name case-insensitively (no hyphen-stripping), so the
        # uppercase variant is used here.
        parsed = parse_text(await project_op(client, "switch", name="CAMELCASE-PROJECT"))
        assert parsed["success"] is True
        assert parsed["result"]["project_name"] == project_name  # Should show canonical name

        # Test that MCP operations work correctly after case-insensitive switch

        # 1. Create a note in the switched project
        write_result = await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "Case Test Note",
                    "folder": "case-test",
                    "content": "# Case Test Note\n\nTesting case-insensitive operations.\n\n- [test] Case insensitive switch\n- relates_to [[Another Note]]",
                    "tags": "case,test",
                }
            },
        )
        write_parsed = parse_text(write_result)
        assert write_parsed["success"] is True
        assert write_parsed["result"]["title"] == "Case Test Note"

        # 2. Verify current project stats correctly
        # NOTE: adn_project status echoes the URL permalink as project.name, so
        # the canonical name is verified via ls current_project instead.
        current = await current_project(client, name=project_name)
        assert current["result"]["project"]["name"] == "camel-case-project"  # permalink form
        assert current["result"]["statistics"]["total_entities"] >= 1
        parsed_list = await list_projects(client)
        assert parsed_list["result"]["current_project"] == project_name  # canonical name

        # 3. Test search works in the switched project
        search_result = await client.call_tool(
            "adn_search",
            {"op": {"operation": "query", "text": "case insensitive"}},
        )
        assert len(search_result.content) == 1
        assert "Case Test Note" in search_result.content[0].text

        # 4. Test read works
        read_result = await client.call_tool(
            "adn_notes",
            {"op": {"operation": "read", "identifier": "Case Test Note"}},
        )
        assert len(read_result.content) == 1
        read_parsed = parse_text(read_result)
        content = read_parsed["result"]["content"]
        assert "Case Test Note" in content
        assert "case insensitive" in content.lower()

        # Clean up
        await project_op(client, "switch", name="test-project")
        await project_op(client, "rm", name=project_name)


@pytest.mark.asyncio
async def test_case_insensitive_error_handling(mcp_server, app):
    """Test error handling for case-insensitive project operations."""

    async with Client(mcp_server) as client:
        # Test non-existent project with various cases
        non_existent_cases = [
            "NonExistent",
            "non-existent",
            "NON-EXISTENT",
            "Non-Existent-Project",
        ]

        for test_case in non_existent_cases:
            parsed = parse_text(await project_op(client, "switch", name=test_case))

            # Should show error for all case variations
            assert parsed["success"] is False
            assert f"Project '{test_case}' does not exist" in parsed["message"]
            assert "test-project" in parsed.get("available_projects", [])


@pytest.mark.asyncio
async def test_case_preservation_in_project_list(mcp_server, app):
    """Test that project names preserve their original case in listings."""

    async with Client(mcp_server) as client:
        # Create projects with different casing patterns
        test_projects = [
            "lowercase-project",
            "UPPERCASE-PROJECT",
            "CamelCase-Project",
            "Mixed-CASE-project",
        ]

        # Create all test projects
        for project_name in test_projects:
            parsed = parse_text(await project_op(client, "create", name=project_name, path=f"/tmp/{project_name}"))
            assert parsed["success"] is True

        # List projects and verify each appears with its original case
        parsed_list = await list_projects(client)
        project_names = [p["name"] for p in parsed_list["result"]["projects"]]

        for project_name in test_projects:
            assert project_name in project_names, f"Project {project_name} not found in list"

        # Test switching to each project with different case input
        for project_name in test_projects:
            # Switch using lowercase input
            lowercase_input = project_name.lower()
            parsed = parse_text(await project_op(client, "switch", name=lowercase_input))

            # Should succeed and show original case in response
            assert parsed["success"] is True
            assert parsed["result"]["project_name"] == project_name  # Original case preserved

            # Verify the session is on the canonical project (via ls current_project;
            # NOTE: adn_project status echoes the URL permalink, not the canonical name)
            parsed_list = await list_projects(client)
            assert parsed_list["result"]["current_project"] == project_name

        # Clean up - switch back and delete test projects
        await project_op(client, "switch", name="test-project")
        for project_name in test_projects:
            await project_op(client, "rm", name=project_name)


@pytest.mark.asyncio
async def test_session_state_consistency_after_case_switch(mcp_server, app):
    """Test that session state remains consistent after case-insensitive project switching."""

    async with Client(mcp_server) as client:
        # Create a project with specific case
        project_name = "Session-Test-Project"
        parsed = parse_text(await project_op(client, "create", name=project_name, path=f"/tmp/{project_name}"))
        assert parsed["success"] is True

        # Switch using different case
        parsed = parse_text(await project_op(client, "switch", name="session-test-project"))  # lowercase
        assert parsed["success"] is True

        # Perform multiple operations and verify consistency
        operations = [
            (
                "adn_notes",
                {
                    "operation": "write",
                    "title": "Session Consistency Test",
                    "folder": "session",
                    "content": "# Session Test\n\n- [test] Session consistency",
                    "tags": "session,test",
                },
            ),
            ("adn_project", {"operation": "status", "name": project_name}),
            ("adn_search", {"operation": "query", "text": "session"}),
            ("adn_project", {"operation": "ls"}),
        ]

        for tool_name, op in operations:
            result = await client.call_tool(tool_name, {"op": op})

            # All operations should work and reference the canonical project name
            if tool_name == "adn_project" and op["operation"] == "status":
                parsed = parse_text(result)
                # NOTE: status echoes the URL permalink form of the name
                assert parsed["result"]["project"]["name"] == "session-test-project"
                assert "statistics" in parsed["result"]
            elif tool_name == "adn_project" and op["operation"] == "ls":
                parsed = parse_text(result)
                assert project_name in [p["name"] for p in parsed["result"]["projects"]]
                assert parsed["result"]["current_project"] == project_name

        # Clean up
        await project_op(client, "switch", name="test-project")
        await project_op(client, "rm", name=project_name)
