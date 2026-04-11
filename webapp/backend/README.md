# Node MCP bridge (optional, developer-only)

This folder contains **Express** scripts used for **stdio MCP ↔ HTTP** experiments (`bridge-server.js`, `startup-service.js`, etc.). They are **not** started by the main webapp flow.

**End users:** start the UI with **`../start.ps1`** only (Python FastAPI + Vite).

**Bridge development:** from `backend/`, run `npm install` and e.g. `npm run start:bridge` or `node bridge-server.js` as needed. Default bridge port is **10705** — do not run at the same time as the Python API on the same port.
