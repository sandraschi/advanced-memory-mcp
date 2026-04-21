# Advanced Memory Webapp

React (Vite) frontend and Python **FastAPI** backend. **Start the webapp with `start.ps1` only** (from this `webapp` folder).

## Architecture

| Service     | Port  | Description |
| :---------- | :---- | :---------- |
| **Frontend** | 10704 | Vite + React + Tailwind |
| **Backend**  | 10705 | Python FastAPI (`advanced_memory.server:app`) |

Ports use the 10700–10800 band by convention. Edit `start.ps1` to change them.

## Directory structure

```
webapp/
├── frontend/       # React + Vite + Tailwind (package.json here)
├── backend/        # Optional Node MCP bridge (see backend/README.md) — not used by start.ps1
├── start.ps1       # Launcher: Python backend + Vite
├── start.bat       # Thin wrapper: runs start.ps1 (double-click / cmd)
├── shutdown.ps1
└── shutdown.bat
```

## Start

From this **`webapp`** directory, either:

```powershell
.\start.ps1
```

Or (same behavior — calls `start.ps1`):

```bat
start.bat
```

This will:

1. Free ports **10704** and **10705** if something is listening.
2. Run `npm install` in `frontend/` if `node_modules` is missing.
3. Start the **Python backend** in a new window: `uv run uvicorn advanced_memory.server:app --host 127.0.0.1 --port 10705` (working directory is the **repository root** so `advanced_memory` imports correctly).
4. Wait and check that the backend is listening on **10705**.
5. Start the **Vite** dev server on **10704**.

Open **http://localhost:10704/** in your browser.

### Requirements

- **Node.js** (frontend dev server and build).
- **uv** and **Python 3.12+** (backend).

## Configuration

The Vite dev server proxies **`/api/*`** to **`http://127.0.0.1:10705`**, so the frontend can use the same origin (`/api/v1/...`) instead of hard-coding `localhost:10705` (this also works when you open the UI via another host on the LAN). Override with **`VITE_API_URL`** if the API is elsewhere (for example in Docker).

Ports at the top of `start.ps1`:

```powershell
$WebPort = 10704
$BackendPort = 10705
```

## Troubleshooting

- **Backend "not responding"**: Check the backend PowerShell window for uvicorn errors.
- **npm errors in webapp root**: `start.ps1` runs npm only inside `frontend/`; there is no `package.json` in `webapp/` itself.
- **Tailwind/PostCSS**: Arbitrary values with commas in `@apply` must use underscores — see `frontend/src/styles/main.css`.

## Tests page

To enable pytest from the **Tests** page, start the backend with `ENABLE_WEBAPP_TESTS=1` (see comments in `start.ps1` or run uvicorn with that env var). Disabled by default (403).

## API endpoints used by the frontend

- **Semantic search (Deep Search page)**  
  `POST /api/v1/{project}/search/semantic` — body: `{ "query": "...", "limit": 20 }`. Returns chunks from the LanceDB pipeline.

- **Note content (full note for chunk click)**  
  `GET /api/v1/{project}/knowledge/entities/{permalink}/content` — full note body for the modal.

- **Extra RAG folders (Vault sync page, 1.8.1+)**  
  `GET` / `PUT /api/v1/management/rag-extra-roots` — read or replace the list of absolute server paths (`rag_extra_roots` in config).  
  `POST /api/v1/management/rag-extra-roots/validate` — check which paths exist as directories on the API host.

`{project}` is the current project name/permalink from the projects API.

**Where vectors live:** LanceDB data for Advanced Memory is stored in the **`vectors`** folder **next to** the app SQLite file (`memory.db`), typically under `%USERPROFILE%\.advanced-memory\`. It is separate from other projects’ RAG stores (for example another repo’s own LanceDB default).

## Shutdown

Close the backend and Vite windows, or run **`shutdown.ps1`** (or `shutdown.bat`) to free the usual ports.

---

[Repository README](../README.md) · [Usage](../docs/USAGE.md)
