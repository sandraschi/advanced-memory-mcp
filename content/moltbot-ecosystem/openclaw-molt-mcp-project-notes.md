# openclaw-molt-mcp Project Notes

**Timestamp**: 2025-02-08
**Status**: Active Development
**Repo**: [github.com/sandraschi/openclaw-molt-mcp](https://github.com/sandraschi/openclaw-molt-mcp)
**Local path**: `D:\Dev\repos\openclaw-molt-mcp`

**Rename (2025-02)**: Renamed from clawd-mcp to openclaw-molt-mcp to avoid clashing with official/closely-related releases by steipete (Peter Steinberger, OpenClaw author).

## Overview

openclaw-molt-mcp is a **FastMCP 2.14+** MCP server that bridges Cursor and Claude Desktop with the OpenClaw (openclaw.ai) and Moltbook (moltbook.com) ecosystem. It enables AI assistants to invoke OpenClaw tools, manage sessions, channels, routing, skills, gateway security, and Moltbook (feed, search, post, comment, upvote, heartbeat).

## Architecture

```
MCP Clients (Cursor, Claude Desktop)
    |
    v
openclaw-molt-mcp (stdio) -- FastMCP 2.14+
    |
    +-- clawd_agent     -> POST /hooks/wake, /tools/invoke
    +-- clawd_sessions  -> sessions_list, sessions_history, sessions_send
    +-- clawd_channels  -> channels: list_channels, get_channel_config, send_message, get_recent_messages
    +-- clawd_routing   -> routing: get_routing_rules, update_routing, test_routing, get_session_by_channel
    +-- clawd_skills    -> Local workspace/skills/, SKILL.md read
    +-- clawd_gateway   -> Tools Invoke probe, openclaw doctor
    +-- clawd_security  -> audit, check_skills, validate_config, recommendations, provision_sandbox
    +-- clawd_moltbook  -> feed, search, post, comment, upvote, heartbeat_run, heartbeat_dm, status
    |
    v
OpenClaw Gateway (HTTP :18789)
```

## Design Decisions

### Portmanteau Tools

Tools consolidated into logical groups: clawd_agent, clawd_sessions, clawd_channels, clawd_routing, clawd_skills, clawd_gateway, clawd_security, clawd_moltbook. Each uses an `operation` parameter. Prevents tool explosion while maintaining full functionality.

### Dialogic Returns

All tools return `{success, message, data?}`. Natural language `message` for conversational replies; structured `data` for processing. Enables both human-readable and machine-parseable responses.

### Monorepo

- `src/clawd_mcp/` — MCP server (Python, FastMCP)
- `webapp/` — React + Tailwind dark dashboard (Startpage, AI/Ollama, Integrations, Clawnews, Skills, Security, Settings)
- `webapp_api/` — FastAPI backend (OpenClaw proxy, Ollama proxy, skills, clawnews)
- `mcpb/` — MCPB packaging, prompts, examples
- `scripts/` — start.ps1, start.bat (kill zombies on 5180/5181, then API + webapp), check.ps1
- `tests/` — pytest, conftest, unit tests (incl. test_channels, test_routing)

### Configuration

- `OPENCLAW_GATEWAY_URL` — default `http://127.0.0.1:18789`
- `OPENCLAW_GATEWAY_TOKEN` — Bearer token when Gateway auth enabled
- `MOLTBOOK_API_KEY` — Moltbook operations
- `OLLAMA_BASE` — webapp API Ollama proxy (default `http://localhost:11434`)
- `CLAWD_MOUNT_VBOX` — set to 1 to mount virtualization-mcp at vbox_*

## Implementation Status

| Tool | Operations | Status |
|------|------------|--------|
| clawd_agent | wake | Done |
| clawd_agent | run_agent, send_message | Stub (Webhook pending) |
| clawd_sessions | list, history, send | Done (Tools Invoke) |
| clawd_channels | list_channels, get_channel_config, send_message, get_recent_messages | Done (Gateway tool: channels) |
| clawd_routing | get_routing_rules, update_routing, test_routing, get_session_by_channel | Done (Gateway tool + config fallback) |
| clawd_skills | list, read | Done (local workspace) |
| clawd_gateway | status, health, doctor | Done |
| clawd_security | audit, check_skills, validate_config, recommendations, provision_sandbox | Done |
| clawd_moltbook | feed, search, post, comment, upvote, heartbeat_run, heartbeat_dm, status | Done |

## Webapp and Start Scripts

- **Webapp**: React dashboard on port 5180; API on 5181. AI page: Ollama status, models, quick prompt, shortcuts, chat (preprompt). Logger modal (client + server logs). Ask OpenClaw, Clawnews, Skills, Security, Settings.
- **Start scripts**: `.\scripts\start.ps1` or `scripts\start.bat` kill processes on 5180/5181, wait 2s, then start API and webapp in two windows. Pause on exit so errors stay visible.

## Security

- **SECURITY.md** (repo root) and **docs/SECURITY_HARDENING.md**: Threats, hardening checklist, Tailscale/tailnet (transitive trust caveat), Traefik patterns, security patterns, clawd_security tool.

## Testing

- conftest: test_settings, mock_context, skills_workspace, empty_skills_workspace
- test_config, test_gateway_client, test_agent, test_gateway_tool, test_sessions, test_skills, test_channels, test_routing, test_server, test_security
- ruff, mypy, pytest via `.\scripts\check.ps1 -All` or `just check`

## References

- relates_to [[openclaw-moltbook-revolutionary-ecosystem]]
- relates_to [[openclaw-detailed-notes]]
- relates_to [[moltbook-detailed-notes]]
- relates_to [[moltbook-heartbeat-architecture]]
- relates_to [[mcp-central-docs Integrations]]
