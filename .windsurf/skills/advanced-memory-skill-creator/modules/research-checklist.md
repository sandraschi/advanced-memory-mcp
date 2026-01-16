# Research Checklist

Follow these steps before trusting this skill:

1. Identify the freshness risk (APIs, frameworks, standards, or safety-critical topics).
2. Review Anthropic’s upstream repository (`https://github.com/anthropics/skills`) for changes to `skill-creator/`.
3. Run targeted web searches (official docs, release notes, expert articles) dated 2025 or newer.
4. Record each source with title, URL, and access date in this module and in `metadata.sources`.
5. Validate the guidance inside [core-guidance.md](core-guidance.md) against the new sources and update examples if any commands changed.
6. Confirm CLI usage by testing the latest `am-skill-creator` entry point on Windows and macOS environments (if available).
7. Update `metadata.last_validated`, `metadata.confidence`, and cite the confirmed material.
8. Move confirmed instructions into dedicated topic modules and mark obsolete content for removal.
9. Document remaining unknowns in [known-gaps.md](known-gaps.md).

> Tip: Use `adn_skills("distill_from_wikipedia", ...)`, `adn_skills("distill_from_arxiv", ...)`, and trusted web research to bootstrap validation.

## Collected sources (2025-11-08)
- Anthropic skill-creator SKILL.md (https://github.com/anthropics/skills/blob/main/skill-creator/SKILL.md)
- Anthropic skill-creator scripts (`scripts/init_skill.py`, `scripts/package_skill.py`) – same repository
- Advanced Memory Skill Creator Design (docs-private/ADVANCED_MEMORY_SKILL_CREATOR_DESIGN.md)
- Advanced Memory MCP implementation (`src/advanced_memory/mcp/tools/adn_skills_creator.py`)
