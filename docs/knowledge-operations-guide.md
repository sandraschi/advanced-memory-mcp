# Knowledge Operations Guide 🛠️

Swiss Army Knife tool for bulk operations, tag management, and content validation in Basic Memory.

## Overview

The `knowledge_operations` tool consolidates multiple related operations into one comprehensive tool, reducing complexity while providing powerful batch operations and maintenance capabilities.

## Operations

### 1. Tag Analytics (`tag_analytics`)

Analyze tag usage patterns and statistics across your knowledge base.

```python
await knowledge_operations.fn(
    operation="tag_analytics",
    action={"analyze_usage": True}
)
```

**Output:**
- Total tag usage statistics
- Tag frequency distribution
- Most/least used tags
- Recommendations for consolidation

### 2. Tag Consolidation (`consolidate_tags`)

Merge similar tags, including semantic similarity detection.

```python
# Manual consolidation
await knowledge_operations.fn(
    operation="consolidate_tags",
    action={
        "semantic_groups": [
            ["mcp", "mcp-server", "mcp_server"],
            ["ai", "artificial-intelligence", "machine-learning"],
            ["python", "py", "python3"]
        ]
    },
    dry_run=True
)

# AI-powered auto-detection
await knowledge_operations.fn(
    operation="consolidate_tags",
    action={"auto_detect": True},
    dry_run=True
)
```

### 3. Tag Maintenance (`tag_maintenance`)

Clean up tag inconsistencies and issues.

```python
await knowledge_operations.fn(
    operation="tag_maintenance",
    action={
        "actions": [
            "remove_empty",      # Remove null/empty tags
            "standardize_case",  # Convert to lowercase
            "remove_duplicates", # Remove duplicate tags on same entity
            "remove_special_chars" # Clean invalid characters
        ]
    },
    dry_run=True
)
```

### 4. Bulk Update (`bulk_update`)

Batch update multiple notes based on filters.

```python
# Add tags to all draft notes
await knowledge_operations.fn(
    operation="bulk_update",
    filters={"tags": ["draft"]},
    action={"add_tags": ["reviewed"], "remove_tags": ["draft"]},
    dry_run=True
)

# Replace text across multiple notes
await knowledge_operations.fn(
    operation="bulk_update",
    filters={"folder": "/research"},
    action={
        "find_text": "old-term",
        "replace_text": "new-term"
    },
    dry_run=True
)
```

### 5. Content Validation (`validate_content`)

Check note quality and identify issues.

```python
await knowledge_operations.fn(
    operation="validate_content",
    filters={"folder": "/articles"},
    action={
        "checks": [
            "broken_links",     # Find broken internal/external links
            "formatting",       # Check markdown formatting
            "missing_tags",     # Notes without tags
            "freshness"         # Outdated content
        ],
        "auto_fix": False      # Set to True to apply fixes
    },
    dry_run=True
)
```

### 6. Project Statistics (`project_stats`)

Generate comprehensive project analytics.

```python
await knowledge_operations.fn(
    operation="project_stats",
    action={"include_activity": True}
)
```

**Output:**
- Content distribution by folder
- Tag usage patterns
- Activity timelines
- Recommendations for organization

### 7. Find Duplicates (`find_duplicates`)

Identify duplicate or similar content.

```python
await knowledge_operations.fn(
    operation="find_duplicates",
    filters={"folder": "/notes"},
    limit=50
)
```

**Detection Methods:**
- Exact title matches
- Content hashing (identical content)
- Text similarity (cosine similarity)
- Semantic similarity (embedding-based)

### 8. Bulk Move (`bulk_move`)

Move multiple notes to a new folder.

```python
await knowledge_operations.fn(
    operation="bulk_move",
    filters={"tags": ["archive"]},
    action={"destination_folder": "/archived"},
    dry_run=True
)
```

### 9. Bulk Delete (`bulk_delete`)

Delete multiple notes with confirmation.

```python
# Preview deletion
await knowledge_operations.fn(
    operation="bulk_delete",
    filters={"tags": ["temp"], "created_before": "2023-01-01"},
    dry_run=True
)

# Confirm deletion (DESTRUCTIVE!)
await knowledge_operations.fn(
    operation="bulk_delete",
    filters={"tags": ["temp"]},
    action={"confirm_deletion": True},
    dry_run=False
)
```

## Filtering System

All operations support comprehensive filtering:

### Basic Filters
```python
filters = {
    "folder": "/research",           # Limit to folder
    "tags": ["important"],           # Must have these tags
    "content_match": "machine learning", # Text search
    "limit": 100                     # Max items to process
}
```

### Date Filters
```python
filters = {
    "created_after": "2024-01-01",   # ISO date or relative
    "created_before": "30d",         # 30 days ago
    "updated_since": "1w"            # 1 week ago
}
```

### Advanced Filters
```python
filters = {
    "folder": "/projects",
    "tags": ["active"],
    "created_after": "2024-01-01",
    "content_match": "deadline",
    "has_relationships": True,       # Notes with links
    "size_range": "1KB-10MB"         # File size range
}
```

## Safety Features

### Dry Run Mode
All operations default to `dry_run=True` for safety:

