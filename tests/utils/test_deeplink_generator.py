"""Tests for deeplink generator."""

import json
import urllib.parse

import pytest

from advanced_memory.utils.deeplink_generator import (
    decode_cursor_config,
    generate_claude_config,
    generate_cursor_deeplink,
    generate_vscode_deeplink,
    validate_deeplink,
)


class TestCursorDeeplink:
    """Tests for Cursor deeplink generation."""

    def test_stdio_transport(self):
        """Test generating Cursor deeplink with stdio transport."""
        link = generate_cursor_deeplink(transport="stdio")

        assert link.startswith("cursor://anysphere.cursor-deeplink/mcp/install?")
        assert "name=advanced-memory" in link
        assert "config=" in link

        # Decode and verify config
        config = decode_cursor_config(link)
        assert config["command"] == "npx"
        assert "@smithery/cli" in config["args"]
        assert "advanced-memory-mcp" in config["args"]

    def test_http_transport(self):
        """Test generating Cursor deeplink with HTTP transport."""
        link = generate_cursor_deeplink(transport="streamable-http", host="localhost", port=8000)

        assert link.startswith("cursor://anysphere.cursor-deeplink/mcp/install?")

        # Decode and verify config
        config = decode_cursor_config(link)
        assert "url" in config
        assert "localhost" in config["url"]
        assert "8000" in config["url"]
        assert "agent=cursor" in config["url"]

    def test_custom_name(self):
        """Test generating deeplink with custom name."""
        link = generate_cursor_deeplink(name="my-server")

        assert "name=my-server" in link

    def test_https_port(self):
        """Test HTTPS protocol is used for port 443."""
        link = generate_cursor_deeplink(transport="streamable-http", port=443)

        config = decode_cursor_config(link)
        assert config["url"].startswith("https://")


class TestVSCodeDeeplink:
    """Tests for VS Code deeplink generation."""

    def test_stdio_transport(self):
        """Test generating VS Code deeplink with stdio transport."""
        link = generate_vscode_deeplink(transport="stdio")

        assert link.startswith("vscode:mcp/install?")

        # Decode and verify config
        query = link[len("vscode:mcp/install?") :]
        config_json = urllib.parse.unquote(query)
        config = json.loads(config_json)

        assert config["name"] == "advanced-memory"
        assert config["type"] == "stdio"
        assert config["command"] == "npx"
        assert "@smithery/cli" in config["args"]

    def test_http_transport(self):
        """Test generating VS Code deeplink with HTTP transport."""
        link = generate_vscode_deeplink(transport="streamable-http", host="192.168.1.10", port=9000)

        # Decode and verify config
        query = link[len("vscode:mcp/install?") :]
        config_json = urllib.parse.unquote(query)
        config = json.loads(config_json)

        assert config["name"] == "advanced-memory"
        assert config["type"] == "http"
        assert "192.168.1.10" in config["url"]
        assert "9000" in config["url"]


class TestClaudeConfig:
    """Tests for Claude Desktop config generation."""

    def test_stdio_transport(self):
        """Test generating Claude Desktop config with stdio transport."""
        config = generate_claude_config(transport="stdio")

        assert "advanced-memory" in config
        assert "command" in config["advanced-memory"]
        assert "args" in config["advanced-memory"]
        assert config["advanced-memory"]["command"] == "npx"

    def test_http_transport(self):
        """Test generating Claude Desktop config with HTTP transport."""
        config = generate_claude_config(transport="streamable-http", host="example.com", port=8080)

        assert "advanced-memory" in config
        assert "url" in config["advanced-memory"]
        assert "example.com" in config["advanced-memory"]["url"]
        assert "8080" in config["advanced-memory"]["url"]

    def test_custom_name(self):
        """Test generating config with custom name."""
        config = generate_claude_config(name="my-knowledge-base")

        assert "my-knowledge-base" in config


class TestDecodeCursorConfig:
    """Tests for Cursor config decoding."""

    def test_decode_valid_link(self):
        """Test decoding a valid Cursor deeplink."""
        link = generate_cursor_deeplink()
        config = decode_cursor_config(link)

        assert isinstance(config, dict)
        assert "command" in config or "url" in config

    def test_decode_invalid_prefix(self):
        """Test decoding link with invalid prefix."""
        with pytest.raises(ValueError, match="Invalid Cursor deeplink format"):
            decode_cursor_config("invalid://link")

    def test_decode_missing_config(self):
        """Test decoding link missing config parameter."""
        with pytest.raises(ValueError, match="Missing config parameter"):
            decode_cursor_config("cursor://anysphere.cursor-deeplink/mcp/install?name=test")


class TestValidateDeeplink:
    """Tests for deeplink validation."""

    def test_validate_cursor_link(self):
        """Test validating Cursor deeplink."""
        link = generate_cursor_deeplink()
        assert validate_deeplink(link, "cursor") is True

    def test_validate_vscode_link(self):
        """Test validating VS Code deeplink."""
        link = generate_vscode_deeplink()
        assert validate_deeplink(link, "vscode") is True

    def test_validate_invalid_cursor(self):
        """Test validating invalid Cursor link."""
        assert validate_deeplink("invalid://link", "cursor") is False

    def test_validate_invalid_vscode(self):
        """Test validating invalid VS Code link."""
        assert validate_deeplink("invalid://link", "vscode") is False

    def test_validate_claude_desktop_returns_false(self):
        """Test validating Claude Desktop (no deeplink support)."""
        config = generate_claude_config()
        assert validate_deeplink(str(config), "claude-desktop") is False


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_sse_transport(self):
        """Test generating deeplink with SSE transport."""
        link = generate_cursor_deeplink(transport="sse", port=3000)

        config = decode_cursor_config(link)
        assert "url" in config
        assert "3000" in config["url"]

    def test_ipv6_host(self):
        """Test generating deeplink with IPv6 host."""
        link = generate_cursor_deeplink(transport="streamable-http", host="::1", port=8000)

        config = decode_cursor_config(link)
        assert "::1" in config["url"]

    def test_special_characters_in_name(self):
        """Test handling special characters in server name."""
        link = generate_cursor_deeplink(name="my-server_v2.0")
        assert "my-server_v2.0" in link
