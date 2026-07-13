# Phase 1 Triage & Progress — Advanced Memory 2.0

**Spec:** ARCHITECTURE_2_0.md Phase 1 (rev 2026-07-07, HEAD-audited numbers)
**This file is the resumption point after any context reset.** Update it after every step.

---

## Step status

| Step | Status | Notes |
|------|--------|-------|
| 0 — Surface decision | ⛔ **PENDING — BLOCKING** | Option (a) namespace surface + compact profile is the spec default. Sandra to confirm. Steps 2–3 cannot start before this. |
| 1 — Extract content domain to services/ | ✅ **DONE 2026-07-09** | See inventory below. Pure moves, verbatim; pytest not yet run. |
| 2 — Rewire tool entry points to services | ⬜ | Blocked on Step 0 |
| 3 — Mount namespace apps | ⬜ | Blocked on Step 0 (or delete them, under option b) |
| 4 — Triage 31 adn_* + ~20 standalone files | ⬜ | Checklist section below, to be filled during triage |
| 5 — Delete content_manager.py + legacy | ⬜ | |
| 6 — SKILL.md rewrite + external adn_ sweep (mcd + IDE configs) | ⬜ | |

## Step 1 inventory (complete)

`services/content/` — all sixteen `_*_operation` functions moved out of content_manager.py:

| Module | Functions | Source lines (content_manager.py) | By |
|--------|-----------|-----------------------------------|----|
| `crud.py` | write_note, read_note, get_latest_identifier, read_latest_note, view_note, view_note_rendered, edit_note, move_note, delete_note | 1106–1486, 1697–1707, 1988–2006 | earlier session |
| `capture.py` | quick_capture, daily_note | 1894–1987 | earlier session |
| `tagging.py` | edit_tags, extract_content_tags, suggest_tags | 1487–1696, 1708–1893, 2007–2103 | 2026-07-09 |
| `ai_enrich.py` | summarize_note, enhance_note, generate_note | 2104–2408 | 2026-07-09 |
| `__init__.py` | package exports for all four modules | — | 2026-07-09 (was missing — package didn't import) |

**Verified during extraction:**
- `call_get`, `call_put`, `build_success_response`, `build_error_response` all exist in shared `mcp/tools/utils.py` (lines 74/150/649/660) with signatures identical to content_manager's local copies — the shared imports in all four service modules resolve.
- capture.py's previously dangling `from ...content.tagging import extract_content_tags` now resolves.
- `generate_note` (ex `_generate_operation`) calls `write_note` from crud instead of `_write_operation` — same signature, only adaptation in the whole extraction.
- Preserved quirk (documented in module headers): `suggest_tags`/`summarize_note` annotated `-> dict` but return markdown strings on success paths — verbatim behavior; normalize post-extraction, not now.

**Not yet done for Step 1:** `uv run pytest` (the spec's referee) — content_manager.py still contains the original functions, so nothing is broken yet regardless; services are additive until Step 2.

## Step 0 decision record

*(fill in when decided)*

- Decision: (a) namespace surface / (b) portmanteau canonical
- Compact profile plan (`ADVANCED_MEMORY_TOOL_PROFILE=compact`, ≤20 tools):
- Date / decided by:

## Step 4 triage checklist

*(fill during triage — one line per file: delete / extract / promote, with target)*

### 26 adn_* in mcp/tools/
- [ ] …

### 5 adn_* in mcp/beta/
- [ ] …

### ~20 standalone stratum
- [ ] delete inter_server_tools.py.backup (unconditional per spec)
- [ ] …
