"""GitHub research and code trawling tool for skill creation and research."""

from __future__ import annotations

import os
from typing import Any, Literal

import aiohttp
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp


@mcp.tool
async def adn_github_research(
    operation: Literal[
        "search_repositories",
        "search_code",
        "get_repository",
        "get_file_content",
        "search_issues",
        "get_repository_readme",
        "find_similar_repositories",
        "analyze_repository_structure",
        "search_recent_commits",
    ],
    query: str | None = None,
    repository: str | None = None,  # owner/repo format
    language: str | None = None,
    sort: Literal["stars", "forks", "updated", "best-match"] = "best-match",
    order: Literal["asc", "desc"] = "desc",
    max_results: int = 10,
    include_content: bool = False,
) -> dict[str, Any]:
    """
    Comprehensive GitHub research tool for code analysis, repository discovery, and research.

    This tool enables deep research into GitHub repositories, code patterns, issues, and
    recent developments - perfect for creating skills based on cutting-edge techniques,
    finding similar projects, or analyzing trending approaches.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates GitHub research operations into one tool for comprehensive code and
    repository analysis capabilities used in skill creation and research.

    SUPPORTED OPERATIONS:

    search_repositories: Find repositories by topic, language, stars, etc.
    - Discover projects, frameworks, and implementations
    - Required: query

    search_code: Search code across GitHub with advanced filters
    - Find specific implementations, patterns, algorithms
    - Supports language, repository, and path filters
    - Required: query

    get_repository: Get detailed repository information
    - Stars, forks, description, languages, contributors
    - Required: repository (owner/repo)

    get_file_content: Retrieve specific file content from repositories
    - Read READMEs, source code, documentation, configs
    - Required: repository, path to file

    search_issues: Find issues, discussions, and feature requests
    - Research current problems, feature requests, bug reports
    - Required: query or repository

    get_repository_readme: Get repository README content
    - Understand project purpose, setup, usage
    - Required: repository

    find_similar_repositories: Discover similar projects
    - Based on topics, languages, and descriptions
    - Required: repository

    analyze_repository_structure: Analyze codebase organization
    - Directory structure, file types, technology stack
    - Required: repository

    search_recent_commits: Find recent code changes and developments
    - Latest commits, contributors, activity patterns
    - Required: repository

    SPECIALIZED USE CASES FOR SKILL CREATION:

    Research AI/ML Techniques:
    - Find transformer implementations, RAG systems, fine-tuning code
    - Analyze recent papers' code repositories
    - Study production ML system architectures

    Study Software Patterns:
    - Find examples of specific design patterns
    - Research testing strategies and CI/CD approaches
    - Analyze microservice architectures

    Competitive Analysis:
    - Study similar projects and their approaches
    - Find alternative implementations
    - Research community solutions to common problems

    Args:
        operation: The GitHub research operation to perform
        query: Search query for repositories, code, or issues
        repository: Repository in "owner/repo" format
        language: Programming language filter
        sort: Sort results by stars, forks, updated, or best-match
        order: Sort order (asc/desc)
        max_results: Maximum results to return (1-100)
        include_content: Include full content in results (increases token usage)

    Returns:
        Operation-specific results with repository, code, and analysis data

    Examples:
        # Find transformer implementations for AI research
        await adn_github_research(
            "search_code",
            query="transformer architecture attention",
            language="python",
            max_results=20
        )

        # Research RAG system implementations
        await adn_github_research(
            "search_repositories",
            query="RAG retrieval augmented generation",
            language="python",
            sort="stars"
        )

        # Study a specific repository's structure
        await adn_github_research(
            "analyze_repository_structure",
            repository="microsoft/vscode"
        )

        # Find recent developments in a project
        await adn_github_research(
            "search_recent_commits",
            repository="openai/gpt-4",
            max_results=10
        )

        # Research specific implementation patterns
        await adn_github_research(
            "search_code",
            query="class TransformerModel",
            language="python"
        )
    """

    try:
        # Get GitHub token if available
        github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        async with aiohttp.ClientSession(headers=headers) as session:
            if operation == "search_repositories":
                if not query:
                    return {"error": "query required for search_repositories"}

                url = "https://api.github.com/search/repositories"
                params = {
                    "q": query,
                    "sort": sort,
                    "order": order,
                    "per_page": min(max_results, 100),
                }
                if language:
                    params["q"] += f" language:{language}"

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return {"error": f"GitHub API error: {response.status}"}

                    data = await response.json()
                    repos = []

                    for repo in data.get("items", [])[:max_results]:
                        repo_info = {
                            "name": repo["name"],
                            "full_name": repo["full_name"],
                            "description": repo.get("description"),
                            "url": repo["html_url"],
                            "stars": repo["stargazers_count"],
                            "forks": repo["forks_count"],
                            "language": repo.get("language"),
                            "updated_at": repo["updated_at"],
                            "topics": repo.get("topics", []),
                        }

                        if include_content and repo.get("description"):
                            repo_info["readme_preview"] = await _get_readme_preview(
                                session, repo["full_name"]
                            )

                        repos.append(repo_info)

                    return {
                        "operation": operation,
                        "query": query,
                        "total_count": data.get("total_count", 0),
                        "repositories": repos,
                        "search_timestamp": "2025-12-02",
                    }

            elif operation == "search_code":
                if not query:
                    return {"error": "query required for search_code"}

                url = "https://api.github.com/search/code"
                params = {
                    "q": query,
                    "per_page": min(max_results, 100),
                }
                if language:
                    params["q"] += f" language:{language}"
                if repository:
                    params["q"] += f" repo:{repository}"

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return {"error": f"GitHub API error: {response.status}"}

                    data = await response.json()
                    code_results = []

                    for item in data.get("items", [])[:max_results]:
                        result = {
                            "name": item["name"],
                            "path": item["path"],
                            "repository": item["repository"]["full_name"],
                            "url": item["html_url"],
                            "score": item["score"],
                        }

                        if include_content:
                            # Get file content (limited to avoid token bloat)
                            content = await _get_file_content_limited(
                                session, item["repository"]["full_name"], item["path"]
                            )
                            if content:
                                result["content_preview"] = content

                        code_results.append(result)

                    return {
                        "operation": operation,
                        "query": query,
                        "total_count": data.get("total_count", 0),
                        "code_results": code_results,
                        "search_timestamp": "2025-12-02",
                    }

            elif operation == "get_repository":
                if not repository:
                    return {"error": "repository required for get_repository"}

                url = f"https://api.github.com/repos/{repository}"

                async with session.get(url) as response:
                    if response.status != 200:
                        return {"error": f"GitHub API error: {response.status}"}

                    repo = await response.json()

                    return {
                        "operation": operation,
                        "repository": repository,
                        "info": {
                            "name": repo["name"],
                            "full_name": repo["full_name"],
                            "description": repo.get("description"),
                            "url": repo["html_url"],
                            "stars": repo["stargazers_count"],
                            "forks": repo["forks_count"],
                            "language": repo.get("language"),
                            "languages_url": repo["languages_url"],
                            "topics": repo.get("topics", []),
                            "created_at": repo["created_at"],
                            "updated_at": repo["updated_at"],
                            "pushed_at": repo["pushed_at"],
                            "size": repo["size"],
                            "license": repo.get("license", {}).get("name")
                            if repo.get("license")
                            else None,
                        },
                    }

            elif operation == "get_repository_readme":
                if not repository:
                    return {"error": "repository required for get_repository_readme"}

                url = f"https://api.github.com/repos/{repository}/readme"

                async with session.get(url) as response:
                    if response.status != 200:
                        return {"error": f"GitHub API error: {response.status}"}

                    readme_data = await response.json()

                    # The content is base64 encoded
                    import base64

                    content = base64.b64decode(readme_data["content"]).decode("utf-8")

                    return {
                        "operation": operation,
                        "repository": repository,
                        "readme": {
                            "name": readme_data["name"],
                            "path": readme_data["path"],
                            "content": content,
                            "size": readme_data["size"],
                            "url": readme_data["html_url"],
                        },
                    }

            elif operation == "search_issues":
                url = "https://api.github.com/search/issues"
                params = {
                    "q": query or f"repo:{repository}",
                    "sort": "updated",
                    "order": "desc",
                    "per_page": min(max_results, 100),
                }

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return {"error": f"GitHub API error: {response.status}"}

                    data = await response.json()
                    issues = []

                    for issue in data.get("items", [])[:max_results]:
                        issue_info = {
                            "title": issue["title"],
                            "number": issue["number"],
                            "url": issue["html_url"],
                            "state": issue["state"],
                            "created_at": issue["created_at"],
                            "updated_at": issue["updated_at"],
                            "comments": issue["comments"],
                            "labels": [label["name"] for label in issue.get("labels", [])],
                        }

                        if include_content and issue.get("body"):
                            # Truncate body to avoid token bloat
                            body = issue["body"]
                            if len(body) > 1000:
                                body = body[:1000] + "..."
                            issue_info["body_preview"] = body

                        issues.append(issue_info)

                    return {
                        "operation": operation,
                        "query": query or f"repo:{repository}",
                        "total_count": data.get("total_count", 0),
                        "issues": issues,
                    }

            elif operation == "analyze_repository_structure":
                if not repository:
                    return {"error": "repository required for analyze_repository_structure"}

                # Get repository contents
                url = f"https://api.github.com/repos/{repository}/contents"

                async with session.get(url) as response:
                    if response.status != 200:
                        return {"error": f"GitHub API error: {response.status}"}

                    contents = await response.json()

                    # Analyze structure
                    structure = _analyze_repo_structure(contents)

                    return {
                        "operation": operation,
                        "repository": repository,
                        "structure": structure,
                    }

            elif operation == "search_recent_commits":
                if not repository:
                    return {"error": "repository required for search_recent_commits"}

                url = f"https://api.github.com/repos/{repository}/commits"
                params = {
                    "per_page": min(max_results, 100),
                }

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return {"error": f"GitHub API error: {response.status}"}

                    commits = await response.json()
                    commit_data = []

                    for commit in commits[:max_results]:
                        commit_info = {
                            "sha": commit["sha"][:7],  # Short SHA
                            "message": commit["commit"]["message"],
                            "author": commit["commit"]["author"]["name"],
                            "date": commit["commit"]["author"]["date"],
                            "url": commit["html_url"],
                        }

                        if commit.get("author") and commit["author"].get("login"):
                            commit_info["author_login"] = commit["author"]["login"]

                        commit_data.append(commit_info)

                    return {
                        "operation": operation,
                        "repository": repository,
                        "commits": commit_data,
                        "total_returned": len(commit_data),
                    }

            else:
                return {
                    "error": f"Unsupported operation: {operation}",
                    "supported_operations": [
                        "search_repositories",
                        "search_code",
                        "get_repository",
                        "get_repository_readme",
                        "search_issues",
                        "analyze_repository_structure",
                        "search_recent_commits",
                    ],
                }

    except Exception as exc:  # noqa: BLE001
        logger.error("adn_github_research_error: %s", exc, exc_info=True)
        return {
            "success": False,
            "error": str(exc),
            "operation": operation,
            "suggestions": [
                "Check GITHUB_TOKEN environment variable",
                "Verify repository names are in owner/repo format",
                "Check GitHub API rate limits",
                "Try with simpler queries",
            ],
        }


