"""Inbox portmanteau tool for Advanced Memory MCP server.

This tool provides inbox management for dropping files into the knowledge base.
Supports markdown files and automatic conversion of .docx, .html, .pdf, and .txt files.
"""

from textwrap import dedent

from fastmcp import Context
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.project_session import add_project_metadata, session
from advanced_memory.services.inbox_processor import get_inbox_processor


@mcp.tool
async def adn_inbox(
    operation: str,
    file_name: str | None = None,
    ctx: Context | None = None,
) -> str:
    """Manage the zettelkasten inbox for file drops and automatic processing.

    The inbox allows you to drop files (markdown, Word docs, PDFs, HTML, text) into a
    watched directory. Files are automatically converted to markdown and added to your
    knowledge base.

    SUPPORTED OPERATIONS:
    - status: Show inbox status and statistics
    - process: Process all files currently in inbox
    - info: Get information about inbox directory and supported formats
    - watch: Start watching inbox for new files (background task)

    SUPPORTED FILE FORMATS:
    - .md: Markdown files (moved directly to project)
    - .docx: Word documents (converted via Pandoc)
    - .html: HTML files (converted via Pandoc)
    - .pdf: PDF documents (text extraction)
    - .txt: Plain text files (wrapped in markdown)

    Args:
        operation: The operation to perform (status, process, info, watch)
        file_name: Optional specific file to process
        ctx: Optional MCP context for progress reporting

    Returns:
        Operation result with status, file counts, processing results

    Examples:
        # Check inbox status
        adn_inbox("status")

        # Process all files in inbox
        adn_inbox("process")

        # Get inbox information
        adn_inbox("info")

        # Start inbox watcher (background)
        adn_inbox("watch")
    """
    logger.info(f"MCP tool call tool=adn_inbox operation={operation}")

    # Route to appropriate operation
    if operation == "status":
        return await _status_operation(ctx)
    elif operation == "process":
        return await _process_operation(file_name, ctx)
    elif operation == "info":
        return await _info_operation(ctx)
    elif operation == "watch":
        return await _watch_operation(ctx)
    else:
        return dedent(
            f"""
            # Error

            Invalid operation '{operation}'.

            Supported operations:
            - status: Show inbox status
            - process: Process files in inbox
            - info: Get inbox information
            - watch: Start inbox watcher

            Use: adn_inbox("status")
            """
        ).strip()


async def _status_operation(ctx: Context | None) -> str:
    """Handle status operation - show inbox status and file counts"""
    processor = get_inbox_processor()

    inbox_dir = processor.inbox_dir
    converted_dir = processor.converted_dir

    # Count files in inbox
    inbox_files = []
    if inbox_dir.exists():
        inbox_files = [f for f in inbox_dir.iterdir() if f.is_file()]
        inbox_files = [
            f
            for f in inbox_files
            if f.name not in ["README.md", ".gitkeep"] and not f.name.startswith(".")
        ]

    # Count files in converted
    converted_files = []
    if converted_dir.exists():
        converted_files = [f for f in converted_dir.iterdir() if f.is_file()]

    # Group by file type
    def group_by_type(files):
        groups = {}
        for f in files:
            ext = f.suffix.lower()
            groups[ext] = groups.get(ext, 0) + 1
        return groups

    inbox_by_type = group_by_type(inbox_files)
    converted_by_type = group_by_type(converted_files)

    # Format file type breakdown
    def format_breakdown(groups):
        if not groups:
            return "None"
        return ", ".join(f"{ext}: {count}" for ext, count in sorted(groups.items()))

    result = dedent(
        f"""
        # 📥 Inbox Status

        **Inbox Directory:** `{inbox_dir}`
        **Converted Directory:** `{converted_dir}`

        ## Current Status

        **Files in Inbox:** {len(inbox_files)}
        {f"**Breakdown:** {format_breakdown(inbox_by_type)}" if inbox_by_type else ""}

        **Previously Converted:** {len(converted_files)}
        {f"**Breakdown:** {format_breakdown(converted_by_type)}" if converted_by_type else ""}

        ## Supported Formats

        - **`.md`** - Markdown (moved directly)
        - **`.docx`** - Word documents (requires Pandoc)
        - **`.html`** - HTML files (requires Pandoc)
        - **`.pdf`** - PDF documents (text extraction)
        - **`.txt`** - Plain text (wrapped in markdown)

        ## Next Steps

        {f"✅ **Process {len(inbox_files)} file(s):** `adn_inbox('process')`" if inbox_files else "✅ Inbox is empty - drop files to get started!"}

        ## How to Use Inbox

        1. Copy/drop files into: `{inbox_dir}`
        2. Run: `adn_inbox("process")`
        3. Files are automatically converted and added to your knowledge base

        **Or enable auto-processing:** `adn_inbox("watch")`

        ---
        *Files are preserved in `converted/` directory for reference*
        """
    ).strip()

    return add_project_metadata(result, session.get_current_project())


