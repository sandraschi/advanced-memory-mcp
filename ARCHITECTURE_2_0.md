# Advanced Memory 2.0 — Architecture Spec

**Version**: 2.0.0-draft (rev 2026-07-07, Phase 1 rewritten against HEAD audit)  
**Target**: Fable 5 (frontier reasoning)  
**Status**: Spec phase — no code yet  
**Source of truth**: This document survives context resets. All implementation work references it. Phase 1 inventory numbers were verified against HEAD on 2026-07-07 (grep sweeps; see Verified Inventory). If HEAD moves before the sprint, re-run the inventory greps first.

---

## Why 2.0

v1.8.1 is a transitional architecture that stalled mid-transition. 31 legacy `adn_*` files exist (12 of them serve as the entire runtime tool surface; the rest are logic providers or dead). Eleven FastMCP namespace apps are fully written and decorated — and never mounted, so their 71 tools are unreachable at runtime. The search system has three layers with fragile path management. Skills reference stale tool names. The knowledge graph is a flat triple-store with no versioning, no federation, and no conflict resolution.

v2.0 finishes the transition and adds the capabilities that justify a major version bump: entity versioning, cross-project federation, dynamic skills, and a unified retrieval architecture.

---

## Phase 1: Kill the Dual Tool Surface (P0)

> **Rewritten 2026-07-07.** The previous Phase 1 was written from memory of the codebase and was wrong in every load-bearing number and in its core instruction. Verified state below. Do not trust any earlier revision of this section.

### Verified Inventory (HEAD, 2026-07-07)

| Fact | Old spec claimed | Verified reality |
|------|-----------------|------------------|
| Legacy `adn_*` files | 22 | **31** (26 in `mcp/tools/`, 5 in `mcp/beta/`) |
| Namespace decorators | "commented out" | **Active.** 71 `@*_app.tool()` registrations across 11 namespace apps (notes 7, search 3, audio 10, inbox 4, mcp 4, nav 6, project 6, skills 11, system 5, typora 8, zettel 7) |
| Namespace apps mounted | "partially registered" | **Never mounted.** Zero `.mount()` calls anywhere in `src/`. `tools/__init__.py` docstring promises "mounting domain-specific sub-apps in server.py"; server.py contains no mounts. All 71 namespace tools are dead code on orphan `FastMCP` instances |
| Runtime tool surface | 79 tools | **12 tools**: the `adn_*` portmanteaus side-effect-imported in `server.py` (adn_audio, adn_automation, adn_inbox, adn_knowledge, adn_nav, adn_notes, adn_project, adn_search, adn_skills, adn_system, adn_typora, adn_zettel). `beta/` is never imported — its 5 tools don't serve either |
| Source-level registrations | 79 | **95 active decorators** (71 namespace + 24 `@mcp.tool`), plus 40+ commented-out `@mcp.tool` decorators, plus 3 in dead file `inter_server_tools.py.backup` |
| `_dispatch_content_operations` | "500-line bottleneck" | Lines 64–559 of `content_manager.py` (~495 lines) — roughly right, but it is not the main problem |
| `content_manager.py` | implied: a hub to delete | **~2,405 lines.** The dispatch function is one fifth of it. The other ~1,800 lines are sixteen `_*_operation` functions (`_write_operation`, `_read_operation`, `_edit_operation`, `_edit_tags_operation`, `_move_operation`, `_delete_operation`, `_quick_capture_operation`, `_daily_note_operation`, `_suggest_tags_operation`, `_summarize_operation`, `_enhance_operation`, `_generate_operation`, …) that ARE the content domain's business logic, plus 4 commented-out tool defs (`adn_notes`, `adn_note_ai`, `adn_corpus_qc`, `adn_content`) |
| Tool strata | two (namespace + adn_*) | **Three.** A pre-portmanteau stratum of ~20 standalone single-tool files with commented decorators but live logic (`delete_note.py`, `edit_note.py`, `edit_in_notepadpp.py`, ten `export_*.py`, `external_mcp_clients.py`, `build_context.py`, `canvas.py`, `help.py`, `portmanteau_skills.py`, …), invoked as logic providers by the portmanteaus |