```python
# Preview changes
result = await knowledge_operations.fn(
    operation="bulk_update",
    filters={"tags": ["draft"]},
    action={"add_tags": ["published"]},
    dry_run=True  # No changes applied
)

# Apply changes
result = await knowledge_operations.fn(
    operation="bulk_update",
    filters={"tags": ["draft"]},
    action={"add_tags": ["published"]},
    dry_run=False  # Changes applied!
)
```

### Confirmation for Destructive Operations
```python
# Bulk delete requires explicit confirmation
await knowledge_operations.fn(
    operation="bulk_delete",
    filters={"tags": ["temp"]},
    action={"confirm_deletion": True},  # Required for delete
    dry_run=False
)
```

### Progress Reporting
Operations provide real-time feedback:
```
🔄 Bulk Update Progress:
  Processing: 45/100 notes
  Changes applied: 23 tag additions, 12 replacements
  Estimated completion: 30 seconds
```

## Batch Processing

### Large Operations
For operations affecting many items:

```python
# Process in batches
await knowledge_operations.fn(
    operation="bulk_update",
    filters={"folder": "/archive"},
    action={"add_tags": ["processed"]},
    batch_size=50,      # Process 50 at a time
    delay=1.0          # 1 second between batches
)
```

### Error Handling
```python
# Continue on errors
await knowledge_operations.fn(
    operation="validate_content",
    action={"checks": ["all"]},
    continue_on_error=True,  # Don't stop on single failures
    error_log="validation_errors.txt"
)
```

## Integration Examples

### Workflow Automation
```python
# Process meeting notes
await knowledge_operations.fn(
    operation="bulk_update",
    filters={"folder": "/meetings", "created_after": "1w"},
    action={"add_tags": ["processed"], "extract_action_items": True}
)

# Archive old content
await knowledge_operations.fn(
    operation="bulk_move",
    filters={"created_before": "1y", "tags": ["stale"]},
    action={"destination_folder": "/archive/old"}
)
```

### Content Maintenance
```python
# Monthly cleanup routine
await knowledge_operations.fn("tag_maintenance", action={"actions": ["all"]})
await knowledge_operations.fn("validate_content", action={"auto_fix": True})
await knowledge_operations.fn("find_duplicates", action={"auto_merge": True})
```

### Project Management
```python
# End-of-sprint cleanup
await knowledge_operations.fn(
    operation="bulk_update",
    filters={"tags": ["sprint-current"]},
    action={"add_tags": ["sprint-completed"], "remove_tags": ["sprint-current"]}
)
```

## Performance Considerations

### Optimization Tips
- Use specific filters to reduce processing scope
- Enable `dry_run=True` first to estimate operation size
- Use `limit` parameter for testing large operations
- Consider batch processing for operations > 1000 items

### Resource Usage
- Tag operations: Low memory, fast
- Content validation: Medium CPU for text analysis
- Bulk operations: Scales with number of items
- Duplicate detection: High memory for similarity analysis

## Best Practices

### 1. Always Dry Run First
```python
# Test before applying
await knowledge_operations.fn(operation="...", dry_run=True)
await knowledge_operations.fn(operation="...", dry_run=False)
```

### 2. Use Specific Filters
```python
# Good: specific folder
filters={"folder": "/projects/active"}

# Avoid: broad scope
filters={}  # Processes everything!
```

### 3. Regular Maintenance
```python
# Weekly tag cleanup
await knowledge_operations.fn("tag_maintenance", action={"actions": ["standardize_case"]})

# Monthly content validation
await knowledge_operations.fn("validate_content", action={"auto_fix": True})
```

### 4. Backup Before Bulk Operations
```python
# Backup before major changes
await export_to_archive.fn("backup-before-changes.zip")

await knowledge_operations.fn(operation="bulk_update", ...)
```

## Troubleshooting

### Common Issues

#### "No items found"
- Check filter specificity
- Verify folder paths exist
- Confirm tag names are correct

#### "Operation timed out"
- Reduce `limit` parameter
- Use more specific filters
- Enable batch processing

#### "Permission denied"
- Check file permissions
- Ensure Basic Memory has write access
- Verify project is active

#### "Database locked"
- Wait for other operations to complete
- Reduce concurrency
- Check for long-running queries

### Recovery Options

#### Undo Operations
Some operations support undo:
```python
await knowledge_operations.fn(
    operation="undo_last",
    operation_id="bulk_update_2024_01_15_143022"
)
```

#### Restore from Backup
```python
await import_from_archive.fn("backup-before-changes.zip")
```

## Future Enhancements

### Planned Features
- **AI-powered tag suggestions** during bulk operations
- **Automatic duplicate merging** with conflict resolution
- **Content clustering** for organization
- **Version control integration** for bulk operations
- **Scheduled maintenance** routines
- **Performance analytics** for operations

### API Extensions
- **Webhooks** for operation completion
- **Progress callbacks** for long operations
- **Custom operation plugins**
- **Operation templates** for common workflows

---

**The `knowledge_operations` tool provides a powerful, safe, and efficient way to manage your knowledge base at scale. Start with `dry_run=True` and gradually build confidence with the operations that matter most to your workflow.** 🚀
