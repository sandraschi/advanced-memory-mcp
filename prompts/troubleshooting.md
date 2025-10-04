# Advanced Memory MCP - Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Installation and Setup Issues

#### **Problem**: Package won't install in Claude Desktop
**Symptoms**: 
- Extension fails to install
- Error messages about invalid manifest
- Package validation fails

**Solutions**:
1. **Verify package integrity**:
   ```bash
   mcpb verify advanced-memory-mcp.mcpb
   ```

2. **Check Claude Desktop version**:
   - Ensure Claude Desktop is updated to latest version
   - MCPB support requires recent versions

3. **Re-download package**:
   - Package may be corrupted during download
   - Try downloading again

#### **Problem**: Dependencies fail to install
**Symptoms**:
- Server won't start
- Python import errors
- Missing package errors

**Solutions**:
1. **Check Python version**:
   ```python
   # Ensure Python 3.12+ is available
   adn_navigation("status")
   ```

2. **Verify uv availability**:
   - MCPB uses `uv` for dependency management
   - Ensure `uv` is installed and accessible

3. **Check network connectivity**:
   - Dependencies are downloaded during installation
   - Ensure internet connection is stable

### Configuration Issues

#### **Problem**: Tools not appearing in Claude Desktop
**Symptoms**:
- No Advanced Memory tools visible
- Empty tool list
- Server starts but no tools available

**Solutions**:
1. **Check portmanteau tools setting**:
   ```python
   # Verify in Claude Desktop settings
   # Enable "Portmanteau Tools" option
   ```

2. **Check maximum tools limit**:
   ```python
   # Ensure limit is set appropriately
   # Default: 50 tools
   # Portmanteau tools: 8 tools total
   ```

3. **Verify project path**:
   ```python
   # Check if project path is valid
   adn_navigation("status")
   ```

#### **Problem**: Project path not working
**Symptoms**:
- "Project not found" errors
- Empty project list
- Cannot create notes

**Solutions**:
1. **Verify path exists**:
   ```python
   # Check if directory exists and is accessible
   adn_project("list")
   ```

2. **Check permissions**:
   - Ensure read/write access to project directory
   - On Windows: Run as administrator if needed

3. **Use absolute paths**:
   ```python
   # Use full path instead of relative path
   adn_project("create", project_name="test", project_path="C:/Users/me/Documents/notes")
   ```

### Content Management Issues

#### **Problem**: Cannot create notes
**Symptoms**:
- "Permission denied" errors
- "Directory not found" errors
- Notes not appearing

**Solutions**:
1. **Check folder permissions**:
   ```python
   # Ensure write access to project directory
   adn_navigation("status")
   ```

2. **Verify folder structure**:
   ```python
   # Check if target folder exists
   adn_navigation("list_directory", dir_name="/")
   ```

3. **Use valid identifiers**:
   ```python
   # Avoid special characters in identifiers
   adn_content("write", identifier="Valid-Note-Name", content="Content", folder="test")
   ```

#### **Problem**: Notes not saving
**Symptoms**:
- Content appears to save but disappears
- "File locked" errors
- Inconsistent behavior

**Solutions**:
1. **Check file locks**:
   - Close any editors that might have files open
   - Restart Claude Desktop if needed

2. **Verify disk space**:
   - Ensure sufficient disk space available
   - Clean up temporary files

3. **Check sync status**:
   ```python
   # Verify sync is working
   adn_navigation("sync_status")
   ```

### Search Issues

#### **Problem**: Search not returning results
**Symptoms**:
- Empty search results
- "No matches found" for known content
- Search appears to hang

**Solutions**:
1. **Check sync status**:
   ```python
   # Ensure content is indexed
   adn_navigation("sync_status")
   ```

2. **Verify search parameters**:
   ```python
   # Try different search types
   adn_search("notes", query="test", search_type="full_text")
   adn_search("notes", query="test", search_type="tags")
   ```

3. **Check content exists**:
   ```python
   # Verify content is actually there
   adn_navigation("list_directory", dir_name="/")
   ```

#### **Problem**: Search is slow
**Symptoms**:
- Long response times
- Timeout errors
- Poor performance

**Solutions**:
1. **Use pagination**:
   ```python
   # Limit results for better performance
   adn_search("notes", query="test", page=1, page_size=10)
   ```

2. **Optimize search queries**:
   ```python
   # Use specific search types when possible
   adn_search("notes", query="tag:urgent", search_type="tags")
   ```

3. **Check system resources**:
   ```python
   # Monitor system performance
   adn_navigation("status", level="detailed")
   ```

### Import/Export Issues

#### **Problem**: Import fails
**Symptoms**:
- "Source not found" errors
- "Invalid format" errors
- Import appears to hang

**Solutions**:
1. **Verify source path**:
   ```python
   # Ensure source file/directory exists
   adn_import("obsidian", source_path="/path/to/vault", destination_folder="imported")
   ```

2. **Check file permissions**:
   - Ensure read access to source files
   - Check if files are locked by other applications