**Delegation chain (verified):** both `adn_notes` (registered) and `notes_app`'s seven tools (orphaned) are thin wrappers over the same `_dispatch_content_operations`. Activating the namespace surface as-is would NOT remove the hub — the namespace tools import it too. The hub dies only when the business logic moves to services and the tools call services directly.

### Step 0 — Decide the target tool surface (blocking, do first)

The old spec silently assumed the namespace surface (`notes_write`-style) wins. That assumption conflicts with the documented reason the portmanteaus exist: IDE tool-count limits (the `adn_notes` docstring says so explicitly — Cursor/Antigravity budgets). Mounting all 11 namespace apps raises the surface from 12 tools to ~71.

Options:

- **(a) Namespace surface wins** (the 2.0 thesis). 71 tools. Mitigations now exist that didn't when the portmanteaus were designed: FastMCP 3.1+ SearchTools/CodeMode (BM25 discovery), Claude Desktop deferred tool loading via `tool_search`, and FastMCP tag-based tool filtering to serve a reduced set per client profile. Breaking change for every external caller — correct for a 2.0.
- **(b) Portmanteau surface stays canonical.** Delete the 11 orphan namespace apps (~71 dead tools), keep 12 `adn_*` entry points, still extract logic to services underneath. Smallest diff, no client breakage, but 2.0 ships with the surface 1.x had and the "dual surface" problem is solved by killing the new one.
- **(c) Both, behind config.** Rejected — the straddle IS the current disease. Do not implement.

**Default recommendation: (a)**, with a FastMCP tag-filter profile (`ADVANCED_MEMORY_TOOL_PROFILE=compact`) that serves a curated ~15-tool subset for tool-budget-constrained IDEs. If (b) is chosen instead, Steps 2–5 below still apply; only Step 3 changes (delete namespace apps instead of mounting them). Phases 2 and 4 depend on this decision (stable tool names) — it cannot be deferred past Phase 1 day one.

### Steps

1. **Extract the content domain out of `content_manager.py`** (the real Phase 1 workload, ~1,800 lines). Move the sixteen `_*_operation` functions into `services/content/` grouped by concern (roughly: `crud.py` — write/read/view/move/delete; `capture.py` — quick/daily; `tagging.py` — edit_tags/extract/suggest; `ai_enrich.py` — summarize/enhance/generate; keep `build_success_response`/`build_error_response` in the existing shared utils). Pure moves with signature cleanup — no behavior changes in this step; the test suite is the referee.

2. **Rewire tool entry points to services.** Namespace app tools (and, until deleted, the `adn_*` wrappers) call services directly. Delete every `from ...content_manager import _dispatch_content_operations`. The `mcp_tool=` provenance strings move into a logging decorator or a service-layer context arg — do not lose call-site attribution, it is the only forensics for multi-IDE contention.

3. **Mount the namespace apps** — the step the architecture promised and never executed. In `server.py`: `mcp.mount(notes_app)` (and the other ten), replacing the block of `import advanced_memory.mcp.tools.adn_*` side-effect imports. Runtime verification is mandatory: a test that calls `tools/list` on the composed server and asserts the namespace tool names are present. The orphan-app failure mode survived review precisely because nothing ever checked the served surface.

4. **Triage all 31 `adn_*` files AND the ~20-file standalone stratum.** For each file, one of: **delete** (pure dispatch/wrapper — most `adn_*` after step 2), **extract** (business logic not yet in services — most of the standalone `export_*` stratum and the unregistered logic providers like `adn_editor`, `adn_export`, `adn_import`, `adn_llm`, `adn_document_ingest`), or **promote** (beta tools worth keeping become namespace tools; the rest are deleted — beta was never served, so nothing external can miss it). Delete `inter_server_tools.py.backup` unconditionally. Track the triage in a checklist file (`docs/development/PHASE1_TRIAGE.md`) — 50+ files is too many to hold in one context window; the checklist is the resumption point after any context reset.

