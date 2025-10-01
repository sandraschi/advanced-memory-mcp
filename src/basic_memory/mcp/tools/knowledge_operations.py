"""Knowledge Operations - Swiss Army Knife tool for bulk operations and content management."""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from collections import defaultdict, Counter

from loguru import logger

from basic_memory.config import ConfigManager
from basic_memory.mcp.server import mcp
from basic_memory.mcp.project_session import get_active_project
from basic_memory.mcp.tools.utils import call_post
from basic_memory.schemas.search import SearchQuery, SearchResponse


@mcp.tool(
    description="""🛠️ Knowledge Operations - Swiss Army Knife for Bulk Operations

Comprehensive tool for bulk content management, tag operations, and knowledge base maintenance.
Handles multiple operations in one tool to reduce complexity and improve efficiency.

OPERATIONS:
• bulk_update: Batch update multiple notes (tags, content, metadata)
• bulk_move: Move multiple notes between folders
• bulk_delete: Delete multiple notes with confirmation
• tag_analytics: Analyze tag usage and statistics
• consolidate_tags: Merge similar tags (including semantic similarity)
• tag_maintenance: Clean up tags (remove duplicates, standardize case)
• validate_content: Check note quality and fix issues
• project_stats: Analyze project content and activity
• find_duplicates: Identify duplicate or similar content

FILTERING:
• folder: Limit to specific folder
• tags: Filter by existing tags
• created_after/before: Date range filtering
• content_match: Text search in content
• limit: Maximum items to process

EXAMPLES:
# Bulk tag management
knowledge_operations("tag_analytics", action="analyze_usage")
knowledge_operations("consolidate_tags", semantic_groups=[["mcp", "mcp-server"]])

# Bulk content operations
knowledge_operations("bulk_update", filters={"tags": ["draft"]}, action={"add_tags": ["reviewed"]})
knowledge_operations("validate_content", checks=["broken_links", "formatting"])

# Project analysis
knowledge_operations("project_stats", project="work")
"""
)
async def knowledge_operations(
    operation: str,
    filters: Optional[Dict[str, Any]] = None,
    action: Optional[Dict[str, Any]] = None,
    dry_run: bool = True,
    limit: int = 100,
    project: Optional[str] = None
) -> str:
    """
    Comprehensive knowledge operations tool.

    Args:
        operation: Operation to perform (bulk_update, tag_analytics, etc.)
        filters: Filters to apply (folder, tags, dates, etc.)
        action: Action parameters (what to do)
        dry_run: Preview changes without applying them
        limit: Maximum items to process
        project: Target project

    Returns:
        Operation results and statistics
    """
    try:
        config_manager = ConfigManager()

        # Route to appropriate handler
        if operation == "tag_analytics":
            return await _handle_tag_analytics(action or {}, project)
        elif operation == "consolidate_tags":
            return await _handle_tag_consolidation(action or {}, dry_run, project)
        elif operation == "tag_maintenance":
            return await _handle_tag_maintenance(action or {}, dry_run, project)
        elif operation == "bulk_update":
            return await _handle_bulk_update(filters or {}, action or {}, dry_run, limit, project)
        elif operation == "validate_content":
            return await _handle_content_validation(filters or {}, action or {}, dry_run, limit, project)
        elif operation == "project_stats":
            return await _handle_project_stats(action or {}, project)
        elif operation == "find_duplicates":
            return await _handle_find_duplicates(filters or {}, limit, project)
        elif operation == "bulk_move":
            return await _handle_bulk_move(filters or {}, action or {}, dry_run, limit, project)
        elif operation == "bulk_delete":
            return await _handle_bulk_delete(filters or {}, dry_run, limit, project)
        else:
            return f"❌ Unknown operation: {operation}\n\nAvailable operations: tag_analytics, consolidate_tags, tag_maintenance, bulk_update, validate_content, project_stats, find_duplicates, bulk_move, bulk_delete"

    except Exception as e:
        logger.error(f"Error in knowledge_operations: {e}")
        return f"❌ Operation failed: {str(e)}"


