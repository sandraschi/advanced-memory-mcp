"""Generate MCP deeplinks for various AI clients.

This module provides utilities to generate one-click installation deeplinks
for different AI clients (Cursor, VS Code, Claude Desktop) supporting the
Model Context Protocol (MCP).
"""

import base64
import json
import urllib.parse
from typing import Literal

TransportType = Literal["stdio", "streamable-http", "sse"]
ClientType = Literal["cursor", "vscode", "claude-desktop"]


def generate_cursor_deeplink(
    name: str = "advanced-memory",
    transport: TransportType = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> str:
    """Generate Cursor deeplink for Advanced Memory MCP.

    Args:
        name: Server name to display in Cursor
        transport: Transport type (stdio, streamable-http, sse)
        host: Host for HTTP transports (ignored for stdio)
        port: Port for HTTP transports (ignored for stdio)

    Returns:
        Cursor deeplink URL for one-click installation

    Examples:
        # Local stdio (default)
        >>> generate_cursor_deeplink()
        'cursor://anysphere.cursor-deeplink/mcp/install?name=advanced-memory&config=...'

        # Network HTTP
        >>> generate_cursor_deeplink(transport="streamable-http", port=8000)
        'cursor://anysphere.cursor-deeplink/mcp/install?name=advanced-memory&config=...'
    """
    if transport == "stdio":
        config = {"command": "npx", "args": ["@smithery/cli", "run", "advanced-memory-mcp"]}
    else:
        # For HTTP transports, use URL
        protocol = "https" if port == 443 else "http"
        url = f"{protocol}://{host}:{port}/mcp"
        if transport == "streamable-http":
            url += "?agent=cursor"
        config = {"url": url}

    # Encode config as base64
    config_json = json.dumps(config)
    config_b64 = base64.b64encode(config_json.encode()).decode()

    return f"cursor://anysphere.cursor-deeplink/mcp/install?name={name}&config={config_b64}"


def generate_vscode_deeplink(
    name: str = "advanced-memory",
    transport: TransportType = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> str:
    """Generate VS Code deeplink for Advanced Memory MCP.

    Args:
        name: Server name to display in VS Code
        transport: Transport type (stdio, streamable-http, sse)
        host: Host for HTTP transports (ignored for stdio)
        port: Port for HTTP transports (ignored for stdio)

    Returns:
        VS Code deeplink URL for one-click installation

    Examples:
        # Local stdio
        >>> generate_vscode_deeplink()
        'vscode:mcp/install?%7B%22name%22%3A%22advanced-memory%22...'

        # Network HTTP
        >>> generate_vscode_deeplink(transport="streamable-http")
        'vscode:mcp/install?%7B%22name%22%3A%22advanced-memory%22...'
    """
    if transport == "stdio":
        config = {
            "name": name,
            "type": "stdio",
            "command": "npx",
            "args": ["@smithery/cli", "run", "advanced-memory-mcp"],
        }
    else:
        # For HTTP transports
        protocol = "https" if port == 443 else "http"
        url = f"{protocol}://{host}:{port}/mcp"
        config = {"name": name, "type": "http", "url": url}

    config_json = json.dumps(config)
    config_encoded = urllib.parse.quote(config_json)

    return f"vscode:mcp/install?{config_encoded}"


def generate_claude_config(
    name: str = "advanced-memory",
    transport: TransportType = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> dict:
    """Generate Claude Desktop JSON config (no deeplink support).

    Claude Desktop doesn't support deeplinks, so this returns a JSON
    configuration object that users can manually add to their config file.

    Args:
        name: Server name to display in Claude Desktop
        transport: Transport type (stdio, streamable-http, sse)
        host: Host for HTTP transports (ignored for stdio)
        port: Port for HTTP transports (ignored for stdio)

    Returns:
        Dictionary containing Claude Desktop MCP server configuration

    Examples:
        # Local stdio
        >>> generate_claude_config()
        {'advanced-memory': {'command': 'npx', 'args': [...]}}

        # Network HTTP
        >>> generate_claude_config(transport="streamable-http")
        {'advanced-memory': {'url': 'http://127.0.0.1:8000/mcp'}}
    """
    if transport == "stdio":
        return {name: {"command": "npx", "args": ["@smithery/cli", "run", "advanced-memory-mcp"]}}
    else:
        # For HTTP transports
        protocol = "https" if port == 443 else "http"
        url = f"{protocol}://{host}:{port}/mcp"
        return {name: {"url": url}}


def decode_cursor_config(deeplink: str) -> dict:
    """Decode configuration from Cursor deeplink for validation.

    Args:
        deeplink: Cursor deeplink URL

    Returns:
        Decoded configuration dictionary

    Raises:
        ValueError: If deeplink format is invalid
    """
    if not deeplink.startswith("cursor://anysphere.cursor-deeplink/mcp/install?"):
        raise ValueError("Invalid Cursor deeplink format")

    # Extract query parameters
    query_start = deeplink.index("?") + 1
    query = deeplink[query_start:]
    params = urllib.parse.parse_qs(query)

    if "config" not in params:
        raise ValueError("Missing config parameter in deeplink")

    # Decode base64
    config_b64 = params["config"][0]
    config_json = base64.b64decode(config_b64).decode()
    return json.loads(config_json)


def validate_deeplink(deeplink: str, client: ClientType) -> bool:
    """Validate deeplink format for specified client.

    Args:
        deeplink: Deeplink URL to validate
        client: Client type (cursor, vscode, claude-desktop)

    Returns:
        True if deeplink is valid, False otherwise
    """
    try:
        if client == "cursor":
            if not deeplink.startswith("cursor://anysphere.cursor-deeplink/mcp/install?"):
                return False
            # Try to decode config
            decode_cursor_config(deeplink)
            return True

        elif client == "vscode":
            if not deeplink.startswith("vscode:mcp/install?"):
                return False
            # Try to decode config
            query = deeplink[len("vscode:mcp/install?") :]
            config_json = urllib.parse.unquote(query)
            json.loads(config_json)
            return True

        elif client == "claude-desktop":
            # Claude Desktop uses JSON config, not deeplinks
            return False

        return False

    except Exception:
        return False
