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
├── shutdown.ps1
└── shutdown.bat
```

## Start

From this **`webapp`** directory:

```powershell
.\start.ps1
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

`{project}` is the current project name/permalink from the projects API.

## Shutdown

Close the backend and Vite windows, or run **`shutdown.ps1`** (or `shutdown.bat`) to free the usual ports.

---

[Repository README](../README.md) · [Usage](../docs/USAGE.md)
