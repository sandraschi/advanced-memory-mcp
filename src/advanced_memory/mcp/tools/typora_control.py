"""
Typora Control via json_rpc Plugin

Swiss Army Knife tool for full Typora automation using the obgnail/typora_plugin json_rpc plugin.

PRIMARY USE CASE: Manual editing of long skill markdown files in a rich editor.

REQUIRES: obgnail/typora_plugin with json_rpc enabled on port 8888

Provides direct API control of Typora without GUI automation brittleness.

NOTE: For quick note editing, use adn_content. For Notepad++ workflows, use notepadpp-mcp server.

NOTE: Handler functions temporarily return dict | str. The main function wraps string results
in structured responses via _wrap_handler_result(). Handlers will be fully updated incrementally.
"""

# pyright: reportReturnType=false

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import websockets

from advanced_memory.config import logger
from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response


class TyporaRPCClient:
    """WebSocket client for Typora json_rpc communication."""

    def __init__(self, host: str | None = None, port: int | None = None):
        # Use environment variables or defaults
        self.host = host or os.getenv("TYPORA_HOST", "localhost")
        self.port = port or int(os.getenv("TYPORA_PORT", "8888"))
        self.uri = f"ws://{self.host}:{self.port}"
        self.connection_timeout = float(os.getenv("TYPORA_CONNECTION_TIMEOUT", "5.0"))
        self.request_timeout = float(os.getenv("TYPORA_REQUEST_TIMEOUT", "10.0"))

    async def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a JSON-RPC call to Typora."""
        if params is None:
            params = {}

        request = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": method,
            "params": params,
        }

        try:
            async with websockets.connect(
                self.uri,
                extra_headers={"Origin": "advanced-memory-mcp"},
                open_timeout=self.connection_timeout,
            ) as websocket:
                await websocket.send(json.dumps(request))

                # Set timeout for response
                response = await asyncio.wait_for(websocket.recv(), timeout=self.request_timeout)

                result = json.loads(response)

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"].get("message", "Unknown error"),
                        "code": result["error"].get("code", -1),
                    }

                return {"success": True, "result": result.get("result")}

        except TimeoutError:
            return {"success": False, "error": "Request timeout"}
        except websockets.exceptions.ConnectionClosedError:
            return {"success": False, "error": "Connection closed by Typora"}
        except Exception as e:
            return {"success": False, "error": f"Connection failed: {str(e)}"}

    def _generate_id(self) -> int:
        """Generate unique request ID."""
        import time

        return int(time.time() * 1000000) % 1000000


# Global client instance
typora_client = TyporaRPCClient()


@mcp.tool
async def typora_control(
    operation: str,
    # Common parameters
    format: str | None = None,
    output_path: str | None = None,
    text: str | None = None,
    file_path: str | None = None,
    content: str | None = None,
    position: str | None = None,
    # Search/replace parameters
    find_text: str | None = None,
    replace_text: str | None = None,
    # Batch operation parameters
    files: list[str] | None = None,
    # Theme/UI parameters
    theme: str | None = None,
    visible: bool | None = None,
    # Template parameters
    template_name: str | None = None,
    # Advanced parameters
    options: dict[str, Any] | None = None,
) -> dict:
    """Swiss Army Knife tool for Typora control via json_rpc.

    RESPONSES:
    Success: {"success": true, "operation": "...", "summary": "...", "result": {...}}
    Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

    For errors, check recovery_options for next steps.

    ERRORS:
    - Connection failed: Typora not running or json_rpc plugin not enabled on port 8888
    - Request timeout: Typora took too long to respond
    - Export requires format parameter: Missing required argument for export
    - File Not Found: Provided file path does not exist
    - Unsupported operation: Operation not recognized by the tool
    """

    # Default options
    if options is None:
        options = {}

    # Helper to wrap string results (temporary until all handlers are updated)
    def _wrap_handler_result(handler_result: dict | str, operation_name: str) -> dict:
        """Wrap handler result in structured response if it's a string."""
        if isinstance(handler_result, dict):
            return handler_result
        # String result - wrap it
        if "[UNICODE]" in handler_result or "[DOC]" in handler_result:
            # Error-like string
            return build_error_response(
                error="typora_operation_error",
                error_code="TYPORA_HANDLER_ERROR",
                message=f"Operation '{operation_name}' returned error",
                recovery_options=["Check Typora connection", "Verify operation parameters"],
                diagnostic_info={"raw_response": handler_result},
                urgency="medium",
            )
        # Success-like string
        return build_success_response(
            operation=operation_name,
            summary=f"Operation '{operation_name}' completed",
            result={"message": handler_result},
            next_steps=["Check result for details"],
        )

    # Route to appropriate handler
    try:
        handler_result = None
        if operation == "export":
            handler_result = await _handle_export(format, output_path, options)
        elif operation == "get_content":
            handler_result = await _handle_get_content()
        elif operation == "set_content":
            handler_result = await _handle_set_content(content)
        elif operation == "insert_text":
            handler_result = await _handle_insert_text(text, position)
        elif operation == "get_cursor":
            handler_result = await _handle_get_cursor()
        elif operation == "open_file":
            handler_result = await _handle_open_file(file_path)
        elif operation == "save_file":
            handler_result = await _handle_save_file()
        elif operation == "new_file":
            handler_result = await _handle_new_file()
        elif operation == "get_metadata":
            handler_result = await _handle_get_metadata()
        elif operation == "set_metadata":
            handler_result = await _handle_set_metadata(options)
        elif operation == "search_replace":
            handler_result = await _handle_search_replace(find_text, replace_text, options)
        elif operation == "get_themes":
            handler_result = await _handle_get_themes()
        elif operation == "set_theme":
            handler_result = await _handle_set_theme(theme)
        elif operation == "toggle_sidebar":
            handler_result = await _handle_toggle_sidebar(visible)
        elif operation == "toggle_toolbar":
            handler_result = await _handle_toggle_toolbar(visible)
        elif operation == "batch_export":
            handler_result = await _handle_batch_export(files, format, output_path, options)
        elif operation == "content_analysis":
            handler_result = await _handle_content_analysis()
        elif operation == "link_validation":
            handler_result = await _handle_link_validation()
        elif operation == "template_apply":
            handler_result = await _handle_template_apply(template_name, options)
        elif operation == "sync_to_advanced_memory":
            handler_result = await _handle_sync_to_advanced_memory(options)
        else:
            handler_result = await _handle_unknown_operation(operation)

        # Wrap string results in structured responses (temporary until all handlers are updated)
        return _wrap_handler_result(handler_result, operation)

    except Exception as e:
        logger.error(f"Typora control operation failed: {str(e)}")
        return build_error_response(
            error="typora_operation_failed",
            error_code="TYPORA_OPERATION_ERROR",
            message=f"Operation '{operation}' failed: {str(e)}",
            recovery_options=[
                "Ensure Typora is running",
                "Check json_rpc plugin is enabled on port 8888",
                "Verify port 8888 is available",
                "Restart Typora if issues persist",
                "Check Typora plugin configuration",
            ],
            diagnostic_info={"operation": operation, "error": str(e)},
            urgency="medium",
        )


