"""Skills resources for Advanced Memory MCP server."""

import json
from pathlib import Path

import frontmatter
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


def _skills_root() -> Path:
    """Resolve the skills directory relative to the active project home."""
    from advanced_memory.mcp.project_session import get_active_project

    active = get_active_project()
    candidate = Path(active.home) / "skills"
    if candidate.is_dir():
        return candidate
    fallback = Path("skills")
    return fallback if fallback.is_dir() else candidate


@mcp.resource(
    uri="memory://skills",
    description="List Claude skills available in the active project skills/ directory.",
)
def skill_list() -> str:
    """Return JSON catalog of skills with metadata."""
    logger.info("Loading skill list resource")
    skills_root = _skills_root()
    records: list[dict[str, str | list[str]]] = []

    if not skills_root.exists():
        return json.dumps(
            {"skills": [], "count": 0, "root": str(skills_root), "message": "No skills directory found"},
            indent=2,
        )

    for skill_file in sorted(skills_root.glob("**/SKILL.md")):
        try:
            post = frontmatter.loads(skill_file.read_text(encoding="utf-8"))
            fm = post.metadata
            records.append(
                {
                    "name": str(fm.get("name", skill_file.parent.name)),
                    "description": str(fm.get("description", "")),
                    "path": skill_file.parent.relative_to(skills_root).as_posix(),
                }
            )
        except Exception as exc:
            logger.warning(f"Failed to parse {skill_file}: {exc}")
            records.append(
                {
                    "name": skill_file.parent.name,
                    "description": f"Parse error: {exc}",
                    "path": skill_file.parent.relative_to(skills_root).as_posix(),
                }
            )

    return json.dumps({"skills": records, "count": len(records), "root": str(skills_root)}, indent=2)


@mcp.resource(
    uri="memory://skills/{skill_path}",
    description="Read a skill's SKILL.md content by relative path under skills/.",
)
def skill_content(skill_path: str) -> str:
    """Return raw SKILL.md content for a skill."""
    logger.info(f"Loading skill content resource: {skill_path}")
    skills_root = _skills_root()
    skill_dir = (skills_root / skill_path).resolve()

    if not str(skill_dir).startswith(str(skills_root.resolve())):
        return f"# Error\n\nInvalid skill path: {skill_path}"

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        skill_md = skills_root / skill_path
        if skill_md.is_file() and skill_md.name == "SKILL.md":
            pass
        else:
            return f"# Error\n\nSKILL.md not found for: {skill_path}"

    if not skill_md.exists():
        return f"# Error\n\nSKILL.md not found for: {skill_path}"

    return skill_md.read_text(encoding="utf-8")
