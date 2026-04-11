# Advanced Memory MCP - Installation Guide (SOTA v14.1.0)

## 0. Prerequisites
- **Python 3.12+**
- **uv** (RECOMMENDED for high-performance dependency management)
- **Tesseract OCR** (For PDF processing)
- **Pandoc** (For high-fidelity document exports)

## 1. Fast MCP Installation (via uv)

The most robust way to run Advanced Memory in a production environment is through `uv`.

```bash
# Install as a global tool
uv tool install advanced-memory

# Update to latest industrialized version
uv tool upgrade advanced-memory
```

## 2. Manual Installation (Development)

If you are modifying the source or running from a local checkout:

```bash
# Clone the repository
git clone https://github.com/sandraschi/advanced-memory-mcp
cd advanced-memory-mcp

# Initialize the environment
uv sync
```

## 3. IDE Integration (Claude Desktop / Cursor)

To integrate Advanced Memory as a native brain for your agentic workflow:

### Claude Desktop
Add to `%APPDATA%\Claude\claude_desktop_config.json`:
```json
"mcpServers": {
  "advanced-memory": {
    "command": "uv",
    "args": [
      "--directory", 
      "D:/Dev/repos/advanced-memory-mcp", 
      "run", 
      "advanced-memory", 
      "mcp", 
      "--transport", 
      "stdio"
    ]
  }
}
```

### Cursor
1. Go to **Settings** -> **Features** -> **MCP Servers**.
2. Add a new server named `advanced-memory`.
3. Use the same `command` and `args` as shown for Claude above.

## 4. Webapp

Browser UI (Vite + Python FastAPI). From the repository clone:

```powershell
Set-Location webapp
.\start.ps1
```

Or from `webapp`: `.\start.bat` (runs the same `start.ps1`).

Opens the frontend at **http://localhost:10704/** with the API on **10705**. See [webapp/README.md](../webapp/README.md).

---

[Back to README](../README.md) | [Architecture](ARCHITECTURE.md) | [Standard Compliance](COMPLIANCE_AND_STANDARDS.md)
