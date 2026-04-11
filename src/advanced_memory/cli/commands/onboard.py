"""Onboarding command for Advanced Memory - creates personalized starter Zettelkasten."""

import asyncio
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from advanced_memory.cli.app import app
from advanced_memory.mcp.tools import write_note as mcp_write_note
from advanced_memory.services.template_loader import get_content_templates

# Create onboard subcommand
onboard_app = typer.Typer(help="Create personalized starter Zettelkasten")
app.add_typer(onboard_app, name="onboard")

console = Console()

# Load all content templates from new zettelkasten/templates/ directory
CONTENT_TEMPLATES: dict[str, dict[str, Any]] = get_content_templates()


async def create_note_from_template(template: dict[str, Any]) -> None:
    """Create a single note from a template."""
    await (mcp_write_note.fn if hasattr(mcp_write_note, "fn") else mcp_write_note)(
        title=template["title"], content=template["content"], folder=template["folder"]
    )


def get_user_interests() -> dict[str, list[str]]:
    """Interactive prompt to select user interests."""
    console.print("\n[bold]Welcome to Advanced Memory Onboarding! 🚀[/bold]")
    console.print("Let's create your personalized starter Zettelkasten.\n")

    console.print(
        Panel(
            "We'll create high-quality, interconnected notes based on your interests.\n"
            "These serve as a foundation you can build upon.",
            title="About Onboarding",
        )
    )

    # Show available categories
    categories = {
        "1": "developer",
        "2": "researcher",
        "3": "writer",
        "4": "knowledge-worker",
        "5": "devops",
        "6": "data-scientist",
        "7": "uiux-designer",
        "8": "product-manager",
        "9": "entrepreneur",
        "10": "creative",
    }

    console.print("\n[bold]Available Categories:[/bold]")
    console.print("1. Developer (Python, Git, Testing, Architecture)")
    console.print("2. Researcher (Methods, Critical Thinking, Writing)")
    console.print("3. Writer (Craft, Storytelling, Publishing)")
    console.print("4. Knowledge Worker (Productivity, PKM, Communication)")
    console.print("5. DevOps Engineer (Docker, Kubernetes, CI/CD, IaC)")
    console.print("6. Data Scientist (ML, Statistics, Data Analysis)")
    console.print("7. UI/UX Designer (Design Principles, Figma, Research)")
    console.print("8. Product Manager (Strategy, Roadmaps, Metrics)")
    console.print("9. Entrepreneur (Business Models, Fundraising, Growth)")
    console.print("10. Creative Professional (Photography, Video, Design)")

    # Get category selection
    selection = Prompt.ask(
        "\nSelect categories (comma-separated numbers, or 'all')",
        default="all",
    )

    selected_interests: dict[str, list[str]] = {}

    if selection.lower() == "all":
        # All categories
        for category in categories.values():
            selected_interests[category] = list(CONTENT_TEMPLATES[category].keys())
    else:
        # Parse selected categories
        selected_nums = [n.strip() for n in selection.split(",")]
        for num in selected_nums:
            if num in categories:
                category = categories[num]
                # Ask for sub-interests
                sub_interests = list(CONTENT_TEMPLATES[category].keys())
                console.print(f"\n[cyan]{category.title()}[/cyan] focus areas:")
                for i, sub in enumerate(sub_interests, 1):
                    console.print(f"  {i}. {sub}")

                sub_selection = Prompt.ask(
                    f"Select {category} areas (comma-separated, or 'all')",
                    default="all",
                )

                if sub_selection.lower() == "all":
                    selected_interests[category] = sub_interests
                else:
                    selected_nums = [int(n.strip()) - 1 for n in sub_selection.split(",")]
                    selected_interests[category] = [
                        sub_interests[i] for i in selected_nums if 0 <= i < len(sub_interests)
                    ]

    return selected_interests


