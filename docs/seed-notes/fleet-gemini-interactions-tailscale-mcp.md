---
title: "Fleet memo — Interactions API + Tailscale for remote MCP"
type: note
permalink: fleet/google/gemini-interactions-tailscale-mcp-2026-04
tags:
  - fleet
  - google
  - gemini
  - interactions-api
  - tailscale
  - mcp
date: 2026-04-22
---

# Interactions API

Long-running **agents** (including Deep Research class work) use the **Interactions** resource: create an interaction, then **poll** or **stream** until a terminal status. This is a different surface from ad-hoc `generateContent` chat loops for that agent class.

Always read the **live** `ai.google.dev` Interactions page before locking SDK calls.

# Remote MCP ingress (fleet)

Google’s backend must reach your MCP over **HTTPS**. This fleet already uses **Tailscale** mesh connectivity.

**Prefer Tailscale Funnel** (or another Tailscale-supported HTTPS exposure you approve) instead of Cloudflare Tunnel **unless** compliance or DNS already mandates Cloudflare.

## Ops checklist

1. Confirm **streamable HTTP** vs legacy **SSE-only** expectations for remote MCP on the date of deployment.  
2. Pilot **one** read-only MCP; measure timeouts and cold start before attaching many servers.  
3. Treat Funnel as **public ingress**: authenticate tools, rate-limit, and avoid logging secrets.

Tailscale Funnel docs: https://tailscale.com/kb/1223/funnel  
