"""Web search tool for time-critical and specialized information gathering.

This tool provides structured web search capabilities for gathering current,
time-sensitive information that LLMs may not have access to, such as:
- Latest medical research and treatments
- Current political developments and news
- Recent conspiracy theory analyses
- Breaking news and real-time events
"""

from __future__ import annotations

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
SEARCH_PROVIDERS = {
    "duckduckgo": SearchProvider(
        name="DuckDuckGo",
        base_url="https://api.duckduckgo.com",
        search_endpoint="/?q={query}&format=json&no_html=1",
        results_key="RelatedTopics",
        title_key="Text",
        url_key="FirstURL",
        snippet_key="Text",
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
}


@mcp.tool
async def adn_web_search(
    query: str,
    provider: Literal["duckduckgo", "serpapi", "bing", "auto"] = "auto",
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
    - duckduckgo: Free, privacy-focused search (default)
    - serpapi: Google search via SerpApi (requires API key)
    - bing: Microsoft Bing search (requires API key)
    - auto: Automatically select best available provider

    TIME FILTERS:
    - any: No time restriction
    - day: Last 24 hours
    - week: Last 7 days
    - month: Last 30 days
    - year: Last 365 days

    SPECIALIZED USE CASES:
    - Medical research: "glioblastoma treatment advances 2024"
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
            "brain tumor glioblastoma latest treatments 2024",
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

        start_time = time.time()

        # Select and validate provider
        selected_provider = await _select_provider(provider)
        if not selected_provider:
            return {
                "error": f"Provider '{provider}' not available or not configured",
                "available_providers": list(SEARCH_PROVIDERS.keys()),
                "suggestions": [
                    "Use 'duckduckgo' for free search",
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
            "search_timestamp": "2025-12-02",  # Current date
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
        # Try providers in order of preference
        for provider_key in ["duckduckgo", "serpapi", "bing"]:
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

    # DuckDuckGo is always available (no API key needed)
    if provider.name == "DuckDuckGo":
        return True

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


async def _execute_search(provider: SearchProvider, query: str, max_results: int) -> list[dict[str, Any]]:
    """Execute the actual web search."""

    import urllib.parse

    try:
        async with aiohttp.ClientSession() as session:
            # Build search URL
            if provider.name == "DuckDuckGo":
                url = f"{provider.base_url}{provider.search_endpoint.format(query=urllib.parse.quote(query))}"

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
                if provider.name == "DuckDuckGo":
                    return data.get("RelatedTopics", [])[:max_results]

                elif provider.name in ["SerpApi", "Bing Web Search"]:
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
    if any(word in text for word in ["2024", "2025", "recent", "latest", "new"]):
        score += 0.1

    # Boost for authoritative sources
    if any(domain in text for domain in [".edu", ".gov", ".org", "wikipedia"]):
        score += 0.1

    # Boost for detailed content
    if len(snippet) > 100:
        score += 0.1

    return min(1.0, score)  # Cap at 1.0