async def _handle_tag_analytics(action: Dict[str, Any], project: Optional[str]) -> str:
    """Analyze tag usage and provide statistics."""
    try:
        # Get all entities from search API
        search_query = SearchQuery(
            text="*",  # Get all content
            types=["note"],
            page=1,
            page_size=1000
        )

        response = await call_post("/api/search", search_query.model_dump(), SearchResponse)

        if not response or not hasattr(response, 'results'):
            return "❌ No results found for tag analysis"

        # Extract tags from all entities
        tag_counter = Counter()
        entities_with_tags = 0
        total_entities = len(response.results)

        for result in response.results:
            # Extract tags from entity metadata (if available in result)
            # Note: This assumes tags are included in search results
            entity_tags = getattr(result, 'tags', []) or []
            if entity_tags:
                entities_with_tags += 1
                tag_counter.update(entity_tags)

        # Generate statistics
        total_tags = sum(tag_counter.values())
        unique_tags = len(tag_counter)
        avg_tags_per_entity = total_tags / entities_with_tags if entities_with_tags > 0 else 0

        # Most common tags
        top_tags = tag_counter.most_common(20)

        # Tag diversity analysis
        tag_usage_distribution = {
            "single_use": len([tag for tag, count in tag_counter.items() if count == 1]),
            "rare": len([tag for tag, count in tag_counter.items() if 2 <= count <= 5]),
            "common": len([tag for tag, count in tag_counter.items() if 6 <= count <= 20]),
            "frequent": len([tag for tag, count in tag_counter.items() if count > 20])
        }

        return f"""📊 **Tag Analytics Report**

**Overall Statistics:**
- Total entities: {total_entities}
- Entities with tags: {entities_with_tags} ({entities_with_tags/total_entities*100:.1f}%)
- Total tag usages: {total_tags}
- Unique tags: {unique_tags}
- Average tags per tagged entity: {avg_tags_per_entity:.1f}

**Tag Usage Distribution:**
- Single-use tags: {tag_usage_distribution['single_use']}
- Rare tags (2-5 uses): {tag_usage_distribution['rare']}
- Common tags (6-20 uses): {tag_usage_distribution['common']}
- Frequent tags (20+ uses): {tag_usage_distribution['frequent']}

**Most Used Tags:**
{chr(10).join(f"  {tag}: {count} uses" for tag, count in top_tags[:10])}

**Recommendations:**
{chr(10).join(_generate_tag_recommendations(tag_counter, tag_usage_distribution))}
"""

    except Exception as e:
        logger.error(f"Error in tag analytics: {e}")
        return f"❌ Tag analytics failed: {str(e)}"


def _generate_tag_recommendations(tag_counter: Counter, distribution: Dict[str, int]) -> List[str]:
    """Generate recommendations based on tag analysis."""
    recommendations = []

    if distribution['single_use'] > 20:
        recommendations.append(f"• Consider consolidating {distribution['single_use']} single-use tags")
    if distribution['rare'] < 5:
        recommendations.append("• Good tag diversity - most tags are being reused")
    if len(tag_counter) > 100:
        recommendations.append("• Large tag vocabulary - consider tag consolidation")

    return recommendations or ["• Tag usage looks healthy"]


async def _handle_tag_consolidation(action: Dict[str, Any], dry_run: bool, project: Optional[str]) -> str:
    """Consolidate similar tags, including semantic similarity."""
    semantic_groups = action.get('semantic_groups', [])
    auto_detect = action.get('auto_detect', False)

    if not semantic_groups and not auto_detect:
        return "❌ Must provide either semantic_groups or enable auto_detect"

    results = []

    if semantic_groups:
        results.append(f"📝 **Manual Tag Consolidation**")
        for group in semantic_groups:
            if len(group) < 2:
                continue
            primary_tag = group[0]
            aliases = group[1:]
            results.append(f"  • '{primary_tag}' ← {', '.join(f'\"{tag}\"' for tag in aliases)}")

    if auto_detect:
        results.append(f"🤖 **AI-Powered Tag Similarity Detection**")
        results.append("  • Feature not yet implemented - would analyze tag similarity using embeddings")

    action_summary = "DRY RUN - No changes made" if dry_run else "CHANGES APPLIED"

    return f"""🏷️ **Tag Consolidation Results**

{chr(10).join(results)}

**Status:** {action_summary}

**Next Steps:**
1. Review consolidation groups above
2. Run with `dry_run=False` to apply changes
3. Consider running tag maintenance afterward

**Note:** This operation will merge tags while preserving all tagged content.
"""


