# Advanced Memory Webapp

React-based web interface for the Advanced Memory MCP (ADN). Runs a Vite frontend and a Python FastAPI backend, with optional Node.js bridge/startup services.

## Architecture

| Service        | Port  | Description                                      |
|----------------|-------|--------------------------------------------------|
| **Frontend**   | 10704 | Vite + React + Tailwind                         |
| **Backend**    | 10705 | Python FastAPI (`advanced_memory.server:app` via `start.ps1`) |

Ports use the 10700–10800 band by convention. Edit `start.ps1` to change them.

## Directory structure

```
webapp/
├── frontend/       # React + Vite + Tailwind (package.json here)
├── backend/        # Optional Node bridge/startup services
├── start.ps1       # Recommended launcher (Python backend + Vite)
├── start.bat       # Alternative (Node bridge + startup + Vite)
├── shutdown.ps1
└── shutdown.bat
```

## Quick start (PowerShell)

From the **webapp** directory:

```powershell
.\start.ps1
```

This will:

1. Kill any process using ports 10704 and 10705.
2. Run `npm install` in `frontend/` if `node_modules` is missing.
3. Start the **Python backend** in a new window (from repo root): `uv run uvicorn advanced_memory.server:app --host 127.0.0.1 --port 10705`.
4. Wait up to ~12s and check that the backend is listening on 10705; print "Backend is up" or a warning.
5. Start the **Vite dev server** from `frontend/` on port 10704.

Open **http://localhost:10704/** in your browser.

### Requirements

- **Node.js** (for frontend build and dev server).
- **uv** and **Python 3.12+** (for backend). Backend must run from the **repository root** so `advanced_memory` is importable.

## Alternative: `start.bat` (Node MCP bridge — not the Python API)

**Use `start.ps1` for normal development.** It runs the **real app API**: Python **FastAPI** on **10705** plus Vite on **10704**.

`start.bat` does **not** start Python or uvicorn. It starts three separate things:

| What | Port | Role |
| :--- | :--- | :--- |
| **Vite** | 10704 | Same dev frontend as `start.ps1`. |
| **`bridge-server.js`** | 10705 | **Node (Express)** “MCP bridge”: exposes HTTP endpoints that talk to **stdio MCP** processes (spawn/manage MCP servers from the browser side). This is **not** `advanced_memory.server:app`. |
| **`startup-service.js`** | 10733 | Small **control service** with `POST /start-bridge` and `POST /stop-bridge` to launch or stop the bridge process. |

So **10705 means two different servers** depending on which script you used: FastAPI (`.ps1`) vs Node bridge (`.bat`). The React UI’s REST features (semantic search, note content, etc.) expect the **Python** backend — use **`start.ps1`** for that.

Use **`start.bat`** only when you are developing or testing the **Node MCP bridge** / startup control path, not as a drop-in replacement for the Python web API.

## Configuration

Ports are set at the top of `start.ps1`:

```powershell
$WebPort = 10704
$BackendPort = 10705
```

## Troubleshooting

- **Backend "not responding"**: Check the backend PowerShell window for uvicorn errors. Ensure you run from repo root (start.ps1 does this for the backend).
- **npm errors in webapp root**: `start.ps1` runs npm only inside `frontend/`; there is no `package.json` in `webapp/` itself.
- **Tailwind/PostCSS**: Arbitrary values with commas (e.g. `rgba(a,b,c,d)`) in `@apply` must use underscores in Tailwind (e.g. `rgba(a_b_c_d)`). See `frontend/src/styles/main.css` for examples.

## Tests page

The webapp can run the project test suite (pytest) from the **Tests** page. To enable it, start the backend with:

```powershell
$env:ENABLE_WEBAPP_TESTS = "1"
uv run uvicorn advanced_memory.server:app --host 127.0.0.1 --port 10705
```

Or in `start.ps1`, set the env var before starting the backend. The endpoint is disabled by default (returns 403) so it is not run in production.

## API endpoints used by the frontend

- **Semantic search (Deep Search page)**  
  `POST /api/v1/{project}/search/semantic` — body: `{ "query": "...", "limit": 20 }`. Returns `{ "chunks": [ { "entity_id", "permalink", "title", "snippet", "chunk_text", "score" }, ... ] }` from the RAG (LanceDB) pipeline.

- **Note content (full note for chunk click)**  
  `GET /api/v1/{project}/knowledge/entities/{permalink}/content` — returns `{ "title", "permalink", "content" }` for the full note body. Used when the user clicks a semantic search chunk to open the full note in a modal.

Project in the path is the project name/permalink (e.g. default or the current project from the projects API).

## Shutdown

- Close the backend window and the terminal where Vite is running, or run `shutdown.ps1` / `shutdown.bat` if configured.
