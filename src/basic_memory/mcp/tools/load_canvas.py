"""Load Obsidian canvas tool for Basic Memory MCP server.

This tool imports Obsidian canvas files (.canvas) and converts them into
Basic Memory entities and relations.
"""

import json
from typing import Optional, Dict, List, Any
from pathlib import Path

from loguru import logger

from basic_memory.mcp.server import mcp
from basic_memory.mcp.tools.read_content import read_content
from basic_memory.mcp.tools.write_note import write_note
from basic_memory.mcp.tools.search import search_notes
from basic_memory.schemas.memory import memory_url_path


@mcp.tool(
    description="""Import Obsidian Canvas visual mind maps into Basic Memory as structured knowledge.

This tool converts Obsidian's visual canvas files (.canvas) into Basic Memory entities and relationships,
transforming visual thinking into structured, searchable knowledge.

CANVAS FEATURES SUPPORTED:
- Text nodes: Converted to individual notes with full content
- File nodes: Create references to existing or external files
- Link nodes: Establish relationships between entities
- Group nodes: Organize content into folder structures
- Edge connections: Become semantic relationships

PARAMETERS:
- canvas_path (str, REQUIRED): Filesystem path to .canvas JSON file
- destination_folder (str, default="imported/canvases"): Basic Memory folder for imported content
- create_missing_files (bool, default=False): Create placeholder notes for missing file references
- project (str, optional): Target Basic Memory project

NODE TYPE CONVERSION:
- Text nodes → Markdown notes with canvas content
- File nodes → Reference links to existing files
- Link nodes → Entity relationship mappings
- Groups → Folder organization structures

USAGE EXAMPLES:
Basic canvas: load_obsidian_canvas("mindmap.canvas")
Custom folder: load_obsidian_canvas("project.canvas", destination_folder="projects/visual")
With placeholders: load_obsidian_canvas("overview.canvas", create_missing_files=True)

RETURNS:
Import summary showing nodes processed, relationships created, and any issues encountered.

NOTE: Canvas files are JSON-based visual layouts. This tool extracts the structured content
and relationships, converting visual thinking into Basic Memory's entity-relationship model.""",
)
async def load_obsidian_canvas(
    canvas_path: str,
    destination_folder: str = "imported/canvases",
    create_missing_files: bool = False,
    project: Optional[str] = None,
) -> str:
    """Load an Obsidian canvas file and import its content into Basic Memory.

    This tool reads a JSON Canvas file (.canvas) and converts its nodes and edges
    into Basic Memory entities and relations. Text nodes become notes, file nodes
    reference existing content, and edges become relations between entities.

    Args:
        canvas_path: Path to the .canvas file to import (e.g., "diagrams/project-overview.canvas")
        destination_folder: Folder where imported notes should be created (default: "imported/canvases")
        create_missing_files: If True, create placeholder notes for referenced files that don't exist
        project: Optional project name to import into. If not provided, uses current active project.

    Returns:
        A summary of the import operation including created entities and relations.

    Examples:
        # Import a canvas file
        result = await load_obsidian_canvas("diagrams/project-overview.canvas")

        # Import to specific folder
        result = await load_obsidian_canvas(
            "diagrams/project-overview.canvas",
            destination_folder="projects/my-project"
        )

        # Import and create missing files
        result = await load_obsidian_canvas(
            "diagrams/project-overview.canvas",
            create_missing_files=True
        )

        # Import to specific project
        result = await load_obsidian_canvas(
            "diagrams/project-overview.canvas",
            project="work-project"
        )
    """
    try:
        logger.info(f"Starting canvas import: {canvas_path}")

        # Read the canvas file
        canvas_content = await read_content(canvas_path, project)
        if canvas_content.get("type") == "error":
            return f"# Canvas Import Failed\n\nError reading canvas file '{canvas_path}': {canvas_content['error']}"

        if canvas_content.get("type") != "text":
            return f"# Canvas Import Failed\n\nFile '{canvas_path}' is not a valid canvas file (expected JSON text)"

        # Parse JSON
        try:
            canvas_data = json.loads(canvas_content["text"])
        except json.JSONDecodeError as e:
            return f"# Canvas Import Failed\n\nInvalid JSON in canvas file '{canvas_path}': {e}"

        # Validate canvas structure
        validation_result = _validate_canvas_structure(canvas_data)
        if not validation_result["valid"]:
            return f"# Canvas Import Failed\n\n{validation_result['error']}"

        # Process the canvas
        result = await _process_canvas(
            canvas_data,
            canvas_path,
            destination_folder,
            create_missing_files,
            project
        )

        return result

    except Exception as e:
        logger.error(f"Canvas import failed: {e}")
        return f"# Canvas Import Failed\n\nUnexpected error: {e}"