5. **Delete `content_manager.py` and the legacy files.** Archive nothing as commented-out code; git history is the archive.

6. **Rewrite SKILL.md files and sweep external references.** All skill files and session-injection prompts use final tool names. Then the external sweep: rg over mcd (`D:\Dev\repos\mcp-central-docs`) and all IDE configs (Claude Desktop, Cursor, Windsurf, OpenCode, Antigravity) for `adn_` — the rename breaks every external client simultaneously on flip day. Ship the compact tool profile (Step 0) in the same release the portmanteaus disappear.

### Success criteria (all measurable, run in order)

- `rg "adn_" src/advanced_memory/ -g "*.py"` returns 0 results (except type aliases and CHANGELOG references)
- `rg "_dispatch_content_operations" src/` returns 0 results; `content_manager.py` deleted
- `rg "^\s*#\s*@[a-z_]+\.tool" src/` returns 0 results (no commented-out decorators anywhere — currently 40+)
- No `.backup` files in `src/`
- Runtime check: `tools/list` on the served instance returns the namespace tools (or, under option b, exactly the 12 portmanteaus) — asserted by a test, not by eyeball
- Compact tool profile serves ≤ 20 tools when `ADVANCED_MEMORY_TOOL_PROFILE=compact`
- All SKILL.md files use current tool names; mcd + IDE-config sweep documented in the triage file
- Full test suite passes (count to be re-verified at sprint start — the old "90+ tests" figure predates the audit and is untrusted)

**Risk**: Tool name changes are breaking for external clients. v2.0 is the right version for this — document in CHANGELOG. Secondary risk: Step 1 is a 1,800-line mechanical extraction — do it in one sitting per concern group with a test run between groups, never interleaved with Step 4 triage.

---

## Phase 2: Knowledge Graph v2 (P1)

**Problem**: The current triple-store (Entity → Observation → Relation) is flat. Observations are children of Entities, not independent nodes. Relations are always from-entity-owned. There's no:

- Entity versioning (no edit history)
- Bidirectional relation integrity (resolved vs unresolved)
- Conflict resolution for concurrent edits
- Entity templates beyond Zettelkasten roles
- Cross-project entity references

**Plan**:

### 2a. Entity Versioning

Add a `revisions` table with diff storage:

```python
class Revision(Base):
    id: int (PK)
    entity_id: int (FK → entity.id)
    version: int  # monotonically increasing per entity
    diff: str     # unified diff from previous version
    created_at: datetime
    author: str   # "user" | "sync" | "agent:<client>" e.g. agent:opencode
```

- Every `notes_edit` creates a revision record
- `notes_read` accepts optional `version=` parameter
- `notes_revert` restores to a specific version
- Diff computed via Python `difflib.unified_diff`
- **Snapshot anchoring**: store a full-content snapshot every 20 revisions (git packfile style). A pure diff chain makes `notes_revert` replay O(n) diffs, and one corrupted diff poisons every version after it
- `author` uses the convention `user`, `sync`, or `agent:<client>` — with four IDEs hitting this server, a coarse enum makes contention forensics impossible

### 2b. Observation Independence

Promote Observations to first-class nodes that can have their own relations:

```python
class Observation(Base):
    # existing fields stay
    outgoing_relations → list[Relation]  # NEW: observations can link
```

This enables: "This fact from paper X contradicts this fact from paper Y" as a relation between two observations, not just between their parent entities.

**Schema note**: relations are currently entity-owned. Observation-owned relations require either a polymorphic source FK (SQLAlchemy generic-FK patterns are all ugly) or a separate `observation_relations` table. Use the separate table: explicit, indexable, no generic-FK tricks. Do not let the implementing model default to the polymorphic option.

