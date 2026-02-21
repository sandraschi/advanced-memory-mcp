# Content Management (adn_content)

Unified tool for knowledge content management with conversational responses. This tool manages the lifecycle of content within notes, including reading, writing, editing, and specialized assessments.

## Operations

| Operation | Description | Required Parameters |
|:---|:---|:---|
| `write` | Create or update a note | `identifier`, `content` |
| `read` | Read raw note content | `identifier` |
| `view` | View note content | `identifier` |
| `edit` | Perform specialized edit operations | `identifier`, `edit_operation` |
| `quick` | Quickly capture a thought or snippet | `content` |
| `daily` | Add an entry to the daily journal | `content` |
| `move` | Move note to another folder | `identifier`, `folder` |
| `delete` | Remove a note | `identifier` |
| `suggest_tags` | Get AI-powered tag suggestions | `identifier` |
| `summarize` | Generate a summary of the note | `identifier` |
| `enhance` | Upgrade note quality using SOTA LLM | `identifier` |
| `generate` | Generate new content from description | `content` |
| `find_runts` | Find notes below a character threshold | `max_content_length` |
| `find_junk` | Assess note quality and find low-value content | - |

## Parameters

- `operation` (str): The specific content operation to perform.
- `identifier` (str, optional): Note title or permalink.
- `content` (str, optional): Markdown content for the operation.
- `folder` (str, optional): Target folder path.
- `tags` (list[str]|str, optional): Tags for categorization.
- `edit_operation` (str, optional): Type of edit (`append`, `prepend`, `find_replace`, `replace_section`, etc.).
- `find_text` (str, optional): Text to find for replacement.
- `expected_replacements` (int, optional): Expected number of matches (Default: 1).
- `use_regex` (bool, optional): Use regex for find/replace (Default: False).
- `section` (str, optional): Targeted markdown section.
- `update_content` (bool, optional): Fix typos/facts during enhancement (Default: True).
- `update_style` (bool, optional): Improve readability during enhancement (Default: True).
- `max_content_length` (int, optional): Threshold for `find_runts` (Default: 500).

## Examples

### Capture a quick note
```python
adn_content("quick", content="Remember to check the new API endpoints.")
```

### Add to daily journal
```python
adn_content("daily", content="Completed the Tools page integration and docstring refactoring.")
```

### Enhance a note
```python
adn_content("enhance", identifier="research/notes", add_bibliography=True)
```

### Find short notes (runts)
```python
adn_content("find_runts", max_content_length=200)
```
