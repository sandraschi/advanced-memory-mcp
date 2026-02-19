# ADN Webapp

The unified web interface for the Advanced Memory MCP (ADN). This directory contains both the frontend interface and the bridge services required to orchestrate the research grid.

## Architecture Overview

The webapp is composed of three primary services orchestrated via a central startup script:

| Service | Port | Description |
| :--- | :--- | :--- |
| **Frontend** | 10704 | Vite-based React interface (the "Neural Interface") |
| **Bridge** | 10705 | Node.js Express server relaying requests to the Python MCP server |
| **Startup Service** | 10733 | Management API for service orchestration and health monitoring |

## Directory Structure

```text
webapp/
├── frontend/          # React + Vite + Tailwind source
├── backend/           # Node.js Express + Startup services
├── start.ps1          # Unified PowerShell launcher (Recommended)
├── start.bat          # Simple CMD launcher
├── shutdown.ps1       # Graceful shutdown script
└── shutdown.bat       # CMD shutdown script
```

## Quick Start

The webapp requires Node.js, and will automatically install dependencies on first run.

### Windows (Recommended)
Double-click `start.bat` or run:
```powershell
.\start.ps1
```

This will:
1. Clear existing processes on ports 10704, 10705, and 10733.
2. Install `node_modules` for both frontend and backend if missing.
3. Start the Bridge, Startup Service, and Frontend in parallel.
4. Open the interface at [http://localhost:10704](http://localhost:10704).

## Configuration

Port allocations are standardized for SOTA compliance (10700-10800 range). To adjust ports, modify `start.ps1`:

```powershell
$WebPort = 10704
$BridgePort = 10705
$StartupPort = 10733
```

## Component Details

### Frontend
A high-performance "Neural Interface" built with React and Tailwind CSS. It features a dark-themed, glassmorphic design with real-time research tracking and skill generation capabilities.

### Backend Bridge
The bridge server (`bridge-server.js`) acts as a secure intermediary between the web interface and the Python-based Advanced Memory MCP server, handling JSON-RPC communication over HTTP.

### Startup Service
The `startup-service.js` monitors the health of the underlying MCP platform and provides the webapp with real-time status updates on model availability and research providers.

---
*Zero Runts Policy Enforced — High-Cap/Zero-Crash Architecture*
