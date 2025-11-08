# Anthropic “skill-creator” Reference (Gold Standard)

**Updated:** 2025-11-08  
**Source Repository:** `https://github.com/anthropics/skills` (cloned locally in `D:/Dev/repos/external/anthropic-skills/skill-creator/`)  
**Purpose:** Capture the canonical skill creation methodology that Advanced Memory MCP mirrors.

---

## 1. Why This Matters

Anthropic’s `skill-creator` skill is the official playbook for producing Claude Skills. Our goal is to build an equivalent (or extended) facility in Advanced Memory MCP. This document records the structure, scripts, and patterns we must track to stay aligned with Anthropic’s standards.

---

## 2. Directory Layout

```
skill-creator/
├── SKILL.md
├── scripts/
│   ├── init_skill.py
│   ├── package_skill.py
│   └── quick_validate.py
└── LICENSE.txt
```

- **SKILL.md**: Detailed procedural guide for creating skills (six-step workflow, progressive disclosure, resource guidance).
- **scripts/init_skill.py**: Scaffolds new skill folders with templated `SKILL.md`, example scripts, references, assets.
- **scripts/package_skill.py**: Validates a skill folder (via `quick_validate.py`) and packages it into a ZIP.
- **scripts/quick_validate.py**: Minimal validator ensuring required frontmatter, hyphen-case naming, no angle brackets in description.

---

## 3. SKILL.md: Key Concepts

### Progressive Disclosure
1. **Metadata** – `name` + `description` tell Claude when to activate (<100 words).  
2. **SKILL.md** – Main instructions (≤5k words).  
3. **Bundled Resources** – Load or execute only when needed (scripts/references/assets).

### Six-Step Skill Creation Process
1. **Understanding** – Gather concrete usage examples; clarify triggers.  
2. **Planning** – Identify reusable contents (scripts, references, assets) for recurring tasks.  
3. **Initializing** – Run `init_skill.py` to scaffold folders.  
4. **Editing** – Write for another Claude (imperative tone, reference bundled resources).  
5. **Packaging** – Run `package_skill.py` which auto-validates via `quick_validate.py`.  
6. **Iteration** – Test on real tasks, refine skill, update resources.

### Resource Guidance
- **scripts/** – Deterministic code, frequently reused procedures.  
- **references/** – Documentation loaded into context on demand (schemas, policies).  
- **assets/** – Files not loaded into context but used in outputs (templates, fonts, boilerplate).

---

## 4. init_skill.py Highlights

Usage:
```bash
python scripts/init_skill.py <skill-name> --path <output-directory>
```

- Generates `<path>/<skill-name>/` directory.  
- Creates SKILL.md template with TODO placeholders, suggested structures (workflow/task/reference/capabilities).  
- Seeds `scripts/`, `references/`, `assets/` with example placeholders.  
- Encourages deleting unused directories, customizing content.  
- Helper `title_case_skill_name()` converts hyphen-case to Title Case headings.

---

## 5. package_skill.py & quick_validate.py

### Packaging Flow
```bash
python scripts/package_skill.py <path/to/skill-folder> [output-dir]
```

1. Ensure folder and `SKILL.md` exist.  
2. Run `quick_validate.validate_skill(skill_path)`:
   - SKILL.md has YAML frontmatter.  
   - `name` present, hyphen-case.  
   - `description` present, no angle brackets.  
3. If valid, create ZIP with relative paths; otherwise print errors and abort.

### quick_validate Logic
- Regex-based extraction of frontmatter.  
- Enforces naming/description quality.  
- Designed to be lightweight, fast, and extendable.

---

## 6. Adoption Plan for Advanced Memory MCP

1. **Mirror Structure** – Convert our skills into modular layout while preserving Anthropic’s metadata expectations.  
2. **Provide Tools** – Build MCP operations or CLI wrappers analogous to `init_skill.py` and `package_skill.py`.  
3. **Extend Validation** – Layer on our modular requirements (known gaps, research checklist, last_validated).  
4. **Document Workflow** – Keep this doc updated; ensure `.cursorrules` references the repo as authoritative.  
5. **Monitor Upstream** – Re-sync whenever Anthropic updates the skill-creator skill.

---

## 7. References

- Anthropic repo clone: `D:/Dev/repos/external/anthropic-skills/skill-creator/`  
- Advanced Memory docs:
  - `docs/architecture/CLAUDE_SKILLS_ACTUAL_FORMAT.md`
  - `docs/architecture/THE_SKILLS_UNIVERSE.md`
  - `docs/patterns/claude-skills/skill-creator-reference.md` (in this repo)
- `.cursorrules` entry – enforces use of this reference for all new skills.

---

## 8. Next Actions

- [ ] Implement Advanced Memory’s `skill_creator` tooling modeled on Anthropic scripts.  
- [ ] Integrate modular compliance checks (research checklist, known gaps, core guidance).  
- [ ] Provide user-facing documentation (portmanteau operation, CLI helper).  
- [ ] Automate validation tests in CI.

This document is the central hub inside MCP central docs; update as we evolve the Advanced Memory skill-creator facility.

