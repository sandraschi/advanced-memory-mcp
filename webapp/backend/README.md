# ADN Webapp Backend

Node.js-based service layer for the ADN Webapp. This component manages the bridge between the frontend neural interface and the Python-based MCP research engine.

## Services

### 1. Bridge Server (`bridge-server.js`)
- **Port**: 10705
- **Function**: Acts as an HTTP-to-JSON-RPC adapter.
- **Protocol**: Accepts standard REST requests and translates them into MCP-compatible JSON-RPC payloads.

### 2. Startup Service (`startup-service.js`)
- **Port**: 10733
- **Function**: Monitors MCP server status and handles resource discovery.
- **Reporting**: Provides health telemetry and model availability data.

### 3. Auto-Start Service (`auto-start-service.js`)
- **Function**: Background watcher for automatic MCP server recovery.

## Development

Install dependencies:
```bash
npm install
```

Start the bridge:
```bash
npm run start:bridge
```

## Logs
Logs are maintained in `bridge_logs.json` for persistent debugging and audit trails.