async def _handle_export(
    format: str | None, output_path: str | None, options: dict[str, Any]
) -> dict | str:
    """Handle document export operation."""
    if not format:
        return build_error_response(
            error="missing_format",
            error_code="MISSING_FORMAT_PARAMETER",
            message="Export requires 'format' parameter",
            recovery_options=[
                "Provide format parameter: pdf, html, docx, odt, etc.",
                "Check supported formats for your Typora version",
            ],
            supported_formats=["pdf", "html", "docx", "odt"],
            urgency="medium",
        )
    if not output_path:
        return build_error_response(
            error="missing_output_path",
            error_code="MISSING_OUTPUT_PATH_PARAMETER",
            message="Export requires 'output_path' parameter",
            recovery_options=[
                "Provide output_path parameter with destination file path",
                "Ensure output directory exists or is writable",
            ],
            urgency="medium",
        )

    # Ensure output directory exists
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Build export parameters
    export_params = {
        "format": format,
        "outputPath": str(output_path_obj),
        "includeImages": options.get("include_images", True),
        "embedStyles": options.get("embed_styles", True),
        "embedImages": options.get("embed_images", True),
        "keepSource": options.get("keep_source", False),
    }

    # Add format-specific options
    if format == "pdf":
        export_params.update(
            {
                "pageSize": options.get("page_size", "A4"),
                "margins": options.get("margins", "1cm"),
                "printBackground": options.get("print_background", True),
            }
        )
    elif format in ["html", "docx"]:
        export_params.update(
            {
                "embedImages": options.get("embed_images", True),
                "keepSource": options.get("keep_source", False),
            }
        )

    result = await typora_client.call("export", export_params)

    if not result["success"]:
        return build_error_response(
            error="export_failed",
            error_code="TYPORA_EXPORT_ERROR",
            message=f"Export failed: {result.get('error', 'Unknown error')}",
            recovery_options=[
                "Ensure current document is open in Typora",
                "Check output path is writable",
                "Verify format is supported by Typora",
                "Check Typora plugin configuration",
            ],
            diagnostic_info={
                "format": format,
                "output_path": output_path,
                "typora_error": result.get("error"),
            },
            urgency="medium",
        )

    return build_success_response(
        operation="export",
        summary=f"Document exported successfully as {format.upper()}",
        result={
            "format": format.upper(),
            "output_path": output_path,
            "images_embedded": export_params.get("embedImages", True),
            "export_params": export_params,
        },
        next_steps=[
            f"Open {output_path} to verify export",
            "Share or archive the exported file",
            "Use batch_export for multiple files",
        ],
    )


