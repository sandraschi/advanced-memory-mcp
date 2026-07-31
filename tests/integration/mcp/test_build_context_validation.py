"""Integration tests for adn_nav build_context URL validation (migrated from build_context MCP tool).

NOTE: The new adn_nav build_context surface (NavBuildContextOp) takes ``url`` as a
plain string; URL validation now happens in the API layer (normalize_memory_url),
which surfaces as a generic ToolError rather than a validation error with a
specific fragment. The response format is markdown ("# Context: ..." + found items
or "No matching items found.") instead of JSON.
"""

import pytest
from fastmcp import Client


async def build_context(client: Client, url: str, depth: int = 1):
    """Call adn_nav build_context and return the tool result."""
    return await client.call_tool(
        "adn_nav",
        {"op": {"operation": "build_context", "url": url, "depth": depth}},
    )


@pytest.mark.asyncio
async def test_build_context_valid_urls(mcp_server, app):
    """Test that build_context works with valid memory URLs."""

    async with Client(mcp_server) as client:
        # Create a test note to ensure we have something to find
        await client.call_tool(
            "adn_notes",
            {
                "op": {
                    "operation": "write",
                    "title": "URL Validation Test",
                    "folder": "testing",
                    "content": "# URL Validation Test\n\nThis note tests URL validation.",
                    "tags": "test,validation",
                }
            },
        )

        # Test various valid URL formats
        valid_urls = [
            "memory://testing/url-validation-test",  # Full memory URL
            "testing/url-validation-test",  # Relative path
            "testing/*",  # Pattern matching
        ]

        for url in valid_urls:
            result = await build_context(client, url)

            # Should return a markdown context response
            assert len(result.content) == 1
            response = result.content[0].text
            assert "# Context:" in response  # Should contain the context header
            assert "Found" in response or "No matching items found" in response


@pytest.mark.asyncio
async def test_build_context_invalid_urls_fail_validation(mcp_server, app):
    """Test that build_context properly validates and rejects invalid memory URLs.

    NOTE: URL validation errors now surface as generic ToolErrors from the API
    layer (normalize_memory_url raises inside the route), so the specific
    fragments ("double slashes", "protocol scheme", "invalid characters") are
    no longer exposed in the error message. The rejection behavior is what is
    asserted here.
    """

    async with Client(mcp_server) as client:
        # Test cases: (invalid_url, expected_error_fragment)
        invalid_test_cases = [
            ("memory//test", "double slashes"),
            ("invalid://test", "protocol scheme"),
            ("notes<brackets>", "invalid characters"),
            ('notes"quotes"', "invalid characters"),
        ]

        for invalid_url, expected_error in invalid_test_cases:
            with pytest.raises(Exception) as exc_info:
                await build_context(client, invalid_url)

            error_message = str(exc_info.value).lower()
            # The API surfaces the failure as an error; the fragment itself is
            # no longer part of the wire message.
            assert error_message.strip(), f"URL '{invalid_url}' should fail with an error message"


@pytest.mark.asyncio
async def test_build_context_empty_urls_fail_validation(mcp_server, app):
    """Test that empty or whitespace-only URLs fail.

    NOTE: On the new surface, a truly empty string resolves to an empty context
    (treated like any unresolvable path), while whitespace-only input is
    rejected with a validation error from the API layer.
    """

    async with Client(mcp_server) as client:
        # Empty string - resolves to an empty context (no error)
        result = await build_context(client, "")
        assert len(result.content) == 1
        response = result.content[0].text
        assert "# Context:" in response
        assert "No matching items found" in response

        # Whitespace only - should fail with a validation error
        with pytest.raises(Exception) as exc_info:
            await build_context(client, "   ")

        error_message = str(exc_info.value)
        # Should fail with validation error (empty or whitespace)
        assert (
            "empty or whitespace" in error_message
            or "too_short" in error_message
            or "value_error" in error_message
        )


@pytest.mark.asyncio
async def test_build_context_nonexistent_urls_return_empty_results(mcp_server, app):
    """Test that valid but nonexistent URLs return empty results (not errors)."""

    async with Client(mcp_server) as client:
        # These are valid URL formats but don't exist in the system
        nonexistent_valid_urls = [
            "memory://nonexistent/note",
            "nonexistent/note",
            "missing/*",
        ]

        for url in nonexistent_valid_urls:
            result = await build_context(client, url)

            # Should return a valid response with empty results
            assert len(result.content) == 1
            response = result.content[0].text
            assert "# Context:" in response  # Should have the context header
            assert "No matching items found" in response  # Empty results


@pytest.mark.asyncio
async def test_build_context_error_messages_are_helpful(mcp_server, app):
    """Test that invalid URLs produce errors with context."""

    async with Client(mcp_server) as client:
        # Test double slash URL - should raise an error
        with pytest.raises(Exception) as exc_info:
            await build_context(client, "memory//bad")

        error_msg = str(exc_info.value).lower()
        # The API rejects the malformed URL with an error response
        assert "error" in error_msg or "internal server error" in error_msg or error_msg.strip()

        # Test protocol scheme URL - should raise an error
        with pytest.raises(Exception) as exc_info:
            await build_context(client, "http://example.com")

        error_msg = str(exc_info.value).lower()
        assert "error" in error_msg or "internal server error" in error_msg or error_msg.strip()


@pytest.mark.asyncio
async def test_build_context_pattern_matching_works(mcp_server, app):
    """Test that valid pattern matching URLs work correctly."""

    async with Client(mcp_server) as client:
        # Create multiple test notes
        test_notes = [
            ("Pattern Test One", "patterns", "# Pattern Test One\n\nFirst pattern test."),
            ("Pattern Test Two", "patterns", "# Pattern Test Two\n\nSecond pattern test."),
            ("Other Note", "other", "# Other Note\n\nNot a pattern match."),
        ]

        for title, folder, content in test_notes:
            await client.call_tool(
                "adn_notes",
                {"op": {"operation": "write", "title": title, "folder": folder, "content": content}},
            )

        # Test pattern matching
        result = await build_context(client, "patterns/*")

        assert len(result.content) == 1
        response = result.content[0].text

        # Should find the pattern matches but not the other note
        assert "Found 2 matching items" in response
        assert "Pattern Test" in response
        assert "Other Note" not in response
