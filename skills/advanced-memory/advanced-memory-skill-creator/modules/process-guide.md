# Process Guide

**Confidence**: 🟡 MEDIUM
**Last captured**: 2025-11-08

> This module adapts Anthropic’s six-step skill-creator methodology to Advanced Memory MCP. Use it when gathering requirements or coaching the user through the workflow.

---

## Step 1 — Understanding
1. Interview the requestor. Ask for concrete tasks (minimum three) that should trigger the skill.
2. Clarify target users, platforms, and guardrails.
3. Capture representative prompts and expected outputs in your working note.

## Step 2 — Planning Reusable Contents
1. For each example, determine which artifacts will be reused:
   - Scripts (automation, data processing)
   - References (schema docs, policies, decision trees)
   - Assets (templates, logos, boilerplate code)
2. Map each artifact to the appropriate folder (`scripts/`, `references/`, `assets/`).
3. Document decisions inside the project log or `modules/known-gaps.md`.

## Step 3 — Initializing the Skill
1. Run the scaffold operation (`adn_skills_creator` or `am-skill-creator` CLI).
2. Confirm the following files exist before proceeding:
   - `SKILL.md`
   - `_toc.md`
   - `modules/core-guidance.md`
   - `modules/known-gaps.md`
   - `modules/research-checklist.md`
3. Delete placeholder assets you do not need.

## Step 4 — Editing and Enrichment
1. Replace placeholder content in `modules/core-guidance.md` with imperative instructions.
2. Add additional modules for domain-specific processes (for example, `modules/sql-workflow.md`).
3. Reference bundled resources directly (e.g., “Load `references/api-spec.md` before calling the endpoint”).
4. Maintain consistent tone: instructive, concise, verified.

## Step 5 — Packaging Readiness
1. Run `adn_skills_creator(operation="validate", ...)`.
2. Resolve every issue returned by the validator (metadata, modules, sources).
3. Update `metadata` fields (`confidence`, `last_validated`, `status`).
4. Attach current TODOs to `modules/known-gaps.md`.

## Step 6 — Iteration and Maintenance
1. Package the skill (`package` operation) and share the archive.
2. Schedule refresh cycles for high-volatility domains (APIs, security, platform integrations).
3. Log feedback or breakages; open a task in `known-gaps.md` or project tracker.
4. Re-run validation after each significant update.

## Integration Tips
- Combine this guide with the research checklist to prevent stale instructions.
- Use the CLI in automated pipelines to enforce validation before publishing.
- Encourage teams to store manifests and source citations with each packaged skill.
