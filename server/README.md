# Advanced Memory MCP Server (DXT Package)

This is the DXT (Desktop Extension) package for Advanced Memory MCP, designed to work seamlessly with Claude Desktop and other MCP-compatible applications.

## Features

- **Portmanteau Tools**: 8 consolidated tools that replace 40+ individual tools
- **Multi-Project Support**: Switch between different knowledge bases
- **Import/Export**: Support for Obsidian, Notion, Evernote, Joplin
- **Full-Text Search**: Semantic search with filtering
- **Entity Relationships**: Knowledge graph with bidirectional links
- **Editor Integration**: Typora, Notepad++ support

## Installation

1. Install the DXT package in Claude Desktop:
   - Open Claude Desktop
   - Go to Settings > Extensions
   - Select the `advanced-memory-mcp.dxt` file

2. Configure your project path:
   - Set the project path to your Advanced Memory directory
   - Enable portmanteau tools for Cursor IDE compatibility

## Usage

Once installed, you can use the Advanced Memory tools directly in Claude Desktop:

### Portmanteau Tools (Recommended)

```python
# Content management
adn_content("write", identifier="Meeting Notes", content="# Meeting\n\nNotes here", folder="meetings")
adn_content("read", identifier="Meeting Notes")

# Project management  
adn_project("list")
adn_project("switch", project_name="work-project")

# Export/Import
adn_export("pandoc", export_path="output.pdf", format_type="pdf")
adn_import("obsidian", source_path="/path/to/vault")

# Search
adn_search("notes", query="machine learning", page=1, page_size=10)

# Knowledge operations
adn_knowledge("tag_analytics", action={"analyze_usage": True})

# Navigation
adn_navigation("build_context", url="memory://projects/ai", depth=2)

# Editor integration
adn_editor("notepadpp_edit", note_identifier="Meeting Notes")
```

### Configuration

The DXT package supports the following configuration options:

- **Project Path**: Directory containing your Advanced Memory projects
- **Enable Portmanteau Tools**: Use the new consolidated tools (recommended)
- **Maximum Tools**: Limit the number of tools exposed (for IDE compatibility)

## Troubleshooting

### Common Issues

1. **Server won't start**: Check that the project path is valid and accessible
2. **Tools not appearing**: Ensure portmanteau tools are enabled in configuration
3. **Import/Export failures**: Verify that source paths exist and are readable

### Logs

Check the Claude Desktop logs for detailed error information:
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`

## Support

For issues and feature requests, visit:
- GitHub: https://github.com/advanced-memory-mcp/advanced-memory-mcp
- Documentation: https://docs.advanced-memory-mcp.com

## License

MIT License - see LICENSE file for details.
