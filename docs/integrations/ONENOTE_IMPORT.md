# OneNote Import Integration

## Overview

Advanced Memory can now import OneNote pages from HTML content, converting OneNote's idiosyncratic HTML output into clean, readable notes that Claude/Cursor/Sandra can easily parse.

This is particularly useful when working with **office-365-mcp** or other OneNote API sources that return HTML content.

## Quick Start

### Import via adn_import (Portmanteau Tool)

```python
# Import from JSON file (with page data)
adn_import("onenote", source_path="onenote-pages.json", destination_folder="imported/onenote")

# Import from HTML file
adn_import("onenote", source_path="page.html", destination_folder="imported/onenote")

# Import directory of HTML files
adn_import("onenote", source_path="onenote-export/", destination_folder="imported/onenote")
```

### Import via load_onenote_html (Direct Tool)

```python
# Import direct HTML content
load_onenote_html(html_content="<html>...", page_title="Meeting Notes", folder="imported/onenote")

# Import from file
load_onenote_html(source_path="page.html", page_title="My Note", folder="imported/onenote")

# Import from JSON file
load_onenote_html(source_path="onenote-pages.json", folder="imported/onenote")
```

## Integration with office-365-mcp

When using office-365-mcp to get OneNote pages, you can import them directly:

### Step 1: Get HTML from office-365-mcp

```python
# Using office-365-mcp (example)
onenote_html = await office365_mcp.get_onenote_page(page_id)
```

### Step 2: Import to Advanced Memory

**Option A: Save to file and import**
```python
# Save HTML to file
with open("onenote-page.html", "w", encoding="utf-8") as f:
    f.write(onenote_html)

# Import via adn_import
adn_import("onenote", source_path="onenote-page.html", destination_folder="imported/onenote")
```

**Option B: Direct import (using load_onenote_html)**
```python
# Import directly
load_onenote_html(
    html_content=onenote_html,
    page_title="My OneNote Page",
    folder="imported/onenote"
)
```

**Option C: Batch import (JSON format)**
```python
# Collect multiple pages
pages = [
    {"title": "Page 1", "html_content": html1},
    {"title": "Page 2", "html_content": html2},
]

# Save to JSON
import json
with open("onenote-pages.json", "w", encoding="utf-8") as f:
    json.dump(pages, f, indent=2)

# Import all at once
adn_import("onenote", source_path="onenote-pages.json", destination_folder="imported/onenote")
```

## Supported Input Formats

### 1. Direct HTML String
```python
load_onenote_html(
    html_content="<html><body><h1>Title</h1><p>Content</p></body></html>",
    page_title="My Note"
)
```

### 2. HTML File
```python
# Single HTML file
adn_import("onenote", source_path="page.html")
```

### 3. JSON File
```json
[
  {
    "title": "Page Title",
    "html_content": "<html>...</html>"
  },
  {
    "title": "Another Page",
    "html_content": "<html>...</html>"
  }
]
```

### 4. Directory of HTML Files
```python
# Import all HTML files from directory
adn_import("onenote", source_path="onenote-export/")
```

## What Gets Imported

- ✅ **Clean, readable text** - HTML converted to structured markdown-like text
- ✅ **Preserved structure** - Headings, paragraphs, lists, tables maintained
- ✅ **Metadata** - Page titles preserved
- ✅ **Tags** - Automatically tagged with `onenote` and `imported`
- ✅ **Searchable** - Full-text searchable via Advanced Memory

## Text Extraction Features

The OneNote HTML extractor:
- Removes scripts and styles
- Preserves document structure (headings, paragraphs, lists, tables)
- Formats headings with underlines for clarity
- Converts lists to numbered format
- Converts tables to pipe-separated text
- Handles malformed HTML gracefully

## Example Workflow

```python
# 1. Get OneNote pages from office-365-mcp
pages = await office365_mcp.list_onenote_pages()

# 2. Collect HTML content
page_data = []
for page in pages:
    html = await office365_mcp.get_onenote_page(page.id)
    page_data.append({
        "title": page.title,
        "html_content": html
    })

# 3. Save to JSON
import json
with open("onenote-export.json", "w", encoding="utf-8") as f:
    json.dump(page_data, f, indent=2)

# 4. Import to Advanced Memory
adn_import("onenote", source_path="onenote-export.json", destination_folder="imported/onenote")

# 5. Search imported notes
search_notes("keyword", folder="imported/onenote")
```

## Benefits

✅ **Clean Output**: Removes OneNote's HTML quirks
✅ **AI-Friendly**: Easy for Claude/Cursor/Sandra to parse
✅ **Preserves Structure**: Maintains document hierarchy
✅ **Batch Import**: Import multiple pages at once
✅ **Flexible Input**: Accepts files, directories, or direct HTML

## Troubleshooting

**Empty text extracted:**
- Check that HTML is valid
- The extractor will still create a note with a placeholder if extraction fails

**Import errors:**
- Verify file paths are correct
- Check file encoding (should be UTF-8)
- Ensure JSON format is correct (array of objects with `title` and `html_content`)

**File not found:**
- Use absolute paths or paths relative to current working directory
- Check file permissions

## Related Tools

- `adn_import` - Portmanteau import tool (supports onenote operation)
- `load_onenote_html` - Direct OneNote HTML import tool
- `adn_content` - Content management (used internally)
- `adn_search` - Search imported notes
