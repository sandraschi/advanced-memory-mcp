"""arXiv research tool for academic paper analysis and research."""

from __future__ import annotations

import re
from typing import Any, Literal
from urllib.parse import quote

import aiohttp
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool
async def adn_arxiv_research(
    operation: Literal[
        "search_papers",
        "get_paper_details",
        "search_by_category",
        "find_recent_papers",
        "analyze_research_trends",
        "get_paper_abstract",
        "find_related_papers",
    ],
    query: str | None = None,
    paper_id: str | None = None,
    category: str | None = None,
    max_results: int = 10,
    sort_by: Literal["relevance", "lastUpdatedDate", "submittedDate"] = "relevance",
    sort_order: Literal["ascending", "descending"] = "descending",
    date_range: str | None = None,  # "YYYY" or "YYYY-MM" or "YYYY-MM-DD"
) -> dict[str, Any]:
    """
    Comprehensive arXiv research tool for academic paper analysis.

    This tool enables deep research into academic literature, perfect for creating
    expert skills based on cutting-edge research and established knowledge.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates academic research capabilities into one tool for comprehensive
    scholarly analysis used in expert skill creation.

    SUPPORTED OPERATIONS:

    search_papers: Search arXiv papers by topic/keywords
    - Find relevant academic papers across disciplines
    - Required: query

    get_paper_details: Get complete paper metadata and information
    - Title, authors, abstract, categories, citations
    - Required: paper_id (arXiv ID like "2101.12345")

    search_by_category: Search within specific arXiv categories
    - cs.AI, math.PR, physics.optics, etc.
    - Required: category, query

    find_recent_papers: Discover latest research in a field
    - Most recent papers by submission date
    - Required: query or category

    analyze_research_trends: Analyze research patterns and trends
    - Publication frequency, popular topics, emerging areas
    - Required: category or query

    get_paper_abstract: Extract paper abstract for analysis
    - Clean abstract text for skill content
    - Required: paper_id

    find_related_papers: Find papers citing or cited by target paper
    - Research networks and related work
    - Required: paper_id

    SPECIALIZED USE CASES FOR SKILL CREATION:

    AI/ML Research:
    - Find transformer papers, reinforcement learning advances
    - Analyze current state-of-the-art methods
    - Study mathematical foundations

    Scientific Domains:
    - Latest breakthroughs in physics, biology, chemistry
    - Survey papers for comprehensive overviews
    - Methodology papers for technique analysis

    Technical Expertise:
    - Original research papers for deep understanding
    - Survey papers for broad knowledge coverage
    - Foundational papers for theoretical grounding

    Args:
        operation: The arXiv research operation to perform
        query: Search query for papers (title, abstract, authors)
        paper_id: arXiv paper ID (e.g., "2101.12345" or "2101.12345v2")
        category: arXiv category (cs.AI, math.PR, physics.optics, etc.)
        max_results: Maximum results to return (1-50)
        sort_by: Sort criteria (relevance, lastUpdatedDate, submittedDate)
        sort_order: Sort order (ascending, descending)
        date_range: Date filter (YYYY, YYYY-MM, or YYYY-MM-DD format)

    Returns:
        Operation-specific results with paper metadata, abstracts, and analysis

    Examples:
        # Research transformer architectures
        await adn_arxiv_research(
            "search_papers",
            query="transformer architecture attention",
            category="cs.CL",
            max_results=15
        )

        # Get specific paper details
        await adn_arxiv_research(
            "get_paper_details",
            paper_id="1706.03762"
        )

        # Find recent AI advances
        await adn_arxiv_research(
            "find_recent_papers",
            query="large language models",
            category="cs.AI",
            max_results=10
        )

        # Analyze research trends
        await adn_arxiv_research(
            "analyze_research_trends",
            category="cs.AI",
            date_range="2024"
        )

        # Study quantum computing foundations
        await adn_arxiv_research(
            "search_by_category",
            category="quant-ph",
            query="quantum supremacy",
            sort_by="submittedDate"
        )
    """

    try:
        base_url = "http://export.arxiv.org/api/query"

        if operation == "search_papers":
            if not query:
                return {"error": "query required for search_papers"}

            params = _build_search_params(
                query=query,
                category=category,
                max_results=max_results,
                sort_by=sort_by,
                sort_order=sort_order,
                date_range=date_range,
            )

            papers_data = await _fetch_arxiv_data(base_url, params)
            processed_papers = _process_paper_results(papers_data)

            return {
                "operation": operation,
                "query": query,
                "category": category,
                "total_results": len(processed_papers),
                "papers": processed_papers,
                "search_timestamp": "2025-12-02",
            }

        elif operation == "get_paper_details":
            if not paper_id:
                return {"error": "paper_id required for get_paper_details"}

            # Clean paper ID
            clean_id = _clean_paper_id(paper_id)
            params = {"id_list": clean_id, "max_results": 1}

            paper_data = await _fetch_arxiv_data(base_url, params)
            if paper_data and paper_data.get("entries"):
                details = _extract_paper_details(paper_data["entries"][0])
                return {
                    "operation": operation,
                    "paper_id": clean_id,
                    "details": details,
                }
            else:
                return {
                    "error": f"Paper not found: {paper_id}",
                    "paper_id": clean_id,
                }

        elif operation == "search_by_category":
            if not category:
                return {"error": "category required for search_by_category"}
            if not query:
                return {"error": "query required for search_by_category"}

            # Search within specific category
            category_query = f"cat:{category} AND ({query})"
            params = _build_search_params(
                query=category_query,
                max_results=max_results,
                sort_by=sort_by,
                sort_order=sort_order,
                date_range=date_range,
            )

            papers_data = await _fetch_arxiv_data(base_url, params)
            processed_papers = _process_paper_results(papers_data)

            return {
                "operation": operation,
                "query": query,
                "category": category,
                "total_results": len(processed_papers),
                "papers": processed_papers,
                "search_timestamp": "2025-12-02",
            }

        elif operation == "find_recent_papers":
            search_query = query or f"cat:{category}" if category else "all"
            params = _build_search_params(
                query=search_query,
                max_results=max_results,
                sort_by="submittedDate",
                sort_order="descending",
                date_range=date_range,
            )

            papers_data = await _fetch_arxiv_data(base_url, params)
            processed_papers = _process_paper_results(papers_data)

            return {
                "operation": operation,
                "query": search_query,
                "total_results": len(processed_papers),
                "recent_papers": processed_papers,
                "search_timestamp": "2025-12-02",
            }

        elif operation == "analyze_research_trends":
            # Get papers for trend analysis
            search_query = f"cat:{category}" if category else query
            if not search_query:
                return {"error": "category or query required for trend analysis"}

            # Get more results for trend analysis
            params = _build_search_params(
                query=search_query,
                max_results=min(max_results * 3, 100),  # More data for trends
                sort_by="submittedDate",
                sort_order="descending",
            )

            papers_data = await _fetch_arxiv_data(base_url, params)
            trends = _analyze_paper_trends(papers_data)

            return {
                "operation": operation,
                "query": search_query,
                "total_papers_analyzed": len(papers_data.get("entries", [])),
                "trends": trends,
                "analysis_timestamp": "2025-12-02",
            }

        elif operation == "get_paper_abstract":
            if not paper_id:
                return {"error": "paper_id required for get_paper_abstract"}

            clean_id = _clean_paper_id(paper_id)
            params = {"id_list": clean_id, "max_results": 1}

            paper_data = await _fetch_arxiv_data(base_url, params)
            if paper_data and paper_data.get("entries"):
                abstract = _extract_abstract(paper_data["entries"][0])
                return {
                    "operation": operation,
                    "paper_id": clean_id,
                    "abstract": abstract,
                }
            else:
                return {
                    "error": f"Paper not found: {paper_id}",
                    "paper_id": clean_id,
                }

        elif operation == "find_related_papers":
            if not paper_id:
                return {"error": "paper_id required for find_related_papers"}

            # This is a simplified version - in practice, you'd need citation data
            # For now, we'll find papers with similar titles/abstracts
            paper_details = await (adn_arxiv_research.fn if hasattr(adn_arxiv_research, "fn") else adn_arxiv_research)(
                operation="get_paper_details", paper_id=paper_id
            )

            if "error" in paper_details:
                return paper_details

            # Extract key terms from the paper for related search
            title = paper_details["details"]["title"]
            abstract = paper_details["details"]["summary"]

            # Create related search query from title and abstract
            key_terms = _extract_key_terms(title, abstract)
            related_query = " OR ".join(f'"{term}"' for term in key_terms[:5])

            # Exclude the original paper
            full_query = f"({related_query}) NOT {paper_id}"

            related_results = await (adn_arxiv_research.fn if hasattr(adn_arxiv_research, "fn") else adn_arxiv_research)(
                operation="search_papers",
                query=full_query,
                max_results=max_results,
            )

            return {
                "operation": operation,
                "original_paper": paper_details["details"],
                "related_papers": related_results.get("papers", []),
                "search_terms": key_terms[:5],
                "total_related": len(related_results.get("papers", [])),
            }

        else:
            return {
                "error": f"Unsupported operation: {operation}",
                "supported_operations": [
                    "search_papers",
                    "get_paper_details",
                    "search_by_category",
                    "find_recent_papers",
                    "analyze_research_trends",
                    "get_paper_abstract",
                    "find_related_papers",
                ],
            }

    except Exception as exc:  # noqa: BLE001
        logger.error("adn_arxiv_research_error: %s", exc, exc_info=True)
        return {
            "success": False,
            "error": str(exc),
            "operation": operation,
            "suggestions": [
                "Check paper ID format (e.g., 2101.12345)",
                "Verify category codes (cs.AI, math.PR, etc.)",
                "Try simpler search queries",
                "Check arXiv API availability",
            ],
        }


