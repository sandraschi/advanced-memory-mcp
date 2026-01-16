# Core Guidance (Legacy Template)

**Confidence**: 🔴 LOW
**Last captured**: 2025-11-08

> This module preserves the original skill instructions prior to modular conversion.
> Treat every section as unverified until you complete the research checklist and add dated sources.

---

# Core Guidance — Advanced Memory Skill Creator

## Overview
Follow the steps below whenever you need to create or maintain a Claude skill inside the Advanced Memory ecosystem. Every section is written in imperative voice so Claude can execute the workflow without ambiguity.

## 1. Gather Requirements
1. Capture three or more concrete user requests that should trigger the new skill.
2. Identify reusable artifacts (scripts, references, assets) needed to fulfil those requests repeatedly.
3. Record preliminary notes in your project journal or zettelkasten entry.

## 2. Scaffold the Skill
1. Choose a hyphen-case skill name (example: `brand-guidelines-refresh`).
2. Run one of the following:
   ```python
   adn_skills_creator(
       operation="scaffold",
       skill_name="brand-guidelines-refresh",
       output_dir="skills/company",
       category="enterprise"
   )
   ```
   or
   ```bash
   uv run am-skill-creator scaffold brand-guidelines-refresh --output-dir skills/company --category enterprise
   ```
3. Review generated files:
   - `SKILL.md` (status banner + metadata)
   - `_toc.md`
   - `modules/` (core-guidance, known-gaps, research-checklist)
   - Placeholder `scripts/`, `references/`, `assets/`

## 3. Populate Instructional Content
1. Replace the placeholder paragraph in this module with step-by-step procedures tailored to the new skill.
2. Create additional topic modules (e.g., `modules/workflow.md`) as needed and add them to `_toc.md`.
3. Add imperative instructions that reference bundled resources by relative path (for example: “Load `references/finance-schema.md` before drafting SQL queries”).

## 4. Capture Research and Sources
1. Execute the workflow in [modules/research-checklist.md](research-checklist.md).
2. Record each authoritative source in both the checklist and `metadata.sources`.
3. Update `metadata.last_validated`, `metadata.confidence`, and `metadata.status` when research is complete.

## 5. Validate the Skill
1. Run validation via MCP tool or CLI:
   ```python
   adn_skills_creator(operation="validate", skill_path="skills/company/brand-guidelines-refresh")
   ```
2. If issues are reported, address them immediately (missing modules, metadata gaps, etc.).
3. Record resolved issues in `modules/known-gaps.md`.

## 6. Package for Distribution
1. Package only after validation succeeds:
   ```python
   adn_skills_creator(
       operation="package",
       skill_path="skills/company/brand-guidelines-refresh",
       output_dir="dist"
   )
   ```
2. Deliver the generated ZIP archive along with the manifest JSON (contains metadata and SHA-256 checksum).
3. Archive the manifest in your release notes or project documentation for traceability.

## 7. Upgrade Legacy Skills (When Needed)
1. For a single legacy folder:
   ```python
   adn_skills_creator(operation="upgrade", skill_path="skills/legacy/old-skill")
   ```
2. For bulk upgrades, run `python scripts/refactor_skills_modular.py`.
3. After upgrading, revisit Steps 3–6 to insert modern instructions and metadata.

## 8. Automate Repetitive Tasks
1. Use the CLI in scripts or CI pipelines to ensure every commit keeps skills validated.
2. Integrate validation into `scripts/pre_commit_check.py` if working on critical skills.
3. Schedule periodic `validate` runs for high-risk skills (APIs, fast-moving frameworks).

## 9. Handoff Checklist
- [ ] Frontmatter description and metadata completed.
- [ ] Core modules contain current, imperative instructions.
- [ ] Known gaps reflect outstanding research or TODOs.
- [ ] Research checklist executed and sources recorded.
- [ ] Validation succeeds with zero issues.
- [ ] Package archived and shared with stakeholders.
