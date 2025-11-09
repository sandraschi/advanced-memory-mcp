# Research Checklist

Review quarterly or when Anthropic releases new FastMCP versions, marketplace policies change, or distribution tooling shifts.

## 1. Source Refresh
- [ ] FastMCP repo releases & migration guides (check for >=2.14 updates).  
- [ ] Anthropic documentation (MCP overview, MCPB packaging, developer announcements).  
- [ ] Advanced Memory `.cursorrules` and internal standards.  
- [ ] Marketplace requirements (skillsmp.com, mcp.cool, new directories).  
- [ ] Node/npm ecosystem changes impacting bootstrapper scripts.

## 2. Control Review
- [ ] Verify portmanteau inventory accuracy; update docs if tool counts change.  
- [ ] Ensure error-handling helpers still meet standards.  
- [ ] Re-run tool exercisers to confirm structured errors unaffected by updates.  
- [ ] Confirm CI pipeline covers Windows/macOS/Linux targets.

## 3. Distribution Audit
- [ ] Test MCPB package install/remove paths.  
- [ ] Validate npx/npm scripts on clean Windows + macOS images.  
- [ ] Update config template outputs if client formats change.  
- [ ] Refresh release notes template with new sections if needed.

## 4. Ecosystem Pulse
- [ ] Check marketplace listings for accuracy (versions, screenshots).  
- [ ] Survey community forums for new submission channels or spotlight opportunities.  
- [ ] Capture success stories or user testimonials for marketing.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-11 | Anthropic FastMCP repo (v2.13.0), developer forum updates | Confirmed lifespan/persistence guidance |
| 2025-11-11 | Advanced Memory `.cursorrules` | Synced error/documentation standards |
| 2025-11-11 | skillsmp.com + mcp.cool listings | Validated submission requirements |
| 2025-11-11 | Advanced Memory bootstrap documentation | Captured npx/npm dual-install strategy |
| 2025-11-11 | Cursor documentation on rules (docs.cursor.com) | Confirmed `.cursorrules` behaviors + MCP config expectations |
| 2025-11-11 | Agency Swarm Cursor onboarding guide | Verified project setup steps & best practices for Cursor users |
| 2025-11-11 | Anthropic MCP announcement & community threads | Captured historical context, public reaction, future roadmap signals |
| 2025-11-11 | skillsmp.com landing page statistics | Recorded ~2.3k skill listings; note delta for adoption trend tracking |
| 2025-11-11 | GitHub `awesome-mcp-servers` index | Snapshotted ~180 maintained servers for history module adoption data |

> Tip: use `adn_skills("import_from_github", repository="anthropic/fastmcp")` to scan release notes quickly, and `adn_skills("distill_from_wikipedia", topic="Model Context Protocol")` or `adn_skills("distill_from_arxiv", query="context protocol automation")` to summarize emerging guidance before updating architecture and ecosystem modules.***