async def _handle_get_content() -> dict:
    """Get current document content."""
    result = await typora_client.call("getContent")

    if not result["success"]:
        return build_error_response(
            error="content_retrieval_failed",
            error_code="TYPORA_CONTENT_ERROR",
            message=f"Content retrieval failed: {result.get('error', 'Unknown error')}",
            recovery_options=[
                "Ensure document is open in Typora",
                "Check json_rpc plugin is enabled",
                "Verify Typora connection",
            ],
            diagnostic_info={"typora_error": result.get("error")},
            urgency="medium",
        )

    content = result["result"]
    if not content:
        return build_success_response(
            operation="get_content",
            summary="Current document is empty or no document open",
            result={"content": "", "line_count": 0, "char_count": 0},
            next_steps=["Open a document in Typora", "Use new_file to create a new document"],
        )

    # Provide summary and preview
    lines = content.split("\n")
    line_count = len(lines)
    char_count = len(content)

    # Get first few lines as preview
    preview_lines = lines[:10] if len(lines) > 10 else lines
    preview = "\n".join(preview_lines)
    if len(lines) > 10:
        preview += f"\n... ({len(lines) - 10} more lines)"

    return build_success_response(
        operation="get_content",
        summary=f"Document content retrieved: {line_count} lines, {char_count} characters",
        result={
            "content": content,
            "line_count": line_count,
            "char_count": char_count,
            "preview": preview,
        },
        next_steps=[
            "Use set_content to replace entire document",
            "Use insert_text to add content at cursor",
            "Use search_replace to modify specific text",
        ],
    )


async def _handle_set_content(content: str | None) -> dict | str:
    """Replace entire document content."""
    if content is None:
        return "[UNICODE] set_content requires 'content' parameter"

    result = await typora_client.call("setContent", {"content": content})

    if not result["success"]:
        return f"[UNICODE] **Content Update Failed**\n\nError: {result['error']}"

    return f"""[UNICODE] **Document Content Updated**

**New Content Length**: {len(content)} characters
**Lines**: {len(content.split(chr(10)))}

**Note**: Previous content has been replaced. Use `save_file` to persist changes."""


async def _handle_insert_text(text: str | None, position: str | None) -> dict:
    """Insert text at cursor position."""
    if text is None:
        return "[UNICODE] insert_text requires 'text' parameter"

    insert_params = {"text": text}
    if position:
        insert_params["position"] = position

    result = await typora_client.call("insertText", insert_params)

    if not result["success"]:
        return f"[UNICODE] **Text Insertion Failed**\n\nError: {result['error']}\n\n**Check**:\n[UNICODE] Document is open in Typora\n[UNICODE] Cursor position is valid"

    return f"""[UNICODE] **Text Inserted Successfully**

**Inserted Text**: {text[:50]}{"..." if len(text) > 50 else ""}
**Position**: {position or "current cursor"}

**Tip**: Use `get_cursor` to check current position before inserting."""


