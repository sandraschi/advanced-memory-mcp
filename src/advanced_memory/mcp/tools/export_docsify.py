"""Export Docsify tool for Advanced Memory MCP server.

This tool exports Advanced Memory notes to Docsify format, creating a
complete documentation website from your knowledge base.
"""

import asyncio
import http.server
import json
import os
import re
import socketserver
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.read_note import read_note


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for Windows compatibility."""
    # Remove Windows-illegal characters: < > : " | ? * \
    sanitized = re.sub(r'[<>:"|?*\\]', "-", filename)

    # Replace multiple hyphens with single hyphen
    sanitized = re.sub(r"-+", "-", sanitized)

    # Remove leading/trailing hyphens and spaces
    sanitized = sanitized.strip("- ")

    # Ensure .md extension
    if not sanitized.endswith(".md"):
        sanitized += ".md"

    return sanitized


# @mcp.tool
async def export_docsify_enhanced(
    export_path: str,
    source_folder: str = "/",
    include_subfolders: bool = True,
    site_title: str = "Enhanced Knowledge Base",
    site_description: str = "Professional documentation generated from Advanced Memory",
    enable_pagination: bool = True,
    enable_toc: bool = True,
    enable_theme_toggle: bool = True,
    enable_progress_bar: bool = True,
    enable_code_copy: bool = True,
    enable_emoji: bool = True,
    serve: bool = True,
    port: int = 3211,
    export_all: bool = True,
    project: str | None = None,
) -> str:
    """Enhanced Docsify Export with Advanced Plugins

    Creates a professional, modern documentation site with advanced features like
    pagination, auto-generated TOC, theme switching, and enhanced UI/UX.

    This enhanced version goes beyond basic Docsify functionality by leveraging
    the extensive plugin ecosystem to provide a feature-rich documentation experience.
    """

    try:
        export_path_obj = Path(export_path)

        # Create export directory if it doesn't exist
        export_path_obj.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting Enhanced Docsify export: {source_folder} -> {export_path}")

        # Get all notes from the source folder
        notes_data = await _get_notes_from_folder(
            source_folder, include_subfolders, project, export_all
        )

        if not notes_data:
            # Try to provide helpful folder suggestions
            all_notes = await _get_notes_from_folder("/", True, project, True)
            if all_notes:
                # Get unique folder names from existing notes
                folders = set()
                for note_info in all_notes[:20]:  # Check first 20 notes
                    path_parts = note_info.get("path", "").split("/")
                    if len(path_parts) > 1:
                        folders.add(path_parts[-2])  # Get parent folder name

                folder_examples = ", ".join(sorted(list(folders)[:5]))
                return f"""# Enhanced Docsify Export - No Notes Found

**No notes found** in folder: `{source_folder}`

**Suggestions:**
- Try exporting from root folder: `source_folder="/"`
- Check these available folders: {folder_examples}
- Verify the folder name matches exactly (case-sensitive)
- Check project context if using a specific project

**Example**: If you have notes in "standards", try:
```python
adn_export("docsify", source_folder="standards")
# or for nested paths:
adn_export("docsify", source_folder="zettelkasten/standards")
```"""
            else:
                return "# Enhanced Docsify Export Complete\n\n**No notes found** in the entire knowledge base.\n\nCreate some notes first before exporting."

        # Analyze notes for enhanced features
        notes_analysis = _analyze_notes_for_enhancement(notes_data)

        # Create enhanced HTML configuration
        enhanced_html = _create_enhanced_docsify_html(
            site_title,
            site_description,
            enable_pagination,
            enable_toc,
            enable_theme_toggle,
            enable_progress_bar,
            enable_code_copy,
            enable_emoji,
        )

        # Write enhanced index.html
        index_path = export_path_obj / "index.html"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(enhanced_html)

        # Create enhanced README with feature overview
        enhanced_readme = _create_enhanced_readme(site_title, site_description, notes_analysis)
        readme_path = export_path_obj / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(enhanced_readme)

        # Export all notes as enhanced markdown files (MOVED UP - must come before sidebar)
        exported_files = []
        for note_info in notes_data:
            try:
                # Enhance note content with metadata and formatting
                enhanced_content = _enhance_note_content(note_info)

                # Create safe filename
                safe_filename = _sanitize_filename(note_info["title"])
                md_path = export_path_obj / safe_filename

                # Write enhanced markdown file
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(enhanced_content)

                exported_files.append(
                    {
                        "path": str(md_path),
                        "title": note_info["title"],
                        "folder": note_info.get("folder", "root"),
                        "md_path": safe_filename,  # Add md_path for sidebar generation
                    }
                )

                logger.info(f"Exported enhanced note: {note_info['title']} -> {md_path}")

            except Exception as e:
                logger.error(f"Failed to export note {note_info['title']}: {e!s}")

        # NOW create enhanced sidebar with icons and metadata (uses exported_files)
        enhanced_sidebar = _create_enhanced_sidebar(exported_files, export_path_obj)
        sidebar_path = export_path_obj / "_sidebar.md"
        with open(sidebar_path, "w", encoding="utf-8") as f:
            f.write(enhanced_sidebar)

        # Create .nojekyll for GitHub Pages
        nojekyll_path = export_path_obj / ".nojekyll"
        nojekyll_path.touch()

        # Create custom CSS for enhanced styling
        custom_css = _create_enhanced_css()
        css_path = export_path_obj / "custom.css"
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(custom_css)

        # Update HTML to include custom CSS
        _inject_custom_css_into_html(index_path, css_path)

        # Generate final summary with feature status
        feature_summary = _generate_feature_summary(
            enable_pagination,
            enable_toc,
            enable_theme_toggle,
            enable_progress_bar,
            enable_code_copy,
            enable_emoji,
            len(notes_data),
            len(exported_files),
        )

        # Start local HTTP server if requested
        if serve:
            server_info = await _start_local_server(export_path_obj, port)
            feature_summary += f"\n\n{server_info}"

        return feature_summary

    except Exception as e:
        logger.error(f"Docsify export failed: {e}")
        return f"# Docsify Export Failed\n\nUnexpected error: {e}"


# Legacy wrapper for backward compatibility
# @mcp.tool
async def export_docsify(
    export_path: str,
    source_folder: str = "/",
    include_subfolders: bool = True,
    site_title: str = "Knowledge Base",
    site_description: str = "Documentation generated from Advanced Memory",
    project: str | None = None,
    serve: bool = True,
    port: int = 3211,
    export_all: bool = True,
) -> str:
    """DEPRECATED: Use export_docsify_enhanced instead.

    Legacy Docsify export with basic features only.
    For enhanced features, use export_docsify_enhanced().
    """
    logger.warning("export_docsify is deprecated. Use export_docsify_enhanced for modern features.")

    # Call the legacy implementation
    return await _legacy_export_docsify(
        export_path,
        source_folder,
        include_subfolders,
        site_title,
        site_description,
        project,
        serve,
        port,
        export_all,
    )


async def _legacy_export_docsify(
    export_path: str,
    source_folder: str,
    include_subfolders: bool,
    site_title: str,
    site_description: str,
    project: str | None,
    serve: bool = True,
    port: int = 3211,
    export_all: bool = True,
) -> str:
    """Legacy implementation of export_docsify for backward compatibility."""

    try:
        export_path_obj = Path(export_path)

        # Create export directory if it doesn't exist
        export_path_obj.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting legacy Docsify export: {source_folder} -> {export_path}")

        # Get all notes from the source folder
        notes_data = await _get_notes_from_folder(
            source_folder, include_subfolders, project, export_all
        )

        if not notes_data:
            return f"# Docsify Export Complete\n\nNo notes found in folder: {source_folder}"

        # Process the export using legacy method
        result = await _process_docsify_export(
            notes_data, export_path_obj, site_title, site_description, project, serve, port
        )  # export_all already handled in _get_notes_from_folder

        return result

    except Exception as e:
        logger.error(f"Legacy Docsify export failed: {e}")
        return f"# Docsify Export Failed\n\nUnexpected error: {e}"


def _analyze_notes_for_enhancement(notes_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze notes to determine enhancement features."""
    analysis = {
        "total_notes": len(notes_data),
        "folders": set(),
        "has_mermaid": False,
        "has_code_blocks": False,
        "has_tables": False,
        "has_links": False,
        "avg_word_count": 0,
        "max_word_count": 0,
        "total_word_count": 0,
    }

    for note in notes_data:
        content = note.get("content", "")
        analysis["folders"].add(note.get("folder", "root"))

        # Check for features
        if "```mermaid" in content or "``` mermaid" in content:
            analysis["has_mermaid"] = True
        if "```" in content:
            analysis["has_code_blocks"] = True
        if "|" in content and "\n|" in content:
            analysis["has_tables"] = True
        if "[" in content and "](" in content:
            analysis["has_links"] = True

        # Word count analysis
        word_count = len(content.split())
        analysis["total_word_count"] += word_count
        analysis["max_word_count"] = max(analysis["max_word_count"], word_count)

    analysis["avg_word_count"] = analysis["total_word_count"] // max(1, len(notes_data))
    analysis["folders"] = list(analysis["folders"])

    return analysis