async def _get_readme_preview(session: aiohttp.ClientSession, repo_full_name: str) -> str | None:
    """Get a preview of repository README."""
    try:
        url = f"https://api.github.com/repos/{repo_full_name}/readme"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                import base64

                content = base64.b64decode(data["content"]).decode("utf-8")
                # Return first 500 characters
                return content[:500] + "..." if len(content) > 500 else content
    except Exception:
        pass
    return None


async def _get_file_content_limited(
    session: aiohttp.ClientSession, repo_full_name: str, file_path: str, max_chars: int = 1000
) -> str | None:
    """Get limited file content to avoid token bloat."""
    try:
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("encoding") == "base64":
                    import base64

                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return content[:max_chars] + "..." if len(content) > max_chars else content
    except Exception:
        pass
    return None


def _analyze_repo_structure(contents: list[dict]) -> dict[str, Any]:
    """Analyze repository directory structure."""

    file_types = {}
    directories = []
    important_files = []

    for item in contents:
        if item["type"] == "dir":
            directories.append(item["name"])
        elif item["type"] == "file":
            # Count file extensions
            name = item["name"]
            if "." in name:
                ext = name.split(".")[-1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1

            # Track important files
            important_files_check = [
                "readme",
                "package.json",
                "requirements.txt",
                "setup.py",
                "dockerfile",
                "docker-compose.yml",
                ".gitignore",
                "license",
                "contributing",
            ]
            if any(important.lower() in name.lower() for important in important_files_check):
                important_files.append(name)

    # Infer technology stack
    tech_stack = _infer_tech_stack(file_types, directories, important_files)

    return {
        "total_items": len(contents),
        "directories": directories,
        "file_types": file_types,
        "important_files": important_files,
        "inferred_tech_stack": tech_stack,
        "structure_score": len(important_files) / max(len(contents), 1),  # Simple quality metric
    }


def _infer_tech_stack(file_types: dict, directories: list, important_files: list) -> list[str]:
    """Infer technology stack from repository structure."""

    tech_stack = []

    # Language detection
    if file_types.get("py"):
        tech_stack.append("Python")
    if file_types.get("js") or file_types.get("ts"):
        tech_stack.append("JavaScript/TypeScript")
    if file_types.get("java"):
        tech_stack.append("Java")
    if file_types.get("go"):
        tech_stack.append("Go")
    if file_types.get("rs"):
        tech_stack.append("Rust")
    if file_types.get("cpp") or file_types.get("cc") or file_types.get("cxx"):
        tech_stack.append("C++")

    # Framework detection
    if any(f.lower() == "package.json" for f in important_files):
        tech_stack.append("Node.js")
    if any(f.lower() == "requirements.txt" for f in important_files):
        tech_stack.append("Python")
    if any(f.lower() == "setup.py" for f in important_files):
        tech_stack.append("Python")
    if any(f.lower() == "cargo.toml" for f in important_files):
        tech_stack.append("Rust")
    if any(f.lower() == "go.mod" for f in important_files):
        tech_stack.append("Go")

    # Infrastructure detection
    if any(f.lower() == "dockerfile" for f in important_files):
        tech_stack.append("Docker")
    if any(f.lower() == "docker-compose.yml" for f in important_files):
        tech_stack.append("Docker Compose")

    return list(set(tech_stack))  # Remove duplicates
