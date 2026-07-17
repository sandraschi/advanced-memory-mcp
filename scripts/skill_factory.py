"""Skill factory batch tool - triage, enrich, promote, archive the skill catalog.

Created 2026-07-17 (TODO P3). Reality check that shaped this tool: the
~/.claude/skills catalog has 26 top-level skills (discoverable by Claude Code)
plus ~105 category-nested ones (linguistic/, technical/, ...) that Claude Code
CANNOT discover because it only scans <root>/<name>/SKILL.md. Most nested
skills have real content; the 'Draft scaffold' status shown by adn_skills list
is merely the default for missing frontmatter metadata (adn_skills.py:593).

Therefore: no blind regeneration (a small local model rewriting an already
correct keigo table is a downgrade). Instead, explicit subcommands:

  inventory                     - table: category, skill, size, compliant, status
  metadata                      - patch frontmatter (status/category) on nested
                                  skills so adn_skills list shows truth
  enrich   --category X [--limit N] [--min-bytes B]
                                - research_first_create ONLY for thin skills
                                  (< min-bytes, default 1200); original kept as
                                  SKILL.md.pre-factory
  promote  --category X         - copy spec-compliant nested skills to top level
                                  (Claude-discoverable); no overwrite of
                                  existing top-level names
  archive  --category X         - move category out of the active tree to
                                  _archive/ (still on disk, not discoverable)

Run: uv run --directory D:\\Dev\\repos\\advanced-memory-mcp python scripts/skill_factory.py <cmd> ...
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILLS_ROOT = Path.home() / ".claude" / "skills"
ARCHIVE_DIR = SKILLS_ROOT / "_archive"
CATEGORY_DIRS_EXCLUDE = {"_archive"}
THIN_BYTES_DEFAULT = 1200

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _categories() -> list[Path]:
    """Category dirs = dirs with SKILL.md children one level down.

    Note: categories are HYBRIDS - they carry their own hub SKILL.md (the
    'door' skill Claude Code discovers) AND nested sub-skill dirs. So having
    a top-level SKILL.md does not disqualify a dir from being a category.
    """
    cats = []
    for d in sorted(SKILLS_ROOT.iterdir()):
        if not d.is_dir() or d.name in CATEGORY_DIRS_EXCLUDE:
            continue
        if any((c / "SKILL.md").exists() for c in d.iterdir() if c.is_dir()):
            cats.append(d)
    return cats


def _skills_in(cat: Path) -> list[Path]:
    return sorted(c for c in cat.iterdir() if c.is_dir() and (c / "SKILL.md").exists())


def _validate(skill_dir: Path):
    from advanced_memory.services.skill_creator import validate_skill_agentskills

    try:
        ok, warnings, checks = validate_skill_agentskills(skill_dir)
        return ok, warnings
    except Exception as exc:
        return False, [f"validator error: {exc}"]


def _read_frontmatter(md: Path) -> tuple[dict, str]:
    text = md.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = {}
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip()
            return fm, parts[2]
    return {}, text


def cmd_inventory(_args) -> int:
    total = thin = noncompliant = 0
    for cat in _categories():
        print(f"\n== {cat.name} ==")
        for s in _skills_in(cat):
            md = s / "SKILL.md"
            size = md.stat().st_size
            ok, _ = _validate(s)
            fm, _ = _read_frontmatter(md)
            status = fm.get("status", "(no status metadata)")
            marks = []
            if size < THIN_BYTES_DEFAULT:
                marks.append("THIN")
                thin += 1
            if not ok:
                marks.append("NONCOMPLIANT")
                noncompliant += 1
            total += 1
            print(f"  {s.name:44s} {size:6d}B  {' '.join(marks) or 'ok':14s} {status[:40]}")
    top = [d for d in SKILLS_ROOT.iterdir() if d.is_dir() and (d / 'SKILL.md').exists()]
    print(f"\nTotals: {total} nested skills ({thin} thin, {noncompliant} noncompliant), "
          f"{len(top)} top-level (Claude-discoverable)")
    return 0


def cmd_metadata(_args) -> int:
    """Add status/category frontmatter so adn_skills list stops defaulting to 'Draft scaffold'."""
    patched = 0
    for cat in _categories():
        for s in _skills_in(cat):
            md = s / "SKILL.md"
            fm, body = _read_frontmatter(md)
            if "status" in fm and "category" in fm:
                continue
            size = md.stat().st_size
            fm.setdefault("category", cat.name)
            fm.setdefault(
                "status",
                "catalog - thin, needs enrichment" if size < THIN_BYTES_DEFAULT else "catalog - substantive",
            )
            fm_text = "\n".join(f"{k}: {v}" for k, v in fm.items())
            md.write_text(f"---\n{fm_text}\n---{body}", encoding="utf-8")
            patched += 1
    print(f"metadata: patched {patched} skills")
    return 0


def cmd_enrich(args) -> int:
    import asyncio

    from advanced_memory.mcp.tools.make_skill_advanced import make_skill_advanced

    fn = getattr(make_skill_advanced, "fn", make_skill_advanced)
    cat = SKILLS_ROOT / args.category
    if not cat.is_dir():
        print(f"no such category: {args.category}", file=sys.stderr)
        return 1

    done = 0
    for s in _skills_in(cat):
        if done >= args.limit:
            break
        md = s / "SKILL.md"
        if md.stat().st_size >= args.min_bytes:
            continue
        fm, _ = _read_frontmatter(md)
        topic = fm.get("description") or s.name.replace("-", " ")
        print(f"enrich: {s.name} ({md.stat().st_size}B) topic='{topic[:60]}'")
        shutil.copy2(md, s / "SKILL.md.pre-factory")
        result = asyncio.run(
            fn(
                operation="research_first_create",
                topic=topic,
                skill_name=s.name,
                output_path=str(cat),
                research_sources=["web"],
                max_research_iterations=1,
                enable_review_loop=True,
            )
        )
        ok = result.get("success") and result.get("spec_compliant")
        print(f"  -> success={result.get('success')} compliant={result.get('spec_compliant')} "
              f"coverage={result.get('coverage_score')}")
        if not ok:
            # restore original rather than leave a worse artifact
            shutil.copy2(s / "SKILL.md.pre-factory", md)
            print("  -> restored original (generation not compliant)")
        else:
            fm2, body2 = _read_frontmatter(md)
            fm2["category"] = cat.name
            fm2["status"] = "enriched via research_first_create 2026-07-17"
            fm_text = "\n".join(f"{k}: {v}" for k, v in fm2.items())
            md.write_text(f"---\n{fm_text}\n---{body2}", encoding="utf-8")
        done += 1
    print(f"enrich: processed {done} thin skill(s) in {args.category}")
    return 0


def cmd_fix_names(_args) -> int:
    """Set frontmatter name = directory name (agentskills name_matches_directory)."""
    fixed = 0
    for cat in _categories():
        for s in _skills_in(cat):
            md = s / "SKILL.md"
            fm, body = _read_frontmatter(md)
            if fm.get("name") == s.name:
                continue
            fm["name"] = s.name
            fm_text = "\n".join(f"{k}: {v}" for k, v in fm.items())
            md.write_text(f"---\n{fm_text}\n---{body}", encoding="utf-8")
            fixed += 1
            print(f"fixed name: {cat.name}/{s.name}")
    print(f"fix-names: {fixed} corrected")
    return 0


def cmd_doorify(_args) -> int:
    """Append an explicit sub-skill file listing to each category hub SKILL.md.

    The hubs reference sub-skills by bare name; Claude can only load them if
    it knows the relative path to Read. Idempotent (marker section).
    """
    marker = "## Sub-skill files (staged loading)"
    patched = 0
    for cat in _categories():
        hub = cat / "SKILL.md"
        if not hub.exists():
            continue
        text = hub.read_text(encoding="utf-8", errors="replace")
        if marker in text:
            continue
        lines = [
            "",
            marker,
            "",
            "Load a sub-skill on demand by reading its file (paths relative to this skill's folder):",
            "",
        ]
        for s in _skills_in(cat):
            fm, _ = _read_frontmatter(s / "SKILL.md")
            desc = fm.get("description", "")[:90]
            lines.append(f"- `./{s.name}/SKILL.md` - {desc}")
        hub.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
        patched += 1
        print(f"doorified: {cat.name} ({len(_skills_in(cat))} sub-skills listed)")
    print(f"doorify: patched {patched} category hubs")
    return 0


def cmd_promote(args) -> int:
    cat = SKILLS_ROOT / args.category
    if not cat.is_dir():
        print(f"no such category: {args.category}", file=sys.stderr)
        return 1
    promoted = skipped = 0
    for s in _skills_in(cat):
        target = SKILLS_ROOT / s.name
        if target.exists():
            print(f"skip (exists top-level): {s.name}")
            skipped += 1
            continue
        ok, warnings = _validate(s)
        if not ok:
            print(f"skip (noncompliant): {s.name} {warnings[:1]}")
            skipped += 1
            continue
        shutil.copytree(s, target)
        promoted += 1
        print(f"promoted: {s.name}")
    print(f"promote: {promoted} promoted, {skipped} skipped from {args.category}")
    return 0


def cmd_archive(args) -> int:
    cat = SKILLS_ROOT / args.category
    if not cat.is_dir():
        print(f"no such category: {args.category}", file=sys.stderr)
        return 1
    ARCHIVE_DIR.mkdir(exist_ok=True)
    target = ARCHIVE_DIR / args.category
    if target.exists():
        print(f"archive target exists: {target}", file=sys.stderr)
        return 1
    shutil.move(str(cat), str(target))
    print(f"archived: {args.category} -> _archive/{args.category}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inventory")
    sub.add_parser("metadata")
    sub.add_parser("doorify")
    sub.add_parser("fix-names")
    e = sub.add_parser("enrich")
    e.add_argument("--category", required=True)
    e.add_argument("--limit", type=int, default=3)
    e.add_argument("--min-bytes", type=int, default=THIN_BYTES_DEFAULT)
    pr = sub.add_parser("promote")
    pr.add_argument("--category", required=True)
    a = sub.add_parser("archive")
    a.add_argument("--category", required=True)
    args = p.parse_args()
    return {
        "inventory": cmd_inventory,
        "metadata": cmd_metadata,
        "doorify": cmd_doorify,
        "fix-names": cmd_fix_names,
        "enrich": cmd_enrich,
        "promote": cmd_promote,
        "archive": cmd_archive,
    }[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