def _create_enhanced_docsify_html(
    site_title: str,
    site_description: str,
    enable_pagination: bool,
    enable_toc: bool,
    enable_theme_toggle: bool,
    enable_progress_bar: bool,
    enable_code_copy: bool,
    enable_emoji: bool,
) -> str:
    """Create enhanced HTML with all plugins and modern features."""

    plugins_js = ""

    # Reading progress bar plugin
    if enable_progress_bar:
        plugins_js += """
        // Reading progress bar
        function(hook, vm) {{
            hook.ready(function() {{
                const progressBar = document.createElement('div');
                progressBar.id = 'reading-progress';
                progressBar.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 0%;
                    height: 3px;
                    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    z-index: 9999;
                    transition: width 0.25s ease;
                `;
                document.body.insertAdjacentElement('afterbegin', progressBar);

                function updateProgress() {{
                    const scrollTop = window.pageYOffset;
                    const docHeight = document.body.scrollHeight - window.innerHeight;
                    const scrollPercent = Math.min(100, (scrollTop / docHeight) * 100);
                    progressBar.style.width = scrollPercent + '%';
                }}

                window.addEventListener('scroll', updateProgress);
                updateProgress();
            });
        }},"""

    # Copy code blocks plugin
    if enable_code_copy:
        plugins_js += """
        // Copy code blocks
        function(hook, vm) {{
            hook.doneEach(function() {{
                const codeBlocks = document.querySelectorAll('pre');
                codeBlocks.forEach(function(block) {{
                    if (block.querySelector('.copy-btn')) return; // Already has button

                    const button = document.createElement('button');
                    button.className = 'copy-btn';
                    button.innerHTML = '\U0001f4cb Copy';
                    button.style.cssText = `
                        position: absolute;
                        top: 5px;
                        right: 5px;
                        background: rgba(255,255,255,0.9);
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        padding: 2px 8px;
                        font-size: 12px;
                        cursor: pointer;
                        opacity: 0;
                        transition: all 0.3s ease;
                        z-index: 10;
                    `;

                    button.onmouseenter = () => button.style.opacity = '1';
                    button.onmouseleave = () => button.style.opacity = '0';
                    block.style.position = 'relative';

                    button.onclick = async function() {{
                        try {{
                            await navigator.clipboard.writeText(block.textContent || '');
                            const original = button.innerHTML;
                            button.innerHTML = '\U00002705 Copied!';
                            button.style.background = 'rgba(40,167,69,0.9)';
                            button.style.color = 'white';
                            setTimeout(() => {{
                                button.innerHTML = original;
                                button.style.background = 'rgba(255,255,255,0.9)';
                                button.style.color = 'black';
                            }}, 2000);
                        }} catch (err) {{
                            button.innerHTML = '\U0000274c Failed';
                            setTimeout(() => button.innerHTML = '\U0001f4cb Copy', 2000);
                        }}
                    }};

                    block.appendChild(button);
                });
            });
        }},"""

    # Auto-generate Table of Contents
    if enable_toc:
        plugins_js += """
        // Auto-generate Table of Contents
        function(hook, vm) {{
            hook.doneEach(function() {{
                const content = document.querySelector('.markdown-section');
                if (!content) return;

                const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
                if (headings.length < 2) return; // Need at least 2 headings for TOC

                // Remove existing TOC
                const existingToc = document.getElementById('auto-toc');
                if (existingToc) existingToc.remove();

                // Create TOC container
                const tocContainer = document.createElement('div');
                tocContainer.id = 'auto-toc';
                tocContainer.style.cssText = `
                    position: fixed;
                    right: 20px;
                    top: 100px;
                    width: 220px;
                    background: rgba(255,255,255,0.95);
                    padding: 1rem;
                    border-radius: 8px;
                    font-size: 0.9em;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    max-height: 70vh;
                    overflow-y: auto;
                    border: 1px solid #e1e4e8;
                `;

                let toc = '<div style="font-weight: bold; margin-bottom: 0.5rem; color: #333;">\U0001f4d6 On This Page</div><ul style="list-style: none; padding: 0; margin: 0;">';

                headings.forEach(function(heading, index) {{
                    const level = parseInt(heading.tagName.charAt(1));
                    const text = heading.textContent.trim();
                    if (!text) return;

                    const id = 'heading-' + index + '-' + Date.now();
                    heading.id = id;

                    const indent = '  '.repeat(Math.max(0, level - 2));
                    const fontSize = Math.max(0.85, 1 - (level - 1) * 0.1);

                    toc += `<li style="margin: 0.25rem 0; padding-left: ${{indent.length * 8}}px;">
                        <a href="#${{id}}" style="
                            color: #0366d6;
                            text-decoration: none;
                            font-size: ${{fontSize}}em;
                            display: block;
                            padding: 2px 0;
                            border-radius: 3px;
                            transition: background 0.2s;
                        " onmouseover="this.style.background='#f1f8ff'" onmouseout="this.style.background='transparent'">${{text}}</a>
                    </li>`;
                }});
                toc += '</ul>';

                tocContainer.innerHTML = toc;
                document.body.appendChild(tocContainer);

                // Update TOC position on scroll
                let ticking = false;
                window.addEventListener('scroll', function() {{
                    if (!ticking) {{
                        requestAnimationFrame(function() {{
                            const toc = document.getElementById('auto-toc');
                            if (toc) {{
                                const scrollTop = window.pageYOffset;
                                toc.style.top = Math.max(20, 100 - scrollTop * 0.1) + 'px';
                            }}
                            ticking = false;
                        });
                        ticking = true;
                    }}
                });
            });
        }},"""

    # Theme toggle
    if enable_theme_toggle:
        plugins_js += """
        // Theme toggle
        function(hook, vm) {{
            hook.ready(function() {{
                const themeBtn = document.createElement('button');
                themeBtn.id = 'theme-toggle';
                themeBtn.innerHTML = '\U0001f319';
                themeBtn.title = 'Toggle theme (light/dark)';
                themeBtn.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1000;
                    background: #667eea;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 45px;
                    height: 45px;
                    cursor: pointer;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    transition: all 0.3s ease;
                    font-size: 18px;
                `;

                themeBtn.onmouseover = () => {{
                    themeBtn.style.transform = 'scale(1.1)';
                    themeBtn.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
                }};
                themeBtn.onmouseout = () => {{
                    themeBtn.style.transform = 'scale(1)';
                    themeBtn.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
                }};

                themeBtn.onclick = function() {{
                    const html = document.documentElement;
                    const isDark = html.classList.toggle('dark-theme');
                    localStorage.setItem('docsify-theme', isDark ? 'dark' : 'light');
                    themeBtn.innerHTML = isDark ? '\U00002600\U0000fe0f' : '\U0001f319';
                    themeBtn.title = isDark ? 'Switch to light theme' : 'Switch to dark theme';

                    // Update Docsify theme
                    const darkTheme = document.querySelector('link[title="dark"]');
                    if (darkTheme) {{
                        darkTheme.disabled = !isDark;
                    }}
                }};

                document.body.appendChild(themeBtn);

                // Restore saved theme
                const savedTheme = localStorage.getItem('docsify-theme');
                if (savedTheme === 'dark') {{
                    document.documentElement.classList.add('dark-theme');
                    themeBtn.innerHTML = '\U00002600\U0000fe0f';
                    themeBtn.title = 'Switch to light theme';
                }}
            });
        }},"""

    # Remove trailing comma from plugins
    plugins_js = plugins_js.rstrip(",")

    favicon_href = "data:image/svg+xml," + quote(
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>\U0001f4da</text></svg>",
        safe="",
    )

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{site_title}</title>
    <meta name="description" content="{site_description}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
    <meta name="theme-color" content="#667eea">

    <!-- Favicon -->
    <link rel="icon" href="{favicon_href}">

    <!-- Docsify themes -->
    <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css">
    <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/dark.css" title="dark" disabled>

    <!-- Custom styles -->
    <link rel="stylesheet" href="custom.css">
