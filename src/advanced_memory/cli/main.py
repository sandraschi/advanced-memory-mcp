"""Main CLI entry point for advanced-memory."""  # pragma: no cover

from advanced_memory.cli.app import app  # pragma: no cover

# Register commands
from advanced_memory.cli.commands import (  # pragma: no cover
    convert,
    db,
    import_chatgpt,
    import_claude_conversations,
    import_claude_projects,
    import_memory_json,
    mcp,
    onboard,
    project,
    status,
    sync,
    tool,
)

if __name__ == "__main__":  # pragma: no cover
    # start the app
    app()
