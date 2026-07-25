"""Wiki REST API router for Advanced Memory.

Serves the compiled wiki index and page content to the frontend.
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from loguru import logger

from advanced_memory.config import ConfigManager

router = APIRouter(prefix="/api/v1/wiki", tags=["wiki"])


def _wiki_root() -> Path:
    cfg = ConfigManager().config
    return cfg.app_database_path.parent / "wiki" / "compiled"


@router.get("/status")
async def wiki_status():
    """Return compilation status and stats."""
    root = _wiki_root()
    index_path = root / "INDEX.json"
    if not index_path.exists():
        return {"compiled": False, "page_count": 0}
    index = json.loads(index_path.read_text(encoding="utf-8"))
    total_size = sum(f.stat().st_size for f in root.glob("*") if f.is_file())
    return {
        "compiled": True,
        "page_count": index["page_count"],
        "entity_count": index["entity_count"],
        "compiled_at": index["compiled_at"],
        "total_size_bytes": total_size,
    }


@router.get("/index")
async def wiki_index():
    """Return the compiled wiki INDEX.json."""
    root = _wiki_root()
    index_path = root / "INDEX.json"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="No wiki compiled yet. Run adn_wiki(operation='compile') first.")
    return json.loads(index_path.read_text(encoding="utf-8"))


@router.get("/page/{permalink:path}")
async def wiki_page(permalink: str):
    """Return a compiled wiki page by permalink."""
    root = _wiki_root()
    page_file = root / f"{permalink}.md"
    if not page_file.exists():
        index_path = root / "INDEX.json"
        if index_path.exists():
            index = json.loads(index_path.read_text(encoding="utf-8"))
            for p in index["pages"]:
                if p["permalink"] == permalink:
                    page_file = root / f"{p['permalink']}.md"
                    break
    if not page_file.exists():
        raise HTTPException(status_code=404, detail=f"Wiki page '{permalink}' not found")
    return {"permalink": permalink, "content": page_file.read_text(encoding="utf-8")}


@router.get("/search")
async def wiki_search(q: str = ""):
    """Search compiled wiki page titles."""
    if not q:
        return {"results": []}
    root = _wiki_root()
    index_path = root / "INDEX.json"
    if not index_path.exists():
        return {"results": []}
    index = json.loads(index_path.read_text(encoding="utf-8"))
    ql = q.lower()
    results = [p for p in index["pages"] if ql in p["title"].lower()]
    return {"results": results, "total": len(results)}
