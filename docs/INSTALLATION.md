# Installation Guide

This guide covers installation and setup of Advanced Memory MCP for various MCP clients and standalone usage.

## Prerequisites

- Python 3.11 or higher
- Compatible MCP client (Claude Desktop, Cursor IDE, Windsurf)
- Node.js 18+ (for web interface)

## MCP Server Installation

### PyPI Installation
```bash
pip install advanced-memory-mcp
```

### Development Installation
```bash
git clone https://github.com/sandraschi/advanced-memory-mcp.git
cd advanced-memory-mcp
pip install -e ".[dev]"
```

### Verification
```bash
advanced-memory --version
# Advanced Memory MCP v1.2.0
```

## MCP Client Configuration

### Claude Desktop

#### Option 1: MCPB Package (Recommended)
1. Download `advanced-memory-mcp.mcpb` from [Releases](https://github.com/sandraschi/advanced-memory-mcp/releases)
2. Open Claude Desktop → Settings → Extensions
3. Drag and drop the `.mcpb` file
4. Configure project path in the extension UI

#### Option 2: Manual Configuration
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"]
    }
  }
}
```

### Cursor IDE

#### Portmanteau Mode (Recommended for Cursor)
```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "ADVANCED_MEMORY_PORTMANTEAU_ONLY": "true"
      }
    }
  }
}
```

This provides 10 consolidated tools compatible with Cursor's 50-tool limit.

### Windsurf IDE

Add to Windsurf MCP configuration:
```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"]
    }
  }
}
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Research API Keys (optional)
OPENAI_API_KEY=your_openai_key
SERPAPI_KEY=your_serpapi_key
BING_SEARCH_KEY=your_bing_key

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LM_STUDIO_BASE_URL=http://localhost:1234

# Application Settings
ADVANCED_MEMORY_HOME=~/.advanced-memory
ADVANCED_MEMORY_LOG_LEVEL=INFO
```

### Configuration File

Create `~/.advanced-memory/config.yaml`:

```yaml
advanced_memory:
  home: "~/.advanced-memory"
  database: "memory.db"
  log_level: "INFO"

research:
  web_search:
    default_provider: "duckduckgo"
    serpapi_key: ""
    bing_key: ""
  github:
    token: ""
  arxiv:
    max_results: 50

skills:
  export_path: "~/claude-skills"
  import_path: "~/anthropic-skills"

llm:
  provider: "ollama"
  model: "llama3:8b"
```

## Web Interface Setup

The web interface provides standalone access without MCP client requirements.

### Installation
```bash
cd webapp
npm install
```

### Development
```bash
npm run dev  # Starts on http://localhost:3000
```

### Production Build
```bash
npm run build
npm run preview  # Test production build locally
```

### Docker Deployment
```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
```

## Verification

### MCP Server Test
```bash
# Test basic functionality
advanced-memory status

# Test tool availability
advanced-memory mcp  # Should show available tools
```

### Web Interface Test
1. Start the web application
2. Navigate to http://localhost:3000
3. Verify dashboard loads
4. Test settings page LLM provider detection

## Troubleshooting

### Common Issues

#### MCP Server Not Connecting
- Verify Python path: `which python`
- Check MCP configuration syntax
- Ensure package is installed: `pip show advanced-memory-mcp`

#### Web Interface Not Loading
- Verify Node.js version: `node --version`
- Check npm dependencies: `npm list`
- Clear cache: `rm -rf node_modules && npm install`

#### LLM Provider Not Detected
- Verify Ollama/LM Studio are running
- Check network connectivity
- Review environment variables

### Logs and Diagnostics

#### MCP Server Logs
Logs are written to `~/.advanced-memory/logs/` with rotation.

#### Web Interface Logs
Check browser developer console for client-side errors.

#### Manual Testing
```bash
# Test research functionality
python -c "
from advanced_memory.mcp.tools.adn_web_search import adn_web_search
result = adn_web_search('search', 'test query', 'duckduckgo')
print('Web search test:', 'PASSED' if result else 'FAILED')
"
```

## Platform-Specific Notes

### Windows
- Use PowerShell for command execution
- Ensure Python is in PATH
- Use forward slashes in configuration paths

### macOS
- Use Homebrew Python if system Python issues
- Check firewall settings for local LLM servers

### Linux
- Verify Python development headers for compilation
- Check SELinux/AppArmor for local server access

## Security Considerations

- API keys are stored locally and not transmitted
- LLM providers communicate directly with their respective APIs
- Web interface runs locally and does not expose external ports by default
- Database files contain user content and should be secured appropriately

## Support

For installation issues:
1. Check the [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
2. Verify all prerequisites are met
3. Test with minimal configuration
4. Check logs for error details

For additional support, see the main repository documentation or create an issue.
