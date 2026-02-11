# OpenClaw Security Vulnerability Scan ADN 2026-02-06

**Timestamp**: 2026-02-06
**Type**: adn
**Scope**: Security audit, vulnerability findings, mitigation plan

---

## Summary

- [adn] Opus 4.6-assisted security audit of OpenClaw (D:\Dev\repos\external\openclaw). 3 HIGH, 6 MEDIUM, 2 LOW findings. P0 mitigations: remove default --dangerously-skip-permissions, add auth rate limiting, harden dangerouslyDisableDeviceAuth. Docs created in openclaw repo, mcp-central-docs, and ADN. #adn #security

- [decision] Feb 2026: Major PII exfiltration incident (new hotness, breach as cold water bucket). **Security-first workflow**: Clone only first; run Opus-assisted assessment before build. Do not build until assessment passes. #security #workflow

## Decisions

- [decision] Vulnerability scan docs live in three places: openclaw/docs/security/, mcp-central-docs/docs/projects/openclaw/, advanced-memory content (this ADN). OpenClaw repo is canonical for full report and mitigation plan. #documentation

- [decision] P0 (1-2 weeks): Remove --dangerously-skip-permissions from CLI backend defaults; add gateway auth rate limiting; require env override for dangerouslyDisableDeviceAuth. #security #mitigation

- [decision] P1 (1-2 months): Token expiry/rotation, Chrome extension auth, path traversal fix, WebSocket size limits, Docker Compose defaults. #security #roadmap

## Implemented

- [implementation] openclaw/docs/security/vulnerability-scan-2026-02.md - Full audit report with findings by severity. #implementation

- [implementation] openclaw/docs/security/mitigation-plan-2026-02.md - P0/P1/P2/P3 remediation roadmap with acceptance criteria. #implementation

- [implementation] mcp-central-docs/docs/projects/openclaw/STATUS.md - OpenClaw project status with security summary. #implementation

- [implementation] mcp-central-docs/docs/projects/openclaw/SECURITY_VULN_SCAN_2026_02.md - Condensed scan summary for central docs. #implementation

- [implementation] openclaw/docs/gateway/security/index.md - Added links to vuln scan and mitigation plan. #implementation

## Findings (Condensed)

| Severity | Count | Key |
|----------|-------|-----|
| HIGH | 3 | Default skip-permissions, auth bypass flags, no rate limiting |
| MEDIUM | 6 | Static tokens, unauthed Chrome ext, path traversal, JSON DoS |
| LOW | 2 | Env blocklist gaps, no CSRF |

Positive: timingSafeEqual, SSRF guard, DOMPurify, exec approval system, security audit tool, no hardcoded secrets.

---

- relates_to [[openclaw-detailed-notes]]
- relates_to [[openclaw-moltbook-revolutionary-ecosystem]]
- relates_to [[mcp-central-docs Integrations]]