async def _process_operation(file_name: str | None, ctx: Context | None) -> str:
    """Handle process operation - process files in inbox"""
    processor = get_inbox_processor()

    if ctx:
        await ctx.info("Processing inbox files...")

    if file_name:
        # Process specific file
        file_path = processor.inbox_dir / file_name
        if not file_path.exists():
            return dedent(
                f"""
                # ❌ File Not Found

                File `{file_name}` not found in inbox.

                **Inbox location:** `{processor.inbox_dir}`

                Use `adn_inbox("status")` to see available files.
                """
            ).strip()

        result = await processor.process_file(file_path)

        if result["status"] == "success":
            return dedent(
                f"""
                # ✅ File Processed Successfully

                **File:** {file_name}
                **Action:** {result.get("action", "processed")}
                **Target:** `{result.get("target", "N/A")}`

                {result.get("message", "")}

                ## What Happened

                The file has been processed and added to your knowledge base.

                Use search to find the new note:
                ```
                adn_search("search", query="{file_path.stem}")
                ```
                """
            ).strip()
        else:
            return dedent(
                f"""
                # ⚠️ Processing Issue

                **File:** {file_name}
                **Status:** {result["status"]}
                **Message:** {result.get("message", "Unknown error")}

                ## Troubleshooting

                - Check file format is supported
                - Ensure Pandoc is installed for .docx/.html conversion
                - Verify file is not corrupted
                """
            ).strip()

    # Process all files
    results = await processor.process_inbox()

    if not results:
        return dedent(
            """
            # 📭 Inbox is Empty

            No files to process.

            Drop files into the inbox to get started:
            ```
            {inbox_dir}
            ```

            Supported formats: .md, .docx, .html, .pdf, .txt
            """
        ).strip()

    successful = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")
    skipped = sum(1 for r in results if r["status"] == "skipped")

    # Format results
    results_text = []
    for result in results:
        status_icon = {
            "success": "✅",
            "error": "❌",
            "skipped": "⏭️",
            "unsupported": "⚠️",
        }.get(result["status"], "❓")

        file_name = (
            result.get("source", "").split("/")[-1].split("\\")[-1]
            if "source" in result
            else "unknown"
        )

        results_text.append(
            f"{status_icon} **{file_name}** - {result.get('message', result['status'])}"
        )

    result = dedent(
        f"""
        # 📥 Inbox Processing Complete

        **Total Files:** {len(results)}
        **Successful:** {successful}
        **Errors:** {errors}
        **Skipped:** {skipped}

        ## Results

        {chr(10).join(results_text)}

        ## Next Steps

        {f"✅ Successfully processed {successful} file(s)!" if successful > 0 else ""}
        {f"⚠️ {errors} error(s) - check file formats and dependencies" if errors > 0 else ""}

        Use search to find your new notes.

        ---
        *Original files preserved in `{processor.converted_dir}`*
        """
    ).strip()

    return add_project_metadata(result, session.get_current_project())