3. **Validate source format**:
   ```python
   # Ensure source is in expected format
   # Obsidian: Directory of .md files
   # Joplin: Directory with .md and .json files
   # Notion: .zip file or directory
   # Evernote: .enex file
   ```

#### **Problem**: Export fails
**Symptoms**:
- "Permission denied" errors
- "Invalid format" errors
- Export appears to hang

**Solutions**:
1. **Check output directory**:
   ```python
   # Ensure write access to output directory
   adn_export("pandoc", export_path="/path/to/output.pdf", format_type="pdf")
   ```

2. **Verify format support**:
   ```python
   # Check if requested format is supported
   # Pandoc: pdf, html, docx, odt, rtf, tex, epub
   # Docsify: html website
   # HTML: standalone html files
   ```

3. **Check dependencies**:
   ```python
   # Some exports require external tools
   # Pandoc exports need Pandoc installed
   # PDF exports may need LaTeX
   ```

### Performance Issues

#### **Problem**: Slow response times
**Symptoms**:
- Long delays for simple operations
- Timeout errors
- Poor overall performance

**Solutions**:
1. **Check system resources**:
   ```python
   # Monitor CPU, memory, disk usage
   adn_navigation("status", level="detailed")
   ```

2. **Optimize operations**:
   ```python
   # Use pagination for large result sets
   adn_search("notes", query="test", page=1, page_size=10)
   
   # Limit directory depth
   adn_navigation("list_directory", dir_name="/", depth=1)
   ```

3. **Check sync status**:
   ```python
   # Ensure sync is not blocking operations
   adn_navigation("sync_status")
   ```

#### **Problem**: High memory usage
**Symptoms**:
- System becomes slow
- Memory warnings
- Application crashes

**Solutions**:
1. **Limit result sizes**:
   ```python
   # Use pagination and limits
   adn_search("notes", query="test", page=1, page_size=5)
   ```

2. **Check for memory leaks**:
   ```python
   # Monitor memory usage over time
   adn_navigation("status", level="detailed")
   ```

3. **Restart if needed**:
   - Close and restart Claude Desktop
   - Clear temporary files if necessary

### Database Issues

#### **Problem**: Database errors
**Symptoms**:
- "Database locked" errors
- "Table not found" errors
- Inconsistent data

**Solutions**:
1. **Check database integrity**:
   ```python
   # Verify database is not corrupted
   adn_navigation("status")
   ```

2. **Check file locks**:
   - Ensure no other processes are accessing database
   - Close any editors with files open

3. **Reinitialize if needed**:
   ```python
   # In extreme cases, may need to reinitialize
   # This will rebuild the database from files
   ```

### Network and Connectivity Issues

#### **Problem**: Cannot connect to external services
**Symptoms**:
- Import/export to external services fails
- "Connection timeout" errors
- Network-related errors

**Solutions**:
1. **Check internet connectivity**:
   - Ensure stable internet connection
   - Test with other applications

2. **Check firewall settings**:
   - Ensure Claude Desktop can access network
   - Check corporate firewall restrictions

3. **Verify service availability**:
   - Ensure external services are accessible
   - Check service status pages

## 🔧 Diagnostic Commands

### System Health Check
```python
# Complete system status
status = adn_navigation("status", level="detailed", focus="health")

# Sync status
sync_status = adn_navigation("sync_status")

# Project information
current_project = adn_project("get_current")

# List all projects
all_projects = adn_project("list")
```

### Content Validation
```python
# Validate content quality
validation = adn_knowledge("validate_content", checks=["broken_links", "formatting"])

# Check for duplicates
duplicates = adn_knowledge("find_duplicates", limit=50)

# Analyze tags
tag_analytics = adn_knowledge("tag_analytics", action={"analyze_usage": True})
```

### Performance Monitoring
```python
# Recent activity
recent = adn_navigation("recent_activity", timeframe="today")

# Directory listing
contents = adn_navigation("list_directory", dir_name="/", depth=1)

# Search test
search_test = adn_search("notes", query="test", page=1, page_size=5)
```

## 📋 Getting Help

### Log Files
Check Claude Desktop logs for detailed error information:
- **macOS**: `~/Library/Logs/Claude/`
- **Windows**: `%APPDATA%\Claude\logs\`

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the full guide for detailed information
- **Examples**: Review usage examples for common patterns

### Reporting Issues
When reporting issues, include:
1. **Error messages**: Exact error text
2. **Steps to reproduce**: What you did before the error
3. **System information**: OS, Claude Desktop version
4. **Log files**: Relevant log entries
5. **Configuration**: Project path, tool settings

### Self-Help Checklist
Before seeking help, try:
- [ ] Restart Claude Desktop
- [ ] Check system status: `adn_navigation("status")`
- [ ] Verify sync status: `adn_navigation("sync_status")`
- [ ] Check project configuration: `adn_project("get_current")`
- [ ] Validate content: `adn_knowledge("validate_content")`
- [ ] Review log files for error details
- [ ] Test with simple operations first
- [ ] Check disk space and permissions

---

*Most issues can be resolved by checking system status and ensuring proper configuration. When in doubt, start with the diagnostic commands above.*
