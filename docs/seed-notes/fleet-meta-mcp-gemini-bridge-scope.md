---
title: "Fleet memo — MetaMCP vs Gemini bridge (where code lives)"
type: note
permalink: fleet/mcp/meta-mcp-vs-gemini-bridge-2026-04
tags:
  - fleet
  - meta-mcp
  - gemini
  - architecture
date: 2026-04-22
---

# Decision (2026-04-22)

**Use MetaMCP (`meta_mcp`)** for fleet **orchestration**: catalog, diagnostics, config snippets, Tool Lab calls into **already registered** MCP servers, scaffolding, and heartbeat-style operations.

**Do not** merge **Gemini Interactions / Deep Research client** orchestration (long polls, streaming parsers, Google SDK version pins) into MetaMCP core by default.

# Rationale

MetaMCP and Google’s hosted research agent have **different failure modes**, **credential** models, and **release cadences**. Keeping Google API client code in a **thin separate bridge** (new small repo or `contrib` scripts) limits coupling and security review scope.

# Optional integration pattern

A bridge can **read** MetaMCP’s exported catalog or REST to discover **which** MCP base URLs to register in an interaction’s tool list—coordination without monolith.

# References

- MCP Central ADN: `mcp-central-docs/adn-notes/ADN-2026-04-22-005-meta-mcp-vs-gemini-bridge.md`  
- MetaMCP hub: `mcp-central-docs/projects/meta_mcp/README.md`  
- Gemini hub: `mcp-central-docs/integrations/gemini-deep-research-interactions-2026.md`
