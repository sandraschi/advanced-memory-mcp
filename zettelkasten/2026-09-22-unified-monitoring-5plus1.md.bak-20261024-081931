# Unified Monitoring Standardized (5+1 Contract)

**Date:** 2026-09-22
**Decision:** Standardize fleet observability on `unified-*`; observation is a contract, not a sixth shipped layer.
**Status:** Implemented for aiwatcher + devices; docs updated and committed.

---

## Decision

Fleet repos ship five layers. Observation becomes "+1": a **contract** each
repo honors (GET `/metrics` in Prometheus text + structured logs) plus a
**central stack** the fleet provides (unified Prometheus/Grafana/Loki).
Per-repo Prometheus/Grafana/Loki triples are legacy. New repos onboard to
unified; existing per-project stacks (deepfang-*, avatarmcp-*, tailscale-loki,
mywienerlinien) stay - each belongs to its repo's own five-layer stack
(verified via compose labels), so killing them would break those projects.

Documented in `sandraschi/WHY_FLEET.md` section 3c and
`mcp-central-docs/monitoring/MCP_MONITORING_STANDARDS.md` (Fleet direction
section + corrected wiring). Commits: sandraschi `807f4c4`, mcd `2678d003`,
mcd monitoring `7f2baac3`.

## Implemented

- **aiwatcher scraped:** job `aiwatcher-mcp` added to
  `mcp-central-docs/monitoring/prometheus/prometheus.yml`
  (`host.docker.internal:10946/metrics`, 30s). aiwatcher already emitted
  hand-rolled Prometheus text with zero deps. Hot-reload via
  `POST :12001/-/reload` (200). Verified `aiwatcher_up=1` flowing.
- **Dashboards added** to `unified-grafana` (`:12000`, admin/admin):
  AIWatcher (uid `aiwatcher-mcp`, 8 panels over the 8 `aiwatcher_*` gauges),
  Tapo Camera Monitoring (`tapo-camera`), Tapo PTZ Controls (`tapo-ptz`).
  Tapo JSONs copied from `devices-mcp/grafana/` and modernized from legacy
  `${DS_PROMETHEUS}` refs to `{uid: prometheus}` with stable UIDs.
  Grafana file watcher MISSES new-file creates - restart `unified-grafana`
  after adding JSON (7 to 10 dashboards after restart).
- devices-mcp was already scraped (`:10717`) with `devices-mcp.json` present.

## Facts

- unified-prometheus `:12001`, unified-grafana `:12000`, unified-loki.
  Prometheus config + Grafana provisioning/dashboards bind-mounted from
  `mcp-central-docs/monitoring/`. Datasource UIDs: `prometheus`, `loki`.
  Dashboard schema v39.
- aiwatcher backend `:10946`, devices backend `:10717`. Template for
  zero-dep metrics: `aiwatcher-mcp/src/aiwatcher_mcp/metrics.py`.
- Onboarding a repo = scrape block + reload + optional dashboard JSON.
  Full pre-commit/mypy/biome gate cleanup was needed to land related work
  (mypy hook pointed at project venv, Logging.tsx reindented); see myai
  session notes for the gate war stories.
