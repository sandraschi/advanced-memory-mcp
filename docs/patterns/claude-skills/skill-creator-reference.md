# Anthropic Skill Creator Reference (Gold Standard)

**Updated:** 2025-11-08
**Source Repo:** `D:/Dev/repos/external/anthropic-skills/skill-creator/` (read-only clone)
**Purpose:** Canonical blueprint for Advanced Memory’s skill-creator facility

---

## 1. Overview

Anthropic’s `skill-creator` skill is the reference implementation for building new Claude skills. It ships with:

- `SKILL.md` – A comprehensive playbook describing the six-step creation process, progressive disclosure, and content guidelines.
- `scripts/init_skill.py` – Scaffolds a new skill folder with templated `SKILL.md`, placeholder scripts, references, and assets.
- `scripts/package_skill.py` – Validates a skill using `quick_validate.py` and emits a distributable ZIP.
- `scripts/quick_validate.py` – Minimal validator checking frontmatter requirements and naming conventions.

We mirror these ideas inside Advanced Memory MCP so users—and Claude—can generate high-quality skills with clear standards.

---

## 2. SKILL.md Structure (Anthropic)

Key sections:

1. **Metadata (YAML frontmatter)**
   - `name`: hyphen-case skill identifier
   - `description`: third-person explanation of capabilities & activation conditions
   - Optional `license`, etc.

2. **Skill Body**
   - `# Skill Creator` heading
   - “About Skills” section describing anatomy (SKILL.md plus optional scripts / references / assets)
   - “Progressive Disclosure” principle (metadata → SKILL.md → bundled resources)
   - Six-step “Skill Creation Process”:
     1. Understanding concrete usage examples
     2. Planning reusable contents
     3. Initializing via `init_skill.py`
     4. Editing (focus on imperative voice, references to resources)
     5. Packaging via `package_skill.py`
     6. Iteration

3. **Guidance specifics**
   - When to include scripts, references, assets
   - Examples from other skills
   - Stylistic rules (“Write for another Claude”, imperative tone)
   - Packaging/validation instructions

---

## 3. init_skill.py – Scaffolding Logic

Usage:
```bash
python scripts/init_skill.py <skill-name> --path <output-dir>
```

Behavior:

- Creates `<path>/<skill-name>/` with:
  - `SKILL.md` template:
    - Pre-filled frontmatter (`name`, TODO `description`)
    - Suggested section patterns (“Workflow based”, “Task based”, etc.)
    - Placeholders to encourage concrete content, references to scripts/assets
  - `scripts/`, `references/`, `assets/` folders with example placeholder files.

Notable patterns:

- `title_case_skill_name()` helper to convert hyphen-case to display title.
- Explicit instructions to delete unused directories.
- Rich inline comments to teach best practices directly in the scaffold.

---

## 4. package_skill.py + quick_validate.py

### Validation & Packaging Flow

```bash
python scripts/package_skill.py /path/to/skill [output-dir]
```

1. Resolve paths; verify folder/`SKILL.md` exists.
2. Run `quick_validate.validate_skill(skill_path)`:
   - Ensures frontmatter exists.
   - Checks required fields (`name`, `description`).
   - Enforces hyphen-case naming rules.
   - Guards against angle brackets in description (prevents HTML injection).
3. If validation passes, create ZIP containing entire skill using relative paths.

### quick_validate Highlights

- Minimal dependencies—pure Python with regex parsing.
- Future extension hooks: check module files, required directories, etc.
- Returns tuple `(valid: bool, message: str)` – ready for direct CLI messaging.

---

## 5. Key Patterns to Adopt in Advanced Memory MCP

1. **Three-Level Loading**
   - Metadata: short, precise description (100 words max).
   - SKILL.md: <= 5k words, focus on procedural knowledge.
   - Bundled resources: load or execute only when needed.

2. **Scaffolding Tools**
   - Provide CLI (and future MCP tool) to scaffold new skills following the same template.
   - Generate `_toc.md`, modular `modules/` (Advanced Memory extension) + placeholder resources.

3. **Validation Pipeline**
   - Pre-package validation BEFORE distribution.
   - Enforce naming & description quality.
   - Extend validators with our modular requirements (known gaps, research checklist).

4. **Imperative Style & Cross-References**
   - Write instructions for “another Claude”.
   - Reference scripts/assets by path.
   - Provide concrete examples and decision trees.

5. **Iteration & Research**
   - Encourage recurring validation (last_validated metadata).
   - Document known gaps and research tasks (Advanced Memory modules).

---

## 6. Action Items for Advanced Memory MCP

| Task | Status |
| --- | --- |
| Clone Anthropic repo | ✅ `D:/Dev/repos/external/anthropic-skills/skill-creator/` |
| Reference skill in `.cursorrules` | ✅ Added |
| Design AM skill-creator tool | ⏳ (Use this doc as blueprint) |
| Implement scaffold + package utilities | ⏳ (Leverage Anthropic scripts as inspiration) |
| Extend validator for modular requirements | ⏳ |
| Document process in central docs (this file) | ✅ |

---

## 7. Reference Locations

- Anthropic source: `D:/Dev/repos/external/anthropic-skills/skill-creator/`
  - `SKILL.md`
  - `scripts/init_skill.py`
  - `scripts/package_skill.py`
  - `scripts/quick_validate.py`
- Advanced Memory docs referencing skill-creator:
  - `docs/architecture/CLAUDE_SKILLS_ACTUAL_FORMAT.md`
  - `docs/architecture/THE_SKILLS_UNIVERSE.md`

---

## 8. Next Steps

- Mirror scaffold/packager as MCP tools (`adn_skills("init_from_template")`, `adn_skills("package")`, etc.).
- Integrate modular compliance (core-guidance, known-gaps, research-checklist) into generator.
- Add automated validation tests to enforce metadata, modules, and research guardrails.
- Publish usage guide in Advanced Memory’s user documentation.

This reference stays updated as Anthropic evolves their skill tooling; revisit whenever the upstream repo changes.