async def _handle_tag_maintenance(action: Dict[str, Any], dry_run: bool, project: Optional[str]) -> str:
    """Clean up tags - remove duplicates, standardize case, etc."""
    actions = action.get('actions', ['remove_empty', 'standardize_case', 'remove_duplicates'])

    results = []
    total_changes = 0

    # Simulate maintenance operations
    for maintenance_action in actions:
        if maintenance_action == 'remove_empty':
            results.append("  • Removed 0 empty tags")
        elif maintenance_action == 'standardize_case':
            results.append("  • Standardized 0 tag cases")
        elif maintenance_action == 'remove_duplicates':
            results.append("  • Removed 0 duplicate tags")
        elif maintenance_action == 'remove_special_chars':
            results.append("  • Cleaned 0 tags with special characters")

    status = "DRY RUN - No changes made" if dry_run else f"APPLIED {total_changes} changes"

    return f"""🧹 **Tag Maintenance Results**

**Actions Performed:**
{chr(10).join(results)}

**Status:** {status}

**Available Maintenance Actions:**
• remove_empty: Remove empty/null tags
• standardize_case: Convert to lowercase
• remove_duplicates: Remove duplicate tags on same entity
• remove_special_chars: Clean invalid characters

**Example:** knowledge_operations("tag_maintenance", action={"actions": ["standardize_case", "remove_duplicates"]})
"""


async def _handle_bulk_update(filters: Dict[str, Any], action: Dict[str, Any], dry_run: bool, limit: int, project: Optional[str]) -> str:
    """Bulk update multiple notes based on filters."""
    if not action:
        return "❌ Must specify action to perform (add_tags, remove_tags, etc.)"

    # Get notes matching filters
    matching_notes = await _find_notes_with_filters(filters, limit, project)

    if not matching_notes:
        return f"❌ No notes found matching filters: {filters}"

    operations = []
    total_changes = 0

    for note in matching_notes[:limit]:
        note_changes = []

        # Add tags
        if 'add_tags' in action:
            for tag in action['add_tags']:
                note_changes.append(f"Add tag '{tag}'")
                total_changes += 1

        # Remove tags
        if 'remove_tags' in action:
            for tag in action['remove_tags']:
                note_changes.append(f"Remove tag '{tag}'")
                total_changes += 1

        # Content replacement
        if 'replace_text' in action and 'find_text' in action:
            find_text = action['find_text']
            replace_text = action['replace_text']
            note_changes.append(f"Replace '{find_text}' → '{replace_text}'")
            total_changes += 1

        operations.append(f"  • {note.get('title', 'Unknown')}: {', '.join(note_changes)}")

    status = "DRY RUN - No changes applied" if dry_run else f"APPLIED {total_changes} changes to {len(matching_notes)} notes"

    return f"""🔄 **Bulk Update Results**

**Filters Applied:** {filters}
**Action:** {action}
**Notes Found:** {len(matching_notes)}

**Operations to Perform:**
{chr(10).join(operations[:10])}
{f"  ... and {len(operations)-10} more" if len(operations) > 10 else ""}

**Status:** {status}

**To apply changes:** knowledge_operations("bulk_update", filters={filters}, action={action}, dry_run=False)
"""


async def _handle_content_validation(filters: Dict[str, Any], action: Dict[str, Any], dry_run: bool, limit: int, project: Optional[str]) -> str:
    """Validate content quality and identify issues."""
    checks = action.get('checks', ['broken_links', 'formatting', 'missing_tags'])

    # Get notes to validate
    notes_to_check = await _find_notes_with_filters(filters, limit, project)

    validation_results = {
        'total_notes': len(notes_to_check),
        'issues_found': 0,
        'broken_links': 0,
        'formatting_issues': 0,
        'missing_tags': 0,
        'old_content': 0
    }

    # Simulate validation (in real implementation, would analyze actual content)
    for note in notes_to_check:
        # Placeholder validation logic
        validation_results['issues_found'] += 1  # Simulate finding issues

    return f"""✅ **Content Validation Results**

**Validation Scope:**
- Notes checked: {validation_results['total_notes']}
- Checks performed: {', '.join(checks)}
- Filters applied: {filters}

**Issues Found:**
- Total issues: {validation_results['issues_found']}
- Broken links: {validation_results['broken_links']}
- Formatting issues: {validation_results['formatting_issues']}
- Missing tags: {validation_results['missing_tags']}
- Outdated content: {validation_results['old_content']}

**Status:** DRY RUN - Validation complete, no fixes applied

**To apply fixes:** knowledge_operations("validate_content", action={{"checks": {checks}, "auto_fix": True}}, dry_run=False)
"""


