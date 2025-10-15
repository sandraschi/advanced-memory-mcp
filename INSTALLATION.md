# Installation Guide
## Complete Setup for Advanced Memory

This guide covers all installation methods for Advanced Memory across different platforms and use cases.

## 🎯 Quick Reference

| Platform | Method | Command |
|----------|--------|---------|
| **All Platforms** | Pip (Recommended) | `pip install advanced-memory` |
| **Mac** | Homebrew | `brew tap basicmachines-co/advanced-memory && brew install advanced-memory` |
| **Windows/Linux** | Pip + Virtual Env | `python -m venv venv && venv\Scripts\activate && pip install advanced-memory` |
| **Development** | From Source | `git clone https://github.com/basicmachines-co/advanced-memory-mcp.git && pip install -e .` |
| **Docker** | Container | `docker run -v $(pwd):/vault basicmachines-co/advanced-memory` |

---

## 🚀 Standard Installation

### Option 1: Pip (Recommended)

**Requirements**: Python 3.12+

```bash
# Install from PyPI
pip install advanced-memory

# Verify installation
advanced-memory --version
```

**Upgrade**:
```bash
pip install --upgrade advanced-memory
```

### Option 2: Homebrew (Mac)

```bash
# Add the tap
brew tap basicmachines-co/advanced-memory

# Install
brew install advanced-memory

# Upgrade
brew upgrade advanced-memory
```

### Option 3: uv (Fast Python Package Manager)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Advanced Memory
uv tool install advanced-memory

# Run commands
uvx advanced-memory --version
```

---

## 🖥️ Platform-Specific Setup

### macOS

**1. Install Python 3.12+**
```bash
# Using Homebrew
brew install python@3.12

# Or download from python.org
```

**2. Install Advanced Memory**
```bash
pip install advanced-memory
```

**3. Configure Claude Desktop**
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows

**1. Install Python 3.12+**
- Download from [python.org](https://python.org/downloads/)
- Check "Add Python to PATH" during installation
- Or use `winget`: `winget install Python.Python.3.12`

**2. Install Advanced Memory**
```bash
# Open Command Prompt or PowerShell as Administrator
pip install advanced-memory
```

**3. Configure Claude Desktop**
Location: `%APPDATA%\Claude\claude_desktop_config.json`

### Linux (Ubuntu/Debian)

**1. Install Python 3.12+**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# Or use deadsnakes PPA for latest Python
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
```

**2. Install Advanced Memory**
```bash
pip install advanced-memory
```

**3. Configure Claude Desktop**
Location: `~/.config/Claude/claude_desktop_config.json`

### Linux (Arch/Fedora)

**Arch Linux**:
```bash
sudo pacman -S python python-pip
pip install advanced-memory
```

**Fedora**:
```bash
sudo dnf install python3 python3-pip
pip install advanced-memory
```

---

## 🐳 Docker Installation

### Quick Start with Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  advanced-memory:
    image: basicmachines-co/advanced-memory:latest
    volumes:
      - ./my-vault:/vault
      - ./config:/config
    ports:
      - "8000:8000"
    environment:
      - ADVANCED_MEMORY_VAULT_PATH=/vault
```

```bash
# Start the service
docker-compose up -d

# Check logs
docker-compose logs advanced-memory
```

### Manual Docker Run

```bash
# Run with volume mount
docker run -d \
  --name advanced-memory \
  -v $(pwd)/my-vault:/vault \
  -p 8000:8000 \
  basicmachines-co/advanced-memory:latest
```

### Docker for Development

```bash
# Clone and build
git clone https://github.com/basicmachines-co/advanced-memory-mcp.git
cd advanced-memory-mcp

# Build development image
docker build -t advanced-memory-dev .

# Run with hot reload
docker run -v $(pwd):/app -p 8000:8000 advanced-memory-dev
```

---

## 🛠️ Development Installation

### From Source (Recommended for Contributors)

```bash
# Clone the repository
git clone https://github.com/basicmachines-co/advanced-memory-mcp.git
cd advanced-memory-mcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify
pytest
```

### Development Dependencies

```bash
# Install all development tools
pip install -e ".[dev]"

# Or install individually
pip install ruff mypy pyright pytest pre-commit
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 🧪 Testing Your Installation

### Basic Test

```bash
# Check version
advanced-memory --version

# Test MCP server
advanced-memory mcp --help

# Test CLI tools
advanced-memory tools basic-memory-guide
```

### Comprehensive Test

```bash
# Run the test suite
just test

# Or manually
pytest tests/ -v

# Type checking
just type-check

# Linting
just lint
```

### Integration Test with Claude

1. Configure Claude Desktop (see below)
2. Restart Claude Desktop
3. Ask Claude: "Create a test note about installation verification"
4. Claude should respond that it created the note

---

## 🔧 Claude Desktop Configuration

### Automatic Setup (Smithery)

The easiest way to configure Claude Desktop:

```bash
# Install via Smithery
npx @modelcontextprotocol/inspector npx -y @smithery/cli@latest install @basicmachines-co/advanced-memory --client claude
```

### Manual Configuration

**1. Find your config file:**

| Platform | Path |
|----------|------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

