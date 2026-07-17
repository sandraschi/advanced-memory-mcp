# advanced-memory-mcp — TODO

**Updated**: 2026-07-17. Ranked roadmap from the "underused flagship" assessment
(vault note `2026-07-17 17:20 advanced-memory-mcp improvement roadmap`).

## P1 — Capture & daily pull

- [x] **Session scribe v1** — scheduled scan of Claude session transcripts
  (Cowork + Claude Code jsonl), auto-drafts timestamped/tagged digest notes into
  vault `inbox/` + copy to aiwatcher `data/inbox/`. Shipped 2026-07-17,
  `scripts/session_scribe.py`, hourly scheduled task.
- [x] **Scribe v2: Fritz integration** — fleet-agent-mcp `scribe_watch` coworker
  flow (2h default): state freshness (RED + email if capture stopped >3h), log
  errors, aiwatcher copy check, vault note on non-green. Shipped 2026-07-17;
  live after fleet-agent service restart.
- [x] **Scribe v2: LLM polish** — per-session bullet summaries via local LLM +
  repo auto-tagging in frontmatter + dedupe via per-session seen-message counts
  (verified: immediate rerun reports no new activity). Shipped 2026-07-17.
- [x] **continue-work MCP prompt** — 'Continue Work' prompt returns latest
  START NOTE + recent note titles + newest scribe digest. Shipped 2026-07-17;
  live after service restart.
- [ ] aiwatcher bundle so scribe digests appear in opencode_briefing output.

## P2 — Health & ops

- [ ] **Version-visible /health** — add version, git_sha, started_at,
  shutting_down to /health per new mcd `standards/HEALTH_ENDPOINT_STANDARD.md`.
  Would have caught today's stale-SYSTEM-instance incident in one curl.
- [x] CI: resolved per mcd GITHUB_ACTIONS_NO_PRIVATE_CI.md — NO GitHub Actions
  on private repos; local gates exist and pass (`just check` = lint + format +
  type-check + test; ruff clean on 2026-07-17 changes).
- [x] Fix: readonly instances skip project-sync reconciliation (was running
  DB UPDATEs against a mode=ro URL at every startup). 2026-07-17.
- [x] NSSM log litter: data/nssm-*.log gitignored + untracked. Rotation itself
  is NSSM AppRotateFiles=1 (already set).
- [x] Port 10732 already registered in WEBAPP_PORTS.md (line 73).
- [x] _version.py created; pyproject + CHANGELOG aligned at 1.10.0 (was 1.8.1
  vs CHANGELOG 1.9.0 drift). 2026-07-17.

## P3 — Skill factory as product

- [ ] **Batch-run the 112 draft scaffolds** — nightly queue over
  make_skill_advanced research_first_create, spec-validated, confidence-tagged;
  archive the culinary noise.
- [ ] **Wire webapp skill pages** — SkillCreator/Studio/Research/Marketplace
  currently make zero API calls; back them with REST wrappers over
  make_skill_advanced ops (management_router pattern).
- [ ] **Export to Claude skills dir** — finished skills land where Claude
  Desktop/Cowork actually load them. Closes the loop.

## P4 — Knowledge

- [ ] **Fleet-wide RAG** — rag_extra_roots -> mcp-central-docs + all repo
  STATUS/TODO/HANDOFF/AGENTS files; research chain "rag" source gains real
  fleet knowledge (4090 fastembed lane exists).
- [ ] **Vault hygiene job** — weekly: merge dupes, auto-OBSOLETE superseded
  notes, fix config/DB project drift (9 of 12 inactive), tag-lint.

## P5 — Cleanup

- [ ] **Dead-code triage** — 95 tool files, 15 registered. Archive beta/ (or
  promote), *_new.py, *.backup, inter_server duplicates; consolidate the two
  web-search implementations (beta multi-provider vs services/research_sources).
- [ ] Generate help from tool registry (help.py is 118KB hand-maintained).
- [ ] Decide fate of adn_skills_research / adn_skills_creator (currently
  unregistered; reachable via make_skill_advanced).

## Done 2026-07-17

- [x] stdio proxy hang root-caused + fixed (restore stdout before proxy run).
- [x] make_skill_advanced + adn_llm registered (15 tools); E2E verified with
  grounded, spec-compliant output on llama3.2:3b in 14.4s.
- [x] build_error_response tolerant signature; adn_skills output normalization;
  dynamic Ollama default model; deterministic frontmatter repair.
- [x] services/research_sources.py (real DDG/arXiv/GitHub); research_driven_skill
  imports fixed to mcp/beta/ (modules existed, paths were wrong).
- [x] Webapp LLM selection persists (GET/PUT /management/llm-config), real
  Ollama load/unload replacing setTimeout fakes.