async def _handle_get_cursor() -> dict:
    """Get cursor position and selection."""
    result = await typora_client.call("getCursor")

    if not result["success"]:
        return f"[UNICODE] **Cursor Info Failed**\n\nError: {result['error']}"

    cursor_info = result["result"]
    return f"""[LOCATION] **Cursor Position**

**Line**: {cursor_info.get("line", "N/A")}
**Column**: {cursor_info.get("column", "N/A")}
**Selection Start**: {cursor_info.get("selectionStart", "N/A")}
**Selection End**: {cursor_info.get("selectionEnd", "N/A")}
**Selected Text Length**: {cursor_info.get("selectedTextLength", 0)} characters

**Use this info for**:
[UNICODE] Precise text insertion with `insert_text`
[UNICODE] Understanding current editing context"""


async def _handle_open_file(file_path: str | None) -> dict:
    """Open a file in Typora."""
    if file_path is None:
        return "[UNICODE] open_file requires 'file_path' parameter"

    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        return f"[UNICODE] **File Not Found**\n\nPath: {file_path}\n\n**Check**:\n[UNICODE] File exists at specified path\n[UNICODE] Path is absolute or correct relative path"

    result = await typora_client.call("openFile", {"path": str(file_path_obj)})

    if not result["success"]:
        return f"[UNICODE] **File Open Failed**\n\nError: {result['error']}\n\n**Check**:\n[UNICODE] File is accessible\n[UNICODE] Typora can read the file format"

    return f"""[UNICODE] **File Opened in Typora**

**Path**: {file_path}
**Name**: {file_path_obj.name}

**Ready for**:
[UNICODE] Export operations
[UNICODE] Content manipulation
[UNICODE] Editing workflows"""


async def _handle_save_file() -> dict:
    """Save current file."""
    result = await typora_client.call("saveFile")

    if not result["success"]:
        return f"[UNICODE] **Save Failed**\n\nError: {result['error']}\n\n**Check**:\n[UNICODE] Document is open\n[UNICODE] File path is writable\n[UNICODE] Sufficient disk space"

    return "[UNICODE] **File Saved Successfully**"


async def _handle_new_file() -> dict:
    """Create new document."""
    result = await typora_client.call("newFile")

    if not result["success"]:
        return f"[UNICODE] **New File Failed**\n\nError: {result['error']}"

    return """[UNICODE] **New Document Created**

**Ready for**:
[UNICODE] Content insertion with `set_content` or `insert_text`
[UNICODE] Template application with `template_apply`
[UNICODE] Saving with `save_file`"""


async def _handle_get_metadata() -> dict:
    """Get document metadata."""
    result = await typora_client.call("getMetadata")

    if not result["success"]:
        return f"[UNICODE] **Metadata Retrieval Failed**\n\nError: {result['error']}"

    metadata = result["result"]

    # Format metadata for display
    formatted_metadata = []
    for key, value in metadata.items():
        formatted_metadata.append(f"[UNICODE] **{key}**: {value}")

    return f"""[LIST] **Document Metadata**

{chr(10).join(formatted_metadata)}

**Use `set_metadata` to modify these values**"""


async def _handle_set_metadata(options: dict[str, Any]) -> dict:
    """Set document metadata."""
    if not options:
        return "[UNICODE] set_metadata requires metadata options (e.g., {'title': 'New Title'})"

    result = await typora_client.call("setMetadata", options)

    if not result["success"]:
        return f"[UNICODE] **Metadata Update Failed**\n\nError: {result['error']}"

    updated_fields = list(options.keys())
    return f"""[UNICODE] **Metadata Updated**

**Fields Updated**: {", ".join(updated_fields)}

**Use `get_metadata` to verify changes**"""


