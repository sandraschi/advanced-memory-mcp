"""Textbook-based skill distiller for Advanced Memory.

This module provides functionality to extract and distill knowledge from textbooks
into high-quality Claude Skills.
"""

from pathlib import Path
from typing import Any

from loguru import logger

try:
    import pdfplumber
    import pypdf
except ImportError:
    pypdf = None
    pdfplumber = None


class TextbookDistiller:
    """Distill Claude Skills from textbook PDFs."""

    def __init__(self):
        """Initialize textbook distiller."""
        if pypdf is None and pdfplumber is None:
            raise ImportError(
                "PDF parsing libraries required. Install with: pip install pypdf pdfplumber"
            )
        logger.debug("TextbookDistiller initialized")

    def extract_toc(self, pdf_path: Path) -> list[dict[str, Any]]:
        """Extract table of contents from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of TOC entries with:
            - title: Chapter/section title
            - page: Page number
            - level: Heading level
        """
        try:
            logger.info(f"Extracting TOC from: {pdf_path}")
            toc = []

            # Try pdfplumber first (better TOC extraction)
            if pdfplumber:
                try:
                    with pdfplumber.open(pdf_path) as pdf:
                        # Extract outline if available
                        if hasattr(pdf, "outline") and pdf.outline:
                            toc = self._parse_outline(pdf.outline)
                        else:
                            # Fallback: extract from first pages
                            toc = self._extract_toc_from_pages(pdf)
                except Exception as e:
                    logger.warning(f"pdfplumber TOC extraction failed: {e}")

            # Fallback to pypdf if pdfplumber fails
            if not toc and pypdf:
                try:
                    reader = pypdf.PdfReader(pdf_path)
                    if reader.outline:
                        toc = self._parse_pypdf_outline(reader.outline)
                except Exception as e:
                    logger.warning(f"pypdf TOC extraction failed: {e}")

            logger.info(f"Extracted {len(toc)} TOC entries")
            return toc
        except Exception as e:
            logger.error(f"Error extracting TOC: {e}")
            return []

    def extract_chapter(self, pdf_path: Path, start_page: int, end_page: int) -> str:
        """Extract chapter content from PDF.

        Args:
            pdf_path: Path to PDF file
            start_page: Starting page number (0-indexed)
            end_page: Ending page number (0-indexed)

        Returns:
            Extracted text content
        """
        try:
            logger.info(f"Extracting pages {start_page}-{end_page} from {pdf_path}")

            # Use pdfplumber for better text extraction
            if pdfplumber:
                text_content = []
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num in range(start_page, min(end_page + 1, len(pdf.pages))):
                        page = pdf.pages[page_num]
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                return "\n\n".join(text_content)

            # Fallback to pypdf
            if pypdf:
                reader = pypdf.PdfReader(pdf_path)
                text_content = []
                for page_num in range(start_page, min(end_page + 1, len(reader.pages))):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                return "\n\n".join(text_content)

            raise ValueError("No PDF parsing library available")
        except Exception as e:
            logger.error(f"Error extracting chapter: {e}")
            return ""

    def distill_to_skill(
        self,
        pdf_path: str | Path,
        chapters: list[int] | None = None,
        level: str = "intermediate",
    ) -> dict[str, Any]:
        """Distill textbook into skill format.

        Args:
            pdf_path: Path to textbook PDF
            chapters: Specific chapter numbers to process (optional)
            level: Skill level - "beginner", "intermediate", or "advanced" (default: "intermediate")

        Returns:
            Dictionary with skill information:
            - name: Skill name (from textbook title)
            - description: Skill description
            - content: Skill content (markdown)
            - chapters: List of processed chapters
            - concepts: Extracted key concepts
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise ValueError(f"PDF file not found: {pdf_path}")

            # Extract TOC
            toc = self.extract_toc(pdf_path)
            if not toc:
                logger.warning("Could not extract TOC, using basic extraction")

            # Extract textbook title from filename or first page
            skill_name = self._slugify(pdf_path.stem)

            # Process chapters
            if chapters:
                # Process specific chapters
                content = self._process_specific_chapters(pdf_path, chapters, toc)
            else:
                # Process all chapters
                content = self._process_all_chapters(pdf_path, toc, level)

            description = (
                f"Textbook-based guide for {pdf_path.stem}. "
                f"Use when learning or working with this topic. "
                f"Based on textbook content."
            )

            return {
                "name": skill_name,
                "description": description,
                "content": content,
                "chapters": chapters or list(range(1, len(toc) + 1)),
                "level": level,
                "source": f"Textbook: {pdf_path.name}",
            }
        except Exception as e:
            logger.error(f"Error distilling textbook: {e}")
            raise ValueError(f"Failed to distill textbook '{pdf_path}': {str(e)}") from e

    def _parse_outline(self, outline: list) -> list[dict[str, Any]]:
        """Parse PDF outline structure.

        Args:
            outline: PDF outline structure

        Returns:
            List of TOC entries
        """
        toc = []
        for item in outline:
            if isinstance(item, dict):
                toc.append(
                    {
                        "title": item.get("title", ""),
                        "page": item.get("page", 0),
                        "level": item.get("level", 1),
                    }
                )
        return toc

    def _parse_pypdf_outline(self, outline: list) -> list[dict[str, Any]]:
        """Parse pypdf outline structure.

        Args:
            outline: pypdf outline structure

        Returns:
            List of TOC entries
        """
        toc = []

        def _traverse(outline_items, level=1):
            for item in outline_items:
                if isinstance(item, list):
                    _traverse(item, level + 1)
                else:
                    title = item.title if hasattr(item, "title") else str(item)
                    page = 0
                    if hasattr(item, "page") and item.page:
                        page = item.page.get("/Page", 0) if hasattr(item.page, "get") else 0

                    toc.append({"title": title, "page": page, "level": level})

        _traverse(outline)
        return toc

    def _extract_toc_from_pages(self, pdf) -> list[dict[str, Any]]:
        """Extract TOC from first pages of PDF.

        Args:
            pdf: pdfplumber PDF object

        Returns:
            List of TOC entries
        """
        # Simple heuristic: look for numbered items in first 10 pages
        toc = []
        for page_num in range(min(10, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            # Look for chapter/section patterns
            # This is a simplified implementation
            if text:
                lines = text.split("\n")
                for line in lines[:50]:  # First 50 lines
                    if any(marker in line.lower() for marker in ["chapter", "section", "part"]):
                        toc.append({"title": line.strip(), "page": page_num, "level": 1})
        return toc

    def _process_specific_chapters(
        self, pdf_path: Path, chapters: list[int], toc: list[dict[str, Any]]
    ) -> str:
        """Process specific chapters.

        Args:
            pdf_path: Path to PDF
            chapters: Chapter numbers to process
            toc: Table of contents

        Returns:
            Markdown content
        """
        content_parts = [f"# Textbook: {pdf_path.stem}\n"]
        content_parts.append("\n## Selected Chapters\n\n")

        for chapter_num in chapters:
            # Find chapter in TOC
            chapter_info = None
            for entry in toc:
                if (
                    f"chapter {chapter_num}" in entry["title"].lower()
                    or str(chapter_num) in entry["title"]
                ):
                    chapter_info = entry
                    break

            if chapter_info:
                start_page = chapter_info["page"]
                # Estimate end page (next chapter or +20 pages)
                end_page = start_page + 20
                chapter_text = self.extract_chapter(pdf_path, start_page, end_page)
                content_parts.append(f"### {chapter_info['title']}\n\n{chapter_text[:2000]}...\n\n")

        return "\n".join(content_parts)

    def _process_all_chapters(self, pdf_path: Path, toc: list[dict[str, Any]], level: str) -> str:
        """Process all chapters.

        Args:
            pdf_path: Path to PDF
            toc: Table of contents
            level: Skill level

        Returns:
            Markdown content
        """
        content_parts = [f"# Textbook: {pdf_path.stem}\n"]
        content_parts.append("\n## Overview\n\n")
        content_parts.append(f"This skill is based on the textbook: {pdf_path.name}\n\n")

        if toc:
            content_parts.append("## Table of Contents\n\n")
            for entry in toc[:20]:  # Limit to first 20 entries
                indent = "  " * (entry.get("level", 1) - 1)
                content_parts.append(f"{indent}- {entry['title']}\n")
            content_parts.append("\n")

        content_parts.append(
            "## Content\n\n"
            "For detailed content, please specify chapters to extract. "
            "The textbook has been indexed and is ready for chapter-by-chapter processing.\n"
        )

        return "".join(content_parts)

    def _slugify(self, text: str) -> str:
        """Convert text to hyphen-case slug.

        Args:
            text: Text to slugify

        Returns:
            Hyphen-case slug
        """
        import re

        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text.strip("-")
