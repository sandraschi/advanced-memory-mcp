# Advanced Memory Skill Creator

This directory contains the modular Claude skill that teaches Claude (and teammates) how to use the Advanced Memory skill-creation facility.

## Contents
- `SKILL.md` – Main entry point with status banner, quick start instructions, and links to supporting modules.
- `_toc.md` – Table of contents for all modules.
- `modules/core-guidance.md` – Imperative workflow (requirements, scaffold, validate, package, automate).
- `modules/process-guide.md` – Anthropic six-step methodology customized for Advanced Memory.
- `modules/known-gaps.md` – Outstanding tasks and research TODOs.
- `modules/research-checklist.md` – Mandatory verification process referencing distillation helpers.
- `scripts/` | `references/` | `assets/` – Placeholders for reusable resources.

## Related Tooling
- `adn_skills_creator` MCP tool (portmanteau) – Operations: scaffold, validate, inspect, upgrade, package.
- `uv run am-skill-creator ...` CLI entry point – Same functionality for automation or CI.

## Next Actions
- Complete research checklist, gather upstream citations, and set `metadata.confidence` once verified.
- Add real scripts/references/assets per project needs.
- Publish packaged skill after validation passes with zero issues.
