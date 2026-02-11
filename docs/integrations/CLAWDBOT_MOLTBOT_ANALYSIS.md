# ClawdBot / Moltbot — Analysis, Public Reaction, Use & Extend

**Timestamp**: 2025-01-28
**Repo**: https://github.com/moltbot/moltbot
**Author**: Peter Steinberger (Vienna-based; PSPDFKit founder/exit to Insight Partners)

---

## 1. What It Is

**Moltbot** (formerly ClawdBot) is an open-source, local-first personal AI assistant. You run a **Gateway** (WebSocket control plane on `127.0.0.1:18789`) that owns all messaging surfaces and talks to a **Pi agent** (RPC) with tools. Data stays on your hardware; you bring your own LLM (Anthropic, OpenAI, local, etc.).

- **Stack**: Node 22+, TypeScript (ESM), pnpm, Vitest. CLI: `moltbot`; `clawdbot` remains a compatibility shim.
- **Channels**: WhatsApp (Baileys), Telegram (grammY), Slack, Discord, Google Chat, Signal, iMessage, BlueBubbles, MS Teams, Matrix, Zalo, WebChat, etc.
- **Apps**: Optional macOS menu bar app, iOS/Android nodes (Canvas, Voice Wake, Talk Mode, camera, screen record).
- **Tools**: Browser control (CDP), Canvas/A2UI, bash, cron, webhooks, Gmail Pub/Sub, skills (ClawdHub), sessions (agent-to-agent).

---

## 2. Architecture (Summary)

- Single **Gateway** daemon per host; one Baileys/WhatsApp session.
- Clients (macOS app, CLI, web UI) and **nodes** (macOS/iOS/Android) connect over **WebSocket**. Nodes use `role: node` and expose device-local commands (`canvas.*`, `camera.*`, `system.run`, etc.).
- **Pairing**: device-based; new devices require approval. Local loopback can auto-approve.
- **Protocol**: JSON over WS; first frame must be `connect`. Requests `req`/`res`; server-push `event`. Idempotency keys for `send`/`agent`.
- **Remote**: Tailscale Serve/Funnel or SSH tunnel; gateway stays loopback.

