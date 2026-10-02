"""Web search tool for time-critical and specialized information gathering.

This tool provides structured web search capabilities for gathering current,
time-sensitive information that LLMs may not have access to, such as:
- Latest medical research and treatments
- Current political developments and news
- Recent conspiracy theory analyses
- Breaking news and real-time events
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

import aiohttp
from loguru import logger
from pydantic import BaseModel

from advanced_memory.mcp.mcp_instance import mcp


class SearchProvider(BaseModel):
    """Configuration for different search providers."""

    name: str
    api_key: str | None = None
    base_url: str
    search_endpoint: str
    results_key: str
    title_key: str
    url_key: str
    snippet_key: str
    date_key: str | None = None


class WebSearchResult(BaseModel):
    """Individual web search result."""

    title: str
    url: str
    snippet: str
    date: str | None = None
    source: str
    relevance_score: float = 0.0


class WebSearchResponse(BaseModel):
    """Complete web search response."""

    query: str
    provider: str
    total_results: int
    results: list[WebSearchResult]
    search_timestamp: str
    execution_time_seconds: float


# Provider configurations
# NOTE (2026-10-01): DuckDuckGo Instant Answer API (api.duckduckgo.com) is not a
# full search index - it returns RelatedTopics for entities and nothing for news.
# DDG provider now scrapes lite.duckduckgo.com first (full web results, keyless)
# with Instant Answer as fallback (Abstract + flattened RelatedTopics).
# Local OpenSERP (http://127.0.0.1:7000, Docker karust/openserp) is preferred.
def _openserp_base_url() -> str:
    import os

    return os.getenv("OPENSERP_BASE_URL", "http://127.0.0.1:7000").rstrip("/")


SEARCH_PROVIDERS = {
    "openserp": SearchProvider(
        name="OpenSERP",
        base_url=_openserp_base_url(),
        search_endpoint="/mega/search?text={query}&mode=any&engines=bing,duckduckgo,google",
        results_key="results",
        title_key="title",
        url_key="url",
        snippet_key="snippet",
        date_key=None,
    ),
    "duckduckgo": SearchProvider(
        name="DuckDuckGo",
        base_url="https://lite.duckduckgo.com",
        search_endpoint="/lite/?q={query}",
        results_key="lite",
        title_key="title",
        url_key="url",
        snippet_key="snippet",
        date_key=None,
    ),
    "serpapi": SearchProvider(
        name="SerpApi",
        base_url="https://serpapi.com",
        search_endpoint="/search.json?engine=google&q={query}&api_key={api_key}",
        results_key="organic_results",
        title_key="title",
        url_key="link",
        snippet_key="snippet",
        date_key="date",
    ),
    "bing": SearchProvider(
        name="Bing Web Search",
        base_url="https://api.bing.microsoft.com",
        search_endpoint="/v7.0/search?q={query}",
        results_key="webPages.value",
        title_key="name",
        url_key="url",
        snippet_key="snippet",
        date_key="datePublished",
    ),
    "tavily": SearchProvider(
        name="Tavily",
        base_url="https://api.tavily.com",
        search_endpoint="/search",
        results_key="results",
        title_key="title",
        url_key="url",
        snippet_key="content",
        date_key="published_date",
    ),
}


@mcp.tool
async def adn_web_search(
    query: str,
    provider: Literal["openserp", "tavily", "duckduckgo", "serpapi", "bing", "auto"] = "auto",
    max_results: int = 10,
    time_filter: Literal["any", "day", "week", "month", "year"] = "any",
    include_news: bool = False,
    relevance_threshold: float = 0.0,
    sources_filter: list[str] | None = None,
) -> dict[str, Any]:
    """
    Perform structured web search for time-critical and specialized information.

    This tool enables gathering current, real-time information from the web that
    LLMs may not have access to, such as breaking news, recent research, and
    time-sensitive developments.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates multiple search providers and filtering options into one tool
    for comprehensive web research capabilities.

    SEARCH PROVIDERS:
    - openserp: Local OpenSERP OSS (preferred, no key, OPENSERP_BASE_URL)
    - tavily: Tavily AI search (requires TAVILY_API_KEY, POST + extract-ready)
    - duckduckgo: Free lite scrape (no key, full web results) + Instant Answer fallback
    - serpapi: Google search via SerpApi (requires API key)
    - bing: Microsoft Bing search (requires API key)
    - auto: Automatically select best available provider (openserp first)

    TIME FILTERS:
    - any: No time restriction
    - day: Last 24 hours
    - week: Last 7 days
    - month: Last 30 days
    - year: Last 365 days

    SPECIALIZED USE CASES:
    - Medical research: "glioblastoma treatment advances" (time_filter="year")
    - Political news: "Trump Greenland complications latest developments"
    - Conspiracy analysis: "Kennedy assassination latest debunking evidence"

    Args:
        query: Search query string
        provider: Search provider to use
        max_results: Maximum number of results to return (1-50)
        time_filter: Time-based filtering for results
        include_news: Include news-specific results alongside web results
        relevance_threshold: Minimum relevance score (0.0-1.0)
        sources_filter: Only include results from specified domains

    Returns:
        dict[str, Any]: Structured search results with metadata

    Examples:
        # Medical research search
        await adn_web_search(
            "brain tumor glioblastoma latest treatments",
            provider="auto",
            time_filter="year",
            max_results=15
        )

        # Political news search
        await adn_web_search(
            "Trump Greenland complications latest news",
            provider="bing",
            time_filter="week",
            include_news=True
        )

        # Conspiracy analysis
        await adn_web_search(
            "Kennedy assassination conspiracy debunking evidence",
            provider="serpapi",
            sources_filter=["wikipedia.org", "history.com", "snopes.com"]
        )
    """

    try:
        import time
        from datetime import datetime, timezone

        start_time = time.time()

        # Select and validate provider
        selected_provider = await _select_provider(provider)
        if not selected_provider:
            return {
                "error": f"Provider '{provider}' not available or not configured",
                "available_providers": list(SEARCH_PROVIDERS.keys()),
                "suggestions": [
                    "Use 'openserp' for local search (needs OpenSERP on OPENSERP_BASE_URL)",
                    "Configure TAVILY_API_KEY for AI-friendly cloud search",
                    "Use 'duckduckgo' for free web search (lite scrape, no key)",
                    "Configure SERPAPI_API_KEY for Google search",
                    "Configure BING_API_KEY for Bing search",
                ],
            }

        # Build search query with time filtering
        enhanced_query = _enhance_query_with_time(query, time_filter)

        # Execute search
        raw_results = await _execute_search(selected_provider, enhanced_query, max_results)

        # Process and filter results
        processed_results = await _process_results(
            raw_results,
            selected_provider,
            relevance_threshold,
            sources_filter,
            include_news,
        )

        execution_time = time.time() - start_time

        return {
            "success": True,
            "query": query,
            "enhanced_query": enhanced_query,
            "provider": selected_provider.name,
            "time_filter": time_filter,
            "total_results": len(processed_results),
            "results": [result.model_dump() for result in processed_results],
            "search_timestamp": datetime.now(UTC).isoformat(),
            "execution_time_seconds": round(execution_time, 2),
            "filters_applied": {
                "relevance_threshold": relevance_threshold,
                "sources_filter": sources_filter,
                "include_news": include_news,
            },
        }

    except Exception as exc:
        logger.error("adn_web_search_error: %s", exc, exc_info=True)
        return {
            "success": False,
            "error": str(exc),
            "query": query,
            "provider": provider,
            "suggestions": [
                "Check network connectivity",
                "Verify API keys for paid providers",
                "Try a different search provider",
                "Simplify the search query",
            ],
        }


async def _select_provider(provider_name: str) -> SearchProvider | None:
    """Select and configure the appropriate search provider."""

    if provider_name == "auto":
        # Try providers in order of preference (local OpenSERP first)
        for provider_key in ["openserp", "tavily", "duckduckgo", "serpapi", "bing"]:
            provider = SEARCH_PROVIDERS[provider_key]
            if await _is_provider_available(provider):
                return provider
        return None

    provider = SEARCH_PROVIDERS.get(provider_name)
    if not provider:
        return None

    if await _is_provider_available(provider):
        return provider

    return None


async def _is_provider_available(provider: SearchProvider) -> bool:
    """Check if a search provider is available and configured."""

    # OpenSERP local and DuckDuckGo are always available (no API key needed)
    if provider.name in ("OpenSERP", "DuckDuckGo"):
        return True

    if provider.name == "Tavily":
        import os

        return bool(os.getenv("TAVILY_API_KEY"))

    # Check for API keys for paid providers
    if provider.name == "SerpApi":
        import os

        return bool(os.getenv("SERPAPI_API_KEY"))

    if provider.name == "Bing Web Search":
        import os

        return bool(os.getenv("BING_API_KEY"))

    return False


def _enhance_query_with_time(query: str, time_filter: str) -> str:
    """Enhance search query with time-based filtering."""

    if time_filter == "any":
        return query

    time_modifiers = {
        "day": "past 24 hours",
        "week": "past week",
        "month": "past month",
        "year": "past year",
    }

    time_modifier = time_modifiers.get(time_filter, "")
    if time_modifier:
        return f"{query} {time_modifier}"

    return query


# --- DuckDuckGo lite scrape (keyless full web results, 2026-10-01) ---
# Live lite.duckduckgo.com uses single quotes + href-before-class:
#   <a rel="nofollow" href="...uddg=..." class='result-link'>Title</a>
#   <td class='result-snippet'>Snippet</td>
import html as _html
import re as _re
import urllib.parse as _parse

_DDG_ANCHOR_RE = _re.compile(r"<a\s[^>]*?>(.*?)</a>", _re.S | _re.I)
_DDG_HREF_RE = _re.compile(r"href\s*=\s*[\"']([^\"']+)[\"']", _re.I)
_DDG_CLASS_RE = _re.compile(r"class\s*=\s*[\"']([^\"']*)[\"']", _re.I)
_DDG_SNIPPET_RE = _re.compile(r"<td[^>]*class\s*=\s*[\"']result-snippet[\"'][^>]*>(.*?)</td>", _re.S | _re.I)
_DDG_TAG_RE = _re.compile(r"<[^>]+>")
_DDG_BLOCKED = ("anomaly-modal", "challenge-form", "not a robot")


def _ddg_clean(raw: str) -> str:
    return _DDG_TAG_RE.sub("", _html.unescape(raw or "")).strip()


def _ddg_real_url(href: str) -> str:
    href = _html.unescape(href or "").strip()
    if "uddg=" in href:
        try:
            qs = _parse.parse_qs(_parse.urlsplit(href).query)
            if qs.get("uddg"):
                return qs["uddg"][0]
        except ValueError:
            pass
    if href.startswith("//"):
        return "https:" + href
    return href


def _ddg_parse_lite(body: str) -> list[dict[str, Any]]:
    """Parse lite HTML into title/url/snippet dicts (matches provider keys)."""
    if not body:
        return []
    snippets = [_ddg_clean(m.group(1)) for m in _DDG_SNIPPET_RE.finditer(body)]
    out: list[dict[str, Any]] = []
    idx = 0
    for anchor in _DDG_ANCHOR_RE.finditer(body):
        tag = anchor.group(0)
        inner = anchor.group(1)
        cls = _DDG_CLASS_RE.search(tag)
        if not cls or "result-link" not in cls.group(1).split():
            continue
        href_m = _DDG_HREF_RE.search(tag)
        if not href_m:
            continue
        title = _ddg_clean(inner)
        if not title or title.lower() == "more info":
            continue
        url = _ddg_real_url(href_m.group(1))
        if not url or not title:
            continue
        snippet = snippets[idx] if idx < len(snippets) else ""
        idx += 1
        out.append({"title": title, "url": url, "snippet": snippet})
    return out


async def _duckduckgo_lite_search(session: aiohttp.ClientSession, query: str, max_results: int) -> list[dict[str, Any]]:
    url = "https://lite.duckduckgo.com/lite/?" + _parse.urlencode({"q": query})
    async with session.get(url, headers={"User-Agent": "Advanced-Memory-MCP/1.0"}, timeout=30) as resp:
        body = await resp.text()
        if resp.status != 200 or any(m in body for m in _DDG_BLOCKED):
            return []
        return _ddg_parse_lite(body)[:max_results]


async def _duckduckgo_instant_fallback(
    session: aiohttp.ClientSession, query: str, max_results: int
) -> list[dict[str, Any]]:
    """Instant Answer API: Abstract + flattened RelatedTopics -> same shape."""
    import urllib.parse

    url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode({"q": query, "format": "json", "no_html": 1})
    async with session.get(url, headers={"User-Agent": "Advanced-Memory-MCP/1.0"}, timeout=30) as resp:
        if resp.status != 200:
            return []
        data = await resp.json()

    out: list[dict[str, Any]] = []
    abstract = (data.get("AbstractText") or "").strip()
    abstract_url = (data.get("AbstractURL") or "").strip()
    heading = (data.get("Heading") or "").strip()
    if abstract and abstract_url:
        out.append(
            {
                "title": heading or abstract[:80],
                "url": abstract_url,
                "snippet": abstract,
            }
        )

    def _flatten(topics: list[dict[str, Any]]) -> None:
        for item in topics or []:
            if not isinstance(item, dict):
                continue
            if "Topics" in item and isinstance(item["Topics"], list):
                _flatten(item["Topics"])
                continue
            text = (item.get("Text") or "").strip()
            first_url = (item.get("FirstURL") or "").strip()
            if text and first_url:
                # Split "Title - snippet" convention when present
                if " - " in text:
                    t, s = text.split(" - ", 1)
                else:
                    t, s = text[:80], text
                out.append({"title": t.strip(), "url": first_url, "snippet": s.strip()})
                if len(out) >= max_results:
                    return

    _flatten(data.get("RelatedTopics", []))
    return out[:max_results]


async def _execute_search(provider: SearchProvider, query: str, max_results: int) -> list[dict[str, Any]]:
    """Execute the actual web search."""

    import urllib.parse

    try:
        async with aiohttp.ClientSession() as session:
            # Tavily uses POST with JSON body
            if provider.name == "Tavily":
                import os

                api_key = os.getenv("TAVILY_API_KEY")
                if not api_key:
                    raise ValueError("TAVILY_API_KEY not configured")
                payload: dict[str, Any] = {
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": max_results,
                    "include_answer": False,
                }
                async with session.post(
                    f"{provider.base_url}{provider.search_endpoint}",
                    json=payload,
                    headers={"User-Agent": "Advanced-Memory-MCP/1.0"},
                    timeout=30,
                ) as response:
                    if response.status != 200:
                        raise ValueError(f"Search API returned status {response.status}")
                    data = await response.json()
                    return data.get("results", [])[:max_results]

            # Build search URL
            if provider.name == "OpenSERP":
                url = (
                    f"{provider.base_url}"
                    f"{provider.search_endpoint.format(query=urllib.parse.quote(query))}"
                    f"&limit={max_results}"
                )

            elif provider.name == "DuckDuckGo":
                lite_hits = await _duckduckgo_lite_search(session, query, max_results)
                if lite_hits:
                    return lite_hits
                # Fallback: Instant Answer entities (Abstract + RelatedTopics)
                return await _duckduckgo_instant_fallback(session, query, max_results)

            elif provider.name == "SerpApi":
                import os

                api_key = os.getenv("SERPAPI_API_KEY")
                if not api_key:
                    raise ValueError("SERPAPI_API_KEY not configured")
                url = f"{provider.base_url}{provider.search_endpoint.format(query=urllib.parse.quote(query), api_key=api_key)}"

            elif provider.name == "Bing Web Search":
                import os

                api_key = os.getenv("BING_API_KEY")
                if not api_key:
                    raise ValueError("BING_API_KEY not configured")
                url = f"{provider.base_url}{provider.search_endpoint.format(query=urllib.parse.quote(query))}"

            else:
                raise ValueError(f"Unsupported provider: {provider.name}")

            # Set headers
            headers = {"User-Agent": "Advanced-Memory-MCP/1.0"}
            if provider.name == "Bing Web Search":
                import os

                headers["Ocp-Apim-Subscription-Key"] = os.getenv("BING_API_KEY", "")

            # Execute request
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    raise ValueError(f"Search API returned status {response.status}")

                data = await response.json()

                # Extract results based on provider format
                if provider.name in ["OpenSERP", "Tavily", "SerpApi", "Bing Web Search"]:
                    results_key = provider.results_key
                    if "." in results_key:
                        # Handle nested keys like "webPages.value"
                        keys = results_key.split(".")
                        results = data
                        for key in keys:
                            results = results.get(key, [])
                        return results[:max_results]
                    else:
                        return data.get(results_key, [])[:max_results]

                else:
                    return []

    except Exception as e:
        logger.error(f"Search execution failed for {provider.name}: {e}")
        return []


async def _process_results(
    raw_results: list[dict[str, Any]],
    provider: SearchProvider,
    relevance_threshold: float,
    sources_filter: list[str] | None,
    include_news: bool,
) -> list[WebSearchResult]:
    """Process raw search results into structured format."""

    processed_results = []

    for item in raw_results:
        try:
            # Extract fields based on provider mapping
            title = item.get(provider.title_key, "")
            url = item.get(provider.url_key, "")
            snippet = item.get(provider.snippet_key, "")
            date = item.get(provider.date_key) if provider.date_key else None

            # Skip if missing essential fields
            if not title or not url:
                continue

            # Apply source filtering
            if sources_filter:
                from urllib.parse import urlparse

                domain = urlparse(url).netloc.lower()
                if not any(allowed_domain in domain for allowed_domain in sources_filter):
                    continue

            # Calculate relevance score (simple implementation)
            relevance_score = _calculate_relevance_score(title, snippet, relevance_threshold)

            if relevance_score < relevance_threshold:
                continue

            result = WebSearchResult(
                title=title,
                url=url,
                snippet=snippet,
                date=date,
                source=provider.name,
                relevance_score=relevance_score,
            )

            processed_results.append(result)

        except Exception as e:
            logger.warning(f"Failed to process search result: {e}")
            continue

    # Sort by relevance score
    processed_results.sort(key=lambda x: x.relevance_score, reverse=True)

    return processed_results[:50]  # Limit to prevent overwhelming responses


def _calculate_relevance_score(title: str, snippet: str, threshold: float) -> float:
    """Calculate a simple relevance score for search results."""

    # This is a basic implementation - in practice, you'd want more sophisticated
    # relevance scoring based on the search query, recency, authority, etc.

    text = f"{title} {snippet}".lower()

    # Boost score for certain indicators of quality/relevance
    score = 0.5  # Base score

    # Boost for recent content indicators
    year = datetime.now(UTC).year
    if any(word in text for word in [str(year - 1), str(year), "recent", "latest", "new"]):
        score += 0.1

    # Boost for authoritative sources
    if any(domain in text for domain in [".edu", ".gov", ".org", "wikipedia"]):
        score += 0.1

    # Boost for detailed content
    if len(snippet) > 100:
        score += 0.1

    return min(1.0, score)  # Cap at 1.0