async def _info_operation(ctx: Context | None) -> str:
    """Handle info operation - get inbox information"""
    processor = get_inbox_processor()

    # Check Pandoc availability
    pandoc_status = "✅ Installed" if processor.converter.pandoc_available else "❌ Not installed"

    # Check pypdf availability
    try:
        import pypdf

        pypdf_status = f"✅ Installed (v{pypdf.__version__})"
    except ImportError:
        pypdf_status = "❌ Not installed"

    result = dedent(
        f"""
        # 📥 Inbox Information

        ## Directories

        **Inbox:** `{processor.inbox_dir}`
        - Drop files here for automatic processing

        **Converted:** `{processor.converted_dir}`
        - Original files preserved here after conversion

        **Project:** `{processor.config.get_project_path(processor.config.default_project)}`
        - Processed markdown files end up here

        ## Supported Formats

        ### 1. Markdown (.md)
        - **Processing:** Moved directly to project
        - **Requirements:** None
        - **Status:** ✅ Always available

        ### 2. Word Documents (.docx, .doc)
        - **Processing:** Converted to markdown via Pandoc
        - **Requirements:** Pandoc installed
        - **Status:** {pandoc_status}
        - **Install:** https://pandoc.org

        ### 3. HTML Files (.html)
        - **Processing:** Converted to markdown via Pandoc
        - **Requirements:** Pandoc installed
        - **Status:** {pandoc_status}

        ### 4. PDF Documents (.pdf)
        - **Processing:** Text extraction to markdown
        - **Requirements:** pypdf or pdftotext
        - **Status:** {pypdf_status}
        - **Install:** `pip install pypdf`

        ### 5. Plain Text (.txt)
        - **Processing:** Wrapped in markdown header
        - **Requirements:** None
        - **Status:** ✅ Always available

        ## Workflow

        1. **Drop files** into inbox directory
        2. **Run:** `adn_inbox("process")` to process manually
        3. **Or enable:** `adn_inbox("watch")` for automatic processing

        ## Dependencies

        **Pandoc:** {pandoc_status}
        **pypdf:** {pypdf_status}

        {"⚠️ Install Pandoc for .docx/.html conversion: https://pandoc.org" if not processor.converter.pandoc_available else ""}
        {"💡 Install pypdf for better PDF extraction: `pip install pypdf`" if pypdf_status.startswith("❌") else ""}

        ---
        *Inbox processing is safe - original files are always preserved*
        """
    ).strip()

    return add_project_metadata(result, session.get_current_project())


async def _watch_operation(ctx: Context | None) -> str:
    """Handle watch operation - start inbox watcher"""
    # Note: The actual background watcher is started by the MCP server
    # This operation just provides instructions

    processor = get_inbox_processor()

    result = dedent(
        f"""
        # 👁️ Inbox Watcher

        **Status:** Background watching is managed by Advanced Memory server

        ## Automatic Processing

        The inbox watcher monitors:
        ```
        {processor.inbox_dir}
        ```

        When files are detected:
        1. ✅ Wait for file to finish writing
        2. ✅ Automatically convert to markdown (if needed)
        3. ✅ Move to project directory
        4. ✅ Trigger sync to add to knowledge base

        ## Enable Background Watching

        **Option 1: Server Configuration**
        - Enable `sync_changes: true` in Advanced Memory config
        - Inbox watcher runs automatically alongside file sync

        **Option 2: Manual Processing**
        - Drop files into inbox as needed
        - Run `adn_inbox("process")` manually
        - More control, no background process

        ## Current Files

        Use `adn_inbox("status")` to see what's currently in the inbox.

        ## Next Steps

        1. **Drop files** into: `{processor.inbox_dir}`
        2. **Process manually:** `adn_inbox("process")`
        3. **Or wait** for background watcher (if enabled in config)

        ---
        *Inbox processing is non-destructive - original files preserved*
        """
    ).strip()

    return add_project_metadata(result, session.get_current_project())
