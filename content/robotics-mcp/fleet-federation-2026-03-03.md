# ADN Note: Robotics Fleet Federation & Hub Extraction

| Meta | Value |
| :--- | :--- |
| **Project** | `robotics-mcp` / `yahboom-mcp` |
| **Event** | Architectural Federation (Phase 4) |
| **Date** | 2026-03-03 |
| **Tags** | `#robotics`, `#mcp`, `#federation`, `#architecture`, `#yahboom-mcp` |

## 📝 Summary

Successfully extracted robot-specific documentation and logic from the monolithic `robotics-mcp` hub into a federated fleet architecture. This transition establishes `robotics-mcp` as a coordination and dashboard layer (the Hub), while `yahboom-mcp` (and the upcoming `dreame-mcp`) act as specialized execution nodes.

## 🏗️ Architectural Changes

1. **Monolith to Fleet**: The central `robotics-mcp` central hub is now responsible for fleet-wide status, shared spatial data orchestration, and cross-robot workflows.
2. **Local Documentation**: Each robot server now maintains its own `docs/` folder containing fleet-specific integration guides and local status.
3. **Registry-First Discovery**: Peer discovery is now driven by `mcp-central-docs/operations/fleet-registry.json`.

## 🚀 Accomplishments

- Migrated `README.md`, `ARCHITECTURE.md`, `STATUS.md`, and `INTEGRATION_GUIDE.md` to `yahboom-mcp/docs/`.
- Updated `yahboom-mcp` root documentation with a Phase 4-6 roadmap.
- Created `yahboom-mcp/PRD.md` for the fleet expansion.
- Registered `yahboom-mcp` and `dreame-mcp` in the Global Fleet Registry.
- Redefined `mcp-central-docs/projects/robotics-mcp/` as the Unified Fleet Hub.

## ⚠️ Future Tech Debt
- Extraction of Dreame-specific Python logic from `robotics-mcp` into a separate `dreame-mcp` repository.
- Implementation of the `robotics_agentic_workflow` tool for multi-server sampling.
