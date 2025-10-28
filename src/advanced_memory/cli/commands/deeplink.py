"""Generate MCP deeplinks for easy installation."""

import json

import typer
from rich import print as rprint
from rich.panel import Panel

from advanced_memory.cli.app import app
from advanced_memory.utils.deeplink_generator import (
    generate_claude_config,
    generate_cursor_deeplink,
    generate_vscode_deeplink,
)


@app.command()
def deeplink(
    client: str = typer.Argument(..., help="AI client: cursor, vscode, claude-desktop"),
    transport: str = typer.Option("stdio", help="Transport: stdio, streamable-http, sse"),
    host: str = typer.Option("127.0.0.1", help="Host for HTTP transports"),
    port: int = typer.Option(8000, help="Port for HTTP transports"),
):
    """Generate one-click installation deeplink.

    Examples:
        # Cursor with stdio (local)
        advanced-memory deeplink cursor

        # VS Code with HTTP server
        advanced-memory deeplink vscode --transport streamable-http --port 8000

        # Claude Desktop config
        advanced-memory deeplink claude-desktop
    """
    client_lower = client.lower()

    if client_lower == "cursor":
        link = generate_cursor_deeplink("advanced-memory", transport, host, port)  # type: ignore
        rprint(
            Panel.fit(
                f"[cyan]{link}[/cyan]",
                title="Cursor Deeplink",
                subtitle="Click to install",
                border_style="cyan",
            )
        )
        rprint("\n[green]>> Click the link above to install in Cursor![/green]")
        rprint("[dim]Or copy and paste it into your browser[/dim]\n")

        # Show what will be installed
        if transport == "stdio":
            rprint("[dim]This will install Advanced Memory MCP locally (stdio transport)[/dim]")
        else:
            rprint(
                f"[dim]This will connect to Advanced Memory MCP at {transport}://{host}:{port}/mcp[/dim]"
            )

    elif client_lower == "vscode":
        link = generate_vscode_deeplink("advanced-memory", transport, host, port)  # type: ignore
        rprint(
            Panel.fit(
                f"[cyan]{link}[/cyan]",
                title="VS Code Deeplink",
                subtitle="Click to install",
                border_style="blue",
            )
        )
        rprint("\n[green]>> Click the link above to install in VS Code![/green]")
        rprint("[dim]Or copy and paste it into your browser[/dim]\n")

        if transport == "stdio":
            rprint("[dim]This will install Advanced Memory MCP locally (stdio transport)[/dim]")
        else:
            rprint(
                f"[dim]This will connect to Advanced Memory MCP at {transport}://{host}:{port}/mcp[/dim]"
            )

    elif client_lower == "claude-desktop":
        config = generate_claude_config("advanced-memory", transport, host, port)  # type: ignore
        config_json = json.dumps(config, indent=2)
        rprint(
            Panel.fit(
                f"[cyan]{config_json}[/cyan]",
                title="Claude Desktop Config",
                subtitle="Add to claude_desktop_config.json",
                border_style="magenta",
            )
        )
        rprint("\n[yellow]NOTE: Claude Desktop doesn't support deeplinks.[/yellow]")
        rprint("[green]Add the config above to your claude_desktop_config.json file.[/green]")
        rprint("\n[dim]Config location:[/dim]")
        rprint(
            "[dim]  • macOS: ~/Library/Application Support/Claude/claude_desktop_config.json[/dim]"
        )
        rprint("[dim]  • Windows: %APPDATA%\\Claude\\claude_desktop_config.json[/dim]")
        rprint("[dim]  • Linux: ~/.config/Claude/claude_desktop_config.json[/dim]\n")

    else:
        rprint(f"[red]❌ Unknown client: {client}[/red]")
        rprint("[yellow]Supported clients:[/yellow]")
        rprint("  • cursor - Cursor IDE")
        rprint("  • vscode - Visual Studio Code")
        rprint("  • claude-desktop - Claude Desktop app")
        raise typer.Exit(code=1)