async def generate_starter_content(interests: dict[str, list[str]]) -> int:
    """Generate starter content based on user interests."""
    total_notes = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for category, sub_interests in interests.items():
            for sub_interest in sub_interests:
                if category in CONTENT_TEMPLATES and sub_interest in CONTENT_TEMPLATES[category]:
                    templates = CONTENT_TEMPLATES[category][sub_interest]

                    for template in templates:
                        task = progress.add_task(f"Creating: {template['title']}", total=1)

                        await create_note_from_template(template)
                        total_notes += 1

                        progress.update(task, completed=1)
                        await asyncio.sleep(0.1)  # Small delay for visual feedback

    return total_notes


@onboard_app.command("wizard")
def onboard_wizard():
    """Interactive wizard to create personalized starter Zettelkasten."""
    try:
        # Get user interests
        interests = get_user_interests()

        if not interests:
            console.print("[yellow]No interests selected. Exiting...[/yellow]")
            return

        # Show summary
        total_categories = len(interests)
        total_sub_interests = sum(len(subs) for subs in interests.values())

        console.print(
            f"\n[bold green]Selected {total_categories} categories with {total_sub_interests} focus areas[/bold green]"
        )
        console.print("This will create approximately 50-60 excellent, interconnected starter notes.")

        # Confirm
        proceed = Prompt.ask("Ready to create your starter Zettelkasten?", default="y")
        if proceed.lower() not in ["y", "yes"]:
            console.print("[yellow]Cancelled. Run 'advanced-memory onboard wizard' anytime to start over.[/yellow]")
            return

        # Generate content
        console.print("\n[bold blue]Generating your personalized starter Zettelkasten...[/bold blue]")

        async def run_generation():
            return await generate_starter_content(interests)

        total_notes = asyncio.run(run_generation())

        # Success message
        console.print("\n[bold green]🎉 Success![/bold green]")
        console.print(f"Created [bold]{total_notes}[/bold] high-quality starter notes in your knowledge base!")
        console.print("\n[bold]What's next?[/bold]")
        console.print('• Explore your new notes with: [cyan]advanced-memory search "Python"[/cyan]')
        console.print("• Start connecting ideas by adding wikilinks [[Note Name]]")
        console.print("• Create your own notes to build on this foundation")
        console.print("• Use Claude with your MCP connection for seamless note creation")

        console.print("\n[dim]Welcome to your personal knowledge empire! 🏰📚[/dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Your knowledge base is safe.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during onboarding: {e}[/red]")
        console.print("[yellow]Your existing knowledge base is unchanged.[/yellow]")
        raise typer.Exit(1) from e


@onboard_app.command("quick")
def onboard_quick(
    interests: str = typer.Option(
        ...,
        "--interests",
        "-i",
        help="Comma-separated interests (developer, researcher, writer, knowledge-worker)",
    ),
):
    """Quick setup with predefined interests."""
    try:
        # Parse interests
        interest_list = [i.strip() for i in interests.split(",")]
        interests_dict = {}

        for interest in interest_list:
            if interest in CONTENT_TEMPLATES:
                # Use all sub-interests for this category
                interests_dict[interest] = list(CONTENT_TEMPLATES[interest].keys())

        if not interests_dict:
            console.print(f"[red]No valid interests found in: {interests}[/red]")
            console.print(f"Available: {', '.join(CONTENT_TEMPLATES.keys())}")
            return

        console.print(f"[bold blue]Creating starter Zettelkasten for: {', '.join(interests_dict.keys())}[/bold blue]")

        async def run_generation():
            return await generate_starter_content(interests_dict)

        total_notes = asyncio.run(run_generation())

        console.print(f"\n[bold green]✅ Created {total_notes} excellent starter notes![/bold green]")
        console.print("Run [cyan]advanced-memory onboard wizard[/cyan] for interactive setup anytime.")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@onboard_app.callback()
def onboard_callback():
    """Create your personalized starter Zettelkasten."""
    pass
