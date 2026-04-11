"""
OneNote HTML to Readable Text Extractor

Converts OneNote's idiosyncratic HTML output into clean, readable text
that Claude/Cursor/Sandra can easily parse and understand.

Based on the JavaScript extractReadableText function from read-all-pages.js
"""

import re

from bs4 import BeautifulSoup


def extract_readable_text(html: str) -> str:
    """Extract readable text from OneNote HTML content.

    Processes OneNote's HTML structure and extracts text while preserving
    document structure (headings, paragraphs, lists, tables).

    Args:
        html: Raw HTML content from OneNote API

    Returns:
        Clean, readable text with preserved structure

    Examples:
        >>> html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        >>> text = extract_readable_text(html)
        >>> print(text)
        Title
        -----

        Content
    """
    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()

        text_parts = []

        # Process headings (h1-h6)
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            heading_text = heading.get_text(strip=True)
            if heading_text:
                text_parts.append(f"\n{heading_text}\n{'-' * len(heading_text)}\n")

        # Process paragraphs
        for paragraph in soup.find_all("p"):
            para_text = paragraph.get_text(strip=True)
            if para_text:
                text_parts.append(f"{para_text}\n\n")

        # Process lists (ul, ol)
        for list_elem in soup.find_all(["ul", "ol"]):
            text_parts.append("\n")
            for index, item in enumerate(list_elem.find_all("li", recursive=False), 1):
                item_text = item.get_text(strip=True)
                if item_text:
                    text_parts.append(f"{index}. {item_text}\n")
            text_parts.append("\n")

        # Process divs and spans (only direct text nodes not already captured)
        for element in soup.find_all(["div", "span"]):
            # Only include if it has a single direct text child node
            # and hasn't been processed as part of a paragraph/list
            if element.parent and element.parent.name in [
                "p",
                "li",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            ]:
                continue

            # Check if this is a direct text node
            children = [child for child in element.children if child.name is None]
            if len(children) == 1 and children[0].strip():
                text = element.get_text(strip=True)
                if text and text not in [part.strip() for part in text_parts if part.strip()]:
                    text_parts.append(f"{text}\n\n")

        # Process tables
        for table in soup.find_all("table"):
            text_parts.append("\nTable content:\n")
            for row in table.find_all("tr"):
                cells = []
                for cell in row.find_all(["td", "th"]):
                    cell_text = cell.get_text(strip=True)
                    cells.append(cell_text)
                if cells:
                    text_parts.append(" | ".join(cells) + "\n")
            text_parts.append("\n")

        # Combine all parts
        result = "".join(text_parts)

        # Fallback: If no structured content found, get all body text
        if not result.strip():
            body = soup.find("body")
            if body:
                result = " ".join(body.stripped_strings)
            else:
                result = " ".join(soup.stripped_strings)

        # Clean up excessive whitespace
        result = re.sub(r"\n{3,}", "\n\n", result)
        result = result.strip()

        return result

    except Exception as e:
        return f"Error: Could not extract readable text from HTML content. {e!s}"


def extract_text_summary(html: str, max_length: int = 300) -> str:
    """Extract a text summary from OneNote HTML (first N characters).

    Args:
        html: Raw HTML content from OneNote API
        max_length: Maximum length of summary (default: 300)

    Returns:
        Text summary truncated to max_length
    """
    full_text = extract_readable_text(html)

    if len(full_text) <= max_length:
        return full_text

    # Truncate and add ellipsis
    summary = full_text[:max_length].rsplit(" ", 1)[0]  # Cut at word boundary
    return f"{summary}..."


# Example usage
if __name__ == "__main__":
    # Test with sample HTML
    sample_html = """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>My OneNote Page</h1>
        <p>This is a paragraph with some content.</p>
        <ul>
            <li>First item</li>
            <li>Second item</li>
        </ul>
        <p>Another paragraph here.</p>
        <table>
            <tr><th>Header 1</th><th>Header 2</th></tr>
            <tr><td>Data 1</td><td>Data 2</td></tr>
        </table>
    </body>
    </html>
    """

    readable_text = extract_readable_text(sample_html)
    print("Extracted text:")
    print(readable_text)
    print("\n" + "=" * 50 + "\n")

    summary = extract_text_summary(sample_html, max_length=100)
    print("Summary:")
    print(summary)
