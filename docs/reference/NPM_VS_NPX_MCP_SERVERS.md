# npm vs npx for MCP Servers

**Date**: 2025-12-02
**Context**: Performance and setup recommendations for MCP server "zoo" (53 servers)

## Quick Answer

**npm**: Installs packages permanently (local/global)  
**npx**: Runs packages temporarily (downloads, runs, cleans up)

## Performance Comparison

| Method | First Run | Subsequent Runs | Notes |
|--------|-----------|-----------------|-------|
| **npx** | 1-5 seconds | 100-500ms | Downloads/checks cache, verifies package |
| **npm install** | 5-30 seconds | 50-200ms | One-time install, then fast |
| **Direct Python** | 50-200ms | 50-200ms | Your current Python servers |

### npx Overhead
- Checks npm cache
- Verifies package version
- May download updates
- Spawns Node.js process

## Your Setup: 53 MCP Servers

### Current Configuration
- **Mostly Python servers**: Direct execution (fast)
- **Some npx servers**: docker, github, fetch, playwright, context7, microsoft-365
- **Mix approach**: Works but npx adds startup delay

### Recommendations

#### Option 1: Hybrid Approach (Recommended)

Create a dedicated MCP servers directory:

```powershell
# Create shared MCP servers location
mkdir C:\Users\sandr\.mcp-servers
cd C:\Users\sandr\.mcp-servers
npm init -y
```

Install frequently used servers:
```json
{
  "dependencies": {
    "@modelcontextprotocol/server-docker": "latest",
    "@modelcontextprotocol/server-github": "latest",
    "@modelcontextprotocol/server-fetch": "latest",
    "@modelcontextprotocol/server-playwright": "latest"
  }
}
```

Then update `mcp.json` to use local installs:
```json
{
  "docker": {
    "command": "node",
    "args": ["C:/Users/sandr/.mcp-servers/node_modules/@modelcontextprotocol/server-docker/dist/index.js"]
  }
}
```

**Benefits:**
- Faster startup (50-200ms vs 100-500ms)
- Version control via package.json
- Easy updates: `npm update`
- No cache checks on every run

#### Option 2: Keep npx for Lazy Loading

Keep npx for servers you rarely use. Cursor only starts servers when needed, so:
- **Frequently used**: npm install (faster)
- **Rarely used**: npx (convenient, acceptable delay)

#### Option 3: Global npm Install

```powershell
npm install -g @modelcontextprotocol/server-docker
npm install -g @modelcontextprotocol/server-github
# etc.
```

Then use direct paths in `mcp.json`.

## When to Use Which?

### Use npm when:
- Server is used frequently (daily)
- You want version control
- Startup performance matters
- You have many servers (like your 53-server zoo)

### Use npx when:
- Server is used rarely
- You want always-latest version
- One-off tools/scripts
- Minimal maintenance preferred

## Maintenance Script

Create `update-mcp-servers.ps1`:

```powershell
# update-mcp-servers.ps1
cd C:\Users\sandr\.mcp-servers
npm update
Write-Host "MCP servers updated"
```

## Performance Impact

With 53 servers:
- **All npx**: 5-25 seconds total startup overhead (if all start)
- **Hybrid (npm for frequent)**: 2-10 seconds total
- **All npm**: 2-10 seconds total (but requires maintenance)

**Key insight**: Cursor starts servers lazily (on-demand), so startup time only matters for frequently used servers.

## Recommendation for Your Zoo

1. **Frequently used (daily)**: npm install in shared directory
   - docker, github, fetch, playwright
   
2. **Occasionally used**: Keep npx
   - kubernetes, aws, azure (if you use them rarely)

3. **Python servers**: Keep as-is (already fast)

4. **Create maintenance script**: Update npm-installed servers periodically

## Tags
#mcp #npm #npx #performance #optimization #53-servers

