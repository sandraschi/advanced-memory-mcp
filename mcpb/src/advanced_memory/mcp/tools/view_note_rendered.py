"""View note with rendered Mermaid diagrams in HTML artifact."""

from loguru import logger
from markdown import markdown

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.read_note import read_note


@mcp.tool(
    description="""Display notes as interactive HTML artifacts with rendered Mermaid diagrams.

This specialized viewing tool creates an HTML artifact that renders Mermaid diagrams live
using Mermaid.js, providing a visual viewing experience directly in Claude.

RENDERING FEATURES:
- Live Mermaid diagram rendering via CDN
- Full markdown to HTML conversion
- Syntax highlighting for code blocks
- Styled presentation with proper formatting
- Interactive diagrams (where supported by Mermaid)

MERMAID SUPPORT:
- Flowcharts (graph TD, graph LR)
- Sequence diagrams
- Gantt charts
- Mind maps
- ER diagrams
- Class diagrams
- State diagrams
- All standard Mermaid types

PARAMETERS:
- identifier (str, REQUIRED): Note title, permalink, or memory:// URL
- theme (str, default="default"): Mermaid theme (default, dark, forest, neutral)
- page (int, default=1): Pagination page for long content
- page_size (int, default=10): Items per page
- project (str, optional): Target project (defaults to active project)

USAGE EXAMPLES:
Basic rendered view: view_note_rendered("System Architecture")
Dark theme: view_note_rendered("Database Schema", theme="dark")
By permalink: view_note_rendered("docs/mermaid-guide")

RETURNS:
Interactive HTML artifact with:
- Rendered Mermaid diagrams
- Formatted markdown content
- Syntax-highlighted code blocks
- Professional styling

DIFFERENCE FROM VIEW_NOTE:
- Renders Mermaid diagrams (not just code)
- Returns HTML artifact (not markdown)
- Loads Mermaid.js from CDN
- Interactive viewing experience

NOTE: Requires internet connection for Mermaid.js CDN loading.""",
)
async def view_note_rendered(
    identifier: str,
    theme: str = "default",
    page: int = 1,
    page_size: int = 10,
    project: str | None = None,
) -> str:
    """View a note with rendered Mermaid diagrams as HTML artifact.

    This tool reads a note and displays it as an interactive HTML artifact with
    live Mermaid diagram rendering, providing a visual experience in Claude.

    Args:
        identifier: The title or permalink of the note to view
        theme: Mermaid theme (default, dark, forest, neutral)
        page: Page number for paginated results (default: 1)
        page_size: Number of items per page (default: 10)
        project: Optional project name. If not provided, uses current active project.

    Returns:
        HTML artifact with rendered diagrams and formatted content.
    """

    logger.info(f"Rendering note with Mermaid: {identifier}")

    # Get the note content
    content = await read_note.fn(identifier, page, page_size, project)

    # Check for errors
    if "# Note Not Found:" in content:
        return content

    # Extract title
    title = identifier
    lines = content.split("\n")
    for line in lines:
        if line.startswith("title:"):
            title = line.split("title:", 1)[1].strip().strip('"').strip("'")
            break
        elif line.startswith("# "):
            title = line[2:].strip()
            break

    # Convert markdown to HTML
    html_content = markdown(
        content,
        extensions=[
            "extra",
            "codehilite",
            "toc",
            "fenced_code",
            "tables",
            "nl2br",
        ],
    )

    # Create full HTML with Mermaid support
    html_artifact = _create_html_with_mermaid(html_content, title, theme)

    # Return as HTML artifact
    artifact_xml = f'<artifact identifier="note-rendered-{hash(identifier) & 0x7FFFFFFF}" type="text/html" title="{title}">\n{html_artifact}\n</artifact>'

    return f"""<instructions>
Create an HTML artifact using the returned content. This will display the note with rendered Mermaid diagrams.
</instructions>
{artifact_xml}

✅ Note rendered with Mermaid diagrams: **{title}**"""


def _create_html_with_mermaid(content: str, title: str, theme: str = "default") -> str:
    """Create complete HTML document with Mermaid support."""

    # Validate theme
    valid_themes = ["default", "dark", "forest", "neutral", "base"]
    if theme not in valid_themes:
        theme = "default"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- Mermaid.js -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background: #fff;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        
        h1 {{
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        
        h2 {{
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        
        code {{
            background-color: rgba(27,31,35,0.05);
            border-radius: 3px;
            font-size: 85%;
            margin: 0;
            padding: 0.2em 0.4em;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        }}
        
        pre {{
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            margin: 0;
            display: block;
        }}
        
        blockquote {{
            border-left: 4px solid #dfe2e5;
            color: #6a737d;
            padding: 0 1em;
            margin: 0;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        
        table th,
        table td {{
            border: 1px solid #dfe2e5;
            padding: 6px 13px;
        }}
        
        table th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        
        .mermaid {{
            text-align: center;
            margin: 20px 0;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
        }}
        
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        ul, ol {{
            padding-left: 2em;
        }}
        
        li {{
            margin-bottom: 0.25em;
        }}
        
        hr {{
            border: 0;
            border-top: 1px solid #eaecef;
            margin: 24px 0;
        }}
    </style>
</head>
<body>
    {content}
    
    <script>
        // Initialize Mermaid
        mermaid.initialize({{
            startOnLoad: true,
            theme: '{theme}',
            securityLevel: 'loose',
            fontFamily: 'arial',
            fontSize: 14,
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            sequence: {{
                useMaxWidth: true,
                htmlLabels: true
            }},
            gantt: {{
                useMaxWidth: true
            }}
        }});
        
        // Convert code blocks to Mermaid diagrams
        document.addEventListener('DOMContentLoaded', function() {{
            // Find all code blocks with language "mermaid"
            const codeBlocks = document.querySelectorAll('code.language-mermaid, code.mermaid');
            
            codeBlocks.forEach((block, index) => {{
                // Get the parent pre element
                const pre = block.parentElement;
                if (pre.tagName.toLowerCase() === 'pre') {{
                    // Create a new div for Mermaid
                    const mermaidDiv = document.createElement('div');
                    mermaidDiv.className = 'mermaid';
                    mermaidDiv.textContent = block.textContent;
                    
                    // Replace the pre block with the mermaid div
                    pre.parentElement.replaceChild(mermaidDiv, pre);
                }}
            }});
            
            // Re-render all Mermaid diagrams
            setTimeout(() => {{
                mermaid.init(undefined, document.querySelectorAll('.mermaid'));
            }}, 100);
        }});
    </script>
</body>
</html>"""

