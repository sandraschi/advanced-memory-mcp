# Core Guidance

**Confidence**: 🟢 High
**Last validated**: 2025-11-11

> Every successful MCP server balances Anthropic’s FastMCP contract, disciplined tool design, and a polished release path. Start here to frame your project before diving into deeper modules.

---

## Intake Checklist

| Topic | Questions | Artifacts |
| --- | --- | --- |
| Mission & audience | Which personas will rely on this server (analysts, creative writers, operators)? What “jobs to be done” are you enabling? | Problem statement, user stories |
| Capability boundary | Which operations are essential vs. optional? How will you consolidate them into portmanteau tools? | Capability matrix, operation taxonomy |
| Data sources & security | What external systems or data stores are involved? What auth/secrets model is required? How will you avoid long-running/blocking calls? | Data flow diagrams, secret inventory |
| Platform targets | Which MCP clients must the server support (Claude Desktop, Cursor, Windsurf, custom agents)? Any OS constraints? | Target matrix, acceptance plan |
| Success metrics | How will you measure adoption (daily tool invocations, marketplace installs), reliability (latency, error codes), and quality (structured errors)? | KPI dashboard outline |

Document answers in your architecture brief and keep them visible during implementation.

---

## Principles

1. **Thin `server.py`, rich `tools/` modules** – follow FastMCP 2.13’s modular pattern to keep initialization small and testable.
2. **Portmanteau first** – collapse related operations behind an `operation` parameter to respect tool count limits in Claude Desktop.
3. **AI-friendly errors** – never raise raw exceptions from `@mcp.tool`. Log, structure, and suggest recovery steps.
4. **Automated gatekeeping** – ruff + pytest must pass before publishing. Treat the “ruff pytest dance” as non-negotiable.
5. **Dual distribution paths** – maintain both MCPB (Claude) and npx/npm (general IDEs) installers to maximize reach.
6. **Ecosystem awareness** – track marketplace requirements, update listings, and showcase unique experiences (e.g., “Airbnb itinerary designer”).
7. **Documentation parity** – `.cursorrules`, README, installation docs, and release notes must reflect the reality of the codebase.

---

## Module Map
- Implementation guardrails → [modules/architecture-and-standards.md](modules/architecture-and-standards.md)
- Daily development flow → [modules/development-workflow.md](modules/development-workflow.md)
- Tool consolidation tips → [modules/tooling-strategy.md](modules/tooling-strategy.md)
- Installers & packaging → [modules/distribution-and-installation.md](modules/distribution-and-installation.md)
- Marketplace playbook → [modules/ecosystem-and-publishing.md](modules/ecosystem-and-publishing.md)
- Creative server ideas → [modules/innovation-playbook.md](modules/innovation-playbook.md)
- Release checklist → [modules/release-readiness.md](modules/release-readiness.md)

Revisit this module whenever scope or target platforms change. It anchors the rest of the guidance.***
