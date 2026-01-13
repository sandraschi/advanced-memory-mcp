# Advanced Memory MCP Standards (SOTA v12.0)
**Version**: 1.1.0b1
**Last Updated**: 2026-01-13
**Status**: SOTA Active

---

## Purpose

This document defines the development and documentation standards for Advanced Memory MCP. Following these standards ensures professional quality, AI-agent compatibility, and long-term maintainability.

## 🏗️ SOTA Compliance Requirements

Advanced Memory MCP achieves **SOTA (State Of The Art)** compliance through:

### **The Three Pillars of SOTA Compliance**

1. **Architecture**: FastMCP 2.14.1+ Cooperative pattern with portmanteau tool consolidation
2. **Behavior**: AI-optimized docstrings and conversational response patterns
3. **Operations**: Complete lifecycle management with persistent SQLite storage

---

## 🧠 Core Principles

### 1. Complete
- Document all 56 tools, not just "main" features
- No TODO placeholders in public documentation
- Cover basic to advanced usage scenarios

### 2. Clear
- Write for target audiences (users/developers/operators)
- Use concrete examples over abstract descriptions
- Progressive disclosure (simple → advanced)

### 3. Correct
- Synchronize docs with code implementation
- Test all examples before committing
- Version compatibility specifications
- Regular documentation freshness audits

### 4. Consistent
- Use standard structure across all components
- Apply same quality standards throughout
- Maintain unified terminology

### 5. Discoverable
- Clear navigation and cross-linking
- Comprehensive table of contents
- Searchable content structure
- Proper heading hierarchy

### 6. Professional
- No rough drafts in public docs (use docs-private/)
- Proper grammar and spelling
- Clean markdown formatting
- Appropriate technical tone

---

## 📋 Config and Log Locations

**Standardized locations for agentic IDE configuration and diagnostic data:**

| IDE | Configuration Folder | MCP Config File | Log Folder |
| --- | --- | --- | --- |
| **Antigravity** | `%USERPROFILE%\.gemini\antigravity` | `mcp_config.json` | `%APPDATA%\Antigravity\logs` |
| **Claude Desktop** | `%APPDATA%\Claude` | `claude_desktop_config.json` | `%APPDATA%\Claude\logs` |
| **Windsurf** | `%APPDATA%\Windsurf` | `mcp_config.json` | `%APPDATA%\Windsurf\logs` |
| **Cursor** | `%APPDATA%\Cursor\User\globalStorage\cursor-storage` | `mcp_config.json` | `%APPDATA%\Cursor\logs` |
| **Zed** | `%APPDATA%\Zed` | `settings.json` | `%LOCALAPPDATA%\Zed\logs` |

> **Note**: `%APPDATA%` resolves to `C:\Users\<user>\AppData\Roaming`

> **Debug Tip**: For startup issues, check Claude Desktop logs (`%APPDATA%\Claude\logs`) and Cursor logs (`%APPDATA%\Cursor\logs`) for stderr output or JSON-RPC handshake errors.

---

## FastMCP 2.14.1+ Compliance Standards

### Tool Documentation Requirements

**Advanced Memory MCP uses FastMCP 2.14.1+ standards for SOTA compliance:**

- ✅ **FastMCP 2.14.1+** minimum version required
- ✅ **Conversational Response Patterns** for rich AI dialogue
- ✅ **Portmanteau Tool Consolidation** to prevent tool explosion
- ✅ **Cooperative Architecture** for complex server interactions

### Docstring Standards

**All tool docstrings MUST follow this structure:**

```python
@mcp.tool
async def tool_name(parameters) -> ResponseType:
    """
    Brief description of tool purpose and behavior.

    This tool performs specific operations using real implementations.
    No mock functionality or placeholders allowed.

    Args:
        parameter_name: Description with type hints and validation rules.
        another_param: Additional parameter documentation.

    Returns:
        FastMCP 2.14.1+ conversational response structure with:
        - success: Operation status
        - operation: What was performed
        - summary: Human-readable description
        - result: Operation-specific data
        - next_steps: Suggested follow-up actions
        - context: Additional contextual information

    Raises:
        SpecificError: When specific conditions fail
        ValidationError: When parameters are invalid

    Examples:
        # Basic usage
        result = await tool_name(param="value")
        # Returns: {"success": True, "summary": "Operation completed", ...}

        # Error handling
        result = await tool_name(invalid_param="bad")
        # Returns: {"success": False, "error": "Invalid parameter", ...}
    """
```

### Portmanteau Tool Patterns

**Advanced Memory MCP uses portmanteau tools to prevent MCP tool explosion:**

```python
# ✅ CORRECT: Single portmanteau tool with operation parameter
@mcp.tool
async def adn_content(
    operation: Literal["write", "read", "edit", "delete"],
    **kwargs
) -> str:
    """Content management portmanteau tool."""
    # Implementation routes to specific operations
```