async def _handle_search_replace(
    find_text: str | None, replace_text: str | None, options: dict[str, Any]
) -> dict:
    """Search and replace text."""
    if find_text is None:
        return "[UNICODE] search_replace requires 'find_text' parameter"

    params = {
        "findText": find_text,
        "replaceText": replace_text or "",
        "caseSensitive": options.get("case_sensitive", False),
        "wholeWord": options.get("whole_word", False),
        "regex": options.get("regex", False),
        "replaceAll": options.get("replace_all", True),
    }

    result = await typora_client.call("searchReplace", params)

    if not result["success"]:
        return f"[UNICODE] **Search/Replace Failed**\n\nError: {result['error']}"

    replace_info = result["result"]
    replacements = replace_info.get("replacements", 0)

    return f"""[UNICODE] **Search and Replace Completed**

**Search Term**: "{find_text}"
**Replace With**: "{replace_text or "(empty)"}"
**Replacements Made**: {replacements}
**Options**: Case {"sensitive" if params["caseSensitive"] else "insensitive"}, {"Whole word" if params["wholeWord"] else "Partial match"}

**Tip**: Use `save_file` to persist changes"""


async def _handle_get_themes() -> dict:
    """List available themes."""
    result = await typora_client.call("getThemes")

    if not result["success"]:
        return f"[UNICODE] **Theme List Failed**\n\nError: {result['error']}"

    themes = result["result"].get("themes", [])
    current_theme = result["result"].get("current", "Unknown")

    if not themes:
        return "[LIST] **No Themes Available**"

    theme_list = []
    for theme in themes:
        marker = " [UNICODE] CURRENT" if theme == current_theme else ""
        theme_list.append(f"[UNICODE] {theme}{marker}")

    return f"""[ART] **Available Themes**

{chr(10).join(theme_list)}

**Use `set_theme` to change theme**"""


async def _handle_set_theme(theme: str | None) -> dict:
    """Change theme."""
    if theme is None:
        return "[UNICODE] set_theme requires 'theme' parameter"

    result = await typora_client.call("setTheme", {"theme": theme})

    if not result["success"]:
        return f"[UNICODE] **Theme Change Failed**\n\nError: {result['error']}\n\n**Check**:\n[UNICODE] Theme name is valid (use `get_themes` to list)\n[UNICODE] Theme files exist"

    return f"""[UNICODE] **Theme Changed**

**New Theme**: {theme}

**Changes take effect immediately in Typora**"""


async def _handle_toggle_sidebar(visible: bool | None) -> dict:
    """Toggle sidebar visibility."""
    result = await typora_client.call("toggleSidebar", {"visible": visible})

    if not result["success"]:
        return f"[UNICODE] **Sidebar Toggle Failed**\n\nError: {result['error']}"

    action = "shown" if visible else "hidden" if visible is False else "toggled"
    return f"""[UNICODE] **Sidebar {action.capitalize()}**

**Use `visible=true/false` to explicitly show/hide**"""


async def _handle_toggle_toolbar(visible: bool | None) -> dict:
    """Toggle toolbar visibility."""
    result = await typora_client.call("toggleToolbar", {"visible": visible})

    if not result["success"]:
        return f"[UNICODE] **Toolbar Toggle Failed**\n\nError: {result['error']}"

    action = "shown" if visible else "hidden" if visible is False else "toggled"
    return f"""[UNICODE] **Toolbar {action.capitalize()}**

**Use `visible=true/false` to explicitly show/hide**"""


async def _handle_batch_export(
    files: list[str] | None,
    format: str | None,
    output_path: str | None,
    options: dict[str, Any],
) -> dict:
    """Export multiple files."""
    if not files:
        return "[UNICODE] batch_export requires 'files' parameter (list of file paths)"
    if not format:
        return "[UNICODE] batch_export requires 'format' parameter"
    if not output_path:
        return "[UNICODE] batch_export requires 'output_path' parameter (output directory)"

    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    successful_exports = 0

    for file_path in files:
        try:
            # Open file
            open_result = await typora_client.call("openFile", {"path": file_path})
            if not open_result["success"]:
                results.append(
                    f"[UNICODE] {Path(file_path).name}: Failed to open - {open_result['error']}"
                )
                continue

            # Brief pause for loading - configurable via environment
            sleep_duration = float(os.getenv("TYPORA_LOAD_DELAY", "0.5"))
            await asyncio.sleep(sleep_duration)

            # Export file
            export_filename = Path(file_path).stem + f".{format}"
            export_path = output_dir / export_filename

            export_result = await typora_client.call(
                "export",
                {
                    "format": format,
                    "outputPath": str(export_path),
                    "includeImages": options.get("include_images", True),
                    "embedStyles": options.get("embed_styles", True),
                },
            )

            if export_result["success"]:
                results.append(f"[UNICODE] {export_filename}: Exported successfully")
                successful_exports += 1
            else:
                results.append(
                    f"[UNICODE] {export_filename}: Export failed - {export_result['error']}"
                )

        except Exception as e:
            results.append(f"[UNICODE] {Path(file_path).name}: Error - {str(e)}")

    return f"""[UNICODE][UNICODE] **Batch Export Completed**

**Files Processed**: {len(files)}
**Successful Exports**: {successful_exports}
**Format**: {format.upper()}
**Output Directory**: {output_path}

**Results**:
{chr(10).join(results)}

**Summary**: {successful_exports}/{len(files)} files exported successfully"""


