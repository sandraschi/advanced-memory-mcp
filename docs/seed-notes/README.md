# Seed notes (import into Advanced Memory)

Markdown files in this folder are **canonical text** meant to become **vault notes** or **RAG chunks** on your Advanced Memory host. They are **not** auto-imported from git; pick one path below.

## Option A — `notes:write` or `inbox_capture` (MCP)

From Cursor or Claude with Advanced Memory connected: ask the assistant to create a note using the **title** and **body** from each file (or paste the file).

## Option B — Copy into a vault project

Copy `.md` files into your vault’s `inbox` or `fleet` folder and run a normal sync / index rebuild.

## Option C — `rag_extra_roots` (semantic search only)

If the machine running the Advanced Memory API can read this repo path, add the **absolute** path to `docs/seed-notes` under **`rag_extra_roots`** in `%USERPROFILE%\.advanced-memory\config.json`, then **Rebuild search index** (webapp **Vault sync** or management API). Notes become searchable extras across projects; they do not replace per-project vault files unless you also copy them.

## Contents (Gemini / Google / fleet — 2026-04)

| File | Topic |
|------|--------|
| [fleet-gemini-deep-research-announcement-2026-04.md](fleet-gemini-deep-research-announcement-2026-04.md) | April 2026 two-agent Deep Research + MCP + charts (primary narrative). |
| [fleet-gemini-interactions-tailscale-mcp.md](fleet-gemini-interactions-tailscale-mcp.md) | Interactions API role + Tailscale Funnel for remote MCP ingress. |
| [fleet-meta-mcp-gemini-bridge-scope.md](fleet-meta-mcp-gemini-bridge-scope.md) | Why MetaMCP stays orchestration and a thin bridge handles Google API clients. |

**Central hub (longer analysis):** `mcp-central-docs/integrations/gemini-deep-research-interactions-2026.md`
