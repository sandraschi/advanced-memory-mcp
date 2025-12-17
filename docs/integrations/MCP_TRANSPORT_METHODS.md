# MCP Transport Methods for Advanced Memory

**Last Updated:** 2025-12-03
**Status:** Active

---

## Overview

Advanced Memory MCP supports **stdio transport** (current) and can be extended to support **HTTP transport** (future).

Both transports are valid per Anthropic MCP standard. This guide explains how to connect to Advanced Memory using each method.

---

## Current: Stdio Transport

### How to Connect

**From Claude Desktop:**

```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory_mcp"],
      "env": {
        "PROJECT_NAME": "default"
      }
    }
  }
}
```

**From Python (FastMCP Client):**

```python
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

# Spawn Advanced Memory MCP via stdio
transport = StdioTransport(
    command="python",
    args=["-m", "advanced_memory_mcp"]
)

client = Client(transport)

async with client:
    await client.initialize()

    # Call Advanced Memory tools
    result = await client.call_tool(
        "adn_content",
        operation="write",
        identifier="Test Note",
        content="# Test\n\nHello from stdio!",
        folder="inbox"
    )
```

**From MCP Studio:**

MCP Studio automatically handles stdio transport - just add Advanced Memory to your servers list.

---

## Future: HTTP Transport

Advanced Memory MCP currently **does not** expose an HTTP interface, but this is a planned enhancement.

### Planned Implementation

**Server Side:**

```python
# advanced_memory_mcp/server.py (future)
from fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn
import sys

mcp = FastMCP("advanced-memory", version="2.0.0")

# ... tool definitions ...

# HTTP interface
app = FastAPI(title="Advanced Memory MCP (HTTP)")

@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "http"}

@app.post("/mcp/v1/tools/list")
async def list_tools():
    tools = []
    for name, func in mcp._tools.items():
        tools.append({
            "name": name,
            "description": func.__doc__ or "",
            "inputSchema": getattr(func, "input_schema", {})
        })
    return {"tools": tools}

@app.post("/mcp/v1/tools/call")
async def call_tool(request: dict):
    tool_name = request["tool"]
    params = request.get("params", {})

    if tool_name not in mcp._tools:
        return {"success": False, "error": f"Tool {tool_name} not found"}

    try:
        result = await mcp._tools[tool_name](**params)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if "--http" in sys.argv:
        port = int(sys.argv[sys.argv.index("--http") + 1]
                   if len(sys.argv) > sys.argv.index("--http") + 1
                   else 3060)
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        mcp.run(transport="stdio")
```

**Usage:**

```bash
# Stdio mode (current)
python -m advanced_memory_mcp

# HTTP mode (future)
python -m advanced_memory_mcp --http 3060
```

**HTTP Client:**

```python
import httpx

async def call_adn_tool(tool_name: str, **params):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:3060/mcp/v1/tools/call",
            json={"tool": tool_name, "params": params}
        )
        return response.json()

# Usage
result = await call_adn_tool(
    "adn_content",
    operation="read",
    identifier="Test Note"
)
```

### Benefits of HTTP Transport

1. **Remote Access** - Access Advanced Memory from other machines
2. **Testing** - Use curl/Postman to test tools
3. **Docker** - Easier to containerize with HTTP
4. **Cross-Platform** - Windows client → Linux server
5. **Language Agnostic** - Any HTTP client can connect

---

## Use Cases by Transport

### Stdio (Current)

**Best for:**
- ✅ Claude Desktop integration
- ✅ Cursor integration
- ✅ MCP Studio
- ✅ Local Python clients
- ✅ Single-machine setup

**Limitations:**
- ❌ Can't access remotely
- ❌ Docker containers have issues spawning host processes
- ❌ Platform-specific (Windows/Linux differences)

### HTTP (Future)

**Best for:**
- ✅ Remote Advanced Memory access (Goliath → other machines)
- ✅ Docker/Kubernetes deployments
- ✅ Quick testing with curl
- ✅ Web applications
- ✅ Mobile apps (future)

**Limitations:**
- ❌ Network overhead (slightly slower)
- ❌ Need to manage server lifecycle
- ❌ Security considerations (HTTPS, auth)

---

## Integration Examples

### Vienna Life Assistant (Stdio)

```python
# backend/services/mcp_clients.py
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

transport = StdioTransport(
    command="python",
    args=["-m", "advanced_memory_mcp"]
)

client = Client(transport)

async with client:
    # Search notes
    result = await client.call_tool(
        "adn_search",
        operation="notes",
        query="vienna life"
    )
```

### Vienna Life Assistant (HTTP - Future)

```python
# backend/services/mcp_clients.py
import httpx

async def search_notes(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://goliath:3060/mcp/v1/tools/call",
            json={
                "tool": "adn_search",
                "params": {
                    "operation": "notes",
                    "query": query
                }
            }
        )
        return response.json()
```

---

## Testing Transports

### Test Stdio

```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

async def test_stdio():
    transport = StdioTransport(
        command="python",
        args=["-m", "advanced_memory_mcp"]
    )

    client = Client(transport)

    async with client:
        await client.initialize()
        tools = await client.list_tools()
        print(f"Found {len(tools)} tools")

        # Test a tool
        result = await client.call_tool("adn_info")
        print(result)

asyncio.run(test_stdio())
```

### Test HTTP (Future)

```bash
# Start HTTP server
python -m advanced_memory_mcp --http 3060

# Test with curl
curl http://localhost:3060/health
curl -X POST http://localhost:3060/mcp/v1/tools/list
curl -X POST http://localhost:3060/mcp/v1/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "adn_info", "params": {}}'
```

---

## Roadmap

### Phase 1: Current (Stdio Only)
- ✅ Stdio transport working
- ✅ Claude Desktop integration
- ✅ MCP Studio integration
- ✅ FastMCP client support

### Phase 2: Dual Interface (January 2025)
- [ ] Add HTTP transport support
- [ ] Implement dual interface pattern
- [ ] Add HTTP API documentation
- [ ] Test both transports
- [ ] Update integration guides

### Phase 3: Enhanced HTTP (Future)
- [ ] Add authentication
- [ ] Add rate limiting
- [ ] Add HTTPS support
- [ ] Add health checks
- [ ] Add Prometheus metrics

---

## Related Documentation

- `../user-guide/mcp-basics.md` - MCP basics
- `../mcp-technical/MCP_PRODUCTION_CHECKLIST.md` - Production deployment
- `../architecture/TRIPLE_PLAY_MCP_STRATEGY.md` - MCP strategy
- MCP Central Docs: `D:/Dev/repos/mcp-central-docs/docs/anthropic-ecosystem/mcp-protocol/TRANSPORTS.md`

---

**Current Status:** Stdio transport only
**Future Plan:** Dual interface (stdio + HTTP) in January 2025
**Both transports are valid** per Anthropic MCP standard!