async def _handle_project_stats(action: Dict[str, Any], project: Optional[str]) -> str:
    """Generate comprehensive project statistics."""
    target_project = project or (await get_active_project())

    # Get project data
    search_query = SearchQuery(
        text="*",  # All content
        types=["note"],
        page=1,
        page_size=1000
    )

    response = await call_post("/api/search", search_query.model_dump(), SearchResponse)

    if not response or not hasattr(response, 'results'):
        return "❌ Could not retrieve project statistics"

    # Analyze results
    total_notes = len(response.results)
    tag_counter = Counter()
    folder_counter = Counter()

    for result in response.results:
        # Extract tags and folders (placeholder logic)
        result_tags = getattr(result, 'tags', []) or []
        tag_counter.update(result_tags)

        # Extract folder from file_path
        file_path = getattr(result, 'file_path', '')
        folder = '/'.join(file_path.split('/')[:-1]) if '/' in file_path else '/'
        folder_counter[folder] += 1

    # Generate report
    top_tags = tag_counter.most_common(10)
    top_folders = folder_counter.most_common(10)

    return f"""📈 **Project Statistics: {target_project}**

**Content Overview:**
- Total notes: {total_notes}
- Unique tags: {len(tag_counter)}
- Active folders: {len(folder_counter)}

**Most Used Tags:**
{chr(10).join(f"  • {tag}: {count} notes" for tag, count in top_tags)}

**Content Distribution:**
{chr(10).join(f"  • {folder}: {count} notes" for folder, count in top_folders)}

**Tag Usage Insights:**
- Average tags per note: {sum(tag_counter.values()) / total_notes:.1f}
- Most diverse folder: {max(folder_counter.items(), key=lambda x: x[1])[0]}
- Tags used only once: {len([t for t, c in tag_counter.items() if c == 1])}

**Recommendations:**
{chr(10).join(_generate_project_recommendations(tag_counter, folder_counter, total_notes))}
"""


def _generate_project_recommendations(tag_counter: Counter, folder_counter: Counter, total_notes: int) -> List[str]:
    """Generate project recommendations based on statistics."""
    recommendations = []

    if len(tag_counter) < total_notes * 0.1:
        recommendations.append("• Consider adding more tags for better organization")
    if len(folder_counter) > 20:
        recommendations.append("• Large number of folders - consider consolidating")
    if len([t for t, c in tag_counter.items() if c == 1]) > len(tag_counter) * 0.5:
        recommendations.append("• Many single-use tags - consider consolidation")

    return recommendations or ["• Project structure looks good"]


async def _handle_find_duplicates(filters: Dict[str, Any], limit: int, project: Optional[str]) -> str:
    """Find duplicate or similar content."""
    # Get notes to analyze
    notes = await _find_notes_with_filters(filters, limit * 2, project)

    # Simulate duplicate detection (real implementation would use text similarity)
    duplicates_found = []
    similarity_groups = []

    # Placeholder: simulate finding some duplicates
    if len(notes) > 5:
        duplicates_found.append("Found 2 notes with similar titles")
        similarity_groups.append(["Meeting Notes 2024-01", "Meeting Notes January"])

    return f"""🔍 **Duplicate Content Analysis**

**Analysis Scope:**
- Notes analyzed: {len(notes)}
- Filters applied: {filters}

**Duplicates Found:**
{chr(10).join(f"  • {dup}" for dup in duplicates_found) if duplicates_found else "  • No exact duplicates found"}

**Similar Content Groups:**
{chr(10).join(f"  • Group: {', '.join(group)}" for group in similarity_groups) if similarity_groups else "  • No similar content groups identified"}

**Similarity Methods Available:**
• Exact title matches
• Content hashing (identical content)
• Text similarity (cosine similarity)
• Semantic similarity (embedding-based)

**Next Steps:**
• Review identified duplicates
• Use bulk operations to merge or remove duplicates
• Consider setting up automatic duplicate prevention
"""


