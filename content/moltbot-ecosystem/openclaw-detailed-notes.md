# OpenClaw Detailed Notes

**Timestamp**: 2025-02-01
**Status**: Production / ~132k GitHub stars
**Sources**: openclaw.ai, docs.openclaw.ai, docs.clawd.bot, GitHub openclaw/openclaw

## What Is OpenClaw?

OpenClaw (formerly ClawdBot, Moltbot) is a personal AI assistant platform. "The AI that actually does things." Inbox management, email sending, calendar control, flight check-in—all from WhatsApp, Telegram, Slack, Discord, or any chat app.

## Core Components

### Gateway

- **WebSocket** control plane on port 18789 (loopback-first)
- **HTTP APIs**:
  - `POST /tools/invoke` — invoke any Gateway tool directly; body: `{tool, action?, args, sessionKey}`
  - `POST /hooks/wake` — trigger wake/heartbeat; body: `{text, mode}`
  - `POST /hooks/agent` — run agent turn; optional channel delivery
- **OpenAI Chat Completions** proxy for LLM calls
- **Auth**: `gateway.auth.mode` (token, password), `gateway.auth.token`, `OPENCLAW_GATEWAY_TOKEN` env

### Channels

| Channel | Library/Protocol |
|---------|------------------|
| WhatsApp | Baileys |
| Telegram | grammY |
| Slack, Discord | Native APIs |
| Signal, iMessage | BlueBubbles, etc. |
| WebChat | Built-in |
| Google Chat, MS Teams, Matrix, Zalo | Supported |

### Pi Agent

RPC-mode coding agent from [badlogic/pi-mono](https://github.com/badlogic/pi-mono). Tool streaming, block streaming. Used by OpenClaw for agentic coding and task execution.

### Tools

- **Browser**: CDP (Chrome DevTools Protocol)
- **Canvas / A2UI**: UI automation
- **bash**: Shell execution
- **cron**: Scheduled jobs
- **webhooks**: Inbound triggers
- **Gmail Pub/Sub**: Email events
- **sessions**: Agent-to-agent (`sessions_list`, `sessions_history`, `sessions_send`)

### Skills

AgentSkills-compatible SKILL.md folders. YAML frontmatter + Markdown body. **ClawHub** (clawhub.com) is the public registry—565+ skills. Install: `clawhub install <slug>`. Skills extend agent capabilities (e.g., Moltbook skill for social participation).

## Install

**Preferred clone location**: `D:\Dev\repos\external\openclaw` (move from `D:\Dev\repos\openclaw`). Reclone for fresh release.

```bash
# Standalone clone (external folder)
cd D:\Dev\repos\external
git -c core.longpaths=true clone --depth 1 https://github.com/openclaw/openclaw.git openclaw
# Security assessment before build. Then: cd openclaw; pnpm install; pnpm build
```

Or: `curl -fsSL https://openclaw.ai/install.sh | bash` or `npm i -g openclaw`

## Config Paths

- Config: `~/.openclaw/openclaw.json`
- Workspace: `~/.openclaw/workspace`
- Skills: `~/.openclaw/workspace/skills/`

## Naming Evolution

- **ClawdBot** — Original name
- **Moltbot** — Rebrand (trademark concerns; "molt" = lobster shedding shell)
- **OpenClaw** — Current primary (openclaw.ai, GitHub openclaw/openclaw)

## Public Reaction

- "Open source built a better version of Siri while Apple slept" — Hesamation
- "First true personal assistant" — MacStories
- "AI as teammate, not tool" — lycfyi
- "It's running my company" — therno
- "The lobster is gonna take over the world" — alex_here_now
- Karpathy: "Love oracle and Claw"

## Relation to openclaw-molt-mcp

openclaw-molt-mcp invokes OpenClaw via Tools Invoke API and Webhooks. Gateway must be running at OPENCLAW_GATEWAY_URL. Token required when auth enabled.

## References

- [openclaw.ai](https://openclaw.ai)
- [docs.openclaw.ai](https://docs.openclaw.ai)
- [docs.clawd.bot](https://docs.clawd.bot)
- [clawhub.com](https://clawhub.com)
- [Tools Invoke API](https://docs.clawd.bot/gateway/tools-invoke-http-api)
- [Webhooks](https://docs.clawd.bot/automation/webhook)

- relates_to [[openclaw-moltbook-revolutionary-ecosystem]]
- relates_to [[openclaw-molt-mcp-project-notes]]
- relates_to [[moltbook-detailed-notes]]
- relates_to [[ClawHub]]
