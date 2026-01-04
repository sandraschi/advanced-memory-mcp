# Antigravity IDE Compatibility Guide

**Date**: 2025-12-12
**Status**: Server works in Cursor IDE, Claude Desktop, Zed IDE, but fails in Antigravity IDE

## Known Antigravity IDE Requirements

Based on web research and community reports, Antigravity IDE has stricter MCP protocol requirements:

### 1. ✅ Stdout Must Be Clean (Already Fixed)
- **Issue**: Any non-JSON output to stdout breaks JSON-RPC protocol
- **Status**: ✅ **FIXED** - Server has comprehensive stdout protection:
  - Binary mode set on Windows (`msvcrt.setmode()`)
  - `DevNullStdout` patches stdout during initialization
  - All logging redirected to stderr
  - Loguru disabled in stdio mode

**Files with fixes:**
- `src/advanced_memory/mcp/server.py` (lines 14-36, 46-145)
- `src/advanced_memory/mcp/mcp_instance.py` (lines 14-36, 46-145)

### 2. ⚠️ Tool Count Limit (~25 tools)
- **Issue**: Antigravity has a limit of ~25 active tools across all MCP servers
- **Current**: Server exposes **21 tools** in portmanteau mode (within limit)
- **Full mode**: ~56 tools (exceeds limit)
- **Recommendation**: Use portmanteau mode (default) for Antigravity

**Tool count control:**
- Default: Portmanteau mode (15-21 tools) ✅
- Full mode: Set `ADVANCED_MEMORY_FULL_TOOLS_MODE=true` (56 tools) ❌

### 3. ✅ Tool Naming (No Dots)
- **Issue**: Tool names with dots (e.g., `docs.create`) are NOT allowed
- **Status**: ✅ **COMPLIANT** - All tools use underscores/hyphens:
  - `adn_content`, `adn_search`, `adn_export`, etc.
  - No dots in any tool names

### 4. ⚠️ Absolute Paths Required
- **Issue**: Antigravity requires absolute paths in `mcp_config.json`
- **Status**: ⚠️ **USER CONFIGURATION** - Must be set in Antigravity config

**Example Antigravity config:**
```json
{
  "mcpServers": {
    "advanced-memory-mcp": {
      "command": "python",
      "args": [
        "D:\\Dev\\repos\\advanced-memory-mcp\\src\\advanced_memory\\mcp\\server.py"
      ],
      "env": {
        "ADVANCED_MEMORY_PROJECT_PATH": "D:\\Dev\\repos\\advanced-memory-mcp\\projects"
      }
    }
  }
}
```

### 5. ✅ Binary Mode on Windows (Already Fixed)
- **Issue**: Line ending conversion (`\r\n` → `\n`) causes "invalid trailing data" errors
- **Status**: ✅ **FIXED** - Binary mode set before stdout patching

## Troubleshooting Steps

### Step 1: Verify Configuration
1. Check `mcp_config.json` uses **absolute paths**
2. Verify portmanteau mode (don't set `ADVANCED_MEMORY_FULL_TOOLS_MODE=true`)
3. Ensure Python path is absolute

### Step 2: Check Server Logs
Look for these errors in Antigravity logs:
- `"invalid trailing data"` → Binary mode issue (should be fixed)
- `"Connection failed"` → Path/configuration issue
- `"Tool limit exceeded"` → Too many tools enabled

### Step 3: Test Server Standalone
Run server directly to verify it starts:
```powershell
cd D:\Dev\repos\advanced-memory-mcp
python -m advanced_memory.mcp.server
```

Should see no output (stdout is patched). Check stderr for errors.

### Step 4: Enable Debug Logging (if needed)
Temporarily enable stderr logging to see what's happening:
```python
# In server.py, change:
logger.add(sys.stderr, level="CRITICAL", format="{message}")
# To:
logger.add(sys.stderr, level="DEBUG", format="{message}")
```

## Known Issues from Community

1. **FastMCP Stalling**: Some users report FastMCP servers stall in Antigravity
   - GitHub: https://github.com/jlowin/fastmcp/issues/2489
   - **Workaround**: Ensure stdout is completely clean (already done)

2. **Tool Limit**: Antigravity limits total tools across all servers
   - **Solution**: Use portmanteau mode (default) ✅

3. **Initialization Timeout**: First run might timeout while downloading packages
   - **Solution**: Run server manually once to cache dependencies

## Recommendations

1. ✅ **Keep portmanteau mode** (default) - 21 tools is within limit
2. ✅ **Use absolute paths** in Antigravity config
3. ✅ **Verify binary mode** is working (already implemented)
4. ⚠️ **Monitor Antigravity logs** for specific error messages
5. ⚠️ **Test with minimal config** - disable other MCP servers to isolate issue

## Additional Resources

- [Antigravity MCP Tutorial](https://antigravity.codes/blog/antigravity-mcp-tutorial)
- [FastMCP Issue #2489](https://github.com/jlowin/fastmcp/issues/2489)
- [MCP Error Handling Guide](https://www.stainless.com/mcp/error-handling-and-debugging-mcp-servers)

## Next Steps

If server still fails in Antigravity after verifying above:

1. **Get specific error message** from Antigravity logs
2. **Compare with working IDEs** - what's different?
3. **Test minimal server** - create a simple FastMCP server to isolate issue
4. **Report to Antigravity** - may be an Antigravity-specific bug