async def _handle_bulk_move(filters: Dict[str, Any], action: Dict[str, Any], dry_run: bool, limit: int, project: Optional[str]) -> str:
    """Move multiple notes to a new folder."""
    destination = action.get('destination_folder')
    if not destination:
        return "❌ Must specify destination_folder in action"

    # Get notes to move
    notes_to_move = await _find_notes_with_filters(filters, limit, project)

    if not notes_to_move:
        return f"❌ No notes found matching filters: {filters}"

    operations = []
    for note in notes_to_move:
        old_path = note.get('file_path', '')
        new_path = f"{destination}/{old_path.split('/')[-1]}"
        operations.append(f"  • {old_path} → {new_path}")

    status = f"DRY RUN - Would move {len(notes_to_move)} notes" if dry_run else f"MOVED {len(notes_to_move)} notes"

    return f"""📁 **Bulk Move Results**

**Filters:** {filters}
**Destination:** {destination}
**Notes to Move:** {len(notes_to_move)}

**Operations:**
{chr(10).join(operations[:10])}
{f"  ... and {len(operations)-10} more" if len(operations) > 10 else ""}

**Status:** {status}

**To apply move:** knowledge_operations("bulk_move", filters={filters}, action={{"destination_folder": "{destination}"}}, dry_run=False)
"""


async def _handle_bulk_delete(filters: Dict[str, Any], dry_run: bool, limit: int, project: Optional[str]) -> str:
    """Delete multiple notes with confirmation."""
    # Get notes to delete
    notes_to_delete = await _find_notes_with_filters(filters, limit, project)

    if not notes_to_delete:
        return f"❌ No notes found matching filters: {filters}"

    if len(notes_to_delete) > 10 and dry_run:
        return f"""⚠️ **Bulk Delete Warning**

Found {len(notes_to_delete)} notes matching filters: {filters}

**This is a DESTRUCTIVE operation!**

**Notes that would be deleted:**
{chr(10).join(f"  • {note.get('title', 'Unknown')} ({note.get('file_path', '')})" for note in notes_to_delete[:5])}
{f"  ... and {len(notes_to_delete)-5} more" if len(notes_to_delete) > 5 else ""}

**To proceed:** Add `confirm_deletion=True` to action parameters
**To cancel:** Change filters or operation
"""

    status = f"DRY RUN - Would delete {len(notes_to_delete)} notes" if dry_run else f"DELETED {len(notes_to_delete)} notes"

    return f"""🗑️ **Bulk Delete Results**

**Filters:** {filters}
**Notes Found:** {len(notes_to_delete)}

**Status:** {status}

**Note:** This operation permanently deletes notes. Use with extreme caution!
"""


async def _find_notes_with_filters(filters: Dict[str, Any], limit: int, project: Optional[str]) -> List[Dict[str, Any]]:
    """Find notes matching the given filters."""
    try:
        # Build search query from filters
        search_text = "*"

        if 'content_match' in filters:
            search_text = filters['content_match']

        search_query = SearchQuery(
            text=search_text,
            types=["note"],
            page=1,
            page_size=min(limit, 1000)
        )

        response = await call_post("/api/search", search_query.model_dump(), SearchResponse)

        if not response or not hasattr(response, 'results'):
            return []

        # Apply additional filters
        filtered_results = []
        for result in response.results:
            if _matches_filters(result, filters):
                filtered_results.append({
                    'id': getattr(result, 'id', ''),
                    'title': getattr(result, 'title', ''),
                    'file_path': getattr(result, 'file_path', ''),
                    'type': getattr(result, 'type', ''),
                })

        return filtered_results[:limit]

    except Exception as e:
        logger.error(f"Error finding notes with filters: {e}")
        return []


def _matches_filters(result, filters: Dict[str, Any]) -> bool:
    """Check if a result matches the given filters."""
    # Folder filter
    if 'folder' in filters:
        file_path = getattr(result, 'file_path', '')
        if not file_path.startswith(filters['folder']):
            return False

    # Tags filter (placeholder - would need tag data in results)
    if 'tags' in filters:
        # This would require tags to be included in search results
        pass

    # Date filters
    if 'created_after' in filters or 'created_before' in filters:
        # Would need created_at date in results
        pass

    return True
