# SkillStudio v1 — SPEC

**Status:** draft for review. **Home (v1):** `advanced-memory-mcp` (memops).
**Future home:** `anthropic-skills-mcp` (not yet scaffolded). Everything below is
laid out so the studio moves as one subtree; section 9 lists the extraction rules.

## 1. Problem

The skills scene is write-only: static `SKILL.md` files, no measurement, no
regeneration. In this fleet that compounds: ~105 catalog skills plus one skill
per fleet repo, all triggered by free-text `description` fields nobody scores.
SkillStudio today is a 39-line "Not Yet Available" placeholder
(`webapp/frontend/src/pages/skills/SkillStudio.tsx`).

v1 makes Studio the place where skills are **measured** and **regenerated**.
A third job, fleet-wide routing (which skill owns a task, conflict detection,
coverage gaps), is explicitly v2 — it needs the v1 telemetry to be meaningful.

## 2. v1 slice (and only this)

1. **Trigger lab.** Score a skill's trigger precision/recall against a scenario
   suite. Edit description, re-run, see the delta.
2. **Q&A-to-skill distiller.** Turn answered GitHub Discussions (and vault notes)
   into skill-section drafts behind an approval gate.

Non-goals for v1: mesh router UI, automatic (unapproved) skill rewrites,
marketplace ratings, cross-repo skill search.

## 3. Architecture and extraction seams

New code lives in exactly two subtrees, importable as a unit later:

- Backend: `src/advanced_memory/skills/studio/` — `lab.py` (scoring),
  `distill.py` (Q&A pipeline), `telemetry.py` (event log), `router_studio.py`
  (HTTP management routes). One new MCP portmanteau, `adn_skillstudio`
  (section 4), registered like the other tools. No imports from webapp code;
  only from `skills/` engine helpers and `repository/`.
- Frontend: `webapp/frontend/src/pages/skills/studio/` — `StudioTabs`,
  `LabTab`, `DistillTab`, `TelemetryTab`. Talks only to the section-5 HTTP
  routes, never directly to MCP tools.

Extraction rule for later: move the two subtrees plus the SQLite tables
(section 6) into `anthropic-skills-mcp`; the only rewrite is the tool
registration and the route prefix. No Studio logic may import
`mcp/tools/*` or `services/skill_creator/*` internals — only their public
`operation=` surfaces.

## 4. MCP surface: `adn_skillstudio` (new portmanteau)

Follows the fleet portmanteau pattern (`operation` enum, `{success, message,
data}` envelope). Operations:

| op | args | returns |
|---|---|---|
| `scenario_create` | `skill_id`, `prompt`, `should_fire` (bool), `notes` | scenario id |
| `scenario_list` | `skill_id?` | scenarios |
| `scenario_delete` | `scenario_id` | ok |
| `lab_run` | `skill_id`, `model?` (default ambient Ollama) | run id, precision, recall, per-scenario verdicts |
| `lab_history` | `skill_id`, `limit=10` | past runs with scores |
| `telemetry` | `skill_id?`, `since?` | activation/section-load events |
| `distill_preview` | `source` (`discussion:<n>` or `note:<permalink>`), `skill_id` | draft section markdown (no write) |
| `distill_apply` | `job_id` | appends/replaces section in SKILL.md (backup kept as `SKILL.md.pre-studio-<ts>`) |
| `distill_jobs` | `state?` (pending/approved/applied/rejected) | job list |

`lab_run` judging: for each scenario, prompt the model with the skill's
`description` + TOC (The Door: never the full skill) and the scenario prompt;
verdict = fired or not vs `should_fire`. Deterministic temperature 0.
Precision = fired-correct / fired-total; recall = fired-correct /
should-fire-total. Store both plus the model name — scores are only comparable
within one model.

## 5. HTTP routes for the webapp (`/management/skills-studio/*`)

Thin wrappers over the section-4 operations returning the same envelope:
`GET /scenarios?skill_id=`, `POST /scenarios`, `DELETE /scenarios/{id}`,
`POST /lab-runs`, `GET /lab-runs?skill_id=&limit=`, `GET /telemetry?skill_id=&since=`,
`POST /distill/preview`, `POST /distill/apply`, `GET /distill/jobs`.
Read-only GETs stay unauthenticated like the rest of the management surface;
`distill_apply` requires the same posture as other vault mutations.

## 6. Data model (SQLite, new tables)

- `studio_scenarios(id, skill_id, prompt, should_fire, notes, created_at)` —
  the graded suite. Ships with 5 seed scenarios per pilot skill (section 8).
- `studio_runs(id, skill_id, model, precision, recall, verdicts_json, created_at)`.
- `studio_events(id, skill_id, event` — `activate|load_section|load_resource`,
  `section?, created_at)` — written by instrumented `adn_skills`
  activate/load_section/load_resource (opt-in env `ADN_SKILLS_TELEMETRY=1`,
  default on for local runs; no prompt content logged, only identifiers).
- `studio_distill_jobs(id, skill_id, source, draft_md, state, created_at)`.

Migrations via the repo's existing Alembic/SQLite path; tables prefixed
`studio_` so extraction is a clean cut.

## 7. Q&A distiller flow

1. `distill_preview(source="discussion:22", skill_id=...)`: fetch the answered
   discussion via `gh api graphql` (server-side, same query pattern as the
   manual seeding), extract Q&A pairs, draft one `## FAQ additions`-style
   section in the skill's voice.
2. Operator reviews the draft in DistillTab (side-by-side with the source),
   edits inline, approves or rejects. Approval creates the backup, then
   `replace_section` or `append` into `SKILL.md`.
3. Applied jobs link back to the source discussion URL in a trailing comment.

Same flow accepts `source="note:<permalink>"` for vault notes (scribe
transcripts, postmortems). Never fully automatic in v1: every write passes the
approval screen.

## 8. Frontend (replaces the placeholder)

`SkillStudio.tsx` becomes a tab shell reusing the Help-page tab pattern
(horizontal `border-b` nav, `data-testid="studio-tabs"`,
`studio-tab-lab/distill/telemetry`):
- **LabTab:** skill picker, scenario table (add/delete), Run button, score
  cards (precision/recall + delta vs previous run), per-scenario verdict list.
- **DistillTab:** source picker (answered discussions list via backend,
  note search), Preview button, editable draft pane, Approve/Reject, job
  history with states.
- **TelemetryTab:** event feed per skill (activations, section loads) —
  the raw material that tells which sections earn their context cost.

## 9. Pilot (before calling v1 done)

Three skills, five seed scenarios each, one lab run each with published deltas:
1. This repo's own assistant skill (dogfood the trigger that matters most).
2 + 3. Two fleet repo skills with sharp domains (candidates: `fleet-expert`,
`repo-expert` — owner picks). Success bar: at least one description rewrite
per pilot skill driven by a failing scenario, re-run green.

## 10. Verification

- `pytest` for `lab_run` scoring math (precision/recall on fixture verdicts),
  distill backup/restore round-trip, telemetry event shape.
- `biome check` + `tsc --noEmit` on the frontend subtree.
- Headless pass: run one lab eval, approve one distill job on a scratch skill,
  assert zero failed requests/page errors.
- `just ci` (repo gate) green before merge.

## 11. Open questions for the owner

1. Pilot skills 2 and 3: `fleet-expert` + `repo-expert`, or two domain skills?
2. Telemetry default-on locally: acceptable, or opt-in flag only?
3. Distill sources beyond discussions+notes for v1 (issues? session transcripts)?
