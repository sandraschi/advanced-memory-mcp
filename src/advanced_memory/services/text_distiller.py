"""Text-based skill distiller for Advanced Memory.

This module provides functionality to extract and distill knowledge from famous texts,
classical works, and seminal documents into high-quality Claude Skills.
"""

from pathlib import Path
from typing import Any

from loguru import logger


class TextDistiller:
    """Distill Claude Skills from famous texts and documents."""

    def __init__(self):
        """Initialize text distiller."""
        logger.debug("TextDistiller initialized")

    def read_text_file(self, file_path: str | Path) -> str:
        """Read text file content.

        Args:
            file_path: Path to text file

        Returns:
            File content as string

        Raises:
            ValueError: If file cannot be read
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")

            logger.info(f"Reading text file: {file_path}")
            content = file_path.read_text(encoding="utf-8")
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                content = file_path.read_text(encoding="latin-1")
                logger.warning(f"Read file with latin-1 encoding: {file_path}")
                return content
            except Exception as e:
                logger.error(f"Error reading text file: {e}")
                raise ValueError(f"Failed to read file '{file_path}': {e!s}") from e
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise ValueError(f"Failed to read file '{file_path}': {e!s}") from e

    def read_pdf_text(self, pdf_path: str | Path) -> str:
        """Read PDF file content as text.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            ValueError: If PDF cannot be read
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise ValueError(f"PDF file not found: {pdf_path}")

            logger.info(f"Reading PDF file: {pdf_path}")

            # Try pdfplumber first
            try:
                import pdfplumber

                text_parts = []
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                return "\n\n".join(text_parts)
            except ImportError:
                pass

            # Fallback to pypdf
            try:
                import pypdf

                reader = pypdf.PdfReader(pdf_path)
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return "\n\n".join(text_parts)
            except ImportError:
                raise ImportError("PDF parsing libraries required. Install with: pip install pdfplumber pypdf")
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise ValueError(f"Failed to read PDF '{pdf_path}': {e!s}") from e

    def distill_to_skill(
        self,
        text_path: str | Path,
        focus: str = "principles",
        context_level: str = "basic",
    ) -> dict[str, Any]:
        """Distill text into skill format.

        Args:
            text_path: Path to text file or PDF
            focus: What to distill - "principles", "examples", "methodology", or "all" (default: "principles")
            context_level: Historical context level - "basic", "comprehensive", or "detailed" (default: "basic")

        Returns:
            Dictionary with skill information:
            - name: Skill name (from filename)
            - description: Skill description
            - content: Skill content (markdown)
            - key_passages: Extracted key passages
            - principles: Extracted principles
        """
        try:
            text_path = Path(text_path)
            if not text_path.exists():
                raise ValueError(f"File not found: {text_path}")

            # Read content
            if text_path.suffix.lower() == ".pdf":
                content = self.read_pdf_text(text_path)
            else:
                content = self.read_text_file(text_path)

            # Extract key information
            skill_name = self._slugify(text_path.stem)

            # Build skill content based on focus
            if focus == "principles":
                skill_content = self._extract_principles(content, context_level)
            elif focus == "examples":
                skill_content = self._extract_examples(content, context_level)
            elif focus == "methodology":
                skill_content = self._extract_methodology(content, context_level)
            else:  # "all"
                skill_content = self._extract_all(content, context_level)

            description = (
                f"Guide based on {text_path.stem}. "
                f"Use when working with concepts and principles from this text. "
                f"Focus: {focus}."
            )

            return {
                "name": skill_name,
                "description": description,
                "content": skill_content,
                "key_passages": self._extract_key_passages(content),
                "principles": self._extract_principles_list(content),
                "source": f"Text: {text_path.name}",
                "focus": focus,
                "context_level": context_level,
            }
        except Exception as e:
            logger.error(f"Error distilling text: {e}")
            raise ValueError(f"Failed to distill text '{text_path}': {e!s}") from e

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

    def _extract_principles(self, content: str, context_level: str) -> str:
        """Extract principles from text.

        Args:
            content: Text content
            context_level: Context level

        Returns:
            Markdown content focusing on principles
        """
        # Simple extraction - look for patterns like "principle", "rule", "law"
        # In production, this would use NLP or LLM
        lines = content.split("\n")
        principle_lines = [
            line.strip()
            for line in lines
            if any(
                keyword in line.lower() for keyword in ["principle", "rule", "law", "fundamental", "core", "essential"]
            )
        ][:20]

        context_text = ""
        if context_level != "basic":
            context_text = f"\n## Historical Context\n\n{self._extract_context(content)}\n"

        return f"""# Key Principles

## Core Principles

{chr(10).join(f"- {line}" for line in principle_lines[:10])}

{context_text}

## Source Material

Based on analysis of the source text, extracting key principles and fundamental concepts.
"""

    def _extract_examples(self, content: str, context_level: str) -> str:
        """Extract examples from text.

        Args:
            content: Text content
            context_level: Context level

        Returns:
            Markdown content focusing on examples
        """
        # Simple extraction - look for example patterns
        # In production, would use more sophisticated NLP
        return f"""# Key Examples

## Illustrative Examples

This section contains examples and case studies extracted from the source text.

{content[:2000]}...

## Source Material

Based on examples and illustrations from the source text.
"""

    def _extract_methodology(self, content: str, context_level: str) -> str:
        """Extract methodology from text.

        Args:
            content: Text content
            context_level: Context level

        Returns:
            Markdown content focusing on methodology
        """
        return f"""# Methodology

## Approach

This section describes the methodology and approach presented in the source text.

{content[:2000]}...

## Key Steps

[Methodology steps would be extracted here using NLP]

## Source Material

Based on methodology and approach from the source text.
"""

    def _extract_all(self, content: str, context_level: str) -> str:
        """Extract all aspects from text.

        Args:
            content: Text content
            context_level: Context level

        Returns:
            Comprehensive markdown content
        """
        return f"""# Comprehensive Guide

## Overview

This skill is based on the complete source text.

## Principles

{self._extract_principles(content, context_level)}

## Examples

{self._extract_examples(content, context_level)}

## Methodology

{self._extract_methodology(content, context_level)}

## Source Material

Based on complete analysis of the source text.
"""

    def _extract_key_passages(self, content: str, max_passages: int = 5) -> list[str]:
        """Extract key passages from text.

        Args:
            content: Text content
            max_passages: Maximum number of passages

        Returns:
            List of key passage strings
        """
        # Simple extraction - take first sentences from paragraphs
        # In production, would use more sophisticated extraction
        paragraphs = content.split("\n\n")
        passages = [p[:200] for p in paragraphs[:max_passages] if len(p.strip()) > 50]
        return passages

    def _extract_principles_list(self, content: str) -> list[str]:
        """Extract list of principles.

        Args:
            content: Text content

        Returns:
            List of principle strings
        """
        # Simple extraction
        lines = content.split("\n")
        principles = [
            line.strip()
            for line in lines
            if any(keyword in line.lower() for keyword in ["principle", "rule", "law", "fundamental", "core"])
        ][:10]
        return principles

    def _extract_context(self, content: str) -> str:
        """Extract historical context.

        Args:
            content: Text content

        Returns:
            Context description
        """
        # Simple extraction - would be enhanced with metadata or LLM analysis
        return "Historical context would be extracted here based on the source material."
