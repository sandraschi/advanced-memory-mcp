"""Document converter service for converting various document formats to markdown

Supports conversion of:
- .docx (Word documents) via Pandoc
- .html (HTML files) via Pandoc
- .pdf (PDF files) via text extraction
- .txt (Plain text) via simple wrapping

Requires Pandoc to be installed for .docx and .html conversion.
"""

import re
import shutil
import subprocess
from pathlib import Path
from typing import Literal

from loguru import logger


class DocumentConverter:
    """Convert various document formats to markdown"""

    def __init__(self):
        """Initialize document converter and check for Pandoc"""
        self.pandoc_available = self._check_pandoc()

        if not self.pandoc_available:
            logger.warning(
                "Pandoc not found. Install from https://pandoc.org for .docx and .html conversion"
            )

    def _check_pandoc(self) -> bool:
        """Check if Pandoc is installed and available

        Returns:
            True if Pandoc is available, False otherwise
        """
        return shutil.which("pandoc") is not None

    async def convert(
        self,
        file_path: Path,
        doc_type: Literal["docx", "html", "pdf", "txt"],
    ) -> str | None:
        """Convert document to markdown

        Args:
            file_path: Path to document file
            doc_type: Type of document (docx, html, pdf, txt)

        Returns:
            Markdown content as string, or None if conversion failed
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        logger.info(f"Converting {doc_type.upper()} to markdown: {file_path.name}")

        try:
            if doc_type == "docx":
                return await self.convert_docx(file_path)
            elif doc_type == "html":
                return await self.convert_html(file_path)
            elif doc_type == "pdf":
                return await self.convert_pdf(file_path)
            elif doc_type == "txt":
                return await self.convert_txt(file_path)
            else:
                logger.error(f"Unsupported document type: {doc_type}")
                return None

        except Exception as e:
            logger.error(f"Error converting {doc_type} file {file_path.name}: {e}")
            return None

    async def convert_docx(self, file_path: Path) -> str | None:
        """Convert Word document to markdown using Pandoc

        Args:
            file_path: Path to .docx file

        Returns:
            Markdown content or None if conversion failed
        """
        if not self.pandoc_available:
            logger.error("Pandoc is required for .docx conversion")
            return self._create_placeholder(file_path, "DOCX", "Pandoc is not installed")

        try:
            # Run Pandoc to convert docx to markdown
            result = subprocess.run(
                [
                    "pandoc",
                    str(file_path),
                    "-f",
                    "docx",
                    "-t",
                    "markdown",
                    "--wrap=none",  # Don't wrap lines
                    "--extract-media=.",  # Extract images
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            markdown = result.stdout

            # Add metadata header
            title = file_path.stem.replace("_", " ").replace("-", " ").title()
            markdown = f"# {title}\n\n> **Source:** {file_path.name} (Word document)\n\n{markdown}"

            logger.info(f"Successfully converted {file_path.name} to markdown")
            return markdown

        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc conversion failed for {file_path.name}: {e.stderr}")
            return self._create_placeholder(file_path, "DOCX", str(e.stderr))

        except Exception as e:
            logger.error(f"Error converting docx {file_path.name}: {e}")
            return self._create_placeholder(file_path, "DOCX", str(e))

    async def convert_html(self, file_path: Path) -> str | None:
        """Convert HTML file to markdown using Pandoc

        Args:
            file_path: Path to .html file

        Returns:
            Markdown content or None if conversion failed
        """
        if not self.pandoc_available:
            logger.error("Pandoc is required for .html conversion")
            return self._create_placeholder(file_path, "HTML", "Pandoc is not installed")

        try:
            # Run Pandoc to convert html to markdown
            result = subprocess.run(
                [
                    "pandoc",
                    str(file_path),
                    "-f",
                    "html",
                    "-t",
                    "markdown",
                    "--wrap=none",  # Don't wrap lines
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            markdown = result.stdout

            # Add metadata header
            title = file_path.stem.replace("_", " ").replace("-", " ").title()
            markdown = f"# {title}\n\n> **Source:** {file_path.name} (HTML file)\n\n{markdown}"

            logger.info(f"Successfully converted {file_path.name} to markdown")
            return markdown

        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc conversion failed for {file_path.name}: {e.stderr}")
            return self._create_placeholder(file_path, "HTML", str(e.stderr))

        except Exception as e:
            logger.error(f"Error converting html {file_path.name}: {e}")
            return self._create_placeholder(file_path, "HTML", str(e))

    async def convert_pdf(self, file_path: Path) -> str | None:
        """Extract text from PDF and convert to markdown

        This uses pypdf (if available) or pdftotext command-line tool.

        Args:
            file_path: Path to .pdf file

        Returns:
            Markdown content or None if extraction failed
        """
        try:
            # Try pypdf first (pure Python, no external dependencies)
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(file_path))
                text_parts = []

                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"## Page {i + 1}\n\n{text.strip()}\n")

                if not text_parts:
                    logger.warning(f"No text extracted from PDF: {file_path.name}")
                    return self._create_placeholder(
                        file_path, "PDF", "No extractable text found in PDF"
                    )

                full_text = "\n\n".join(text_parts)

            except ImportError:
                # Fall back to pdftotext command-line tool
                logger.info("pypdf not available, trying pdftotext...")

                if not shutil.which("pdftotext"):
                    logger.error("Neither pypdf nor pdftotext available for PDF conversion")
                    return self._create_placeholder(
                        file_path, "PDF", "PDF extraction tools not installed"
                    )

                result = subprocess.run(
                    ["pdftotext", str(file_path), "-"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                full_text = result.stdout

                if not full_text.strip():
                    logger.warning(f"No text extracted from PDF: {file_path.name}")
                    return self._create_placeholder(
                        file_path, "PDF", "No extractable text found in PDF"
                    )

            # Clean up extracted text
            full_text = self._clean_pdf_text(full_text)

            # Add metadata header
            title = file_path.stem.replace("_", " ").replace("-", " ").title()
            markdown = (
                f"# {title}\n\n"
                f"> **Source:** {file_path.name} (PDF document)\n"
                f"> **Note:** Extracted text may have formatting issues\n\n"
                f"{full_text}"
            )

            logger.info(f"Successfully extracted text from {file_path.name}")
            return markdown

        except Exception as e:
            logger.error(f"Error extracting PDF {file_path.name}: {e}")
            return self._create_placeholder(file_path, "PDF", str(e))

    async def convert_txt(self, file_path: Path) -> str | None:
        """Convert plain text file to markdown

        Args:
            file_path: Path to .txt file

        Returns:
            Markdown content
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # Add header
            title = file_path.stem.replace("_", " ").replace("-", " ").title()
            markdown = f"# {title}\n\n> **Source:** {file_path.name} (text file)\n\n{content}"

            logger.info(f"Converted text file {file_path.name} to markdown")
            return markdown

        except Exception as e:
            logger.error(f"Error reading text file {file_path.name}: {e}")
            return self._create_placeholder(file_path, "TXT", str(e))

    def _clean_pdf_text(self, text: str) -> str:
        """Clean up PDF extracted text

        Args:
            text: Raw extracted text from PDF

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove page breaks (form feed characters)
        text = text.replace("\f", "\n\n")

        # Fix hyphenated words split across lines
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

        # Clean up spaces
        text = re.sub(r" +", " ", text)

        return text.strip()

    def _create_placeholder(self, file_path: Path, file_type: str, error: str) -> str:
        """Create placeholder markdown when conversion fails

        Args:
            file_path: Original file path
            file_type: Type of file (DOCX, PDF, etc.)
            error: Error message

        Returns:
            Placeholder markdown content
        """
        title = file_path.stem.replace("_", " ").replace("-", " ").title()
        return f"""# {title}

> **Source:** {file_path.name} ({file_type} file)
> **Status:** ⚠️ Conversion failed

## Error

{error}

## What Happened

The automatic conversion of this {file_type} file failed.

## Next Steps

1. **Manual Conversion:**
   - Open the file in its native application
   - Copy the content manually
   - Paste into a new markdown note

2. **Install Required Tools:**
   - For .docx/.html: Install Pandoc (https://pandoc.org)
   - For .pdf: Install pypdf (`pip install pypdf`) or pdftotext

3. **Alternative:**
   - Save the file as plain text (.txt) first
   - Drop the .txt file into the inbox

## Original File

The original file is preserved in `zettelkasten/converted/` for reference.
"""


# Singleton instance
_converter: DocumentConverter | None = None


def get_document_converter() -> DocumentConverter:
    """Get singleton document converter instance

    Returns:
        DocumentConverter instance
    """
    global _converter
    if _converter is None:
        _converter = DocumentConverter()
    return _converter