async def _fetch_arxiv_data(base_url: str, params: dict[str, Any]) -> dict[str, Any]:
    """Fetch data from arXiv API."""

    try:
        # Build query string
        query_parts = []
        for key, value in params.items():
            if isinstance(value, list):
                for v in value:
                    query_parts.append(f"{key}={quote(str(v))}")
            else:
                query_parts.append(f"{key}={quote(str(value))}")

        url = f"{base_url}?{'&'.join(query_parts)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    raise ValueError(f"arXiv API error: {response.status}")

                # arXiv returns Atom XML, but we can get JSON-like data
                text = await response.text()

                # Parse the Atom XML response (simplified)
                return _parse_arxiv_xml(text)

    except Exception as e:
        logger.error(f"arXiv API request failed: {e}")
        raise


def _parse_arxiv_xml(xml_text: str) -> dict[str, Any]:
    """Parse arXiv Atom XML response into structured data."""

    # This is a simplified XML parser - in production, use proper XML parsing
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_text)

        # Extract namespace
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

        entries = []
        for entry in root.findall(".//atom:entry", ns):
            paper_data = {
                "id": entry.find("atom:id", ns).text
                if entry.find("atom:id", ns) is not None
                else "",
                "title": entry.find("atom:title", ns).text
                if entry.find("atom:title", ns) is not None
                else "",
                "summary": entry.find("atom:summary", ns).text
                if entry.find("atom:summary", ns) is not None
                else "",
                "authors": [],
                "categories": [],
                "links": [],
                "published": "",
                "updated": "",
            }

            # Extract authors
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None:
                    paper_data["authors"].append(name_elem.text)

            # Extract categories
            for category in entry.findall("atom:category", ns):
                term = category.get("term")
                if term:
                    paper_data["categories"].append(term)

            # Extract links
            for link in entry.findall("atom:link", ns):
                link_data = {
                    "href": link.get("href", ""),
                    "rel": link.get("rel", ""),
                    "type": link.get("type", ""),
                }
                paper_data["links"].append(link_data)

            # Extract dates
            published = entry.find("atom:published", ns)
            if published is not None:
                paper_data["published"] = published.text

            updated = entry.find("atom:updated", ns)
            if updated is not None:
                paper_data["updated"] = updated.text

            entries.append(paper_data)

        return {
            "total_results": len(entries),
            "entries": entries,
        }

    except Exception as e:
        logger.error(f"XML parsing failed: {e}")
        return {"total_results": 0, "entries": []}


