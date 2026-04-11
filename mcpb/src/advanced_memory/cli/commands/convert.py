"""CLI command for converting documents to markdown"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from advanced_memory.cli.app import app as main_app
from advanced_memory.services.document_converter import get_document_converter

# Create convert subcommand
convert_app = typer.Typer(help="Convert documents to markdown")
main_app.add_typer(convert_app, name="convert")

console = Console()


@convert_app.command(name="file")
def convert(
    file_path: Path = typer.Argument(..., help="Path to file to convert"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    doc_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Document type (docx, html, pdf, txt). Auto-detected if not specified.",
    ),
) -> None:
    """Convert a document file to markdown

    Supports:
    - .docx: Word documents (requires Pandoc)
    - .html: HTML files (requires Pandoc)
    - .pdf: PDF documents (text extraction)
    - .txt: Plain text files
    """
    asyncio.run(_convert_async(file_path, output, doc_type))


async def _convert_async(file_path: Path, output: Path | None, doc_type: str | None) -> None:
    """Async implementation of convert command"""
    # Validate input file
    if not file_path.exists():
        console.print(f"❌ Error: File not found: {file_path}", style="bold red")
        raise typer.Exit(1)

    # Auto-detect document type if not specified
    if not doc_type:
        suffix = file_path.suffix.lower()
        type_map = {
            ".docx": "docx",
            ".doc": "docx",
            ".html": "html",
            ".htm": "html",
            ".pdf": "pdf",
            ".txt": "txt",
        }

        doc_type = type_map.get(suffix)

        if not doc_type:
            console.print(f"❌ Error: Unsupported file type: {suffix}", style="bold red")
            console.print("Supported types: .docx, .html, .pdf, .txt")
            raise typer.Exit(1)

    # Validate document type
    if doc_type not in ["docx", "html", "pdf", "txt"]:
        console.print(f"❌ Error: Invalid document type: {doc_type}", style="bold red")
        console.print("Valid types: docx, html, pdf, txt")
        raise typer.Exit(1)

    # Determine output path
    if not output:
        output = file_path.with_suffix(".md")

    # Check if output exists
    if output.exists():
        overwrite = typer.confirm(f"Output file exists: {output}. Overwrite?", default=False)
        if not overwrite:
            console.print("❌ Conversion cancelled", style="yellow")
            raise typer.Exit(0)

    # Convert
    console.print(f"🔄 Converting {file_path.name} to markdown...", style="cyan")

    converter = get_document_converter()
    markdown_content = await converter.convert(file_path, doc_type)  # type: ignore

    if not markdown_content:
        console.print("❌ Conversion failed. Check the log for details.", style="bold red")
        raise typer.Exit(1)

    # Write output
    output.write_text(markdown_content, encoding="utf-8")

    console.print("✅ Conversion successful!", style="bold green")
    console.print(f"Output: {output}", style="green")

    # Show summary
    lines = markdown_content.count("\n") + 1
    chars = len(markdown_content)
    console.print(f"Lines: {lines}, Characters: {chars}", style="dim")


@convert_app.command("info")
def convert_info() -> None:
    """Show information about document conversion capabilities"""
    converter = get_document_converter()

    # Create capabilities table
    table = Table(title="Document Conversion Capabilities", show_header=True)
    table.add_column("Format", style="cyan", no_wrap=True)
    table.add_column("Extension", style="white")
    table.add_column("Method", style="yellow")
    table.add_column("Requires", style="magenta")
    table.add_column("Status", style="green")

    # Check dependencies
    pandoc_available = converter.pandoc_available

    try:
        import pypdf

        pypdf_available = True
    except ImportError:
        pypdf_available = False

    # Add rows
    table.add_row(
        "Word Documents",
        ".docx, .doc",
        "Pandoc",
        "Pandoc",
        "✅ Available" if pandoc_available else "❌ Not installed",
    )

    table.add_row(
        "HTML Files",
        ".html, .htm",
        "Pandoc",
        "Pandoc",
        "✅ Available" if pandoc_available else "❌ Not installed",
    )

    table.add_row(
        "PDF Documents",
        ".pdf",
        "pypdf or pdftotext",
        "pypdf",
        "✅ Available" if pypdf_available else "⚠️ Limited (fallback to pdftotext)",
    )

    table.add_row("Plain Text", ".txt", "Built-in", "None", "✅ Always available")

    console.print(table)

    # Installation instructions
    if not pandoc_available:
        console.print("\n💡 Install Pandoc for .docx and .html conversion:", style="yellow")
        console.print("   https://pandoc.org\n")

    if not pypdf_available:
        console.print("💡 Install pypdf for better PDF extraction:", style="yellow")
        console.print("   pip install pypdf\n")


if __name__ == "__main__":
    convert_app()
