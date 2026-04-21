"""AI-managed project detection and switching service.

This service analyzes conversation context to automatically detect which project
the user is likely referring to, enabling seamless project switching without
explicit user commands.
"""

import re
from typing import Any

from loguru import logger

from advanced_memory.config import ConfigManager
from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.tools.utils import call_get
from advanced_memory.schemas.project_info import ProjectList
from advanced_memory.utils import generate_permalink


class ProjectDetector:
    """Service for detecting relevant projects from conversation context."""

    def __init__(self):
        """Initialize the project detector."""
        self.config_manager = ConfigManager()
        self._project_cache: dict[str, Any] | None = None

    async def detect_project_from_context(
        self,
        user_query: str,
        current_project: str | None = None,
        search_results: list[dict[str, Any]] | None = None,
        file_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        """Detect the most relevant project from conversation context.

        Args:
            user_query: The user's query or message
            current_project: Currently active project (optional)
            search_results: Recent search results with project metadata (optional)
            file_paths: File paths mentioned or accessed (optional)

        Returns:
            Dictionary with:
                - suggested_project: Project name (or None if no clear match)
                - confidence: Confidence score 0.0-1.0
                - reason: Explanation of why this project was suggested
                - should_switch: Whether to automatically switch
        """
        # Get all available projects
        projects = await self._get_all_projects()

        if not projects:
            return {
                "suggested_project": None,
                "confidence": 0.0,
                "reason": "No projects available",
                "should_switch": False,
            }

        # If only one project, no need to detect
        if len(projects) == 1:
            return {
                "suggested_project": projects[0]["name"],
                "confidence": 1.0,
                "reason": "Only one project available",
                "should_switch": False,
            }

        # Score each project based on context
        scores: dict[str, float] = {}
        reasons: dict[str, list[str]] = {p["name"]: [] for p in projects}

        # 1. Check for explicit project name mentions in query
        query_lower = user_query.lower()
        for project in projects:
            project_name_lower = project["name"].lower()
            project_permalink = generate_permalink(project["name"]).lower()

            # Exact name match (high confidence)
            if project_name_lower in query_lower or project_permalink in query_lower:
                scores[project["name"]] = scores.get(project["name"], 0.0) + 0.8
                reasons[project["name"]].append(f"Project name '{project['name']}' mentioned in query")

            # Partial name match (medium confidence)
            words = query_lower.split()
            for word in words:
                if word in project_name_lower or word in project_permalink:
                    scores[project["name"]] = scores.get(project["name"], 0.0) + 0.3
                    reasons[project["name"]].append(f"Partial match with '{word}'")

        # 2. Context-based detection for common project types
        # Personal/private context indicators
        personal_indicators = [
            "meet",
            "meeting",
            "tomorrow",
            "today",
            "family",
            "friend",
            "friends",
            "personal",
            "private",
            "vacation",
            "trip",
            "birthday",
            "anniversary",
            "home",
            "house",
            "apartment",
            "dinner",
            "lunch",
            "coffee",
        ]
        if any(indicator in query_lower for indicator in personal_indicators):
            # Look for private/personal project
            for project in projects:
                project_name_lower = project["name"].lower()
                if project_name_lower in ["private", "personal", "daily", "life"]:
                    scores[project["name"]] = scores.get(project["name"], 0.0) + 0.5
                    reasons[project["name"]].append("Personal context detected (meeting, family, etc.)")

        # Work context indicators
        work_indicators = [
            "work",
            "client",
            "project",
            "meeting",
            "deadline",
            "task",
            "todo",
            "business",
            "professional",
            "office",
            "colleague",
            "team",
            "manager",
        ]
        if any(indicator in query_lower for indicator in work_indicators):
            # Look for work project
            for project in projects:
                project_name_lower = project["name"].lower()
                if project_name_lower in ["work", "business", "professional", "office"]:
                    scores[project["name"]] = scores.get(project["name"], 0.0) + 0.5
                    reasons[project["name"]].append("Work context detected")

        # Research context indicators
        research_indicators = [
            "research",
            "paper",
            "study",
            "academic",
            "learn",
            "learning",
            "deep dive",
            "analysis",
            "investigate",
            "explore",
            "theory",
        ]
        if any(indicator in query_lower for indicator in research_indicators):
            # Look for research project
            for project in projects:
                project_name_lower = project["name"].lower()
                if project_name_lower in ["research", "academic", "study", "learning"]:
                    scores[project["name"]] = scores.get(project["name"], 0.0) + 0.5
                    reasons[project["name"]].append("Research context detected")

        # 3. Check search results for project hints
        if search_results:
            for result in search_results:
                result_project = result.get("project") or result.get("metadata", {}).get("project")
                if result_project:
                    scores[result_project] = scores.get(result_project, 0.0) + 0.5
                    reasons[result_project].append("Found in recent search results")

        # 4. Check file paths for project hints
        if file_paths:
            for file_path in file_paths:
                # Try to match file path to project paths
                for project in projects:
                    project_path = str(project.get("path", "")).lower()
                    if project_path and project_path in file_path.lower():
                        scores[project["name"]] = scores.get(project["name"], 0.0) + 0.6
                        reasons[project["name"]].append(f"File path matches project: {file_path}")

        # 5. Check for folder/folder path mentions
        folder_pattern = r"(?:folder|directory|path)[\s:]+['\"]?([^'\"]+)['\"]?"
        folder_matches = re.findall(folder_pattern, query_lower)
        for folder_match in folder_matches:
            # Try to match folder to project structure
            for project in projects:
                # This is a simplified check - could be enhanced with actual folder scanning
                if folder_match.lower() in project["name"].lower():
                    scores[project["name"]] = scores.get(project["name"], 0.0) + 0.4
                    reasons[project["name"]].append(f"Folder mention matches project: {folder_match}")

        # 6. If current project has any score, give it a small boost (inertia)
        if current_project and current_project in scores:
            scores[current_project] = scores[current_project] + 0.1
            reasons[current_project].append("Currently active project (inertia)")

        # Find the best match
        if not scores:
            # No clear match - stay on current or return None
            return {
                "suggested_project": current_project,
                "confidence": 0.0,
                "reason": "No project context detected",
                "should_switch": False,
            }

        # Get project with highest score
        best_project = max(scores.items(), key=lambda x: x[1])
        best_name, best_score = best_project

        # Normalize confidence (max possible score is ~2.0, so divide by 2)
        confidence = min(best_score / 2.0, 1.0)

        # Determine if we should switch
        should_switch = False
        if best_name != current_project:
            # Only switch if confidence is high enough
            if confidence >= 0.6:
                should_switch = True
            elif confidence >= 0.4 and current_project is None:
                # If no current project, switch even with lower confidence
                should_switch = True

        return {
            "suggested_project": best_name,
            "confidence": confidence,
            "reason": "; ".join(reasons[best_name]) if reasons[best_name] else "Context analysis",
            "should_switch": should_switch,
        }

    async def search_across_projects(self, query: str, max_results_per_project: int = 3) -> dict[str, Any]:
        """Search across all projects to find which project contains relevant content.

        Args:
            query: Search query
            max_results_per_project: Maximum results to check per project

        Returns:
            Dictionary mapping project names to search result counts and relevance
        """
        projects = await self._get_all_projects()
        project_scores: dict[str, float] = {}

        # This would require calling the search API for each project
        # For now, return a placeholder structure
        # TODO: Implement actual cross-project search
        for project in projects:
            project_scores[project["name"]] = 0.0

        return {
            "query": query,
            "project_scores": project_scores,
            "suggested_project": max(project_scores.items(), key=lambda x: x[1])[0] if project_scores else None,
        }

    async def _get_all_projects(self) -> list[dict[str, Any]]:
        """Get all available projects with metadata.

        Returns:
            List of project dictionaries with name, path, and metadata
        """
        if self._project_cache:
            return self._project_cache

        try:
            response = await call_get(client, "/api/v1/projects")
            project_list = ProjectList.model_validate(response.json())

            projects = []
            for project in project_list.projects:
                projects.append(
                    {
                        "name": project.name,
                        "path": project.path,
                        "permalink": project.permalink,
                        "is_default": project.is_default,
                    }
                )

            self._project_cache = projects
            return projects

        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            # Fallback to config manager
            config_projects = self.config_manager.projects
            return [
                {
                    "name": name,
                    "path": str(config.path),
                    "permalink": generate_permalink(name),
                    "is_default": False,
                }
                for name, config in config_projects.items()
            ]

    def clear_cache(self) -> None:
        """Clear the project cache."""
        self._project_cache = None


# Global detector instance
_detector: ProjectDetector | None = None


def get_project_detector() -> ProjectDetector:
    """Get the global project detector instance."""
    global _detector
    if _detector is None:
        _detector = ProjectDetector()
    return _detector
