"""Interactive setup wizard for Advanced Memory MCP."""

import json
import webbrowser

from rich import print as rprint
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from advanced_memory.cli.app import app
from advanced_memory.utils.deeplink_generator import (
    generate_claude_config,
    generate_cursor_deeplink,
    generate_vscode_deeplink,
)


@app.command()
def setup():
    """Interactive setup wizard for AI client installation.

    This command guides you through installing Advanced Memory MCP
    in your preferred AI client with an easy step-by-step process.
    """
    rprint("\n[bold blue]>> Advanced Memory MCP Setup Wizard[/bold blue]\n")

    # Step 1: Choose client
    rprint("[bold]Which AI client are you using?[/bold]\n")
    rprint("  [cyan]1.[/cyan] Cursor IDE")
    rprint("  [cyan]2.[/cyan] VS Code (with ChatGPT/Claude extensions)")
    rprint("  [cyan]3.[/cyan] Claude Desktop")
    rprint("  [cyan]4.[/cyan] Other/Manual setup\n")

    choice = Prompt.ask("Enter number", choices=["1", "2", "3", "4"], default="1")

    client_map = {"1": "cursor", "2": "vscode", "3": "claude-desktop", "4": "manual"}
    client = client_map[choice]

    # Step 2: Choose transport
    rprint("\n[bold]How do you want to run Advanced Memory?[/bold]\n")
    rprint("  [cyan]1.[/cyan] Local (stdio) - Runs on your machine [recommended]")
    rprint("  [cyan]2.[/cyan] Network (HTTP) - Accessible via network\n")

    transport_choice = Prompt.ask("Enter number", choices=["1", "2"], default="1")

    if transport_choice == "1":
        transport = "stdio"
        host = None
        port = None
        rprint("\n[green]>> Using local mode (maximum privacy)[/green]")
    else:
        transport = "streamable-http"
        rprint("\n[bold]Network Configuration[/bold]\n")
        host = Prompt.ask("Host", default="127.0.0.1")
        port = int(Prompt.ask("Port", default="8000"))
        rprint(f"\n[green]>> Will connect to {host}:{port}[/green]")

    # Step 3: Generate and display
    rprint("\n[bold green]Configuration Generated![/bold green]\n")

    if client == "cursor":
        link = generate_cursor_deeplink(
            "advanced-memory",
            transport,
            host or "127.0.0.1",
            port or 8000,  # type: ignore
        )
        rprint(
            Panel.fit(
                f"[cyan]{link}[/cyan]",
                title="Cursor Installation Link",
                border_style="cyan",
            )
        )
        rprint("")

        if Confirm.ask("Open installation link in browser?", default=True):
            try:
                webbrowser.open(link)
                rprint("[green]✓[/green] Opening link in browser...")
                rprint(
                    "\n[yellow]→[/yellow] Cursor should prompt you to install Advanced Memory MCP"
                )
                rprint("[yellow]→[/yellow] Click 'Install' to complete setup\n")
            except Exception as e:
                rprint(f"[red]✗[/red] Could not open browser: {e}")
                rprint(
                    "[yellow]→[/yellow] Please copy the link above and paste it into your browser\n"
                )
        else:
            rprint("\n[yellow]>> Copy the link above and paste it into your browser[/yellow]")
            rprint("[yellow]>> Cursor will prompt you to install[/yellow]\n")

    elif client == "vscode":
        link = generate_vscode_deeplink(
            "advanced-memory",
            transport,
            host or "127.0.0.1",
            port or 8000,  # type: ignore
        )
        rprint(
            Panel.fit(
                f"[cyan]{link}[/cyan]",
                title="VS Code Installation Link",
                border_style="blue",
            )
        )
        rprint("")

        if Confirm.ask("Open installation link in browser?", default=True):
            try:
                webbrowser.open(link)
                rprint("[green]Opening link in browser...[/green]")
                rprint(
                    "\n[yellow]VS Code should prompt you to install Advanced Memory MCP[/yellow]"
                )
                rprint("[yellow]Click 'Install' to complete setup[/yellow]\n")
            except Exception as e:
                rprint(f"[red]Could not open browser: {e}[/red]")
                rprint(
                    "[yellow]Please copy the link above and paste it into your browser[/yellow]\n"
                )
        else:
            rprint("\n[yellow]Copy the link above and paste it into your browser[/yellow]")
            rprint("[yellow]VS Code will prompt you to install[/yellow]\n")

    elif client == "claude-desktop":
        config = generate_claude_config(
            "advanced-memory",
            transport,
            host or "127.0.0.1",
            port or 8000,  # type: ignore
        )
        config_json = json.dumps(config, indent=2)
        rprint(
            Panel.fit(
                f"[cyan]{config_json}[/cyan]",
                title="Claude Desktop Configuration",
                border_style="magenta",
            )
        )
        rprint("\n[yellow]NOTE: Claude Desktop requires manual configuration[/yellow]\n")
        rprint("[bold]Steps:[/bold]")
        rprint("  1. Open your claude_desktop_config.json file:")
        rprint(
            "     [dim]• macOS: ~/Library/Application Support/Claude/claude_desktop_config.json[/dim]"
        )
        rprint("     [dim]• Windows: %APPDATA%\\Claude\\claude_desktop_config.json[/dim]")
        rprint("     [dim]• Linux: ~/.config/Claude/claude_desktop_config.json[/dim]")
        rprint("  2. Add the configuration shown above to the 'mcpServers' section")
        rprint("  3. Restart Claude Desktop\n")

    else:
        rprint(
            Panel.fit(
                "[yellow]For manual setup, please refer to the documentation:[/yellow]\n"
                "[cyan]https://github.com/yourusername/advanced-memory-mcp[/cyan]",
                title="Manual Setup",
                border_style="yellow",
            )
        )
        rprint("")

    # Step 4: Next steps
    if transport == "stdio":
        rprint("[bold]Next Steps:[/bold]")
        rprint("  1. Install will happen automatically via the link")
        rprint("  2. Start using Advanced Memory MCP in your AI client!")
        rprint("  3. Try: 'Create a note about Python best practices'\n")
    else:
        rprint("[bold]Next Steps:[/bold]")
        rprint("  1. Start the Advanced Memory MCP server:")
        rprint(
            f"     [cyan]advanced-memory mcp --transport {transport} --host {host} --port {port}[/cyan]"
        )
        rprint("  2. Click the installation link")
        rprint("  3. Start using Advanced Memory MCP in your AI client!\n")

    rprint("[green]Setup complete! Happy note-taking![/green]\n")
