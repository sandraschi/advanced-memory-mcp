# Official npx MCP Servers Reference

**Date**: 2025-12-02
**Source**: `D:\Dev\repos\veogen\mcp.json`
**Context**: Collection of official MCP servers available via npx

## Overview

The veogen project has a comprehensive collection of official MCP servers from the `@modelcontextprotocol` organization. These are all available via `npx -y` for instant installation.

## Available Official MCP Servers

### File System & Storage
- **filesystem**: `@modelcontextprotocol/server-filesystem`
  - File system operations
  - Example: `npx -y @modelcontextprotocol/server-filesystem /path/to/directory`

- **google-drive**: `@modelcontextprotocol/server-gdrive`
  - Google Drive integration
  - Requires: `GDRIVE_CLIENT_ID`, `GDRIVE_CLIENT_SECRET`

### Database Servers
- **postgres**: `@modelcontextprotocol/server-postgres`
  - PostgreSQL database operations
  - Example: `npx -y @modelcontextprotocol/server-postgres postgresql://user:pass@host:port/db`

- **sqlite**: `@modelcontextprotocol/server-sqlite`
  - SQLite database operations
  - No configuration needed

### Web Automation
- **playwright**: `@modelcontextprotocol/server-playwright`
  - Browser automation with Playwright
  - Already in user's mcp.json

- **puppeteer**: `@modelcontextprotocol/server-puppeteer`
  - Browser automation with Puppeteer
  - Alternative to Playwright

### Search & APIs
- **brave-search**: `@modelcontextprotocol/server-brave-search`
  - Brave Search API integration
  - Requires: `BRAVE_API_KEY`

- **google-maps**: `@modelcontextprotocol/server-google-maps`
  - Google Maps API integration
  - Requires: `GOOGLE_MAPS_API_KEY`

- **fetch**: `@modelcontextprotocol/server-fetch`
  - HTTP fetch operations
  - Already in user's mcp.json (via PowerShell script)

### Development & Infrastructure
- **github**: `@modelcontextprotocol/server-github`
  - GitHub API integration
  - Requires: `GITHUB_PERSONAL_ACCESS_TOKEN`
  - Already in user's mcp.json (via PowerShell script)

- **docker**: `@modelcontextprotocol/server-docker`
  - Docker operations
  - Already in user's mcp.json

- **kubernetes**: `@modelcontextprotocol/server-kubernetes`
  - Kubernetes cluster operations

- **shell**: `@modelcontextprotocol/server-shell`
  - Shell command execution

### Cloud Platforms
- **aws**: `@modelcontextprotocol/server-aws`
  - AWS services integration

- **azure**: `@modelcontextprotocol/server-azure`
  - Azure services integration

### Memory & AI
- **memory**: `@modelcontextprotocol/server-memory`
  - **This is the official "Basic Memory" server!**
  - Simple memory/knowledge management
  - The one with 2k stars on GitHub

- **sequential-thinking**: `@modelcontextprotocol/server-sequential-thinking`
  - Sequential reasoning capabilities

### Utilities
- **time**: `@modelcontextprotocol/server-time`
  - Time and date operations

- **everart**: `@modelcontextprotocol/server-everart`
  - Everart API integration
  - Requires: `EVERART_API_KEY`

## Key Insights

### Official vs Custom Servers
- **Official servers**: Use `@modelcontextprotocol/server-*` naming
- **Custom servers**: User has many custom Python-based servers
- **Hybrid approach**: Mix of official (npx) and custom (Python) servers

### Installation Pattern
All official servers follow the same pattern:
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-{name}"],
  "env": {
    // Optional environment variables
  }
}
```

### Advantages of npx Servers
1. **No installation needed**: `-y` flag auto-installs on first use
2. **Always latest**: Gets latest version from npm registry
3. **Zero maintenance**: No local dependencies to manage
4. **Cross-platform**: Works on Windows, macOS, Linux

### Comparison with User's Setup
User has:
- **Custom Python servers**: Advanced Memory, Blender, Calibre, etc.
- **Some official servers**: docker, github, fetch, playwright
- **Missing opportunities**: Could add more official servers for common tasks

## Potential Additions to User's mcp.json

### High Value Additions
1. **sqlite**: For quick database operations
2. **time**: For time/date utilities
3. **sequential-thinking**: For reasoning tasks
4. **google-maps**: If user needs location services
5. **brave-search**: Alternative search engine

### Already Covered
- **docker**: Already have via npx
- **github**: Already have via PowerShell script
- **fetch**: Already have via PowerShell script
- **playwright**: Already have via npx

## Notes

- The **memory** server is the official "Basic Memory" that inspired Advanced Memory
- Official servers are maintained by Anthropic/MCP team
- npx approach is very convenient for quick server additions
- User's custom servers provide much more functionality than official ones
- Official servers are good for standard operations, custom servers for specialized needs

## Tags
#mcp #npx #official-servers #reference #veogen














