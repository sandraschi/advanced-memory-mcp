"""URL prefixes for API tests — keep in sync with ``advanced_memory.api.app`` router mounts."""

# Mirrors app.include_router(..., prefix=...)
API_V1 = "/api/v1"

# Global (non–project-scoped) routers mounted under API_V1
IMPORT_API_ROOT = f"{API_V1}/import"
PROJECTS_API_ROOT = f"{API_V1}/projects"


def project_api_root(project_permalink: str) -> str:
    """Project-scoped base: ``/api/v1/{permalink}`` (matches ``get_project_id`` / ``project_url`` fixture)."""
    return f"{API_V1}/{project_permalink}"
