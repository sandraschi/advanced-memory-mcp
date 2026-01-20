# Advanced Memory MCP Server - AI Development Context

You are working on **Advanced Memory**, a local-first knowledge management system built on the Model Context Protocol (MCP). This project enables bidirectional communication between LLMs and markdown files, creating a personal knowledge graph.

## 🎯 Project Identity
- **Name**: Advanced Memory MCP Server
- **Purpose**: Personal knowledge graph management via MCP protocol
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Architecture**: FastMCP 2.14.3 portmanteau pattern
- **Storage**: SQLite for indexing, files as source of truth

## 🏗️ Architecture Overview
```
FastAPI Server → MCP Tools → Knowledge Graph → Markdown Files
```

### Core Components:
1. **MCP Server** (`src/advanced_memory/mcp/`): Portmanteau tools for content management
2. **Knowledge Graph** (`src/advanced_memory/`): Entity-observation-relation model
3. **FastAPI Backend** (`src/advanced_memory/api/`): REST endpoints
4. **CLI Interface** (`src/advanced_memory/cli/`): Command-line tools

## 🔧 Development Standards

### ✅ **Portmanteau Pattern**
- **Consolidate** related operations into single tools
- **Prevent tool explosion** (e.g., 7 content ops → 1 tool)
- **Follow FastMCP 2.14.3** standards
- **Maintain full functionality** while improving discoverability

### 📋 **Code Patterns**
```python
# Portmanteau tool with multiple operations
@mcp.tool
async def adn_content(operation: str, **kwargs) -> str:
    """Content management portmanteau tool."""
    if operation == "write":
        return await _write_note(**kwargs)
    elif operation == "read":
        return await _read_note(**kwargs)
    # ... more operations
```

### 🧪 **Testing Requirements**
- Real SQLite database (no mocks)
- File system operations with temp directories
- Async testing with pytest
- Cross-platform compatibility

## 🚫 **Anti-Patterns to Avoid**

### **Mock-Heavy Testing** ❌
```python
# WRONG: Mock database in tests
@pytest.fixture
def mock_db():
    return MagicMock()
```

### **Platform Assumptions** ❌
```python
# WRONG: Windows-only paths
path = "C:\\hardcoded\\path"
```

### **Single-Operation Tools** ❌
```python
# WRONG: One tool per operation
@mcp.tool
async def write_note(): pass

@mcp.tool
async def read_note(): pass
```

## 🎯 **Tool Categories**

### 📝 **Content Management** (1 portmanteau tool)
- Write, read, edit, delete notes
- Tag management and search
- File operations and metadata

### 🔍 **Search & Navigation** (1 portmanteau tool)
- Full-text search across knowledge base
- Knowledge graph traversal
- Recent activity and backlinks

### 📊 **Knowledge Operations** (1 portmanteau tool)
- Bulk operations and maintenance
- LLM-powered analysis and enhancement
- Research orchestration

### 🔧 **Project Management** (1 portmanteau tool)
- Multi-project context switching
- Project lifecycle management
- System status and health

## 🛠️ **Development Workflow**

### **Environment Setup**
1. **Create venv**: `python -m venv venv`
2. **Install dependencies**: `pip install -e .[dev]`
3. **Run tests**: `python -m pytest`

### **Code Standards**
- **Ruff formatting**: 100 character line length
- **Type hints**: Required for all functions
- **Async patterns**: Preferred for I/O operations
- **Pathlib**: Cross-platform file operations

### **Testing Strategy**
- **Real database**: Use SQLite with temp files
- **Integration tests**: Full system testing
- **Async testing**: Proper event loop handling
- **Cross-platform**: Test on multiple OSes

## 🚀 **Key Features**

### **Knowledge Graph**
- Entity-observation-relation model
- Wiki-style linking `[[Entity]]`
- Semantic search and relationships

### **MCP Integration**
- Portmanteau tool consolidation
- Conversational response patterns
- Error recovery and suggestions

### **Cross-Platform**
- Pathlib for file operations
- Platform-agnostic configuration
- Universal markdown processing

## 📦 **Packaging & Deployment**

### **Build Process**
1. Clean virtual environment
2. Install dependencies
3. Run comprehensive tests
4. Package for distribution

### **Installation Methods**
1. **PyPI**: `pip install advanced-memory`
2. **Source**: `pip install -e .`
3. **Docker**: Container deployment

## 🐛 **Common Issues**

### **Database Issues**
- Verify SQLite installation
- Check file permissions
- Review migration status

### **MCP Server Issues**
- Check FastMCP version compatibility
- Verify tool registration
- Review configuration files

### **Cross-Platform Problems**
- Use pathlib.Path consistently
- Test file operations on target platforms
- Avoid hardcoded paths

## 🎯 **Quality Standards**

### **Code Quality**
- **Portmanteau pattern** implementation
- **Real database operations** in tests
- **Cross-platform compatibility**
- **Comprehensive documentation**

### **Documentation**
- **Tool docstrings** with operation details
- **Architecture documentation**
- **API specifications**
- **Migration guides**

### **Testing**
- **Real database tests** (no mocks)
- **File system integration**
- **Async operation testing**
- **Cross-platform validation**

---
**Remember: Advanced Memory uses portmanteau tools to prevent MCP tool explosion while maintaining full functionality. Always prioritize cross-platform compatibility and real database operations over mocks.**