**2. Edit the file** (create if it doesn't exist):

```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "advanced-memory",
      "args": ["mcp"]
    }
  }
}
```

**3. Alternative configurations:**

**With uv**:
```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "uvx",
      "args": ["advanced-memory", "mcp"]
    }
  }
}
```

**From source**:
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

**4. Restart Claude Desktop**

---

## 🎛️ Cursor IDE Configuration

Cursor supports MCP servers natively. Add to your Cursor settings:

```json
{
  "mcp": {
    "servers": {
      "advanced-memory": {
        "command": "advanced-memory",
        "args": ["mcp"]
      }
    }
  }
}
```

---

## 🌐 Other MCP Clients

### VS Code with MCP

```json
// .vscode/settings.json
{
  "mcp": {
    "servers": {
      "advanced-memory": {
        "command": "advanced-memory",
        "args": ["mcp"]
      }
    }
  }
}
```

### Glama.ai

Use the Glama badge to install:

[![Install on Glama](https://glama.ai/mcp/servers/o90kttu9ym/badge)](https://glama.ai/mcp/servers/o90kttu9ym)

---

## 🔍 Troubleshooting

### "Command not found" Errors

**Problem**: `advanced-memory` command not found after installation

**Solutions**:
```bash
# Check if installed
pip list | grep advanced-memory

# Try with python -m
python -m advanced_memory --version

# Check PATH
which advanced-memory

# Reinstall
pip uninstall advanced-memory
pip install advanced-memory
```

### Permission Errors

**Problem**: Permission denied during installation

**Solutions**:
```bash
# Use --user flag
pip install --user advanced-memory

# Or use sudo (not recommended)
sudo pip install advanced-memory

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install advanced-memory
```

### Claude Desktop Won't Connect

**Problem**: Claude can't connect to Advanced Memory

**Solutions**:

1. **Check config file syntax**:
   ```bash
   # Validate JSON
   python -c "import json; json.load(open('path/to/claude_desktop_config.json'))"
   ```

2. **Restart Claude Desktop completely** (quit and reopen)

3. **Check logs**:
   ```bash
   advanced-memory mcp  # Run manually to see errors
   ```

4. **Verify installation**:
   ```bash
   advanced-memory --version
   ```

### Import Errors

**Problem**: `ModuleNotFoundError` or missing dependencies

**Solutions**:
```bash
# Install with all dependencies
pip install -e ".[dev]"

# Upgrade pip
pip install --upgrade pip

# Clear pip cache
pip cache purge
```

### Database Issues

**Problem**: Database errors on first run

**Solutions**:
```bash
# Reset database
rm -rf ~/.advanced-memory/
advanced-memory sync

# Or specify custom path
export ADVANCED_MEMORY_DB_PATH=/custom/path/db.sqlite
```

---

## 📊 Version Management

### Stable Releases

```bash
# Install latest stable
pip install advanced-memory

# Check version
advanced-memory --version
```

### Beta/Pre-releases

```bash
# Install beta versions
pip install advanced-memory --pre

# Force latest dev build
pip install advanced-memory --pre --force-reinstall
```

### Development Versions

Development versions are automatically published with versions like `0.12.4.dev26+468a22f`

---

## 🔄 Updating

### Automatic Updates

```bash
# With pip
pip install --upgrade advanced-memory

# With Homebrew
brew upgrade advanced-memory

# With uv
uv tool upgrade advanced-memory
```

### Manual Updates

```bash
# From source
cd advanced-memory-mcp
git pull
pip install -e .
```

---

## 🏗️ Building from Source

### Complete Development Setup

```bash
# Clone
git clone https://github.com/basicmachines-co/advanced-memory-mcp.git
cd advanced-memory-mcp

# Setup environment
python -m venv venv
source venv/bin/activate

# Install with all extras
pip install -e ".[dev,test,docs]"

# Run full test suite
just check
```

### Build Distribution

```bash
# Build wheel and source distribution
python -m build

# Upload to PyPI (maintainers only)
twine upload dist/*
```

---

## 📱 Mobile and Remote Access

### Web Interface (Future)

Advanced Memory will include a web interface for mobile access. For now:

- Use file sync services (Dropbox, Google Drive, etc.)
- Access via SSH on remote machines
- Use VS Code remote extensions

### Remote Server Setup

```bash
# On server
pip install advanced-memory
advanced-memory sync --watch

# On client (configure to connect to server)
# Use SSH tunneling or direct network access
```

---

## 🆘 Getting Help

### Common Issues

1. **"No such file or directory"** → Check installation path
2. **"Permission denied"** → Use virtual environment or --user flag
3. **"Module not found"** → Reinstall with dependencies
4. **"Connection refused"** → Restart Claude Desktop

### Support Resources

- **Discord**: [Join our community](https://discord.gg/tyvKNccgqN)
- **GitHub Issues**: [Report bugs](https://github.com/basicmachines-co/advanced-memory-mcp/issues)
- **Discussions**: [Ask questions](https://github.com/basicmachines-co/advanced-memory-mcp/discussions)
- **Documentation**: [Complete docs](docs/)

### Debug Information

When reporting issues, include:

```bash
# System info
python --version
pip --version
advanced-memory --version

# Installation details
pip show advanced-memory

# Configuration
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

**Ready to build your knowledge empire?** Head to [Quick Start](QUICKSTART.md) to get running in 5 minutes!

*Installation verified - you're all set! 🚀*
