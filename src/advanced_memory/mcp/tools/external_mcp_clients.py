"""External MCP Server Client Integration.

This module enables Advanced Memory MCP server to act as a client to other MCP servers,
providing universal tool calling capabilities through external MCP server integration.

PORTMANTEAU PATTERN RATIONALE:
Consolidates external MCP client functionality into a single interface for
consistent external server tool access across all integrated services.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response


def _validate_skeleton_key_request(
    server_path: str,
    tool_name: str,
    tool_params: dict[str, Any] | None,
    security_context: str | None
) -> dict[str, Any]:
    """Security validation for skeleton key requests."""

    # ALLOWED SERVERS - Only explicitly whitelisted paths
    # LEGACY ALLOWED_SERVER_PREFIXES - REPLACED BY GRANULAR ALLOWED_SERVER_TOOLS MATRIX

    # ALLOWED TOOLS PER SERVER - Granular security by server + tool combination
    ALLOWED_SERVER_TOOLS = {
        # Weather servers - only safe weather operations
        "D:\\Dev\\repos\\weather-mcp\\": {
            "get_weather", "get_forecast", "get_current_weather",
            "get_weather_history", "get_weather_alerts"
        },

        # Brightdata search - only search operations
        "D:\\Dev\\repos\\brightdata-mcp\\": {
            "search_engine", "search_engine_batch", "web_search",
            "scrape_as_markdown", "search_engine_batch"
        },

        # VRChat monitoring - only status checks
        "D:\\Dev\\repos\\vrchat-mcp\\": {
            "get_server_status", "get_world_info", "check_vrchat_api_direct",
            "get_vrchat_server_status", "get_user_status"
        },

        # Plex media - only read operations
        "D:\\Dev\\repos\\plex-mcp\\": {
            "search", "browse", "get_details", "get_recent",
            "get_library_stats", "get_user_activity"
        },

        # Advanced Memory ecosystem - controlled operations
        "D:\\Dev\\repos\\advanced-memory-mcp\\": {
            "adn_search", "read_note", "view_note_rendered",
            "adn_knowledge", "adn_navigation"
        },

        # MyAI dashboard - status monitoring only
        "D:\\Dev\\repos\\myai\\": {
            "get_server_status", "get_health", "get_service_status",
            "list_containers", "get_container_logs"
        },

        # Robotics - safe monitoring only
        "D:\\Dev\\repos\\robotics-mcp\\": {
            "get_status", "get_lidar", "get_camera_feed",
            "robot_control"  # Only safe control operations
        },

        # Vienna Life Assistant - personal data access (careful!)
        "D:\\Dev\\repos\\vienna-life-assistant\\": {
            "get_weather", "get_transit_schedule", "get_calendar_events",
            "search_notes", "read_note"
        },

        # FILESYSTEM SERVERS - EXPLICITLY BLOCKED (DANGEROUS!)
        # "D:\\Dev\\repos\\filesystem-mcp\\": set(),  # BLOCKED - too dangerous
        # "D:\\Dev\\repos\\file-mcp\\": set(),        # BLOCKED - too dangerous
        # "D:\\Dev\\repos\\system-mcp\\": set(),     # BLOCKED - too dangerous
    }

    # EXPLICITLY BLOCKED SERVER TYPES - These can NEVER be called via skeleton key
    BLOCKED_SERVERS = {
        "filesystem", "file-system", "filemanager", "system", "shell",
        "execution", "process", "admin", "sudo", "root", "kernel"
    }

    # LEGACY SIMPLE TOOL LIST - DEPRECATED (too permissive)
    # ALLOWED_TOOLS = {...}

    # BLOCKED PARAMETERS - Prevent dangerous parameter injection
    BLOCKED_PARAMS = [
        "exec", "eval", "system", "shell", "cmd", "command",
        "script", "code", "python", "bash", "powershell",
        "delete", "remove", "drop", "truncate",
        "admin", "root", "sudo", "privilege",
        "password", "secret", "key", "token",
    ]

    # SECURITY CONTEXTS - Must specify valid context
    VALID_CONTEXTS = [
        "research", "monitoring", "weather", "search",
        "status_check", "safe_discovery", "read_only"
    ]

    errors = []

    # 1. Validate security context
    if not security_context or security_context not in VALID_CONTEXTS:
        errors.append(f"Invalid security context. Must be one of: {', '.join(VALID_CONTEXTS)}")

    # 2. Check for explicitly blocked server types
    server_path_lower = server_path.lower()
    for blocked_type in BLOCKED_SERVERS:
        if blocked_type in server_path_lower:
            errors.append(f"SECURITY BLOCK: Server type '{blocked_type}' is explicitly blocked. Path: {server_path}")
            break

    # 2b. Validate server path against allowed list
    path_valid = any(server_path.startswith(prefix) for prefix in ALLOWED_SERVER_TOOLS.keys())
    if not path_valid:
        errors.append(f"Server path not in allowed list. Path: {server_path}")

    # 3. Validate server+tool combination using granular matrix
    tool_allowed = False
    matching_server = None

    # Find matching server prefix
    for allowed_prefix, allowed_tools in ALLOWED_SERVER_TOOLS.items():
        if server_path.startswith(allowed_prefix):
            matching_server = allowed_prefix
            if tool_name in allowed_tools:
                tool_allowed = True
            else:
                errors.append(f"Tool '{tool_name}' not allowed on server '{server_path}'. Allowed tools: {', '.join(allowed_tools)}")
            break

    if not matching_server:
        errors.append(f"Server '{server_path}' not in granular security matrix. Allowed servers: {', '.join(ALLOWED_SERVER_TOOLS.keys())}")

    # Overall validation
    if not tool_allowed:
        errors.append(f"SECURITY BLOCK: Tool '{tool_name}' not permitted on server '{server_path}'")

    # 4. Validate parameters
    if tool_params:
        for param_name, param_value in tool_params.items():
            # Check for blocked parameter names
            if any(blocked in param_name.lower() for blocked in BLOCKED_PARAMS):
                errors.append(f"Blocked parameter name: {param_name}")

            # Check for dangerous parameter values (basic string check)
            if isinstance(param_value, str):
                if any(blocked in param_value.lower() for blocked in BLOCKED_PARAMS):
                    errors.append(f"Potentially dangerous parameter value in '{param_name}': {param_value[:50]}...")

    if errors:
        return {
            "valid": False,
            "errors": errors,
            "message": f"Security validation failed: {'; '.join(errors)}"
        }

    return {"valid": True}


def _sanitize_path(path: str) -> str:
    """Sanitize file paths to prevent directory traversal."""
    import os.path

    # Resolve any .. or . components
    normalized = os.path.normpath(path)

    # Ensure it's an absolute path (for local servers only)
    if not os.path.isabs(normalized):
        raise ValueError("Only absolute paths allowed for security")

    # Check for dangerous patterns
    if ".." in normalized or path != normalized:
        raise ValueError("Path traversal detected")

    return normalized


@mcp.tool()
async def skeleton_key(
    server_path: str,
    tool_name: str,
    tool_params: dict[str, Any] | None = None,
    security_context: str | None = None
) -> dict[str, Any]:
    """Skeleton Key: Universal MCP Server Tool Caller.

    Dynamically instantiates ANY MCP server and calls any of its tools.
    This is the ultimate MCP gateway - one tool to rule them all.

    PORTMANTEAU PATTERN: Consolidates universal MCP server access into a single
    skeleton key interface that can unlock any MCP server's capabilities.

    Args:
        server_path: Path to MCP server (Python file, executable, or URL)
        tool_name: Name of tool to call on the target server
        tool_params: Dictionary of parameters to pass to the target tool
        security_context: Security context (research, monitoring, weather, search, status_check, safe_discovery, read_only)

    Returns:
        Tool execution result from the target MCP server

    Examples:
        # Call weather tool from a weather MCP server
        skeleton_key(
            server_path="path/to/weather_mcp_server.py",
            tool_name="get_weather",
            tool_params={"location": "Vienna"},
            security_context="weather"
        )

        # Call search tool from Brightdata MCP server
        skeleton_key(
            server_path="path/to/brightdata_mcp_server.py",
            tool_name="search_engine",
            tool_params={"query": "MCP ecosystem 2025"},
            security_context="research"
        )

        # Call VRChat tool from VRChat MCP server
        skeleton_key(
            server_path="path/to/vrchat_mcp_server.py",
            tool_name="get_world_info",
            tool_params={"world_id": "wrld_123"},
            security_context="monitoring"
        )

    Errors:
        - SECURITY_VALIDATION_FAILED: Request failed security validation
        - SERVER_NOT_FOUND: Cannot locate or start the target MCP server
        - TOOL_NOT_FOUND: Specified tool doesn't exist on target server
        - PARAMETER_ERROR: Invalid parameters for the target tool
        - CONNECTION_FAILED: Cannot establish connection to target server
    """
    try:
        # 🔒 SECURITY VALIDATION FIRST
        security_check = _validate_skeleton_key_request(
            server_path, tool_name, tool_params, security_context
        )

        if not security_check["valid"]:
            return build_error_response(
                "SECURITY_VALIDATION_FAILED",
                security_check["message"],
                suggestions=[
                    "Use a valid security_context from: research, monitoring, weather, search, status_check, safe_discovery, read_only",
                    "Ensure server_path is in the allowed server list",
                    "Use only tools from the allowed tools list",
                    "Avoid blocked parameters and dangerous values"
                ]
            )

        # Sanitize the server path
        try:
            sanitized_path = _sanitize_path(server_path)
        except ValueError as e:
            return build_error_response(
                "PATH_SANITIZATION_FAILED",
                f"Path sanitization failed: {str(e)}"
            )

        # Create client for the target server
        client = ExternalMCPClient(sanitized_path)

        # Initialize connection
        init_result = await client.initialize()
        if not init_result["success"]:
            return init_result

        # Call the tool with provided parameters
        params = tool_params or {}
        result = await client.call_tool(tool_name, **params)

        return {
            "success": True,
            "operation": "skeleton_key",
            "server_path": server_path,
            "tool_name": tool_name,
            "tool_params": params,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Skeleton key operation failed: {str(e)}")
        return build_error_response(
            "SKELETON_KEY_FAILED",
            f"Failed to execute tool '{tool_name}' on server '{server_path}': {str(e)}",
            suggestions=[
                "Verify the server_path points to a valid MCP server",
                "Check that the tool_name exists on the target server",
                "Ensure tool parameters are correctly formatted",
                "Verify the target server is running and accessible"
            ]
        )


@mcp.tool()
async def discover_mcp_server_tools(server_path: str) -> dict[str, Any]:
    """Discover all available tools on any MCP server.

    The reconnaissance tool for the skeleton key - finds what tools
    are available on a target MCP server before calling them.

    Args:
        server_path: Path to MCP server to analyze

    Returns:
        List of all available tools and their descriptions
    """
    try:
        client = ExternalMCPClient(server_path)

        init_result = await client.initialize()
        if not init_result["success"]:
            return init_result

        tools = await client.list_tools()

        return {
            "success": True,
            "operation": "discover_tools",
            "server_path": server_path,
            "tools": tools,
            "tool_count": len(tools),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Tool discovery failed: {str(e)}")
        return build_error_response(
            "DISCOVERY_FAILED",
            f"Failed to discover tools on server '{server_path}': {str(e)}"
        )


class ExternalMCPClient:
    """Generic client for connecting to external MCP servers via stdio."""

    def __init__(self, server_path: str | Path, server_name: str, timeout: int = 30):
        """
        Initialize external MCP client.

        Args:
            server_path: Path to the external MCP server script
            server_name: Human-readable name for the server
            timeout: Tool execution timeout in seconds
        """
        self.server_path = Path(server_path)
        self.server_name = server_name
        self.timeout = timeout
        self.transport: Optional[StdioTransport] = None
        self.client: Optional[Client] = None
        self._is_connected = False

    async def connect(self) -> bool:
        """Connect to external MCP server via stdio transport."""
        if self._is_connected and self.client:
            return True

        try:
            # Verify server path exists
            if not self.server_path.exists():
                logger.warning(f"{self.server_name}: Server path does not exist: {self.server_path}")
                return False

            # Create stdio transport
            self.transport = StdioTransport(
                command="python",
                args=[str(self.server_path)],
                env=os.environ.copy()
            )

            # Create FastMCP client
            self.client = Client(self.transport)

            # Test connection
            async with self.client:
                await self.client.initialize()
                tools = await self.client.list_tools()
                logger.info(f"{self.server_name}: Connected via stdio ({len(tools)} tools available)")

            self._is_connected = True
            return True

        except Exception as e:
            logger.error(f"{self.server_name}: Failed to connect via stdio: {e}")
            await self.close()
            return False

    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a tool on the external MCP server.

        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool parameters

        Returns:
            Tool result as dictionary
        """
        if not self._is_connected or not self.client:
            if not await self.connect():
                return build_error_response(
                    "CONNECTION_FAILED",
                    f"{self.server_name} not connected"
                )

        try:
            async with self.client:
                result = await asyncio.wait_for(
                    self.client.call_tool(tool_name, **kwargs),
                    timeout=self.timeout
                )
                return {
                    "success": True,
                    "result": result,
                    "server": self.server_name,
                    "timestamp": datetime.now().isoformat()
                }
        except asyncio.TimeoutError:
            return build_error_response(
                "TIMEOUT",
                f"Tool {tool_name} timed out after {self.timeout}s"
            )
        except Exception as e:
            logger.error(f"{self.server_name}: Error calling {tool_name}: {e}")
            return build_error_response(
                "TOOL_ERROR",
                f"Error calling {tool_name}: {str(e)}"
            )

    async def list_tools(self) -> list[Dict[str, Any]]:
        """List available tools from the external MCP server."""
        if not self._is_connected or not self.client:
            if not await self.connect():
                return []

        try:
            async with self.client:
                tools = await self.client.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools
                ]
        except Exception as e:
            logger.error(f"{self.server_name}: Error listing tools: {e}")
            return []

    async def close(self):
        """Close the external MCP client connection."""
        self._is_connected = False
        # FastMCP handles cleanup automatically
        self.client = None
        self.transport = None