def _validate_canvas_structure(canvas_data: dict) -> dict:
    """Validate that the canvas data follows JSON Canvas format."""
    if not isinstance(canvas_data, dict):
        return {"valid": False, "error": "Canvas data must be a JSON object"}

    if "nodes" not in canvas_data or "edges" not in canvas_data:
        return {"valid": False, "error": "Canvas must contain 'nodes' and 'edges' arrays"}

    if not isinstance(canvas_data["nodes"], list):
        return {"valid": False, "error": "'nodes' must be an array"}

    if not isinstance(canvas_data["edges"], list):
        return {"valid": False, "error": "'edges' must be an array"}

    # Validate node structure
    for i, node in enumerate(canvas_data["nodes"]):
        if not isinstance(node, dict):
            return {"valid": False, "error": f"Node {i} must be an object"}
        if "id" not in node:
            return {"valid": False, "error": f"Node {i} must have an 'id' field"}
        if "type" not in node:
            return {"valid": False, "error": f"Node {i} must have a 'type' field"}

    # Validate edge structure
    for i, edge in enumerate(canvas_data["edges"]):
        if not isinstance(edge, dict):
            return {"valid": False, "error": f"Edge {i} must be an object"}
        if "id" not in edge:
            return {"valid": False, "error": f"Edge {i} must have an 'id' field"}
        if "fromNode" not in edge or "toNode" not in edge:
            return {"valid": False, "error": f"Edge {i} must have 'fromNode' and 'toNode' fields"}

    return {"valid": True}


async def _process_canvas(
    canvas_data: dict,
    canvas_path: str,
    destination_folder: str,
    create_missing_files: bool,
    project: Optional[str]
) -> str:
    """Process the canvas data and create entities and relations."""
    nodes = canvas_data["nodes"]
    edges = canvas_data["edges"]

    logger.info(f"Processing canvas with {len(nodes)} nodes and {len(edges)} edges")

    # Track what we create
    created_entities = []
    created_relations = []
    skipped_items = []

    # Process nodes first
    node_map = {}  # Map canvas node IDs to Basic Memory entity paths

    for node in nodes:
        try:
            entity_path = await _process_canvas_node(
                node, destination_folder, create_missing_files, project
            )
            if entity_path:
                node_map[node["id"]] = entity_path
                if entity_path not in created_entities:
                    created_entities.append(entity_path)
            else:
                skipped_items.append(f"Node {node['id']}: {node.get('text', node.get('file', 'unknown'))}")
        except Exception as e:
            logger.error(f"Failed to process node {node.get('id', 'unknown')}: {e}")
            skipped_items.append(f"Node {node.get('id', 'unknown')}: {e}")

    # Process edges
    for edge in edges:
        try:
            relation_created = await _process_canvas_edge(
                edge, node_map, project
            )
            if relation_created:
                created_relations.append(relation_created)
        except Exception as e:
            logger.error(f"Failed to process edge {edge.get('id', 'unknown')}: {e}")
            skipped_items.append(f"Edge {edge.get('id', 'unknown')}: {e}")

    # Build summary
    summary = [f"# Canvas Import Complete: {Path(canvas_path).name}"]

    if created_entities:
        summary.append(f"\n## Created Entities ({len(created_entities)})")
        for entity in created_entities:
            summary.append(f"- {entity}")

    if created_relations:
        summary.append(f"\n## Created Relations ({len(created_relations)})")
        for relation in created_relations:
            summary.append(f"- {relation}")

    if skipped_items:
        summary.append(f"\n## Skipped Items ({len(skipped_items)})")
        for item in skipped_items[:5]:  # Limit to first 5
            summary.append(f"- {item}")
        if len(skipped_items) > 5:
            summary.append(f"- ... and {len(skipped_items) - 5} more")

    summary.append(f"\n## Import Summary")
    summary.append(f"- Canvas file: {canvas_path}")
    summary.append(f"- Destination folder: {destination_folder}")
    summary.append(f"- Total nodes: {len(nodes)}")
    summary.append(f"- Total edges: {len(edges)}")
    summary.append(f"- Entities created: {len(created_entities)}")
    summary.append(f"- Relations created: {len(created_relations)}")

    return "\n".join(summary)