```python
# ❌ WRONG: Individual tools causing explosion
@mcp.tool
async def write_note(): pass

@mcp.tool
async def read_note(): pass

@mcp.tool
async def edit_note(): pass

@mcp.tool
async def delete_note(): pass
```

---

## Code Quality Standards

### Python Standards

- **Python 3.11+** minimum version
- **Type hints** required for all functions
- **Async/await** patterns for I/O operations
- **Pathlib** for cross-platform file operations
- **Pydantic v2** for data validation

### Linting and Formatting

- **Ruff** for all linting and formatting
- **100 character line length**
- **Black-compatible** import sorting
- **No unused imports or variables**
- **Descriptive variable names**

### Testing Standards

- **Real database operations** (no mocks)
- **File system integration tests**
- **Async operation testing**
- **Cross-platform compatibility**
- **139+ test files** with comprehensive coverage

---

## Documentation Structure

### Repository Documentation

```
docs/
├── README.md              # SOTA-compliant overview
├── STANDARDS.md           # This standards document
├── user-guide/            # User-facing documentation
│   ├── README.md
│   ├── DEEPLINK_INSTALLATION.md
│   └── installation guides...
├── architecture/          # Technical architecture
│   ├── README.md
│   └── component docs...
├── development/           # Contributor documentation
│   ├── README.md
│   └── contribution guides...
├── operations/            # Deployment and operations
│   ├── README.md
│   └── operational docs...
└── testing/               # Testing documentation
    ├── README.md
    └── test guides...
```

### Documentation Freshness

- **Automated audits** monthly
- **Version compatibility** verification
- **Cross-reference validation**
- **Community contribution** guidelines

---

## Development Workflow

### Environment Setup

```bash
# Virtual environment
python -m venv venv
venv\Scripts\activate

# Install with dev dependencies
pip install -e .[dev]

# Run quality checks
ruff check . --fix
ruff format .
mypy src/
```

### Pre-Commit Quality Gates

- **Ruff linting** passes
- **Ruff formatting** applied
- **Type checking** successful
- **Tests pass** (real operations only)
- **Documentation** synchronized

### CI/CD Pipeline

- **Automated testing** on all platforms
- **Security scanning** with bandit/safety
- **Performance monitoring**
- **Documentation freshness** checks

---

## Integration Standards

### MCP Protocol Compliance

- **Stdio transport** for Claude Desktop compatibility
- **JSON-RPC 2.0** message format
- **Tool registration** via FastMCP decorators
- **Error handling** with structured responses

### Claude Desktop Integration

- **Portmanteau tools** for clean UI
- **Conversational responses** for AI dialogue
- **Persistent context** across conversations
- **Real-time synchronization**

### Cross-Platform Compatibility

- **Pathlib.Path** for all file operations
- **Platform detection** where necessary
- **Universal markdown** processing
- **UTF-8 encoding** standards

---

## Security Standards

### Data Protection

- **Local-first architecture** (no cloud dependencies)
- **SQLite encryption** options
- **File permission** management
- **Secure temporary file** handling

### Input Validation

- **Pydantic models** for all inputs
- **Type checking** at runtime
- **Sanitization** of file paths
- **SQL injection prevention**

### Error Handling

- **No sensitive data** in error messages
- **Structured error responses**
- **Graceful degradation**
- **Recovery suggestions**

---

## Performance Standards

### Efficiency Requirements

- **Sub-100ms search** operations
- **Minimal memory footprint** (<50MB)
- **Fast startup time** (<1s)
- **Concurrent operation** support

### Monitoring and Metrics

- **Response time tracking**
- **Memory usage monitoring**
- **Error rate measurement**
- **Performance regression** detection

---

## Maintenance Standards

### Code Health

- **Zero linting errors**
- **Zero type checking errors**
- **Zero unused imports/variables**
- **Regular dependency updates**

### Documentation Health

- **Synchronized with code**
- **Version compatibility**
- **Cross-reference integrity**
- **Freshness audits**

### Testing Health

- **Real operation testing**
- **Cross-platform validation**
- **Integration test coverage**
- **Performance benchmarking**

---

## Compliance Verification

### SOTA Audit Checklist

- [ ] **Architecture**: FastMCP 2.14.1+ Cooperative pattern
- [ ] **Behavior**: AI-optimized docstrings and responses
- [ ] **Operations**: Complete lifecycle management
- [ ] **Documentation**: Complete coverage, clear, correct
- [ ] **Code Quality**: Zero linting errors, full type hints
- [ ] **Testing**: Real operations, comprehensive coverage
- [ ] **Security**: Input validation, secure error handling
- [ ] **Performance**: Efficient operations, monitoring
- [ ] **Maintenance**: Regular updates, health monitoring

### Quality Gates

**Pre-commit:**
- Ruff check passes
- Ruff format applied
- Type checking successful
- Tests pass

**Pre-release:**
- All SOTA requirements met
- Documentation synchronized
- Cross-platform testing completed
- Security audit passed

---

**This standards document ensures Advanced Memory MCP maintains SOTA compliance and professional quality across all development activities.**