class MCPClientManager:
    """Manage connections to multiple external MCP servers."""

    def __init__(self):
        self.clients: Dict[str, ExternalMCPClient] = {}
        self._server_configs = {
            "brightdata": {
                "path": os.getenv("BRIGHTDATA_MCP_PATH", "D:/Dev/repos/brightdata-mcp/server.py"),
                "name": "BrightData MCP"
            },
            "vrchat": {
                "path": os.getenv("VRCHAT_MCP_PATH", "D:/Dev/repos/vrchat-mcp/server.py"),
                "name": "VRChat MCP"
            },
            "plex": {
                "path": os.getenv("PLEX_MCP_PATH", "D:/Dev/repos/plex-mcp/src/plex_mcp/server.py"),
                "name": "Plex MCP"
            }
        }

    async def get_client(self, server_name: str) -> Optional[ExternalMCPClient]:
        """Get or create client for specified server."""
        if server_name not in self.clients:
            if server_name not in self._server_configs:
                logger.error(f"Unknown server: {server_name}")
                return None

            config = self._server_configs[server_name]
            self.clients[server_name] = ExternalMCPClient(
                server_path=config["path"],
                server_name=config["name"]
            )

        return self.clients[server_name]

    async def close_all(self):
        """Close all external MCP client connections."""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()


