"""Path component names skipped by file watch and directory scan (any matching Path.parts segment).

When a project ``path`` points at a user profile root by mistake, ignoring ``AppData`` and
related folders avoids hammering the DB with browser caches, identity stores, etc.
"""

IGNORE_PATTERNS = frozenset(
    {
        # Node.js
        "node_modules",
        # Build outputs
        "dist",
        "build",
        "target",
        "out",
        ".next",
        ".nuxt",
        # Python
        "__pycache__",
        ".pytest_cache",
        ".tox",
        "venv",
        ".venv",
        # Other package managers / build tools
        "vendor",
        ".gradle",
        ".cargo",
        "coverage",
        # IDE and editor files
        ".vscode",
        ".idea",
        # OS files
        ".DS_Store",
        "Thumbs.db",
        # Windows profile (mis-scoped project root under %USERPROFILE%)
        "AppData",
        "Application Data",
        "Local Settings",
    }
)