### 2c. Cross-Project References

Add a `link_type` discriminator to the permalink system:

```
memory://project-name/entity-permalink           # within same project
memory://project-name/entity-permalink#obs-id    # to an observation
memory://@other-project/entity-permalink         # cross-project (resolved lazily)
```

The `@` prefix signals a cross-project reference. Resolution is deferred until read time, avoiding stale references when projects are renamed.

**v2.0 scope constraint**: resolving references into *other database files* depends on Phase 5 (per-project DBs) and Phase 6 (federation) — both P3, both later. For v2.0, cross-project resolution works only within the shared-DB model. Define a `ReferenceResolver` interface now so P5/P6 can swap in new implementations without touching callers; otherwise 2c gets rewritten when P5 lands.

### 2d. Relation Type Taxonomy

Standardize the `relation_type` field with a controlled vocabulary:

```
structural:   "contains", "is_part_of", "implements"
semantic:     "contradicts", "supports", "extends", "refines"
temporal:     "precedes", "follows", "deprecates"
causal:       "causes", "prevents", "enables"
reference:    "cites", "derives_from", "inspired_by"
```

**Success criteria**:
- `notes_read(identifier="x", version=3)` returns a historical version
- Cross-project wikilinks resolve at read time
- Observations appear as nodes in the knowledge graph canvas
- Relation type dropdown in UI shows the taxonomy

---

## Phase 3: Unified Retrieval Architecture (P1)

**Problem**: Three search layers (FTS5, LanceDB, reranker) with separate config, separate index rebuilds, and fragile LanceDB path discovery that uses heuristic directory traversal.

**Plan**:

### 3a. Single Index Manager

Create `services/index_manager.py` — a unified lifecycle manager:

```python
class IndexManager:
    async def reindex_all(self, project_id: int) -> ReindexReport
    async def reindex_entity(self, entity_id: int) -> None
    async def delete_entity(self, entity_id: int) -> None
    async def health_check(self) -> IndexHealth
```

All three layers (FTS5, LanceDB, reranker) are managed through this single interface. No more per-layer rebuild scripts.

### 3b. Deterministic LanceDB Path

Replace heuristic path discovery with an explicit config key: `lancedb_path`. Default: `~/.advanced-memory/vectors/`. No traversal up the directory tree.

### 3c. Incremental Vector Reindex

Instead of dropping and recreating the LanceDB table on every reindex:
- On entity update: delete old chunks, insert new chunks by entity_id
- On entity delete: delete chunks by entity_id
- Full reindex only on config change (model, chunk size) or corruption recovery

### 3d. Embedding Model Config

Move embedding model selection to config, with an explicit registry:

```python
EMBEDDING_MODELS = {
    "bge-small":  {"name": "BAAI/bge-small-en-v1.5", "dims": 384, "gpu_ok": True},
    "bge-base":   {"name": "BAAI/bge-base-en-v1.5",  "dims": 768, "gpu_ok": True},
    "all-minilm": {"name": "sentence-transformers/all-MiniLM-L6-v2", "dims": 384, "gpu_ok": False},
}
```

No more hardcoded model strings scattered across `search_service.py`, `vector_repository.py`, and `fastembed_gpu.py`.

**Model swap is a schema change, not a reindex**: LanceDB tables are dimension-bound (bge-small = 384, bge-base = 768). Switching models drops and recreates the vector table, then re-embeds everything. "Full reindex" in the success criterion means table recreation — never attempt in-place upsert across a dimension change.

**Success criteria**:
- `index_manager.health_check()` returns pass/fail for all three layers
- Updating an entity triggers incremental reindex, not full rebuild
- LanceDB path is a single config key, not a heuristic
- Changing embedding model via config triggers a one-time full reindex with progress feedback

---

