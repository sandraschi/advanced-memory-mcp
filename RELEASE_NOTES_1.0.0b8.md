# Release Notes - v1.0.0b8

**Release Date**: 2025-11-08  
**Focus**: Windows Bootstrapper & Install Refinements

## Highlights

- ✅ Added a Windows-friendly `npx` bootstrapper for scenarios where `.mcpb` packages cannot be installed (Cursor, Windsurf, manual Claude Desktop setups).  
- ✅ Optional config generation (`--generate-configs`) outputs ready-to-use MCP config templates for Cursor, Windsurf, and Claude Desktop—portmanteau-only mode preconfigured.  
- ✅ Installation docs (README + INSTALLATION.md + Quick Start) now feature a dedicated \"Option 3: Windows Bootstrap\" section with prerequisites, usage examples, and expected outputs.  
- ✅ Bootstrapper integrates dependency checks, repo cloning/updating, `uv sync`, `uv run ruff check .`, and optional flagship skill validation.  
- ✅ Prepared for npm publication—script doubles as the future CLI entry-point once a package name is reserved.

## Usage Snapshot

```powershell
# Default target: D:\Dev\repos (falls back to C:\Dev\repos)
npx --yes github:sandraschi/advanced-memory-mcp/scripts/bootstrap/windows

# Custom target + config templates
npx --yes github:sandraschi/advanced-memory-mcp/scripts/bootstrap/windows -- --target C:\Work\mcp --generate-configs
```

**Outputs**:
- Cloned repository path  
- Optional `bootstrap-configs/` folder with JSON templates for Cursor/Windsurf/Claude Desktop  
- Console summary of next steps (where to drop configs, env hints, etc.)

## Quality

- `uv run ruff check` ✅  
- Bootstrapper help and config emission manually verified ✅  
- Repository backups executed post-update ✅

## Upgrade

```powershell
pip install --upgrade advanced-memory-mcp==1.0.0b8
```

No configuration changes required for existing MCP installations. Apply the bootstrapper only if you need a Windows-native setup without `.mcpb` support.

---

**Version**: 1.0.0b8  
**Python**: 3.11+  
**Status**: Beta (polishing installation story for general release)  