async def _handle_content_analysis() -> dict:
    """Analyze document structure and content."""
    result = await typora_client.call("getContent")

    if not result["success"]:
        return f"[UNICODE] **Content Analysis Failed**\n\nError: {result['error']}"

    content = result["result"]
    if not content:
        return "[DOC] **Document Analysis**: Empty document"

    # Analyze content
    lines = content.split("\n")
    headings = [line for line in lines if line.startswith("#")]
    links = len([line for line in lines if "[" in line and "](" in line])
    code_blocks = content.count("```")
    images = len([line for line in lines if "![" in line and "](" in line])

    word_count = len(content.split())
    char_count = len(content)

    # Heading structure
    heading_levels: dict[int, int] = {}
    for heading in headings:
        level = len(heading) - len(heading.lstrip("#"))
        heading_levels[level] = heading_levels.get(level, 0) + 1

    return f"""[CHART] **Document Analysis**

**Basic Stats**:
[UNICODE] Total Lines: {len(lines)}
[UNICODE] Word Count: {word_count}
[UNICODE] Character Count: {char_count}

**Content Elements**:
[UNICODE] Headings: {len(headings)}
[UNICODE] Links: {links}
[UNICODE] Code Blocks: {code_blocks // 2} (paired)
[UNICODE] Images: {images}

**Heading Structure**:
{chr(10).join(f"[UNICODE] Level {level}: {count} headings" for level, count in sorted(heading_levels.items()))}

**Document Health**:
[UNICODE] Has content: {"[UNICODE]" if content.strip() else "[UNICODE]"}
[UNICODE] Has structure: {"[UNICODE]" if headings else "[UNICODE]"}
[UNICODE] Has links: {"[UNICODE]" if links > 0 else "[UNICODE]"}"""


async def _handle_link_validation() -> dict:
    """Validate and fix links in document."""
    result = await typora_client.call("getContent")

    if not result["success"]:
        return f"[UNICODE] **Link Validation Failed**\n\nError: {result['error']}"

    content = result["result"]
    lines = content.split("\n")

    # Find links
    links_found = []
    for i, line in enumerate(lines, 1):
        if "[" in line and "](" in line:
            # Extract link text and URL
            start = line.find("](")
            if start > 0:
                end = line.find(")", start)
                if end > 0:
                    link_text = line[line.find("[") + 1 : start]
                    link_url = line[start + 2 : end]
                    links_found.append(
                        {
                            "line": i,
                            "text": link_text,
                            "url": link_url,
                            "full_match": line,
                        }
                    )

    if not links_found:
        return "[LINK] **Link Validation**: No links found in document"

    # Validate links (basic checks)
    validation_results = []
    valid_links = 0
    broken_links = 0

    for link in links_found:
        is_valid = True
        issues = []

        url = link["url"]

        # Check for basic issues
        if not url.strip():
            issues.append("Empty URL")
            is_valid = False
        elif url.startswith("http") and not url.startswith(("http://", "https://")):
            issues.append("Invalid HTTP/HTTPS URL")
            is_valid = False
        elif url.startswith(("http://", "https://")):
            # Could add HTTP validation here, but keeping it simple
            pass
        elif not Path(url).exists() and not url.startswith(("http://", "https://")):
            issues.append("Local file not found")
            is_valid = False

        if is_valid:
            valid_links += 1
            validation_results.append(
                f"[UNICODE] Line {link['line']}: {link['text']} [UNICODE] {url}"
            )
        else:
            broken_links += 1
            validation_results.append(
                f"[UNICODE] Line {link['line']}: {link['text']} [UNICODE] {url} ({', '.join(issues)})"
            )

    return f"""[LINK] **Link Validation Results**

**Links Found**: {len(links_found)}
**Valid Links**: {valid_links}
**Broken Links**: {broken_links}

**Details**:
{chr(10).join(validation_results)}

**Actions Available**:
[UNICODE] Manual fix broken links
[UNICODE] Use `search_replace` to batch fix link patterns
[UNICODE] Consider using Advanced Memory link resolution for [[WikiLinks]]"""


