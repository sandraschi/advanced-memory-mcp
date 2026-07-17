"""Direct research source implementations (web, arxiv, github).

Created 2026-07-17: skill_research_chain previously imported phantom tool
modules (adn_web_search, adn_arxiv_research, adn_github_research) that never
existed, so every source except rag silently returned zero snippets and
research-first skill creation produced ungrounded, hallucinated output.

Deliberately dependency-light: httpx + feedparser (both already in the venv),
no API keys required (GitHub token picked up from GITHUB_TOKEN/GH_TOKEN env if
present). Output shapes match skill_research_chain._extract_snippets:
  web    -> {"results": [{"title", "snippet", "url"}]}
  arxiv  -> {"papers":  [{"title", "abstract", "url"}]}
  github -> {"items":   [{"full_name", "description", "html_url"}]}
"""

from __future__ import annotations

import os
import re
from html import unescape
from typing import Any
from urllib.parse import unquote

import httpx
from loguru import logger

_UA = {"User-Agent": "advanced-memory-mcp/1.9 (local research tool)"}


def _strip_tags(s: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


async def web_search(query: str, max_results: int = 8) -> dict[str, Any]:
    """DuckDuckGo HTML search. Returns {"results": [...]}, empty list on failure."""
    results: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=_UA, follow_redirects=True) as client:
            resp = await client.post("https://html.duckduckgo.com/html/", data={"q": query})
        if resp.status_code != 200:
            logger.warning("web_search: duckduckgo returned HTTP %s", resp.status_code)
            return {"results": results}
        html = resp.text
        links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
        snips = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)>', html, re.S)
        for i, (url, title) in enumerate(links[: max_results]):
            m = re.search(r"uddg=([^&]+)", url)
            if m:
                url = unquote(m.group(1))
            snippet = snips[i] if i < len(snips) else ""
            results.append(
                {
                    "title": _strip_tags(title),
                    "snippet": _strip_tags(snippet)[:600],
                    "url": url,
                }
            )
    except Exception as exc:
        logger.warning("web_search failed: %s", exc)
    return {"results": results}


async def arxiv_search(query: str, max_results: int = 8) -> dict[str, Any]:
    """arXiv Atom API. Returns {"papers": [...]}, empty list on failure."""
    papers: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=20.0, headers=_UA) as client:
            resp = await client.get(
                "https://export.arxiv.org/api/query",
                params={
                    "search_query": f"all:{query}",
                    "max_results": max_results,
                    "sortBy": "relevance",
                },
            )
        if resp.status_code != 200:
            logger.warning("arxiv_search: HTTP %s", resp.status_code)
            return {"papers": papers}
        import feedparser

        feed = feedparser.parse(resp.text)
        for e in feed.entries[:max_results]:
            papers.append(
                {
                    "title": (e.get("title") or "").replace("\n", " ").strip(),
                    "abstract": (e.get("summary") or "").replace("\n", " ").strip()[:1200],
                    "url": e.get("link", ""),
                }
            )
    except Exception as exc:
        logger.warning("arxiv_search failed: %s", exc)
    return {"papers": papers}


async def github_search(query: str, max_results: int = 8) -> dict[str, Any]:
    """GitHub repository search. Returns {"items": [...]}, empty list on failure."""
    headers = dict(_UA)
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    items: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            resp = await client.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "per_page": max_results, "sort": "stars"},
            )
        if resp.status_code == 200:
            for r in resp.json().get("items", [])[:max_results]:
                items.append(
                    {
                        "full_name": r.get("full_name", ""),
                        "description": r.get("description") or "",
                        "html_url": r.get("html_url", ""),
                    }
                )
        else:
            logger.warning("github_search: HTTP %s", resp.status_code)
    except Exception as exc:
        logger.warning("github_search failed: %s", exc)
    return {"items": items}
