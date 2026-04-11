# Advanced Memory MCP - Fleet Integration Guide

## The Alsergrund Bridge Federation

This server acts as a **Registry Node** and **Memory Hub** within the Alsergrund Bridge fleet.

### Registration Process

Every industrialized server in the fleet is indexed in the central `mcp-central-docs` registry.

1. **Local Configuration**:
   Ensure `pyproject.toml` and `justfile` are synchronized to the latest version.
2. **Registry Pulse**:
   The `adn_status("fleet")` tool scans reachable MCP servers on local ports (10700-10800) and attempts to verify their SOTA compliance.
3. **Registry Update**:
   When this server is updated (e.g., to v1.7.0), the changes must be propagated to:
   - `mcp-central-docs/projects/advanced-memory-mcp/STATUS.md`
   - `mcp-central-docs/projects/FLEET_INDEX.md`

### Federated Operations

- **Cross-Node Search**: Users can query global knowledge that spans across multiple specialized MCP servers.
- **Heartbeat Monitoring**: The Alsergrund Bridge dashboard monitors the uptime and versioning of this node in real-time.

## Standards Compliance

> [!IMPORTANT]
> To remain active in the fleet, this node must maintain **SOTA v14.1.0** compliance. Failure to pass the `just check` quality gate will result in automatic de-indexing from the fleet dashboard.

---

[Back to README](../README.md) | [Compliance Standards](COMPLIANCE_AND_STANDARDS.md) | [Architecture](ARCHITECTURE.md)