# Global client manager instance
mcp_client_manager = MCPClientManager()


# ============================================================================
# WEATHER TOOLS
# ============================================================================

@mcp.tool()
async def get_weather_report(location: str, source: str = "brightdata") -> dict[str, Any]:
    """
    Get weather report for a location using external MCP services.

    This demonstrates external MCP server integration by connecting to
    BrightData MCP server for web search capabilities.

    Args:
        location: City name or location (e.g., "Vienna, Austria")
        source: Data source - "brightdata" for web search, "direct" for API

    Returns:
        Weather information dictionary
    """
    try:
        if source == "brightdata":
            # Use BrightData MCP for web search
            brightdata_client = await mcp_client_manager.get_client("brightdata")
            if not brightdata_client:
                return build_error_response(
                    "CLIENT_UNAVAILABLE",
                    "BrightData MCP client not available"
                )

            # Search for weather information
            search_result = await brightdata_client.call_tool(
                "mcp_brightdata_search_engine",
                query=f"current weather in {location}",
                engine="google"
            )

            if not search_result.get("success"):
                return search_result

            # Parse weather from search results
            return await _parse_weather_from_search(search_result["result"])

        elif source == "direct":
            # Direct weather API call (fallback)
            return await _get_weather_direct(location)

        else:
            return build_error_response(
                "INVALID_SOURCE",
                f"Unsupported weather source: {source}"
            )

    except Exception as e:
        logger.error(f"Weather report failed for {location}: {e}")
        return build_error_response(
            "WEATHER_ERROR",
            f"Failed to get weather for {location}: {str(e)}"
        )


