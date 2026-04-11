# Usage

Set up the app first: [Installation](INSTALLATION.md). Then use either **(1) an MCP client** or **(2) the webapp**. Section **(3)** is optional depth.

---

## 1. MCP clients (Cursor, Claude Desktop, etc.)

The server process is started by your client; you chat normally and the assistant calls tools for you.

### Stdio (typical for local IDEs)

Configure the client to run:

`uv --directory <repo> run advanced-memory mcp --transport stdio`

Replace `<repo>` with the path where you cloned this repository.

**Claude Desktop** — edit `%APPDATA%\Claude\claude_desktop_config.json` and add under `mcpServers`:

```json
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
```

Change the `--directory` value to your checkout. Restart Claude Desktop after saving.

**Cursor** — Settings → MCP: add a server with the same `command` and `args` (or equivalent if you use `uv tool install` and the tool is on your PATH).

**In chat:** ask in plain language, for example: search the vault for a topic, add or update a note, import a file, or run a research query. You do not type raw JSON; the assistant uses the tool list the server exposes.

**Windows:** only one stdio instance should run at a time by default. If startup complains that another instance is running, close the other app or see `ADVANCED_MEMORY_STDIN_SINGLE_INSTANCE` in the MCP command implementation.

### HTTP (`streamable-http` or `sse`)

For a network listener instead of stdio:

```
uv run advanced-memory mcp --transport streamable-http --host 0.0.0.0 --port 8000 --path /mcp
```

Use `advanced-memory mcp --help` for `host`, `port`, and `path`. Point your client at that URL if it supports remote MCP.

### `--agentic`

Adding `--agentic` turns on a compact “code mode” tool surface for automation. For day‑to‑day chat, leave it **off** so you get the full tool set.

---

## 2. Webapp

Browser UI: Vite frontend + FastAPI backend. **Details:** [webapp/README.md](../webapp/README.md).

**Quick start** — from the `webapp` folder in this repo:

```powershell
.\start.ps1
```

Then open **http://localhost:10704/** . Frontend is port **10704**, API **10705** (defaults in `start.ps1`).

---

## 3. Advanced / related docs

| Topic | Where |
| :---- | :---- |
| RAG, agentic flag, MCP sampling | [AI-FEATURES.md](AI-FEATURES.md) |
| How pieces fit together | [ARCHITECTURE.md](ARCHITECTURE.md) |
| More than one server / sync | [FLEET.md](FLEET.md) |
| Standards / audit notes | [COMPLIANCE_AND_STANDARDS.md](COMPLIANCE_AND_STANDARDS.md) |
| Lint, tests, `just` | [DEVELOPMENT.md](DEVELOPMENT.md) |

**Practical habits:** use clear titles and tags in notes; ingest documents before expecting RAG to find them; name projects consistently if your tools are project‑scoped.

---

[README](../README.md) · [Installation](INSTALLATION.md)