async def _handle_template_apply(template_name: str | None, options: dict[str, Any]) -> dict:
    """Apply an Advanced Memory template to the document."""
    if template_name is None:
        return "[UNICODE] template_apply requires 'template_name' parameter"

    # For now, provide common templates. In future, could integrate with actual Advanced Memory templates
    templates = {
        "research_note": """# Research Note

## Overview
[Brief description of research topic]

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Methodology
[How the research was conducted]

## Sources
- Source 1
- Source 2

## Conclusions
[Key takeaways and implications]

## Tags
#research #notes""",
        "meeting_notes": """# Meeting Notes

**Date**: [Meeting Date]
**Attendees**: [List attendees]
**Location**: [Physical or virtual location]

## Agenda
1. Topic 1
2. Topic 2
3. Topic 3

## Discussion Notes

### Topic 1
- Discussion points
- Decisions made
- Action items

### Topic 2
- Discussion points
- Decisions made
- Action items

## Action Items
- [ ] Action 1 - Owner: [Name] - Due: [Date]
- [ ] Action 2 - Owner: [Name] - Due: [Date]

## Next Meeting
**Date**: [Next meeting date]
**Focus**: [Meeting focus/topics]

## Tags
#meeting #notes""",
        "project_plan": """# Project Plan

## Project Overview
**Name**: [Project Name]
**Goal**: [Project goal/objective]
**Timeline**: [Start date] - [End date]
**Budget**: [Budget information]

## Stakeholders
- Sponsor: [Name]
- Team Lead: [Name]
- Team Members: [List]

## Scope
### In Scope
- Deliverable 1
- Deliverable 2

### Out of Scope
- Item 1
- Item 2

## Milestones
- Milestone 1: [Date] - [Description]
- Milestone 2: [Date] - [Description]
- Milestone 3: [Date] - [Description]

## Risk Assessment
### High Risk
- Risk 1: [Description] - Mitigation: [Strategy]

### Medium Risk
- Risk 2: [Description] - Mitigation: [Strategy]

## Communication Plan
- Weekly status updates
- Monthly stakeholder reviews
- Documentation updates

## Success Criteria
- Criterion 1
- Criterion 2
- Criterion 3

## Tags
#project #planning""",
        "code_review": """# Code Review

## Pull Request
**Title**: [PR Title]
**Author**: [Author Name]
**Reviewers**: [Reviewer Names]

## Files Changed
- File 1: [Changes summary]
- File 2: [Changes summary]

## Code Quality
### Strengths
- Good implementation of [feature]
- Clean code structure
- Proper error handling

### Areas for Improvement
- [Issue 1]: [Suggestion]
- [Issue 2]: [Suggestion]

## Security Considerations
- [Security review notes]

## Performance Impact
- [Performance analysis]

## Testing
### Test Coverage
- Unit tests: [Coverage %]
- Integration tests: [Pass/Fail]
- Manual testing: [Results]

### Test Recommendations
- [Additional test suggestions]

## Deployment Notes
- [Deployment considerations]
- [Rollback plan]
- [Monitoring requirements]

## Approval Status
- [ ] Code review complete
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Ready for merge

## Tags
#code-review #development""",
    }

    if template_name not in templates:
        available_templates = ", ".join(templates.keys())
        return f"""[UNICODE] **Unknown Template**

Template '{template_name}' not found.

**Available Templates**:
[UNICODE] {available_templates}

**Usage**: typora_control("template_apply", template_name="research_note")"""

    template_content = templates[template_name]

    # Apply any customizations from options
    if options.get("custom_title"):
        template_content = template_content.replace("[Project Name]", options["custom_title"])
    if options.get("custom_date"):
        template_content = template_content.replace("[Meeting Date]", options["custom_date"])

    result = await typora_client.call("setContent", {"content": template_content})

    if not result["success"]:
        return f"[UNICODE] **Template Application Failed**\n\nError: {result['error']}"

    return f"""[UNICODE] **Template Applied Successfully**

**Template**: {template_name}
**Content Length**: {len(template_content)} characters

**Template includes**:
[UNICODE] Structured sections and placeholders
[UNICODE] Professional formatting
[UNICODE] Action items and checklists
[UNICODE] Tagging suggestions

**Next Steps**:
[UNICODE] Replace [placeholders] with actual content
[UNICODE] Customize sections as needed
[UNICODE] Save with `save_file`"""