async def _parse_weather_from_search(search_result: Dict[str, Any]) -> Dict[str, Any]:
    """Parse weather information from search results."""
    try:
        # Extract weather data from search results
        # This would parse the actual search results structure
        results = search_result.get("results", [])

        if not results:
            return build_error_response(
                "NO_RESULTS",
                "No weather information found in search results"
            )

        # Mock parsing - in real implementation, parse actual weather data
        return {
            "success": True,
            "location": "Parsed from search",
            "temperature": "22°C",
            "condition": "Sunny",
            "humidity": "45%",
            "source": "brightdata_search",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return build_error_response(
            "PARSE_ERROR",
            f"Failed to parse weather from search: {str(e)}"
        )


async def _get_weather_direct(location: str) -> Dict[str, Any]:
    """Get weather using direct API calls."""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use wttr.in API for weather
            response = await client.get(f"https://wttr.in/{location}?format=j1")

            if response.status_code != 200:
                return build_error_response(
                    "API_ERROR",
                    f"Weather API returned status {response.status_code}"
                )

            weather_data = response.json()

            current = weather_data.get("current_condition", [{}])[0]
            return {
                "success": True,
                "location": location,
                "temperature": f"{current.get('temp_C', 'N/A')}°C",
                "condition": current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
                "humidity": f"{current.get('humidity', 'N/A')}%",
                "source": "wttr.in",
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        return build_error_response(
            "DIRECT_API_ERROR",
            f"Direct weather API failed: {str(e)}"
        )


# ============================================================================
# VRCHAT STATUS TOOLS
# ============================================================================

@mcp.tool()
async def get_vrchat_server_status() -> dict[str, Any]:
    """
    Get VRChat server status using VRChat MCP server.

    Demonstrates external MCP server integration by connecting to
    VRChat MCP server for real-time platform status.

    Returns:
        VRChat server status information
    """
    try:
        vrchat_client = await mcp_client_manager.get_client("vrchat")
        if not vrchat_client:
            return build_error_response(
                "CLIENT_UNAVAILABLE",
                "VRChat MCP client not available"
            )

        # Get server status
        status_result = await vrchat_client.call_tool("vrchat_server_status")
        if not status_result.get("success"):
            return status_result

        # Get online user count
        users_result = await vrchat_client.call_tool("vrchat_online_users")
        if not users_result.get("success"):
            users_result = {"result": {"count": "unknown"}}

        # Get popular worlds
        worlds_result = await vrchat_client.call_tool(
            "vrchat_popular_worlds",
            limit=5
        )
        if not worlds_result.get("success"):
            worlds_result = {"result": []}

        return {
            "success": True,
            "server_status": status_result["result"],
            "online_users": users_result["result"].get("count", 0),
            "popular_worlds": worlds_result["result"],
            "source": "vrchat_mcp",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"VRChat status check failed: {e}")
        return build_error_response(
            "VRCHAT_ERROR",
            f"Failed to get VRChat status: {str(e)}"
        )


@mcp.tool()
async def check_vrchat_api_direct() -> dict[str, Any]:
    """
    Check VRChat API status directly (fallback method).

    Uses direct HTTP calls to VRChat API endpoints when MCP server is unavailable.

    Returns:
        VRChat API status information
    """
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check VRChat API configuration endpoint
            config_response = await client.get("https://api.vrchat.cloud/api/1/config")

            if config_response.status_code == 200:
                config_data = config_response.json()

                # Try to get some basic instance data (may require auth)
                try:
                    instances_response = await client.get("https://api.vrchat.cloud/api/1/instances")
                    instance_count = len(instances_response.json()) if instances_response.status_code == 200 else 0
                except:
                    instance_count = "unknown"

                return {
                    "success": True,
                    "api_status": "online",
                    "client_version": config_data.get("clientApiKey", "unknown"),
                    "active_instances": instance_count,
                    "source": "direct_api",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "api_status": "offline",
                    "http_status": config_response.status_code,
                    "source": "direct_api",
                    "timestamp": datetime.now().isoformat()
                }

    except Exception as e:
        return build_error_response(
            "DIRECT_API_ERROR",
            f"Direct VRChat API check failed: {str(e)}"
        )


# ============================================================================
# GENERIC EXTERNAL MCP TOOL CALLER
# ============================================================================

@mcp.tool()
async def call_external_mcp_tool(
    server_name: str,
    tool_name: str,
    tool_params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Call any tool on any configured external MCP server.

    This is a generic interface for external MCP server integration,
    allowing Advanced Memory to leverage any external MCP server's tools.

    Args:
        server_name: Name of the external MCP server (brightdata, vrchat, plex)
        tool_name: Name of the tool to call on that server
        tool_params: Parameters to pass to the tool (optional)

    Returns:
        Tool execution result from external server
    """
    try:
        client = await mcp_client_manager.get_client(server_name)
        if not client:
            return build_error_response(
                "UNKNOWN_SERVER",
                f"Unknown or unavailable server: {server_name}"
            )

        # Call the tool with provided parameters
        params = tool_params or {}
        result = await client.call_tool(tool_name, **params)

        # Add metadata about the external call
        if result.get("success"):
            result["external_call"] = {
                "server": server_name,
                "tool": tool_name,
                "params": params,
                "called_at": datetime.now().isoformat()
            }

        return result

    except Exception as e:
        logger.error(f"External MCP tool call failed: {server_name}.{tool_name}: {e}")
        return build_error_response(
            "EXTERNAL_CALL_ERROR",
            f"Failed to call {tool_name} on {server_name}: {str(e)}"
        )


@mcp.tool()
async def list_external_mcp_tools(server_name: str) -> dict[str, Any]:
    """
    List all available tools from an external MCP server.

    Args:
        server_name: Name of the external MCP server

    Returns:
        List of available tools and their descriptions
    """
    try:
        client = await mcp_client_manager.get_client(server_name)
        if not client:
            return build_error_response(
                "UNKNOWN_SERVER",
                f"Unknown or unavailable server: {server_name}"
            )

        tools = await client.list_tools()

        return {
            "success": True,
            "server": server_name,
            "tools": tools,
            "count": len(tools),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return build_error_response(
            "LIST_TOOLS_ERROR",
            f"Failed to list tools from {server_name}: {str(e)}"
        )