async def _process_canvas_node(
    node: dict,
    destination_folder: str,
    create_missing_files: bool,
    project: Optional[str]
) -> Optional[str]:
    """Process a single canvas node and create a Basic Memory entity."""
    node_type = node.get("type")
    node_id = node.get("id")

    if node_type == "text":
        # Create a note from text content
        text = node.get("text", "").strip()
        if not text:
            return None

        # Use first line as title, rest as content
        lines = text.split("\n")
        title = lines[0][:100]  # Limit title length
        content = "\n".join(lines[1:]) if len(lines) > 1 else ""

        # Create the note
        result = await write_note.fn(
            title=title,
            content=content,
            folder=destination_folder,
            project=project
        )

        logger.info(f"Created text note from canvas node {node_id}: {title}")
        return f"{destination_folder}/{title}"

    elif node_type == "file":
        # Reference to existing file
        file_path = node.get("file")
        if not file_path:
            return None

        # Check if file exists
        try:
            existing = await search_notes.fn(
                query=file_path,
                search_type="permalink",
                project=project
            )

            if existing.results:
                logger.info(f"Found existing file reference for canvas node {node_id}: {file_path}")
                return file_path
            elif create_missing_files:
                # Create a placeholder note
                result = await write_note.fn(
                    title=f"Referenced: {Path(file_path).stem}",
                    content=f"This note was referenced in a canvas but the original file was not found.\n\nOriginal path: {file_path}",
                    folder=destination_folder,
                    project=project
                )
                logger.info(f"Created placeholder note for missing file {file_path}")
                return f"{destination_folder}/Referenced: {Path(file_path).stem}"
            else:
                logger.info(f"Skipping missing file reference: {file_path}")
                return None

        except Exception as e:
            logger.error(f"Error checking file existence for {file_path}: {e}")
            return None

    elif node_type == "link":
        # URL or external link
        url = node.get("url")
        if url:
            result = await write_note.fn(
                title=f"Link: {url[:50]}...",
                content=f"External link referenced in canvas.\n\nURL: {url}",
                folder=destination_folder,
                project=project
            )
            logger.info(f"Created link note from canvas node {node_id}: {url}")
            return f"{destination_folder}/Link: {url[:50]}..."
        return None

    elif node_type == "group":
        # Group node - could create a folder or category note
        label = node.get("label", f"Group {node_id}")
        result = await write_note.fn(
            title=f"Group: {label}",
            content=f"Canvas group node: {label}\n\nThis represents a grouped collection of items from the imported canvas.",
            folder=destination_folder,
            project=project
        )
        logger.info(f"Created group note from canvas node {node_id}: {label}")
        return f"{destination_folder}/Group: {label}"

    else:
        logger.warning(f"Unknown canvas node type: {node_type}")
        return None


async def _process_canvas_edge(
    edge: dict,
    node_map: dict,
    project: Optional[str]
) -> Optional[str]:
    """Process a canvas edge and create a Basic Memory relation."""
    from_node = edge.get("fromNode")
    to_node = edge.get("toNode")
    label = edge.get("label", "connects to")

    if from_node not in node_map or to_node not in node_map:
        logger.warning(f"Cannot create relation: missing node mapping for edge {edge.get('id')}")
        return None

    from_entity = node_map[from_node]
    to_entity = node_map[to_node]

    # For now, we'll create a simple note that documents the relationship
    # In the future, this could be enhanced to use actual relation entities
    relation_note = await write_note.fn(
        title=f"Canvas Relation: {Path(from_entity).name} → {Path(to_entity).name}",
        content=f"""Canvas relationship imported from Obsidian canvas.

**From:** {from_entity}
**To:** {to_entity}
**Relationship:** {label}

This relation was automatically created during canvas import.
""",
        folder="relations",
        project=project
    )

    logger.info(f"Created relation note: {from_entity} → {to_entity}")
    return f"{from_entity} → {to_entity} ({label})"