## Phase 4: Dynamic Skills (P2)

**Problem**: Skills are static SKILL.md files with hardcoded tool names. When tools change, skills go stale. There's no skill activation based on project context, no dynamic composition, and no feedback loop from usage.

**Plan**:

### 4a. Tool Reference Resolution

Instead of hardcoding tool names in SKILL.md:

```markdown
## Tools
- `notes_write` — Create new notes  ← CURRENT (stale risk)
```

Add a `## Tools` frontmatter block that auto-resolves:

```yaml
---
name: agentic-zettelkasten
tools:
  - notes_write
  - notes_read
  - zettel_scaffold
  - search_rag
---
```

On server start, validate every skill's `tools:` list against registered tools. Log warnings for mismatches. The `/api/skills/{name}` endpoint renders the validated tool list, not the static text.

### 4b. Project-Aware Skill Activation

Add `auto_activate` rules to skills:

```yaml
---
name: china-expert
auto_activate:
  project_patterns: ["china-*", "*-cn"]
  content_keywords: ["China", "Chinese", "Beijing", "Shanghai"]
---
```

When a project matches, the session context injection includes the skill. No manual `adn_skills(operation="activate")` needed.

### 4c. Usage Telemetry

Track skill usage in the DB:
- `skill.usage_count` (already exists — actually increment it)
- `skill.last_used_at`
- `skill.effectiveness_rating` (user/agent feedback)

Use telemetry to rank skill suggestions and prune unused skills.

### 4d. Skill Composition

Allow skills to declare dependencies:

```yaml
---
name: full-stack-developer
requires: [api-design-architect, testing-strategy-guide, git-workflow-specialist]
---
```

Activating a composite skill activates all dependencies. Deactivating checks for shared dependencies still in use.

**Success criteria**:
- `GET /api/skills/agentic-zettelkasten` returns validated tool list, not static text
- Server start logs warnings for skills referencing missing tools
- Project switch auto-activates matching skills
- `skill.usage_count` increments on every activation

---

## Phase 5: Project Database Isolation (P3)

**Problem**: All projects share one SQLite database with `project_id` column scoping. A corrupted entity in one project can affect FTS5 indexes for all projects. No per-project backup/restore.

**Plan**:

Add an optional `database_per_project` mode:

```python
# config.json
{
  "projects": {
    "chrono-glenn": {
      "path": "D:/dev/chrono-glenn",
      "database": "D:/dev/chrono-glenn/.advanced-memory/memory.db"  # NEW
    }
  },
  "database_per_project": true
}
```

When enabled:
- Each project gets its own SQLite + LanceDB directory inside the project root
- The global `~/.advanced-memory/memory.db` stores only the project registry (migrations + project table)
- Switch project = close old connection, open new one
- Backup = copy one SQLite file

When disabled (default for small projects): keep the current shared-DB model.

**Priority note**: the recurring multi-IDE lock contention is scoped by database file, so per-project DBs shrink the contention surface directly and reduce reliance on the `ADVANCED_MEMORY_READONLY=1` workaround. Day-to-day this may deliver more relief than Phase 3. Hard requirements: (1) WAL mode is mandatory in per-project mode; (2) the migration appends `.advanced-memory/` to each project repo's `.gitignore`, or SQLite files get committed; (3) project switch must tolerate a second IDE still holding the old connection — close gracefully, never force-unlock.

**Success criteria**:
- Creating a project with `database_per_project=true` creates `{project_path}/.advanced-memory/memory.db`
- Project switch swaps active database connections
- Backup script copies a single file per project

---

## Phase 6: Cross-Fleet Federation (P3)

**Problem**: Advanced Memory is a single-node knowledge graph. The fleet (140+ repos per FLEET_INDEX.md) has no shared memory surface.

**Plan**:

Add a `federation` mode where the server can:

1. **Index external projects as read-only mirrors**: Point at another project's `.advanced-memory/memory.db` and index its entities for cross-project search.

