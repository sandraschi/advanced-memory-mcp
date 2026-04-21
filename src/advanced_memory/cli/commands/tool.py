"""CLI tool commands for Advanced Memory."""

import asyncio
import sys
from typing import Annotated

import typer
from loguru import logger
from rich import print as rprint

from advanced_memory.cli.app import app

# Import prompts
from advanced_memory.mcp.prompts.continue_conversation import (
    continue_conversation as mcp_continue_conversation,
)
from advanced_memory.mcp.prompts.recent_activity import (
    recent_activity_prompt as recent_activity_prompt,
)
from advanced_memory.mcp.tools.build_context import build_context as mcp_build_context
from advanced_memory.mcp.tools.read_note import read_note as mcp_read_note
from advanced_memory.mcp.tools.recent_activity import recent_activity as mcp_recent_activity
from advanced_memory.mcp.tools.search import search_notes as mcp_search
from advanced_memory.mcp.tools.write_note import write_note as mcp_write_note
from advanced_memory.schemas.base import TimeFrame
from advanced_memory.schemas.memory import MemoryUrl
from advanced_memory.schemas.search import SearchItemType

tool_app = typer.Typer()
app.add_typer(tool_app, name="tool", help="Access to MCP tools via CLI")


@tool_app.command()
def write_note(
    title: Annotated[str, typer.Option(help="The title of the note")],
    folder: Annotated[str, typer.Option(help="The folder to create the note in")],
    content: Annotated[
        str | None,
        typer.Option(
            help="The content of the note. If not provided, content will be read from stdin. This allows piping content from other commands, e.g.: cat file.md | advanced-memory tools write-note"
        ),
    ] = None,
    tags: Annotated[list[str] | None, typer.Option(help="A list of tags to apply to the note")] = None,
):
    """Create or update a markdown note. Content can be provided as an argument or read from stdin.

    Content can be provided in two ways:
    1. Using the --content parameter
    2. Piping content through stdin (if --content is not provided)

    Examples:

    # Using content parameter
    advanced-memory tools write-note --title "My Note" --folder "notes" --content "Note content"

    # Using stdin pipe
    echo "# My Note Content" | advanced-memory tools write-note --title "My Note" --folder "notes"

    # Using heredoc
    cat << EOF | advanced-memory tools write-note --title "My Note" --folder "notes"
    # My Document

    This is my document content.

    - Point 1
    - Point 2
    EOF

    # Reading from a file
    cat document.md | advanced-memory tools write-note --title "Document" --folder "docs"
    """
    try:
        # If content is not provided, read from stdin
        if content is None:
            # Check if we're getting data from a pipe or redirect
            if not sys.stdin.isatty():
                content = sys.stdin.read()
            else:  # pragma: no cover
                # If stdin is a terminal (no pipe/redirect), inform the user
                typer.echo(
                    "No content provided. Please provide content via --content or by piping to stdin.",
                    err=True,
                )
                raise typer.Exit(1)

        # Also check for empty content
        if content is not None and not content.strip():
            typer.echo("Empty content provided. Please provide non-empty content.", err=True)
            raise typer.Exit(1)

        _fn = mcp_write_note.fn if hasattr(mcp_write_note, "fn") else mcp_write_note
        note = asyncio.run(_fn(title, content, folder, tags))
        rprint(note)
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during write_note: {e}", err=True)
            raise typer.Exit(1) from e
        raise


@tool_app.command()
def read_note(identifier: str, page: int = 1, page_size: int = 10):
    """Read a markdown note from the knowledge base."""
    try:
        _fn = mcp_read_note.fn if hasattr(mcp_read_note, "fn") else mcp_read_note
        note = asyncio.run(_fn(identifier, page, page_size))
        rprint(note)
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during read_note: {e}", err=True)
            raise typer.Exit(1) from e
        raise


@tool_app.command()
def build_context(
    url: MemoryUrl,
    depth: int | None = 1,
    timeframe: TimeFrame | None = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
):
    """Get context needed to continue a discussion."""
    try:
        _fn = mcp_build_context.fn if hasattr(mcp_build_context, "fn") else mcp_build_context
        context = asyncio.run(
            _fn(
                url=url,
                depth=depth,
                timeframe=timeframe,
                page=page,
                page_size=page_size,
                max_related=max_related,
            )
        )
        # Use json module for more controlled serialization
        import json

        context_dict = context.model_dump(exclude_none=True)
        logger.info(json.dumps(context_dict, indent=2, ensure_ascii=True, default=str))
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during build_context: {e}", err=True)
            raise typer.Exit(1) from e
        raise