async def _handle_sync_to_advanced_memory(options: dict[str, Any]) -> dict:
    """Sync current Typora document to Advanced Memory."""
    # Get current content
    content_result = await typora_client.call("getContent")
    if not content_result["success"]:
        return f"[UNICODE] **Sync Failed - Content Retrieval**\n\nError: {content_result['error']}"

    content = content_result["result"]
    if not content:
        return "[UNICODE] **Sync Failed - No Content**\n\nDocument appears to be empty"

    # Get metadata
    metadata_result = await typora_client.call("getMetadata")
    title = "Synced from Typora"
    if metadata_result["success"]:
        metadata = metadata_result["result"]
        if metadata.get("title"):
            title = metadata["title"]

    # For now, provide guidance. In future, could directly call Advanced Memory APIs
    return f"""[UNICODE][UNICODE] **Ready to Sync to Advanced Memory**

**Document Title**: {title}
**Content Length**: {len(content)} characters

**To complete sync**:
1. Copy the content from Typora
2. Use Advanced Memory's `write_note` tool:
   ```
   write_note(
       title="{title}",
       content="[paste content here]",
       folder="imported/typora"
   )
   ```

**Content Preview**:
{content[:200]}{"..." if len(content) > 200 else ""}

**Future Enhancement**: Direct API integration for seamless sync"""


async def _handle_unknown_operation(operation: str) -> dict | str:
    """Handle unknown operations."""
    available_ops = [
        "export",
        "get_content",
        "set_content",
        "insert_text",
        "get_cursor",
        "open_file",
        "save_file",
        "new_file",
        "get_metadata",
        "set_metadata",
        "search_replace",
        "get_themes",
        "set_theme",
        "toggle_sidebar",
        "toggle_toolbar",
        "batch_export",
        "content_analysis",
        "link_validation",
        "template_apply",
        "sync_to_advanced_memory",
    ]

    return build_error_response(
        error="unknown_operation",
        error_code="UNSUPPORTED_OPERATION",
        message=f"Unknown operation: {operation}",
        recovery_options=[
            "Check available operations list",
            "Verify operation name spelling",
            "Use help() to see all available operations",
        ],
        available_operations=available_ops,
        urgency="low",
    )


# Additional utility functions for integration


async def check_typora_connection() -> bool:
    """Check if Typora json_rpc is available."""
    try:
        result = await typora_client.call("status")
        return result["success"]
    except Exception:
        return False


async def get_typora_status() -> dict[str, Any]:
    """Get comprehensive Typora status."""
    status: dict[str, Any] = {
        "connection": False,
        "current_file": None,
        "theme": None,
        "ui_state": {},
    }

    # Check connection
    status["connection"] = await check_typora_connection()

    if status["connection"]:
        # Get current file info
        try:
            metadata_result = await typora_client.call("getMetadata")
            if metadata_result["success"]:
                metadata = metadata_result["result"]
                status["current_file"] = metadata.get("filePath")
        except Exception:
            pass

        # Get theme
        try:
            theme_result = await typora_client.call("getThemes")
            if theme_result["success"]:
                status["theme"] = theme_result["result"].get("current")
        except Exception:
            pass

    return status