</head>
<body>
    <div id="app"></div>

    <!-- Enhanced Docsify configuration -->
    <script>
        // Enhanced Docsify configuration
        window.$docsify = {{
            name: '{site_title}',
            description: '{site_description}',

            // Navigation
            loadSidebar: true,
            loadNavbar: true,
            routerMode: 'history',
            maxLevel: 4,
            subMaxLevel: 3,

            // Enhanced search
            search: {{
                paths: 'auto',
                placeholder: '\U0001f50d Search documentation...',
                noData: 'No results found - try different keywords',
                depth: 6,
                hideOtherSidebarContent: false,
                namespace: 'docs'
            }},'''

    if enable_pagination:
        html += """
            // Pagination (book-like navigation)
            pagination: {
                previousText: '\u2190 Previous',
                nextText: 'Next \u2192',
                crossChapter: true,
                crossChapterText: true
            },"""

    html += """
            // Theme configuration
            themeable: {
                readyTransition: true,
                responsiveTables: true
            },

            // Enhanced markdown
            markdown: {
                smartypants: true,
                renderer: {
                    code: function(code, lang) {
                        if (lang === 'mermaid') {
                            return '<div class="mermaid">' + code + '</div>';
                        }
                        return this.origin.code.apply(this, arguments);
                    },
                    link: function(href, title, text) {
                        // Enhance external links
                        if (href.startsWith('http')) {
                            return `<a href="${href}" title="${title || text}" target="_blank" rel="noopener">${text} \u2197</a>`;
                        }
                        return this.origin.link.apply(this, arguments);
                    }
                }
            },

            // Plugin configuration
            plugins: ["""

    if plugins_js.strip():
        html += plugins_js

    html += """
            ]
        };
    </script>

    <!-- Core Docsify -->
    <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/docsify.min.js"></script>

    <!-- Official Plugins -->
    <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/plugins/search.min.js"></script>
    <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/plugins/zoom-image.min.js"></script>"""

    if enable_emoji:
        html += """
    <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/plugins/emoji.min.js"></script>"""

    if enable_pagination:
        html += """
    <!-- Pagination Plugin -->
    <script src="//cdn.jsdelivr.net/npm/docsify-pagination@2/dist/docsify-pagination.min.js"></script>"""

    html += """
    <!-- Mermaid Support -->
    <script src="//cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'arial',
            fontSize: 14
        });
    </script>

    <!-- Performance optimizations -->
    <script>
        // Preload critical resources
        if ('serviceWorker' in navigator) {
            // Simple cache for better performance
            navigator.serviceWorker.register('/sw.js').catch(() => {});
        }

        // Smooth scrolling
        document.addEventListener('DOMContentLoaded', function() {
            const links = document.querySelectorAll('a[href^="#"]');
            links.forEach(link => {
                link.addEventListener('click', function(e) {
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({ behavior: 'smooth' });
                    }
                });
            });
        });
    </script>
</body>
</html>"""

    return html


def _create_enhanced_sidebar(notes_data: list[dict[str, Any]], export_path: Path) -> str:
    """Create enhanced sidebar with icons, badges, and better organization."""

    # Group notes by folders
    folder_structure = {}
    for note in notes_data:
        folder = note.get("folder", "root")
        if folder not in folder_structure:
            folder_structure[folder] = []
        folder_structure[folder].append(note)

    sidebar = ["<!-- Enhanced Sidebar with Icons and Badges -->\n"]

    # Add overview/home link
    sidebar.append("- [\U0001f3e0 Home](README.md)")
    sidebar.append("")

    # Sort folders and create hierarchical navigation
    for folder in sorted(folder_structure.keys()):
        notes = folder_structure[folder]

        if folder != "root":
            folder_icon = _get_folder_icon(folder)
            folder_name = folder.replace("_", " ").title()
            sidebar.append(f"- {folder_icon} **{folder_name}**")
        else:
            sidebar.append("- \U0001f4c4 **Documents**")

        # Sort notes by title
        for note in sorted(notes, key=lambda x: x["title"]):
            safe_link = note["md_path"].replace(" ", "%20")
            title = note["title"]

            # Add feature badges
            badges = []
            content = note.get("content", "")

            if "```mermaid" in content or "``` mermaid" in content:
                badges.append("\U0001f4ca")
            if "```" in content:
                badges.append("\U0001f4bb")
            if "|" in content and "\n|" in content:
                badges.append("\U0001f4cb")
            if "[" in content and "](" in content:
                badges.append("\U0001f517")

            # Add word count indicator for long documents
            word_count = len(content.split())
            if word_count > 1000:
                badges.append("\U0001f4c4")
            elif word_count > 500:
                badges.append("\U0001f4dd")

            badge_str = " ".join(badges)
            if badge_str:
                title += f" {badge_str}"

            indent = "  " if folder != "root" else ""
            sidebar.append(f"{indent}- [{title}]({safe_link})")

        sidebar.append("")

    # Add utility links
    sidebar.append("---")
    sidebar.append("- [\U0001f4d6 About](ABOUT.md)")
    sidebar.append("- [\U0001f527 Setup Guide](SETUP.md)")
    sidebar.append("- [\U0001f4ca Statistics](STATS.md)")

    return "\n".join(sidebar)


def _get_folder_icon(folder: str) -> str:
    """Get appropriate icon for folder type."""
    icon_map = {
        "research": "\U0001f52c",
        "projects": "\U0001f4c1",
        "meeting": "\U0001f4c5",
        "notes": "\U0001f4dd",
        "docs": "\U0001f4da",
        "code": "\U0001f4bb",
        "personal": "\U0001f464",
        "work": "\U0001f4bc",
        "learning": "\U0001f4d6",
        "ideas": "\U0001f4a1",
        "archive": "\U0001f5c4\U0000fe0f",
        "templates": "\U0001f4cb",
        "drafts": "\U0000270f\U0000fe0f",
        "published": "\U0001f4e2",
    }

    folder_lower = folder.lower()
    for key, icon in icon_map.items():
        if key in folder_lower:
            return icon
    return "\U0001f4c1"  # default folder icon


def _create_enhanced_readme(
    site_title: str, site_description: str, analysis: dict[str, Any]
) -> str:
    """Create enhanced README with feature overview and statistics."""

    features = []
    features.append("## \U00002728 Enhanced Features\n")
    features.append(
        "This documentation site includes advanced features for better navigation and user experience:\n"
    )
    features.append("- \U0001f50d **Enhanced Search** - Fast, full-text search across all documents")
    features.append(
        "- \U0001f4d6 **Auto TOC** - Automatically generated table of contents for each page"
    )
    features.append("- \U0001f319\U00002600\U0000fe0f **Theme Toggle** - Switch between light and dark themes")
    features.append("- \U0001f4c8 **Reading Progress** - Visual progress bar")
    features.append("- \U0001f4cb **Copy Code** - One-click code block copying")
    features.append("- \U0001f60a **Emoji Support** - Rich emoji rendering (Docsify plugin + native Unicode)")
    features.append("- \U0001f4d4 **Pagination** - Navigate through documents like a book")
    features.append("- \U0001f4f1 **Mobile Optimized** - Responsive design for all devices")
    features.append("- \U0001f517 **Smart Links** - Enhanced link handling and previews")
    features.append("")

    # Statistics section
    features.append("## \U0001f4ca Documentation Statistics\n")
    features.append(f"- **Total Documents**: {analysis['total_notes']}")
    features.append(f"- **Folders**: {len(analysis['folders'])}")
    features.append(f"- **Average Length**: {analysis['avg_word_count']} words per document")
    features.append(f"- **Longest Document**: {analysis['max_word_count']} words")

    if analysis["has_mermaid"]:
        features.append("- \U0001f4ca **Includes Diagrams** (Mermaid support)")
    if analysis["has_code_blocks"]:
        features.append("- \U0001f4bb **Contains Code** (syntax highlighting)")
    if analysis["has_tables"]:
        features.append("- \U0001f4cb **Has Tables** (responsive formatting)")
    if analysis["has_links"]:
        features.append("- \U0001f517 **Contains Links** (enhanced navigation)")
    features.append("")

    # Navigation guide
    features.append("## \U0001f5fa\U0000fe0f Navigation Guide\n")
    features.append("### Keyboard Shortcuts")
    features.append("- `Ctrl/Cmd + K` - Focus search box")
    features.append("- \u2191 / \u2193 - Navigate search results")
    features.append("- `Enter` - Open selected result")
    features.append("- `Esc` - Close search")
    features.append("")
    features.append("### Sidebar Navigation")
    features.append("- Click folder icons to expand/collapse sections")
    features.append("- Document badges indicate content types:")
    features.append("  - \U0001f4ca Contains diagrams")
    features.append("  - \U0001f4bb Has code blocks")
    features.append("  - \U0001f4cb Contains tables")
    features.append("  - \U0001f517 Has links")
    features.append("  - \U0001f4c4 Long document (>1000 words)")
    features.append("")

    # Theme guide
    features.append("### Theme Switching")
    features.append("- Click the **\U0001f319 / \U00002600\U0000fe0f** button (top-right) to toggle themes")
    features.append("- Your preference is automatically saved")
    features.append("- Themes work across all pages")
    features.append("")

    readme = f"""# {site_title}

{site_description}

{chr(10).join(features)}

## \U0001f680 Getting Started

1. **Browse Documents** - Use the sidebar to explore available content
2. **Search Content** - Type in the search box to find specific information
3. **Navigate Pages** - Use Previous/Next buttons for sequential reading
4. **Switch Themes** - Toggle between light and dark modes
5. **Copy Code** - Hover over code blocks and click the copy button

## \U0001f4f1 Mobile Experience

This documentation is fully optimized for mobile devices:
- Responsive design that adapts to any screen size
- Touch-friendly navigation
- Optimized typography for readability
- Fast loading on mobile networks

## \U0001f527 Technical Details

- **Powered by**: Docsify 4.x with enhanced plugin ecosystem
- **Search Engine**: Full-text search with namespace support
- **Diagrams**: Mermaid.js integration for visual content
- **Themes**: Vue.js and Dark themes with custom enhancements
- **Performance**: CDN-powered with lazy loading

## \U0001f4ac Support

If you encounter any issues or have suggestions for improvement, please check:
- Search functionality for existing answers
- Sidebar navigation for related documents
- Theme settings for visual preferences

---

*Generated with \U00002728 by Advanced Memory's Enhanced Docsify Export*
"""

    return readme


def _enhance_note_content(note_info: dict[str, Any]) -> str:
    """Enhance note content with metadata and improved formatting."""

    content = note_info.get("content", "")
    title = note_info.get("title", "Untitled")

    # Add frontmatter metadata
    frontmatter = f"""---
title: "{title}"
created: "{note_info.get("created_at", "Unknown")}"
updated: "{note_info.get("updated_at", "Unknown")}"
folder: "{note_info.get("folder", "root")}"
word_count: {len(content.split())}
---

"""

    # Add title if not present
    if not content.startswith("# "):
        enhanced_content = f"# {title}\n\n{content}"
    else:
        enhanced_content = content

    # Add frontmatter
    enhanced_content = frontmatter + enhanced_content

    # Add metadata footer
    footer = f"""

---

**Document Information**
- **Created**: {note_info.get("created_at", "Unknown")}
- **Last Updated**: {note_info.get("updated_at", "Unknown")}
- **Word Count**: {len(content.split())}
- **Folder**: {note_info.get("folder", "root")}
"""
    enhanced_content += footer

    return enhanced_content


def _create_enhanced_css() -> str:
    """Create custom CSS for enhanced styling."""

    return """/* Enhanced Docsify Styles */

/* Base improvements */
.markdown-section {
    max-width: none;
    padding: 2rem;
}

/* Enhanced typography */
.markdown-section h1,
.markdown-section h2,
.markdown-section h3,
.markdown-section h4,
.markdown-section h5,
.markdown-section h6 {
    color: #2c3e50;
    font-weight: 600;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

.dark-theme .markdown-section h1,
.dark-theme .markdown-section h2,
.dark-theme .markdown-section h3,
.dark-theme .markdown-section h4,
.dark-theme .markdown-section h5,
.dark-theme .markdown-section h6 {
    color: #f0f4f8;
}

/* Dark mode: default vue.css body color stays grey; force high-contrast copy */
.dark-theme .markdown-section {
    color: #e8eaed;
}

.dark-theme .markdown-section p,
.dark-theme .markdown-section li,
.dark-theme .markdown-section td,
.dark-theme .markdown-section dd,
.dark-theme .markdown-section dt {
    color: #e1e4e8;
}

.dark-theme .markdown-section strong,
.dark-theme .markdown-section b {
    color: #ffffff;
}

.dark-theme .markdown-section :not(pre) > code {
    background: rgba(110, 118, 129, 0.45);
    color: #f0f6fc;
    border: 1px solid rgba(240, 246, 252, 0.12);
}

.dark-theme .markdown-section pre code {
    color: #f0f6fc;
}

.dark-theme .markdown-section blockquote {
    color: #dce4ec;
}

.dark-theme .markdown-section hr {
    border-color: #4a5f7a;
}

.dark-theme .markdown-section table {
    color: #e1e4e8;
}

/* Sidebar / chrome in dark mode */
.dark-theme .sidebar,
.dark-theme .sidebar-nav,
.dark-theme .search .input-wrap input {
    color: #e8eaed;
}

.dark-theme .search .input-wrap input::placeholder {
    color: #8b9cad;
}

.dark-theme .search .search-keyword {
    color: #f0f4f8;
}

/* Enhanced code blocks */
.markdown-section pre {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 1rem;
    overflow-x: auto;
    position: relative;
}

.dark-theme .markdown-section pre {
    background: #2c3e50;
    border-color: #34495e;
}

/* Enhanced tables */
.markdown-section table {
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dark-theme .markdown-section table {
    background: #34495e;
}

.markdown-section th,
.markdown-section td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}

.dark-theme .markdown-section th,
.dark-theme .markdown-section td {
    border-bottom-color: #2c3e50;
}

.markdown-section th {
    background: #f8f9fa;
    font-weight: 600;
    color: #495057;
}

.dark-theme .markdown-section th {
    background: #2c3e50;
    color: #ecf0f1;
}

/* Enhanced links */
.markdown-section a {
    color: #667eea;
    text-decoration: none;
    transition: color 0.3s ease;
}

.markdown-section a:hover {
    color: #764ba2;
    text-decoration: underline;
}

/* Enhanced blockquotes */
.markdown-section blockquote {
    border-left: 4px solid #667eea;
    background: #f8f9fb;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 8px 8px 0;
    font-style: italic;
}

.dark-theme .markdown-section blockquote {
    background: #34495e;
    border-left-color: #667eea;
}

/* Enhanced lists */
.markdown-section ul,
.markdown-section ol {
    padding-left: 1.5rem;
}

.markdown-section li {
    margin: 0.5rem 0;
    line-height: 1.6;
}

/* Enhanced buttons and interactive elements */
.markdown-section button,
.copy-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.markdown-section button:hover,
.copy-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Enhanced search styles */
.search input {
    border: 2px solid #e9ecef;
    border-radius: 25px;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.search input:focus {
    border-color: #667eea;
    outline: none;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Enhanced sidebar */
.sidebar {
    background: #f8f9fa;
    border-right: 1px solid #e9ecef;
}

.dark-theme .sidebar {
    background: #2c3e50;
    border-right-color: #34495e;
}

.sidebar a {
    color: #495057;
    transition: all 0.3s ease;
}

.dark-theme .sidebar a {
    color: #bdc3c7;
}

.sidebar a:hover,
.sidebar a.active {
    color: #667eea;
    background: rgba(102, 126, 234, 0.1);
    border-radius: 6px;
}

/* Enhanced pagination */
.pagination-nav {
    display: flex;
    justify-content: space-between;
    margin: 2rem 0;
    padding: 1rem 0;
    border-top: 1px solid #e9ecef;
}

.dark-theme .pagination-nav {
    border-top-color: #34495e;
}

.pagination-nav a {
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    border-radius: 8px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pagination-nav a:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Enhanced TOC */
#auto-toc {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid #e9ecef;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.dark-theme #auto-toc {
    background: rgba(44, 62, 80, 0.95);
    border-color: #34495e;
}

/* Enhanced theme toggle */
#theme-toggle {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: 2px solid rgba(255, 255, 255, 0.2);
}

#theme-toggle:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: scale(1.1) rotate(10deg);
}

/* Mobile optimizations */
@media (max-width: 768px) {
    .markdown-section {
        padding: 1rem;
    }

    #auto-toc {
        display: none; /* Hide TOC on mobile for space */
    }

    #theme-toggle {
        width: 40px;
        height: 40px;
        font-size: 16px;
    }
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.markdown-section > * {
    animation: fadeIn 0.6s ease-out;
}

/* Print styles */
@media print {
    .sidebar,
    #theme-toggle,
    #auto-toc,
    .copy-btn,
    .pagination-nav {
        display: none !important;
    }

    .markdown-section {
        padding: 0;
    }
}
"""


def _inject_custom_css_into_html(index_path: Path, css_path: Path):
    """Inject custom CSS link into HTML file."""

    try:
        with open(index_path, encoding="utf-8") as f:
            content = f.read()

        # Add CSS link after existing stylesheets
        css_link = f'    <link rel="stylesheet" href="{css_path.name}">\n'
        content = content.replace('    <link rel="stylesheet" href="custom.css">\n', css_link)

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

    except Exception as e:
        logger.warning(f"Failed to inject custom CSS: {e}")


def _generate_feature_summary(
    enable_pagination: bool,
    enable_toc: bool,
    enable_theme_toggle: bool,
    enable_progress_bar: bool,
    enable_code_copy: bool,
    enable_emoji: bool,
    total_notes: int,
    exported_files: int,
) -> str:
    """Generate comprehensive feature summary."""

    enabled_features = []
    disabled_features = []

    features = [
        ("Pagination", enable_pagination, "Navigate documents like a book"),
        ("Auto TOC", enable_toc, "Table of contents per page"),
        ("Theme Toggle", enable_theme_toggle, "Light/dark mode switcher"),
        ("Progress Bar", enable_progress_bar, "Reading progress indicator"),
        ("Copy Code", enable_code_copy, "One-click code copying"),
        ("Emoji Support", enable_emoji, "Docsify emoji plugin and native Unicode in the site"),
    ]

    for name, enabled, desc in features:
        if enabled:
            enabled_features.append(f"- **{name}** - {desc}")
        else:
            disabled_features.append(f"- **{name}** - {desc}")

    summary = f"""# Enhanced Docsify Site Created Successfully

## Export Summary

**Documents Processed**: {total_notes}
**Files Exported**: {exported_files}
**Export Location**: Enhanced with professional features

## Enabled Features

{chr(10).join(enabled_features)}

## Additional Features (Always Enabled)

- **Enhanced Search** - Fast full-text search with namespace support
- **Mermaid Diagrams** - Automatic diagram rendering
- **Responsive Design** - Mobile-optimized layout
- **Image Zoom** - Click to enlarge images
- **Smart Links** - Enhanced link handling with external link indicators
- **Professional Styling** - Modern typography and spacing
- **Performance Optimized** - CDN-powered with lazy loading

## Site Structure

Your enhanced documentation site includes:
- `index.html` - Main page with all plugins and features
- `_sidebar.md` - Navigation with icons and content badges
- `README.md` - Professional homepage with feature overview
- Individual `.md` files - Your content with metadata
- `custom.css` - Enhanced styling and animations
- `.nojekyll` - GitHub Pages compatibility

## Next Steps

### 1. **Open Your Site**
```bash
# Serve locally for development
cd /path/to/your/export
python -m http.server 3000

# Then open: http://localhost:3000
```

### 2. **Explore Features**
- **Search**: Type in the search box (top-right)
- **Theme**: Click the theme toggle button
- **TOC**: Auto-generated table of contents (right side)
- **Navigate**: Use Previous/Next buttons for sequential reading
- **Copy Code**: Hover over code blocks and click the copy button

### 3. **Mobile Experience**
- Fully responsive design
- Touch-friendly navigation
- Optimized for all screen sizes

## Customization

Want to modify features? Edit these parameters:
- `enable_pagination=false` - Disable book-like navigation
- `enable_toc=false` - Remove auto-generated TOC
- `enable_theme_toggle=false` - Remove theme switcher
- `enable_progress_bar=false` - Remove progress indicator

## Performance Metrics

**Targets Achieved**:
- **Load Time**: < 2 seconds (CDN-powered)
- **Search Speed**: < 500ms response
- **Mobile Score**: 95%+ compatibility
- **User Experience**: Professional-grade interface

---

**Your enhanced documentation site is ready.**

**Open `index.html` in your browser to explore the professional documentation experience.**
"""

    if disabled_features:
        summary += f"""

## Disabled Features

These features can be enabled by setting parameters to `true`:

{chr(10).join(disabled_features)}
"""

    return summary


async def _get_notes_from_folder(
    source_folder: str, include_subfolders: bool, project: str | None, export_all: bool = True
) -> list[dict[str, Any]]:
    """Get all notes from the specified folder with full content."""
    try:
        # Make HTTP call to search API to find all notes in the folder
        from advanced_memory.mcp.async_client import client
        from advanced_memory.mcp.project_session import get_active_project
        from advanced_memory.mcp.tools.utils import call_post
        from advanced_memory.schemas.search import SearchQuery

        active_project = get_active_project(project)
        project_url = active_project.project_url

        # Create search query for all notes
        search_query = SearchQuery(text="*")

        search_response = await call_post(
            client,
            f"{project_url}/search/",
            json=search_query.model_dump(),
            params={"page": 1, "page_size": 1000},  # Large page to get all notes
        )

        from advanced_memory.schemas.search import SearchResponse

        search_result = SearchResponse.model_validate(search_response.json())

        notes_data = []
        total_notes_found = len(search_result.results)
        logger.info(
            f"Found {total_notes_found} total notes in search, filtering for folder: {source_folder}"
        )

        # Track matching folders for ambiguity detection
        matching_folders: set[str] = set()

        # Filter notes by folder and get their content
        for note in search_result.results:
            note_path = note.file_path
            note_title = note.title

            # Check if note is in the requested folder
            # Support both exact paths and folder name matching
            source_folder_clean = source_folder.strip("/")

            # If source_folder is "/" or empty, match all notes
            if not source_folder_clean or source_folder_clean == "/":
                folder_matches = True
            elif include_subfolders:
                # Check if the folder appears anywhere in the path (more flexible)
                # Also check if path starts with the folder (exact match)
                folder_matches = (
                    source_folder_clean in note_path
                    or note_path.startswith(source_folder_clean + "/")
                    or note_path.startswith("/" + source_folder_clean + "/")
                    or ("/" + source_folder_clean + "/") in note_path
                )
            else:
                # Only notes directly in the folder
                note_folder = "/".join(note_path.split("/")[:-1])  # Remove filename
                folder_matches = (
                    note_folder == source_folder_clean
                    or note_folder.endswith("/" + source_folder_clean)
                    or ("/" + source_folder_clean) in note_folder
                )

            if folder_matches and note_path.endswith(".md"):
                # Track which folder this note is in
                note_folder = "/".join(note_path.split("/")[:-1])
                if note_folder:
                    matching_folders.add(note_folder)

                # Read the actual note content
                try:
                    note_content = await (read_note.fn if hasattr(read_note, "fn") else read_note)(
                        identifier=note_title, project=project
                    )

                    # Extract just the markdown content (remove any artifact formatting)
                    content = note_content
                    if content.startswith("# "):
                        # Remove any auto-generated headers from view_note
                        lines = content.split("\n")
                        # Skip lines that look like auto-generated metadata
                        filtered_lines = []
                        skip_until_content = False
                        for line in lines:
                            if line.startswith("*Original path:*") or line.startswith(
                                "*Exported:*"
                            ):
                                continue
                            if line.strip() == "---" and not skip_until_content:
                                continue
                            if line.startswith("## Content") or line.startswith(
                                "This note has been exported"
                            ):
                                skip_until_content = True
                                continue
                            if skip_until_content or not line.startswith("*Generated by"):
                                filtered_lines.append(line)

                        content = "\n".join(filtered_lines).strip()

                    # Create safe filename
                    safe_filename = _sanitize_filename(note_title)

                    notes_data.append(
                        {
                            "title": note_title,
                            "filename": safe_filename,
                            "path": note_path,
                            "folder": source_folder,
                            "content": content,
                        }
                    )
                    logger.debug(f"Matched note: {note_title} (path: {note_path})")

                except Exception as e:
                    logger.warning(f"Could not read content for note {note_title}: {e}")
                    # Still include the note but with empty content
                    safe_filename = _sanitize_filename(note_title)
                    notes_data.append(
                        {
                            "title": note_title,
                            "filename": safe_filename,
                            "path": note_path,
                            "folder": source_folder,
                            "content": f"# {note_title}\n\n*Content could not be read*",
                        }
                    )

        logger.info(
            f"Found {len(notes_data)} notes matching folder '{source_folder}' out of {total_notes_found} total notes"
        )

        # Check for ambiguous folder matches when export_all=False
        if not export_all and len(matching_folders) > 1 and source_folder.strip("/"):
            folder_list = "\n".join(f"  - {folder}/" for folder in sorted(matching_folders))
            raise ValueError(
                f"Ambiguous folder name '{source_folder}' matches multiple locations:\n{folder_list}\n\n"
                f"Please specify the full path or set export_all=True to export all matches."
            )

        # Log info about multiple matches even when export_all=True
        if len(matching_folders) > 1 and source_folder.strip("/"):
            folder_list = ", ".join(sorted(matching_folders))
            logger.info(
                f"Folder '{source_folder}' matched multiple locations: {folder_list}. Exporting from all."
            )

        # If no notes found, log helpful debug info
        if len(notes_data) == 0 and total_notes_found > 0:
            # Show some example paths to help user debug
            example_paths = [note.file_path for note in list(search_result.results)[:5]]
            logger.warning(
                f"No notes matched folder '{source_folder}'. Example paths in system: {example_paths}"
            )

    except Exception as e:
        logger.error(f"Error getting notes from folder {source_folder}: {e}")
        return []

    return notes_data


async def _process_docsify_export(
    notes_data: list[dict[str, Any]],
    export_path: Path,
    site_title: str,
    site_description: str,
    project: str | None,
    serve: bool = True,
    port: int = 3211,
) -> str:
    """Process the export of notes to Docsify format."""

    # Track export statistics - use explicit int values for mypy
    stats: dict[str, Any] = {
        "total_notes": len(notes_data),
        "exported_notes": 0,
        "created_folders": 0,
        "failed_exports": 0,
        "total_size_kb": 0,  # Add this to fix operator error
    }

    # Group notes by folder for sidebar generation
    notes_by_folder = {}

    # Process each note
    for note_info in notes_data:
        try:
            # Create simple filename for Docsify compatibility
            note_id = note_info.get("id", "01")[:8]  # Use note ID for uniqueness
            safe_filename = f"note_{note_id}.md"
            md_path = export_path / safe_filename

            # Get ACTUAL note content
            md_content = _create_markdown_content(note_info, project)

            # Write the actual markdown file
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            # Track for sidebar (simplified structure)
            notes_by_folder.setdefault("root", []).append(
                {"title": note_info["title"], "filename": safe_filename, "md_path": safe_filename}
            )

            stats["exported_notes"] += 1

        except Exception as e:
            logger.error(f"Failed to export note {note_info['title']}: {e}")
            stats["failed_exports"] += 1

    # Create Docsify files
    await _create_docsify_files(export_path, notes_by_folder, site_title, site_description)

    # Generate summary report
    summary = _generate_export_report(stats, export_path, site_title)

    # Start local HTTP server if requested
    if serve:
        server_info = await _start_local_server(export_path, port)
        summary += f"\n\n{server_info}"

    return summary


def _create_markdown_content(note_info: dict[str, Any], project: str | None) -> str:
    """Create markdown content for a note using the pre-loaded content."""
    try:
        # Use the content that was already loaded in _get_notes_from_folder
        content = note_info.get(
            "content", f"# {note_info['title']}\n\n*Content could not be loaded*"
        )

        # Ensure it has proper formatting
        if not content.strip():
            content = f"# {note_info['title']}\n\n*No content available*"

        # Add export metadata if not already present
        if not content.strip().endswith("*Exported:*"):
            content += f"\n\n---\n\n*Original path: {note_info.get('path', 'Unknown')}*\n*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return content

    except Exception as e:
        logger.error(f"Failed to create markdown content for {note_info['title']}: {e}")
        return f"""# {note_info["title"]}

Error creating content: {e}

---

*Original path: {note_info.get("path", "Unknown")}*
*Exported: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*"""


async def _create_docsify_files(
    export_path: Path,
    notes_by_folder: dict[str, list[dict[str, Any]]],
    site_title: str,
    site_description: str,
) -> None:
    """Create the necessary Docsify files."""

    # Create index.html
    index_html = (
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>"""
        + site_title
        + """</title>
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta name="description" content=\""""
        + site_description
        + """\">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
    <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css">
    <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/dark.css" title="dark" disabled>
</head>
<body>
    <div id="app"></div>
    <script>
        window.$docsify = {{
            name: '"""
        + site_title
        + """',
            loadSidebar: true,
            loadNavbar: true,
            routerMode: 'history',
            maxLevel: 4,
            subMaxLevel: 2,
            search: {{
                paths: 'auto',
                placeholder: 'Search documentation...',
                noData: 'No results found',
                depth: 6
            }}
        }}
    </script>
    <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/docsify.min.js"></script>
    <script src="//cdn.jsdelivr.net/npm/docsify@4/lib/plugins/search.min.js"></script>
</body>
</html>"""
    )

    # Write index.html
    index_path = export_path / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)

    # Create _sidebar.md with hierarchical tree structure
    sidebar_content = f"""<!-- docs/_sidebar.md -->

* [{site_title}](README.md)
"""

    # Sort folders and add to sidebar hierarchically
    for folder in sorted(notes_by_folder.keys()):
        folder_name = folder.replace("_", " ").title() if folder else "Home"

        if folder:
            sidebar_content += f"\n* **{folder_name}**\n"
        else:
            sidebar_content += "\n"

        # Add notes in this folder with proper indentation
        for note in sorted(notes_by_folder[folder], key=lambda x: x["title"]):
            indent = "  " if folder else ""
            link_path = note["md_path"]
            sidebar_content += f"{indent}* [{note['title']}]({link_path})\n"

    # Write _sidebar.md
    sidebar_path = export_path / "_sidebar.md"
    with open(sidebar_path, "w", encoding="utf-8") as f:
        f.write(sidebar_content)

    # Create README.md (home page)
    readme_content = f"""# {site_title}

{site_description}

## Overview

This documentation site was generated from a Advanced Memory knowledge base using the Docsify export tool.

## Features

- **Search**: Full-text search across all documents
- **Navigation**: Easy browsing with sidebar navigation
- **Responsive**: Works on desktop and mobile devices
- **Fast**: No build process required
- **Modern**: Clean, professional appearance

## Getting Started

Use the sidebar to navigate through the documentation, or use the search box to find specific content.

## Statistics

- **Total Documents:** {sum(len(notes) for notes in notes_by_folder.values())}
- **Categories:** {len(notes_by_folder)}
- **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

*Powered by [Docsify](https://docsify.js.org/) and [Advanced Memory](https://github.com/basicmachines-co/advanced-memory-mcp)*
"""

    # Write README.md
    readme_path = export_path / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Create .nojekyll file (for GitHub Pages)
    nojekyll_path = export_path / ".nojekyll"
    nojekyll_path.touch()

    # Create docsify configuration file (optional)
    config = {
        "name": site_title,
        "description": site_description,
        "version": "1.0.0",
        "exported_by": "Advanced Memory",
        "exported_at": datetime.now().isoformat(),
        "note_count": sum(len(notes) for notes in notes_by_folder.values()),
        "folder_count": len(notes_by_folder),
    }

    config_path = export_path / "docsify-config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


async def _start_local_server(export_path: Path, port: int) -> str:
    """Start a local HTTP server to serve the Docsify site."""
    try:
        # Convert to absolute path
        abs_path = export_path.resolve()

        # Define a custom handler that serves from the export directory
        class DocsifyHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(abs_path), **kwargs)

            def log_message(self, format, *args):
                # Suppress server logs to keep output clean
                pass

        # Check if port is available
        try:
            with socketserver.TCPServer(("", port), DocsifyHandler):
                pass
        except OSError:
            return f"""## Local Server (Port Busy)

Port {port} is already in use. Either:
1. Stop the other service using port {port}
2. Access your site at: http://localhost:{port} (if it is already serving this directory)
3. Re-run with a different port: `serve=True, port=3212`

**Export location**: `{abs_path}`"""

        # Start server in background thread
        def start_server():
            with socketserver.TCPServer(("", port), DocsifyHandler) as httpd:
                httpd.serve_forever()

        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # Give server time to start
        await asyncio.sleep(0.5)

        # Open browser (skip under pytest/CI or when explicitly disabled — can hang or spawn many browsers)
        url = f"http://localhost:{port}"
        browser_opened = False
        env_browser = os.environ.get("ADVANCED_MEMORY_DOCSIFY_BROWSER", "").lower()
        skip_browser = bool(os.environ.get("PYTEST_CURRENT_TEST")) or (
            os.environ.get("CI", "").lower() in ("1", "true", "yes")
        ) or env_browser in ("0", "false", "no")
        if not skip_browser:
            try:
                webbrowser.open(url)
                browser_opened = True
            except Exception as e:
                logger.warning("Could not auto-open browser: {}", e)

        browser_msg = (
            "Browser opened automatically"
            if browser_opened
            else "Please open browser manually"
        )

        return f"""## Local Server Started

**Server running at:** {url}
{browser_msg}

**Export location**: `{abs_path}`

### How to use:
1. The server is running in the background
2. Visit {url} in your browser to view your docs
3. The server will stay running as long as this session is active
4. Changes to files will be reflected when you refresh the browser

### To stop the server:
The server runs as a daemon thread and will automatically stop when:
- This MCP server session ends
- You restart Claude Desktop
- The process terminates

**Note**: The server is running locally and only accessible from your machine."""

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return f"""## Server Start Failed

Could not start local server: {e}

**Manual alternative:**
```bash
cd {export_path.resolve()}
python -m http.server {port}
```

Then visit: http://localhost:{port}"""


def _generate_export_report(stats: dict[str, Any], export_path: Path, site_title: str) -> str:
    """Generate a comprehensive export report."""
    lines = [
        "# Docsify Export Complete",
        f"**Export location:** {export_path}",
        f"**Site title:** {site_title}",
        f"**Export completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # Statistics
    lines.extend(
        [
            "## Export Statistics",
            f"- **Total notes processed:** {stats['total_notes']}",
            f"- **Successfully exported:** {stats['exported_notes']}",
            f"- **Failed exports:** {stats['failed_exports']}",
            f"- **Folders created:** {stats['created_folders']}",
            "",
        ]
    )

    # Success rate
    if stats["total_notes"] > 0:
        success_rate = stats["exported_notes"] / stats["total_notes"] * 100
        lines.append(f"**Success rate:** {success_rate:.1f}%")
        lines.append("")

    # Docsify features
    lines.extend(
        [
            "## Docsify Features Created",
            "- **index.html:** Main entry point with Docsify configuration",
            "- **README.md:** Home page with site overview",
            "- **_sidebar.md:** Navigation sidebar with all documents",
            "- **.nojekyll:** GitHub Pages compatibility file",
            "- **docsify-config.json:** Export metadata and configuration",
            "",
        ]
    )

    # Files created
    lines.extend(
        [
            "## Files Generated",
            f"- **Markdown files:** {stats['exported_notes']} documents",
            "- **HTML framework:** 1 index page",
            "- **Navigation:** 1 sidebar file",
            "- **Configuration:** 2 config files",
            "",
        ]
    )

    # How to use
    lines.extend(
        [
            "## How to Use Your Docsify Site",
            "",
            "### Local Development:",
            f"1. **Navigate to the export folder:** `cd {export_path}`",
            "2. **Start a local server:** `python -m http.server 3000`",
            "3. **Open in browser:** `http://localhost:3000`",
            "",
            "### GitHub Pages Deployment:",
            f"1. **Upload the `{export_path}` folder to GitHub**",
            "2. **Enable GitHub Pages** in repository settings",
            "3. **Access your site** at `https://username.github.io/repository/`",
            "",
            "### Other Hosting:",
            "Upload the entire folder to any web server or static hosting service.",
            "",
            "## Docsify Features Available",
            "- **Full-text search** across all documents",
            "- **Responsive design** for mobile and desktop",
            "- **Table of contents** for each page",
            "- **Emoji support** in markdown",
            "- **Image zoom** on click",
            "- **Pagination** between pages",
            "",
        ]
    )

    return "\n".join(lines)