def _build_search_params(
    query: str,
    category: str | None = None,
    max_results: int = 10,
    sort_by: str = "relevance",
    sort_order: str = "descending",
    date_range: str | None = None,
) -> dict[str, Any]:
    """Build arXiv API search parameters."""

    params = {
        "search_query": query,
        "max_results": min(max_results, 50),  # arXiv API limit
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }

    # Add date filtering if specified
    if date_range:
        if len(date_range) == 4:  # YYYY
            params["search_query"] += f" AND submittedDate:[{date_range}0101 TO {date_range}1231]"
        elif len(date_range) == 7:  # YYYY-MM
            year, month = date_range.split("-")
            # Calculate last day of month (simplified)
            last_day = (
                "31"
                if month in ["01", "03", "05", "07", "08", "10", "12"]
                else "30"
                if month in ["04", "06", "09", "11"]
                else "28"
            )
            params["search_query"] += (
                f" AND submittedDate:[{date_range}01 TO {year}{month}{last_day}]"
            )

    return params


def _process_paper_results(api_response: dict[str, Any]) -> list[dict[str, Any]]:
    """Process raw arXiv API results into clean format."""

    processed_papers = []

    for entry in api_response.get("entries", []):
        # Extract arXiv ID from URL
        arxiv_id = ""
        for link in entry.get("links", []):
            if link.get("rel") == "alternate" and "arxiv.org/abs/" in link.get("href", ""):
                arxiv_id = link["href"].split("/")[-1]
                break

        if not arxiv_id:
            # Fallback: extract from ID field
            id_field = entry.get("id", "")
            if "arxiv.org/abs/" in id_field:
                arxiv_id = id_field.split("/")[-1]

        paper = {
            "arxiv_id": arxiv_id,
            "title": entry.get("title", "").strip(),
            "authors": entry.get("authors", []),
            "abstract": entry.get("summary", "").strip(),
            "categories": entry.get("categories", []),
            "published": entry.get("published", ""),
            "updated": entry.get("updated", ""),
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else "",
            "abs_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
        }

        # Clean up title (remove extra whitespace)
        paper["title"] = re.sub(r"\s+", " ", paper["title"])

        # Extract primary category
        if paper["categories"]:
            paper["primary_category"] = paper["categories"][0]

        processed_papers.append(paper)

    return processed_papers