See [Architecture](https://docs.molt.bot/concepts/architecture), [Gateway protocol](https://docs.molt.bot/gateway/protocol).

---

## 3. Public Reaction

### Praise and adoption

- **Trending Topics (EU)**: "Open source built a better version of Siri while Apple slept"; "first true personal assistant"; comparisons to early ChatGPT. Use cases: biz management, health/travel automation, dev workflows.
- **Mashable**: "Viral" among early adopters; "cult following"; Silicon Valley devs sharing Mac Mini setups and memes. Delivers where "high-profile agentic AI implementations failed"; remembers context, email/calendar/docs access, proactive actions.
- **GitHub**: ~75k stars, ~9.6k forks (as of fetch). Active Discord (8.9k+), ClawdHub skills registry.

### Vienna / Austrian angle

- Peter Steinberger (Austrian, Vienna-based); PSPDFKit exit; strong dev community rep. Covered by Trending Topics and German-language tech press as Austrian success.

### Security and caveats

- **Full system access**: Default main session has shell, files, browser. "Running an AI agent with shell access is *spicy*" (docs). No "perfectly secure" setup.
- **Sandboxing**: For groups/external channels, use `agents.defaults.sandbox.mode: "non-main"` (Docker per-session). DM pairing for unknown senders.
- **Bitdefender (Jan 2026)**: Hundreds of internet-facing Moltbot/ClawdBot control panels were exposed (localhost trust + reverse proxy misconfig). Led to config/API keys/conversation history leaks and, in some cases, unauthenticated execution. **Takeaway**: Never expose the gateway UI/WS to the internet without auth (e.g. Tailscale + password, or strict ACLs).
- **Feb 2026 PII exfiltration incident**: Major vulnerability and mass PII exfiltration (new hotness, breach as cold water bucket). Run security assessment (e.g. Opus-assisted audit) before building/running. Clone-only first; build only after assessment passes.

---

## 4. How We Could Use It

| Use case | How |
|----------|-----|
| **Personal assistant over existing chats** | Gateway + WhatsApp/Telegram/Slack/Discord; same inbox, no new app. |
| **Dev / automation** | Bash, browser, cron, webhooks; skills for custom workflows. |
| **Multi-device** | macOS app + iOS/Android nodes for voice, Canvas, camera. |
| **Local-first / privacy** | All orchestration and tooling local; only LLM calls go to provider (or stay local). |
| **MCP / tools ecosystem** | Gateway has tools. Our MCP bridge: [openclaw-molt-mcp](https://github.com/sandraschi/openclaw-molt-mcp) (renamed from clawd-mcp to avoid clash with steipete releases). |

---

## 5. How We Could Extend It

### Integration

- **MCP bridge**: Expose Moltbot's Pi/tools to MCP clients (Cursor, etc.) or consume MCP servers as Moltbot skills/tools.
- **Advanced Memory / knowledge**: Use `~/clawd` workspace + skills; inject custom prompts (e.g. `AGENTS.md`, `TOOLS.md`). Could add a "knowledge" tool that calls our RAG/graph.
- **Games-app / backends**: Webhooks or cron from Moltbot to our services (e.g. stockfish, game APIs); or CLI `moltbot agent --message "..."` for game-related queries.

### New channels / extensions

- **Extensions**: Live under `extensions/` (e.g. msteams, matrix, voice-call). We could add a custom channel (e.g. internal comms, games lobby) following existing patterns.
- **Skills**: ClawdHub + workspace skills. Add skills for domain-specific workflows (e.g. "chess opening lookup", "JLPT practice") that call our backends.

### Ops and security

- **Hardening**: Always use Tailscale/password auth when exposing UI; run `moltbot doctor`; sandbox non-main sessions.
- **Monitoring**: Use health/heartbeat over WS; optionally log to our observability stack.

### Platform

- **Windows**: Official support via WSL2. We could improve native Windows UX (e.g. install path, daemon) if we run there.
- **Docker**: Use official Docker setup for gateway + sandbox; align with our compose workflows if we host it.

---

## 6. Clone and Run (Local)

**Security-first workflow**: Clone only first. Run Opus-assisted security assessment before building. Build only after assessment passes.

Clone targets: `D:\Dev\repos\external\moltbot`, `D:\Dev\repos\external\openclaw`. Standalone (no dependency on this repo):

```powershell
New-Item -ItemType Directory -Force -Path "D:\Dev\repos\external"
cd D:\Dev\repos\external
git -c core.longpaths=true clone --depth 1 https://github.com/moltbot/moltbot.git moltbot
git -c core.longpaths=true clone --depth 1 https://github.com/openclaw/openclaw.git openclaw
# Security assessment before build. Then (moltbot):
cd moltbot
pnpm install
pnpm ui:build
pnpm build
moltbot onboard --install-daemon
moltbot gateway --port 18789 --verbose
```

**Upstream**: [Getting started](https://docs.molt.bot/start/getting-started), [Wizard](https://docs.molt.bot/start/wizard), [Security](https://docs.molt.bot/gateway/security).

---

## 7. References

- [moltbot/moltbot](https://github.com/moltbot/moltbot)
- [docs.molt.bot](https://docs.molt.bot)
- [Architecture](https://docs.molt.bot/concepts/architecture)
- [Trending Topics — Austrian Developer ClawdBot](https://trendingtopics.eu/austrian-developer-creates-clawdbot-an-open-source-ai-assistant-that-runs-locally)
- [Mashable — ClawdBot what it is, how to try](https://mashable.com/article/what-is-clawdbot-how-to-try)
- [Bitdefender — Moltbot security alert](https://bitdefender.com/en-us/blog/hotforsecurity/moltbot-security-alert-exposed-clawdbot-control-panels-risk-credential-leaks-and-account-takeovers)