2. **Expose a federation endpoint**: `GET /api/v1/federation/search?q=...` allows other fleet servers to query this knowledge graph. This is the backend of the "cross-project reference" feature from Phase 2c.

3. **Publish memory events**: On entity create/update/delete, emit events to a configurable webhook. Other servers can subscribe.

```python
# config.json
{
  "federation": {
    "mirrors": ["D:/Dev/repos/arxiv-mcp/.advanced-memory/memory.db"],
    "publish_webhook": "http://localhost:10797/api/v1/fleet/ingest",
    "subscribe_endpoints": []
  }
}
```

**Success criteria**:
- Cross-project search returns results from mirrored projects
- Entity creation in one project triggers an event POST to the publish webhook

---

## Phase 7: Performance & Scale Targets (P2)

**Current** (v1.8.1):
- Cold start: ~2-3s (not measured)
- Simple ops: not measured
- Max entities per project: declared 50K, untested
- Vector reindex: full rebuild only

**Target** (v2.0):
- Cold start: ≤ 1s (measured with 5K entities)
- `notes_read` p95: ≤ 50ms
- `search_rag` p95: ≤ 500ms (with GPU reranker)
- 100K entities per project (benchmarked)
- Index rebuild: ≤ 2 minutes for 10K entities (down from ~5 minutes)
- Memory: ≤ 300MB idle (down from ~400MB) — measured pre-first-search; the GPU reranker is lazy-loaded on first `search_rag` call and sits outside the idle budget (the model alone exceeds 300MB, so a resident reranker fails this target by design)

Add a `just bench` recipe that runs a standard benchmark suite:
1. Create 1K/10K/50K entities, measure write throughput
2. Search latency distribution (p50/p95/p99)
3. Index rebuild time
4. Memory after 1 hour idle

---

## What NOT to Do in 2.0

These are out of scope for v2.0 (v3.0 candidates):

- **Cloud sync / multi-device**: Explicitly out of scope per PRD. Users sync files with Syncthing/OneDrive.
- **Multi-user / collaboration**: Single-user tool. No auth, no sharing.
- **Real-time collaboration**: No CRDT, no OT, no WebSocket sync.
- **Mobile/web client**: The webapp is a dashboard, not a full client.
- **Note content versioning (full git-style)**: Phase 2a does diffs. Full branching/merging is v3.0.
- **Plugin system**: No third-party tool extensions in the MCP server.
- **GraphQL API**: REST remains the webapp API. No GraphQL layer.
- **Tauri mobile**: Desktop Tauri exists (native/). Mobile is out of scope.

---

## Implementation Order

| Phase | Est. effort | Depends on | Risk |
|-------|------------|------------|------|
| P1: Kill Dual Tool Surface | 3-4 days (was 2 — re-scoped after HEAD audit: 2,405-line decomposition + 50-file triage + surface decision, not a 500-line hub deletion) | Step 0 surface decision | High (breaking changes) |
| P2: Knowledge Graph v2 | 2 days | P1 (tool names stable) | Medium (schema migration) |
| P3: Unified Retrieval | 1 day | P1 | Low (internal refactor) |
| P4: Dynamic Skills | 1.5 days | P1 (tool names stable) | Low |
| P5: Project DB Isolation | 1 day | None | Low (opt-in) |
| P6: Cross-Fleet Federation | 2 days | P2 | Medium (new surface) |
| P7: Performance Targets | 1 day | P2-P3 | Low (measurement only) |

**Recommended Fable 5 sprint**: Phase 1 alone if the window is short — it is the architectural keystone and now correctly sized at 3-4 days. Phases 1-3 together are 6-7 days. Phases 4-7 can be done with Opus/Sonnet.

**If only 3 days**: Phase 1 only, Steps 0-3 complete plus triage checklist written. Steps 4-6 are mechanical and resumable from the checklist by a cheaper model.