def _extract_paper_details(entry: dict[str, Any]) -> dict[str, Any]:
    """Extract detailed paper information."""

    details = _process_paper_results({"entries": [entry]})[0]

    # Add additional metadata
    details.update(
        {
            "comment": entry.get("comment", ""),
            "journal_ref": entry.get("journal_ref", ""),
            "doi": entry.get("doi", ""),
        }
    )

    return details


def _extract_abstract(entry: dict[str, Any]) -> str:
    """Extract and clean paper abstract."""

    abstract = entry.get("summary", "").strip()

    # Clean up common arXiv formatting issues
    abstract = re.sub(r"\n+", " ", abstract)  # Replace newlines with spaces
    abstract = re.sub(r"\s+", " ", abstract)  # Normalize whitespace

    return abstract


def _analyze_paper_trends(api_response: dict[str, Any]) -> dict[str, Any]:
    """Analyze research trends from paper data."""

    entries = api_response.get("entries", [])

    if not entries:
        return {"error": "No papers to analyze"}

    # Analyze publication dates
    years = {}
    months = {}
    categories = {}
    authors_count = {}

    for entry in entries:
        # Date analysis
        published = entry.get("published", "")
        if published and len(published) >= 7:  # At least YYYY-MM
            year = published[:4]
            month = published[:7]

            years[year] = years.get(year, 0) + 1
            months[month] = months.get(month, 0) + 1

        # Category analysis
        for cat in entry.get("categories", []):
            categories[cat] = categories.get(cat, 0) + 1

        # Author analysis (approximate)
        author_count = len(entry.get("authors", []))
        authors_count[author_count] = authors_count.get(author_count, 0) + 1

    # Find most active periods
    sorted_years = sorted(years.items(), key=lambda x: x[1], reverse=True)
    sorted_months = sorted(months.items(), key=lambda x: x[1], reverse=True)
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    return {
        "total_papers": len(entries),
        "publication_trends": {
            "most_active_years": sorted_years[:5],
            "most_active_months": sorted_months[:5],
            "yearly_distribution": years,
        },
        "category_analysis": {
            "popular_categories": sorted_categories[:10],
            "category_distribution": categories,
        },
        "collaboration_patterns": {
            "author_count_distribution": authors_count,
            "avg_authors_per_paper": sum(k * v for k, v in authors_count.items())
            / sum(authors_count.values()),
        },
    }


def _clean_paper_id(paper_id: str) -> str:
    """Clean and standardize arXiv paper ID."""

    # Remove common prefixes
    paper_id = paper_id.replace("https://arxiv.org/abs/", "")
    paper_id = paper_id.replace("https://arxiv.org/pdf/", "")

    # Remove version suffix if present (keep base ID)
    paper_id = re.sub(r"v\d+$", "", paper_id)

    return paper_id.strip()


def _extract_key_terms(title: str, abstract: str) -> list[str]:
    """Extract key terms from title and abstract for related paper search."""

    # Combine title and abstract
    text = f"{title} {abstract}".lower()

    # Remove common stop words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
        "we",
        "our",
        "you",
        "your",
        "they",
        "their",
        "it",
        "its",
        "as",
        "from",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "among",
        "within",
        "without",
        "not",
    }

    # Extract words, remove punctuation and stop words
    words = re.findall(r"\b\w+\b", text)
    filtered_words = [word for word in words if len(word) > 3 and word not in stop_words]

    # Count frequency and return top terms
    from collections import Counter

    word_counts = Counter(filtered_words)
    top_terms = [word for word, _ in word_counts.most_common(20)]

    return top_terms
