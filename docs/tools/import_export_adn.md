# Import & Export (adn_import_export)

Unified portmanteau tool for all import and export operations. This tool consolidates 20+ operations across various external app formats and document types into a single interface.

## Operations

| Operation | Description | Formats Supported |
|:---|:---|:---|
| `import` | Import data from external apps or archives | `obsidian`, `notion`, `joplin`, `evernote`, `onenote`, `archive` |
| `export` | Export notes to various formats | `html`, `pdf`, `pandoc`, `docsify`, `archive` |
| `load` | Load specialized file types | `canvas` |
| `search` | Search external vaults without importing | `obsidian`, `notion`, `joplin`, `evernote` |

## Parameters

- `operation` (str): Import/export operation type.
- `format` (str): Data format for the operation.
- `path` (str, optional): Source file or directory path for imports/loading.
- `destination` (str, optional): Export destination path.
- `query` (str, optional): Search query for external vault searches.
- `options` (dict, optional): Format-specific configuration options.

## Examples

### Import Obsidian vault
```python
adn_import_export("import", "obsidian", path="/path/to/vault")
```

### Export to HTML
```python
adn_import_export("export", "html", destination="/output/folder")
```

### Export to PDF
```python
adn_import_export("export", "pdf", destination="/output/file.pdf")
```

### Load Obsidian canvas
```python
adn_import_export("load", "canvas", path="/path/to/canvas.canvas")
```

### Search Evernote vault
```python
adn_import_export("search", "evernote", query="machine learning")
```