@tool_app.command()
def recent_activity(
    type_filter: Annotated[list[SearchItemType] | None, typer.Option("--type", "-t")] = None,
    depth: int | None = 1,
    timeframe: TimeFrame | None = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
    project: Annotated[str | None, typer.Option(help="Project name override")] = None,
):
    """Get recent activity across the knowledge base."""
    try:
        _fn = mcp_recent_activity.fn if hasattr(mcp_recent_activity, "fn") else mcp_recent_activity
        result = asyncio.run(
            _fn(
                type_filter=type_filter,  # pyright: ignore [reportArgumentType]
                depth=depth,
                timeframe=timeframe,
                page=page,
                page_size=page_size,
                max_related=max_related,
                project=project,
            )
        )
        import json

        if hasattr(result, "model_dump"):
            context_dict = result.model_dump(exclude_none=True)
            logger.info(json.dumps(context_dict, indent=2, ensure_ascii=True, default=str))
        else:
            rprint(result)
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during recent_activity: {e}", err=True)
            raise typer.Exit(1) from e
        raise


@tool_app.command("search-notes")
def search_notes(
    query: str,
    permalink: Annotated[bool, typer.Option("--permalink", help="Search permalink values")] = False,
    title: Annotated[bool, typer.Option("--title", help="Search title values")] = False,
    after_date: Annotated[
        str | None,
        typer.Option("--after_date", help="Search results after date, eg. '2d', '1 week'"),
    ] = None,
    page: int = 1,
    page_size: int = 10,
    project: Annotated[str | None, typer.Option(help="Project name override")] = None,
):
    """Search across all content in the knowledge base."""
    if permalink and title:  # pragma: no cover
        typer.echo("Use either --permalink or --title, not both.", err=True)
        raise typer.Exit(1)

    try:
        if title:
            search_type: str = "title"
        elif permalink:
            search_type = "permalink_match" if "*" in query else "permalink"
        else:
            search_type = "text"

        _fn = mcp_search.fn if hasattr(mcp_search, "fn") else mcp_search
        results = asyncio.run(
            _fn(
                query,
                page=page,
                results_per_page=page_size,
                search_type=search_type,
                after_date=after_date,
                project=project,
            )
        )
        import json

        if isinstance(results, str):
            rprint(results)
        elif hasattr(results, "model_dump"):
            logger.info(json.dumps(results.model_dump(exclude_none=True), indent=2, ensure_ascii=True, default=str))
        else:
            rprint(results)
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            logger.exception("Error during search_notes")
            typer.echo(f"Error during search: {e}", err=True)
            raise typer.Exit(1) from e
        raise


@tool_app.command(name="continue-conversation")
def continue_conversation(
    topic: Annotated[str | None, typer.Option(help="Topic or keyword to search for")] = None,
    timeframe: Annotated[str | None, typer.Option(help="How far back to look for activity")] = None,
):
    """Prompt to continue a previous conversation or work session."""
    try:
        # Prompt functions return formatted strings directly
        _fn = mcp_continue_conversation.fn if hasattr(mcp_continue_conversation, "fn") else mcp_continue_conversation
        session = asyncio.run(_fn(topic=topic, timeframe=timeframe))  # type: ignore
        # Use plain print to avoid Rich wrapping of Markdown content
        print(session)
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            logger.exception("Error continuing conversation", e)
            typer.echo(f"Error continuing conversation: {e}", err=True)
            raise typer.Exit(1) from e
        raise


# @tool_app.command(name="show-recent-activity")
# def show_recent_activity(
#     timeframe: Annotated[
#         str, typer.Option(help="How far back to look for activity")
#     ] = "7d",
# ):
#     """Prompt to show recent activity."""
#     try:
#         # Prompt functions return formatted strings directly
#         session = asyncio.run(recent_activity_prompt(timeframe=timeframe))
#         rprint(session)
#     except Exception as e:  # pragma: no cover
#         if not isinstance(e, typer.Exit):
#             logger.exception("Error continuing conversation", e)
#             typer.echo(f"Error continuing conversation: {e}", err=True)
#             raise typer.Exit(1)
#         raise
