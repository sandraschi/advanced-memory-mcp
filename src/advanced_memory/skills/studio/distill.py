"""Q&A distiller: discussions/issues/notes become skill-section drafts.

Writes only happen through distill_apply behind UI approval, always with a
timestamped backup of SKILL.md.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from advanced_memory.skills.studio import repository, skillsource

DEFAULT_REPO = "sandraschi/advanced-memory-mcp"


def _gh_graphql(query: str) -> dict[str, Any]:
    """Run a read-only GraphQL query via gh CLI. Raises RuntimeError.

    Needs gh auth in the server process (keyring or GH_TOKEN). Plain `gh`
    without auth cannot run GraphQL at all — that is a GitHub API rule.
    """
    proc = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "GitHub Discussions need gh auth on the server process "
            "(GH_TOKEN env or keyring login). "
            f"gh said: {proc.stderr.strip()[:200]}"
        )
    try:
        return json.loads(proc.stdout or "{}")
    except ValueError as exc:
        raise RuntimeError(f"gh api returned non-JSON: {exc}") from exc


def _github_rest(path: str) -> Any:
    """Unauthenticated public REST call (issues work without any token)."""
    import httpx

    url = f"https://api.github.com{path}"
    try:
        with httpx.Client(timeout=20.0, headers={"Accept": "application/vnd.github+json"}) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        raise RuntimeError(f"GitHub REST {path} failed: {exc}") from exc


def fetch_discussion(number: int, repo: str = DEFAULT_REPO) -> dict[str, Any]:
    owner, name = repo.split("/", 1)
    q = (
        f'{{repository(owner:"{owner}",name:"{name}")'
        f"{{discussion(number:{number}){{title body category{{name}} comments(first:50)"
        "{nodes{body isAnswer}}}}}"
    )
    data = _gh_graphql(q).get("data", {}).get("repository", {}).get("discussion") or {}
    comments = [c.get("body", "") for c in (data.get("comments") or {}).get("nodes", [])]
    return {"title": data.get("title", ""), "body": data.get("body", ""), "comments": comments}


def fetch_issue(number: int, repo: str = DEFAULT_REPO) -> dict[str, Any]:
    issue = _github_rest(f"/repos/{repo}/issues/{number}")
    comments = _github_rest(f"/repos/{repo}/issues/{number}/comments")
    if not isinstance(issue, dict):
        raise RuntimeError(f"Issue #{number} not found in {repo}.")
    bodies = [c.get("body", "") for c in comments] if isinstance(comments, list) else []
    return {"title": issue.get("title", ""), "body": issue.get("body", ""), "comments": bodies}


def fetch_note_text(source: str) -> str:
    """note:<absolute-path> or note:<permalink>; resolves against vault dirs."""
    ref = source.split(":", 1)[1] if ":" in source else source
    p = Path(ref)
    if p.is_file():
        return p.read_text(encoding="utf-8", errors="replace")
    for root in skillsource.catalog_roots():
        for cand in [root / f"{ref}.md", root / ref]:
            if cand.is_file():
                return cand.read_text(encoding="utf-8", errors="replace")
    raise FileNotFoundError(f"Note source not found: {source}")


def draft_section(skill_id: str, source_title: str, source_text: str, max_chars: int = 2000) -> str:
    """Deterministic first draft (LLM polish happens in the UI approval step)."""
    clipped = (source_text or "").strip()[:max_chars]
    lines = [ln for ln in clipped.splitlines() if ln.strip()][:40]
    digest = "\n".join(f"> {ln}" for ln in lines)
    return (
        f"## Distilled: {source_title}\n\n"
        f"Source: `{skill_id}` studio distillation. Review before keeping.\n\n"
        f"{digest}\n"
    )


async def distill_preview(skill_id: str, source: str) -> dict[str, Any]:
    """Build a draft without writing anything. Returns a pending job."""
    kind = source.split(":", 1)[0].lower() if ":" in source else ""
    try:
        if kind == "discussion":
            fetched = fetch_discussion(int(source.split(":", 1)[1]))
            text = fetched["body"] + "\n\n" + "\n\n".join(fetched["comments"])
            title = f"discussion #{source.split(':', 1)[1]}: {fetched['title']}"
        elif kind == "issue":
            fetched = fetch_issue(int(source.split(":", 1)[1]))
            text = fetched["body"] + "\n\n" + "\n\n".join(fetched["comments"])
            title = f"issue #{source.split(':', 1)[1]}: {fetched['title']}"
        elif kind == "note":
            text = fetch_note_text(source)
            title = source
        else:
            return {"success": False, "error": f"Unknown source '{source}'. Use discussion:<n>, issue:<n>, note:<path>."}
    except (ValueError, RuntimeError, FileNotFoundError, OSError) as exc:
        logger.warning(f"studio distill fetch failed: {exc}")
        return {"success": False, "error": str(exc)}
    draft = draft_section(skill_id, title, text)
    job = await repository.job_create(skill_id=skill_id, source=source, draft_md=draft)
    return {"success": True, "job_id": job["id"], "draft_md": draft, "source_title": title}


async def distill_apply(job_id: int, draft_md: str | None = None) -> dict[str, Any]:
    """Approved write: backup SKILL.md, append (or replace) the section."""
    job = await repository.job_get(job_id)
    if job is None:
        return {"success": False, "error": f"Job {job_id} not found."}
    if job["state"] == "applied":
        return {"success": False, "error": f"Job {job_id} already applied."}
    try:
        path = skillsource.find_skill_file(str(job["skill_id"]))
    except Exception:
        path = None
    if path is None:
        return {"success": False, "error": f"Skill file not found for '{job['skill_id']}'."}
    draft = draft_md if draft_md is not None else str(job["draft_md"])
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"SKILL.md.pre-studio-{stamp}")
    try:
        shutil.copy2(path, backup)
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n\n" + draft.strip() + "\n")
    except OSError as exc:
        return {"success": False, "error": f"Write failed: {exc}"}
    await repository.job_set_state(job_id, "applied", draft)
    return {"success": True, "path": str(path), "backup": str(backup)}
