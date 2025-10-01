"""Help and system information tool for Basic Memory MCP server."""

from typing import Optional

from basic_memory.mcp.server import mcp


@mcp.tool(
    description="""Comprehensive help system for Basic Memory with multiple knowledge levels.

This tool provides contextual assistance and documentation for Basic Memory features,
organized by knowledge levels from basic usage to advanced technical details.

LEVELS:
- basic: Quick start guide and essential commands
- intermediate: Detailed tool descriptions and workflows
- advanced: Technical architecture and implementation details
- expert: Development troubleshooting and system internals

TOPICS:
- semantic-net: Knowledge graph and entity relationships
- claude: AI integration patterns and best practices
- tools: Complete command reference with examples
- import: Data migration from external applications
- export: Content publishing and sharing options
- typora: Rich text editing workflows
- obsidian: Obsidian vault integration guide
- joplin: Joplin export compatibility
- notion: Notion HTML/Markdown import strategies
- evernote: Evernote ENEX file processing
- mermaid: Diagram creation and rendering

PARAMETERS:
- level (str, default="basic"): Help detail level (basic/intermediate/advanced/expert)
- topic (str, optional): Specific topic to focus on (see list above)

USAGE EXAMPLES:
Basic overview: help()
Tool reference: help("intermediate")
Semantic networks: help("advanced", "semantic-net")
Claude integration: help("intermediate", "claude")
Troubleshooting: help("expert")

RETURNS:
Contextual help content formatted for easy reading with examples and guidance.""",
)
async def help(level: str = "basic", topic: Optional[str] = None) -> str:
    """Get help and information about Basic Memory and its capabilities.

    This is a multilevel help system providing different depths of information:

    **Level 1 - "basic"**: Quick overview and getting started
    **Level 2 - "intermediate"**: Detailed tool descriptions and workflows
    **Level 3 - "advanced"**: Technical details and architecture
    **Level 4 - "expert"**: Development and troubleshooting

    Args:
        level: Help level (basic, intermediate, advanced, expert)
        topic: Optional specific topic to focus on

    Returns:
        Comprehensive help information at the requested level

    Examples:
        help() - Basic overview
        help("intermediate") - Detailed tool descriptions
        help("advanced", "semantic-net") - Advanced semantic net info
        help("expert") - Technical troubleshooting
    """

    if topic:
        return _get_topic_help(topic, level)

    if level == "basic":
        return _get_basic_help()
    elif level == "intermediate":
        return _get_intermediate_help()
    elif level == "advanced":
        return _get_advanced_help()
    elif level == "expert":
        return _get_expert_help()
    else:
        return f"""# Help - Invalid Level

Unknown help level: "{level}"

Available levels:
- **basic**: Quick overview and getting started
- **intermediate**: Detailed tool descriptions and workflows
- **advanced**: Technical details and architecture
- **expert**: Development and troubleshooting

Try: `help("basic")`"""


def _get_topic_help(topic: str, level: str) -> str:
    """Get help for a specific topic."""

    topic = topic.lower()

    if topic in ["semantic", "semantic-net", "knowledge-graph"]:
        return _get_semantic_net_help(level)
    elif topic in ["claude", "ide", "interaction"]:
        return _get_claude_interaction_help(level)
    elif topic in ["tools", "commands"]:
        return _get_tools_help(level)
    elif topic in ["import", "export"]:
        return _get_import_export_help(level)
    elif topic in ["typora"]:
        return _get_typora_help(level)
    elif topic in ["obsidian"]:
        return _get_obsidian_help(level)
    elif topic in ["joplin"]:
        return _get_joplin_help(level)
    elif topic in ["notion"]:
        return _get_notion_help(level)
    elif topic in ["evernote"]:
        return _get_evernote_help(level)
    elif topic in ["mermaid"]:
        return _get_mermaid_help(level)
    else:
        return f"""# Help - Unknown Topic

Unknown topic: "{topic}"

Available topics:
- **semantic-net**: Knowledge graph and entity relationships
- **claude**: AI/Claude integration and interaction
- **tools**: Available commands and functions
- **import**: Data import capabilities
- **export**: Data export capabilities
- **typora**: Rich text editing integration
- **obsidian**: Obsidian vault integration
- **joplin**: Joplin export integration
- **notion**: Notion export integration
- **evernote**: Evernote ENEX integration
- **mermaid**: Diagram and visualization support

Try: `help("tools")`"""


def _get_basic_help() -> str:
    """Basic help - quick overview and getting started."""

    return """# Basic Memory - Getting Started

## What is Basic Memory?

Basic Memory is an **enhanced knowledge management system** that combines:
- **Local-first architecture** - Your data stays on your machine
- **Semantic networking** - Entities and relationships form knowledge graphs
- **Multi-format support** - Import from popular note-taking apps
- **Rich editing** - Typora integration for advanced formatting
- **Visual diagrams** - Mermaid diagram support
- **AI integration** - Seamless Claude Desktop interaction

## Quick Start

### 1. Check System Status
```
sync_status()
```
Shows if your knowledge base is ready and processing status.

### 2. Create Your First Note
```
write_note(
    title="Welcome to Basic Memory",
    content="# Hello World\\n\\nThis is my first note in Basic Memory!",
    folder="getting-started"
)
```

### 3. Read and Search
```
read_note("Welcome to Basic Memory")
search_notes("hello world")
```

### 4. Explore Features
```
list_directory("/")  # See all your content
recent_activity()    # Check recent changes
```

## Key Features

### 📝 **Note Management**
- Create, read, edit, and organize notes
- Automatic filename sanitization
- Folder-based organization
- Full-text search with advanced filters

### 🔗 **Semantic Networking**
- Entities automatically link to related content
- Bidirectional relationships
- Knowledge graph visualization
- Smart suggestions and connections

### 📥 **Import from Everywhere**
- **Obsidian**: Vaults, canvas files, and search
- **Joplin**: Export files with metadata
- **Notion**: HTML and Markdown exports
- **Evernote**: ENEX XML files with attachments
- **Typora**: Round-trip rich editing

### 📤 **Export to Anywhere**
- **HTML**: With live Mermaid diagrams
- **Docsify**: Documentation sites
- **Joplin**: Cross-platform notes
- **Notion**: Compatible markdown
- **Evernote**: ENEX XML format

### 🎨 **Rich Features**
- **Mermaid Diagrams**: Flowcharts, mind maps, ER diagrams
- **Typora Integration**: Professional editing workflow
- **File Attachments**: Images, documents, and media
- **Tag System**: Organize content by topics

### 🤖 **AI Integration**
- Seamless Claude Desktop integration
- Context-aware suggestions
- Smart content generation
- Knowledge graph exploration

## Need More Help?

- `help("intermediate")` - Detailed tool descriptions
- `help("tools")` - Complete command reference
- `help("semantic-net")` - Understanding knowledge graphs
- `help("claude")` - AI interaction details

## Getting Started Checklist

- ✅ Install and configure Basic Memory
- ✅ Check sync status with `sync_status()`
- ⏳ Import existing notes from other apps
- ⏳ Create your first knowledge network
- ⏳ Explore Mermaid diagrams
- ⏳ Set up Typora for rich editing

Your enhanced Basic Memory is ready to revolutionize how you manage knowledge! 🚀"""


def _get_intermediate_help() -> str:
    """Intermediate help - detailed tool descriptions."""

    return """# Basic Memory - Tool Reference

## Core Note Operations

### Creating Content
```
write_note(
    title="My Note Title",
    content="# Header\\n\\nNote content here...",
    folder="category/subfolder",
    tags=["tag1", "tag2"]
)
```
- Creates new notes with automatic filename sanitization
- Supports markdown content and metadata
- Optional tags and folder organization

### Reading Content
```
read_note("My Note Title")           # By title
read_note("notes/my-note")          # By permalink
read_note("memory://notes/my-note") # Full URL
read_note("search term")            # Search fallback
```
- Multiple lookup strategies (direct, search, permalink)
- Automatic content sanitization
- Pagination support for long content

### Editing Content
```
edit_note("note-title", content="# Updated content...")
```
- In-place content updates
- Preserves metadata and relationships
- Automatic backup and versioning

### Organization
```
list_directory("/")              # Browse all folders
list_directory("notes/")         # Browse specific folder
move_note("old-path", "new-path") # Move between folders
delete_note("note-title")        # Remove notes
```

## Search & Discovery

### Full-Text Search
```
search_notes("keyword")                    # Basic search
search_notes("phrase", search_type="text") # Full content
search_notes("title", search_type="title") # Title only
search_notes("docs/*", search_type="permalink") # Path patterns
```
- Multiple search types and filters
- Boolean operators (AND, OR, NOT)
- Content type filtering
- Date-based filtering

### Activity & History
```
recent_activity()              # Recent changes
recent_activity("7d")         # Last week
recent_activity("2024-01-01") # Since date
```
- Track content changes and updates
- Filter by timeframe
- See collaboration and editing history

## Import Ecosystem

### From Obsidian
```
load_obsidian_vault("path/to/vault")    # Import entire vault
load_obsidian_canvas("canvas.json")     # Import canvas files
search_obsidian_vault("vault/path", "query") # Search external vaults
```

### From Joplin
```
load_joplin_vault("path/to/export")    # Import Joplin exports
export_joplin_notes("output/path")     # Export to Joplin
search_joplin_vault("export/path", "query") # Search exports
```

### From Notion
```
load_notion_export("notion-export.zip") # Import HTML/MD exports
export_notion_compatible("output/")     # Export as Notion-compatible
search_notion_vault("export/path", "query") # Search exports
```

### From Evernote
```
load_evernote_export("notes.enex")     # Import ENEX files
export_evernote_compatible("output/")  # Export as ENEX
search_evernote_vault("export/path", "query") # Search exports
```

## Export Capabilities

### Web Publishing
```
export_html_notes("site/", folder="docs/") # HTML with Mermaid
export_docsify("docs-site/")               # Docsify documentation
```

### Cross-Platform
```
export_joplin_notes("joplin/")      # Joplin format
export_notion_compatible("notion/") # Notion markdown
export_evernote_compatible("enex/") # Evernote ENEX
```

## Rich Editing

### Typora Integration
```
edit_in_typora("note-title")    # Export for editing
import_from_typora("note-title") # Import changes back
```
- Round-trip editing workflow
- Professional formatting
- Workspace management

## Visual Features

### Mermaid Diagrams
Add diagrams directly in markdown:
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

Supported: flowcharts, sequence diagrams, Gantt charts, mind maps, ER diagrams

## Project Management

### Multi-Project Support
```
list_memory_projects()          # See all projects
switch_project("project-name")  # Change active project
create_memory_project("name", "path") # Create new project
delete_project("name")          # Remove project
```

### System Administration
```
sync_status()                   # Check sync progress
get_current_project()           # Current project info
```

## Advanced Workflows

### Knowledge Networking
1. Create entity notes with consistent naming
2. Use `[[Entity Name]]` syntax for relationships
3. Basic Memory automatically builds knowledge graphs
4. Search across connected concepts

### Migration Strategies
1. Export from source application
2. Import using appropriate loader
3. Verify content integrity
4. Rebuild relationships as needed

### Content Organization
- Use folders for broad categorization
- Tags for cross-cutting concerns
- Entity relationships for semantic connections
- Mermaid diagrams for complex relationships

## Best Practices

### File Naming
- Use descriptive, consistent titles
- Consider permalink structure
- Avoid special characters (auto-sanitized)

### Content Structure
- Use clear headers and sections
- Include metadata in frontmatter
- Link related concepts
- Add visual diagrams for clarity

### Search Optimization
- Use specific keywords
- Leverage boolean operators
- Filter by content type and date
- Combine multiple search strategies

For advanced features: `help("advanced")`
For technical details: `help("expert")`"""


def _get_advanced_help() -> str:
    """Advanced help - technical details and architecture."""

    return """# Basic Memory - Advanced Architecture

## Semantic Network Architecture

### Entity-Relationship Model

Basic Memory implements a **graph-based knowledge representation** where:

#### Entities
- **Core nodes** in the knowledge graph
- Represent people, places, concepts, projects
- Stored as markdown files with metadata
- Automatically discovered and linked

#### Relationships
- **Edges** connecting entities
- Bidirectional links (`[[Entity Name]]` ↔ `[[Entity B]]`)
- Inferred from content patterns
- Support for typed relationships

#### Observations
- **Structured metadata** attached to entities
- Categories: `person`, `project`, `concept`, `location`
- Properties: attributes, dates, status, priority
- Relationships: `relates_to`, `part_of`, `created_by`

### Knowledge Graph Construction

#### Automatic Processing
1. **File Parsing**: Markdown files scanned for entity references
2. **Link Extraction**: `[[Entity Name]]` syntax identified
3. **Relationship Inference**: Bidirectional links established
4. **Metadata Enrichment**: Frontmatter and content analyzed
5. **Graph Updates**: Real-time synchronization

#### Search Integration
- **Entity-aware search**: Results include related entities
- **Relationship traversal**: Follow connections between concepts
- **Context expansion**: Include linked content in results
- **Semantic ranking**: Prioritize highly connected entities

### Content Processing Pipeline

#### Import Phase
```
Raw Content → Parser → Entity Extraction → Link Resolution → Storage
```

#### Sync Phase
```
File Changes → Content Analysis → Graph Updates → Search Index → Ready
```

#### Query Phase
```
User Query → Search Engine → Graph Traversal → Result Ranking → Response
```

## Claude Desktop Integration

### MCP Protocol Implementation

#### Tool Registration
- **Dynamic discovery**: Tools auto-registered on startup
- **Type safety**: Pydantic models for all parameters
- **Error handling**: Comprehensive validation and recovery
- **Async support**: Non-blocking operations

#### Context Management
- **Project awareness**: Multi-project support with isolation
- **Session state**: Maintain conversation context
- **Progress tracking**: Long-running operation status
- **Error recovery**: Graceful failure handling

### AI Interaction Patterns

#### Proactive Assistance
- **Content suggestions**: Related entities and connections
- **Workflow optimization**: Better ways to organize
- **Missing connections**: Suggest new relationships
- **Quality improvements**: Writing and structure suggestions

#### Reactive Responses
- **Direct commands**: Execute specific operations
- **Natural language**: Interpret intent from descriptions
- **Context awareness**: Use conversation history
- **Multi-step workflows**: Guide complex processes

#### Tool Orchestration
- **Sequential execution**: Multi-step workflows
- **Parallel processing**: Independent operations
- **Error recovery**: Alternative approaches on failure
- **Result synthesis**: Combine multiple tool outputs

## Performance Optimization

### Caching Strategy
- **Entity cache**: Recently accessed entities
- **Relationship cache**: Common relationship patterns
- **Search indexes**: Optimized for AI query patterns
- **Content previews**: Generated on demand

### Async Processing
```python
# All tools are async for non-blocking operation
@mcp.tool()
async def search_notes(query: str) -> SearchResponse:
    # Async database queries
    # Async file operations
    # Async API calls
    return await perform_search(query)
```

### Resource Management
- **Connection pooling**: Database connection reuse
- **Memory limits**: Large result set pagination
- **Timeout handling**: Prevent hanging operations
- **Background processing**: Long-running tasks

## Security Architecture

### Path Validation
- **Traversal prevention**: `../` attacks blocked
- **Project boundaries**: Access limited to configured paths
- **Input sanitization**: Malicious content filtered
- **Permission checking**: File access validation

### Data Integrity
- **Atomic operations**: All-or-nothing updates
- **Backup creation**: Automatic content preservation
- **Rollback support**: Failed operations reversible
- **Audit logging**: All changes tracked

## Development & Extension

### Plugin Architecture
- **Tool registration**: Easy addition of new capabilities
- **Hook system**: Extensible processing pipeline
- **Configuration**: Runtime behavior customization
- **API compatibility**: Version-aware extensions

### Testing Framework
- **Unit tests**: Individual component validation
- **Integration tests**: End-to-end workflow verification
- **Performance tests**: Scalability and efficiency checks
- **Compatibility tests**: Cross-platform validation

For expert-level details: `help("expert")`"""


def _get_expert_help() -> str:
    """Expert help - development and troubleshooting."""

    return """# Basic Memory - Expert Reference

## System Architecture

### Core Components

#### MCP Server (`basic_memory/mcp/`)
- **server.py**: FastMCP server initialization and configuration
- **async_client.py**: HTTP client for API communication
- **tools/**: Individual tool implementations
- **project_session.py**: Multi-project context management

#### Data Layer (`basic_memory/`)
- **db.py**: SQLite database connection and session management
- **models/**: SQLAlchemy ORM models
- **schemas/**: Pydantic data validation models
- **repository/**: Database access layer

#### Service Layer (`basic_memory/services/`)
- **sync_status_service.py**: Background synchronization tracking
- **Knowledge graph processing**: Entity relationship management
- **Search indexing**: Full-text search implementation

### Configuration System

#### ConfigManager
```python
# Located in basic_memory/config.py
class ConfigManager:
    def __init__(self):
        self.config = BasicMemoryConfig(
            projects={},  # Dict[str, Path]
            default_project="main",
            sync_delay=1000,  # ms
            log_level="INFO"
        )
```

#### Project Structure
```
basic-memory/
├── src/basic_memory/
│   ├── cli/commands/mcp.py      # MCP server entry point
│   ├── mcp/tools/               # Tool implementations
│   ├── models/                  # Database models
│   ├── schemas/                  # API schemas
│   ├── repository/              # Data access
│   └── services/                # Business logic
├── tests/                       # Test suite
├── docs/                        # Documentation
└── pyproject.toml              # Project configuration
```

## Development Workflow

### Adding New Tools

1. **Create tool file** in `src/basic_memory/mcp/tools/`
```python
@mcp.tool(description="Tool description")
async def my_tool(param: Type) -> Result:
    # Tool implementation
    return result
```

2. **Register in `__init__.py`**
```python
from .my_tool import my_tool
__all__ = ["my_tool", ...]
```

3. **Add to README and CHANGELOG**

### Testing Strategy

#### Unit Tests
```bash
# Run specific test
pytest tests/mcp/test_tool_my_tool.py -v

# Run all MCP tests
pytest tests/mcp/ -v

# Run with coverage
pytest --cov=basic_memory tests/
```

#### Integration Tests
- **API endpoints**: Full request/response cycles
- **File operations**: Real filesystem interactions
- **Cross-tool workflows**: Multi-step operations

### Debugging Techniques

#### Logging Levels
```python
import logging
logging.getLogger('basic_memory').setLevel(logging.DEBUG)
```

#### MCP Debug Mode
```bash
# Enable debug logging
export BASIC_MEMORY_LOG_LEVEL=DEBUG

# Check sync status during debugging
sync_status()
```

#### Common Issues

**MCP Server Won't Start**
- Check Python path and imports
- Verify FastMCP compatibility
- Check port availability (HTTP mode)

**Import Errors**
- Verify file paths in config
- Check file permissions
- Validate JSON/XML formats

**Search Not Working**
- Check sync status completion
- Verify index building
- Test with simple queries

**Performance Issues**
- Monitor sync status for bottlenecks
- Check file watching logs
- Profile memory usage

## API Reference

### REST Endpoints

#### Core Operations
```
GET    /api/memory          # List entities
POST   /api/memory          # Create entity
GET    /api/memory/{id}     # Get entity
PUT    /api/memory/{id}     # Update entity
DELETE /api/memory/{id}     # Delete entity
```

#### Search Operations
```
GET    /api/search?q=query     # Full-text search
GET    /api/search?type=title  # Title search
GET    /api/search?folder=path # Folder search
```

#### Project Management
```
GET    /api/projects           # List projects
POST   /api/projects           # Create project
DELETE /api/projects/{name}    # Delete project
```

### MCP Tool Interface

#### Tool Registration
```python
@mcp.tool(
    description="Human-readable description",
    name="tool_name"  # Optional, defaults to function name
)
async def tool_function(param: Type) -> ReturnType:
    # Tool documentation
    pass
```

#### Parameter Types
- **Primitives**: `str`, `int`, `bool`, `float`
- **Optional**: `Optional[Type] = None`
- **Lists**: `List[str]`, `List[Dict[str, Any]]`
- **Complex**: Pydantic models for structured data

## Performance Tuning

### Configuration Options
```toml
[tool.basic-memory]
sync_delay = 1000          # File watch debounce (ms)
max_file_size = 10485760   # 10MB limit
sync_batch_size = 100      # Files per batch
search_index_memory = 256  # MB for index
```

### Monitoring Commands
```python
# Check memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")

# Check database size
import os
db_path = "path/to/basic_memory.db"
size_mb = os.path.getsize(db_path) / 1024 / 1024
print(f"Database: {size_mb:.1f} MB")
```

## Troubleshooting Guide

### Startup Issues

**"FastMCP run_stdio_async got unexpected keyword argument"**
```bash
# Fix: Remove show_banner parameter from mcp.py
# The parameter was deprecated in newer FastMCP versions
```

**"No module named basic_memory"**
```bash
# Fix: Check Python path and virtual environment
pip install -e .
export PYTHONPATH=src
```

### Sync Issues

**"Sync stuck at 0%"**
- Check file permissions
- Verify paths exist and are readable
- Look for locked files or processes

**"Search returns no results"**
- Run `sync_status()` to check completion
- Wait for initial indexing to finish
- Check log files for indexing errors

### Import/Export Issues

**"ENEX parsing failed"**
- Verify ENEX file is valid XML
- Check file encoding (should be UTF-8)
- Try smaller files first

**"Mermaid diagrams not rendering"**
- Verify HTML export includes CDN links
- Check browser console for JavaScript errors
- Ensure diagram syntax is valid

## Extension Points

### Custom Tool Development
1. **Inherit from existing patterns**
2. **Use service layer for business logic**
3. **Follow async/await patterns**
4. **Add comprehensive error handling**

### Plugin System
- **Tool packages**: Group related functionality
- **Configuration options**: Runtime behavior customization
- **Event hooks**: Extend processing pipeline
- **API extensions**: Add new capabilities

### API Extensions
- **REST endpoints**: Add to FastAPI router
- **WebSocket support**: Real-time updates
- **GraphQL API**: Advanced queries

## Contributing Guidelines

### Code Style
```bash
# Format code
ruff format src/

# Check linting
ruff check src/

# Type checking
mypy src/
```

### Testing Requirements
- **100% coverage** for new code
- **Integration tests** for API changes
- **Performance benchmarks** for optimizations

### Documentation
- **README updates** for new features
- **CHANGELOG entries** for all changes
- **Code comments** for complex logic
- **Example usage** in docstrings

---

*This expert reference is for developers extending or troubleshooting Basic Memory. For user help, see `help("intermediate")` or `help("basic")`.*"""


def _get_semantic_net_help(level: str) -> str:
    """Get detailed help about semantic networking."""

    if level in ["basic", "intermediate"]:
        return """# Semantic Networking in Basic Memory

## What is Semantic Networking?

Semantic networking creates **meaningful connections** between your notes, building a **knowledge graph** that represents how concepts, people, projects, and ideas relate to each other.

## How It Works

### Entity Recognition
Basic Memory automatically identifies **entities** in your content:
- People: `[[John Smith]]`, `[[Dr. Sarah Johnson]]`
- Projects: `[[Project Alpha]]`, `[[Q4 Marketing Campaign]]`
- Concepts: `[[Machine Learning]]`, `[[Agile Development]]`
- Locations: `[[San Francisco]]`, `[[Headquarters Building]]`

### Relationship Building
When you mention entities in your notes, Basic Memory creates **bidirectional links**:
```
Note A mentions [[Entity X]] → Link created: A ↔ X
Note B mentions [[Entity X]] → Link created: B ↔ X
Result: A, B, and X are all connected in the knowledge graph
```

## Using Semantic Links

### Creating Links
```markdown
# My Project Update

Working with [[John Smith]] on [[Project Alpha]].
This relates to our [[Machine Learning]] initiative.
Meeting at [[San Francisco Office]].
```

### Link Benefits
- **Discovery**: Find related content automatically
- **Context**: Understand connections between topics
- **Navigation**: Jump between related concepts
- **Insights**: See how ideas interconnect

## Semantic Search

### Entity-Aware Search
```
search_notes("machine learning")  # Finds direct mentions
# Also finds: notes mentioning ML-related entities
# Plus: notes connected to ML through entity relationships
```

### Relationship Queries
```
# Find all notes related to a project
search_notes("Project Alpha")

# Find people working on specific technologies
search_notes("[[John Smith]] AND [[Machine Learning]]")
```

## Best Practices

### Consistent Naming
- Use consistent entity names across notes
- Prefer specific names over generic ones
- Example: `[[John Smith]]` not `[[the developer]]`

### Structured Content
```
# Project Meeting - [[Project Alpha]]

## Attendees
- [[John Smith]] (Lead Developer)
- [[Sarah Johnson]] (Product Manager)

## Topics
- [[Machine Learning]] model updates
- [[Q4 Roadmap]] planning

## Related
- [[Previous Meeting Notes]]
- [[Technical Specifications]]
```

### Entity Categories
- **People**: Use full names, add titles if relevant
- **Projects**: Include version numbers or phases
- **Concepts**: Use precise terminology
- **Locations**: Be specific (city, building, room)

## Advanced Features

### Observations System
Attach structured metadata to entities:
```
[[John Smith]]
- Category: person
- Role: Senior Developer
- Expertise: [[Machine Learning]], [[Python]]
```

### Relationship Types
Beyond basic links, you can specify relationship types:
- `relates_to`: General connection
- `part_of`: Hierarchical relationship
- `created_by`: Attribution
- `located_at`: Spatial relationships

## Semantic Network Benefits

### Knowledge Discovery
- **Serendipitous connections**: Find unexpected relationships
- **Gap identification**: See missing connections
- **Pattern recognition**: Understand how ideas cluster

### Content Organization
- **Automatic categorization**: Entities self-organize
- **Dynamic folders**: Virtual organization by relationships
- **Cross-cutting concerns**: Tags work across folder boundaries

### Research & Analysis
- **Impact assessment**: See how changes affect related areas
- **Dependency mapping**: Understand project interconnections
- **Knowledge mapping**: Visualize your information landscape

## Getting Started with Semantic Networking

1. **Start small**: Create 2-3 notes with entity links
2. **Be consistent**: Use the same entity names everywhere
3. **Review connections**: Use search to explore relationships
4. **Expand gradually**: Add more entities as you write
5. **Use observations**: Add metadata to important entities

The semantic network grows organically as you write, creating a rich web of knowledge that enhances both writing and discovery."""

    else:  # advanced/expert
        return """# Advanced Semantic Networking

## Graph Theory Fundamentals

### Entity-Relation Model
Basic Memory implements a **labeled property graph** where:

**Nodes (Entities):**
- Properties: title, content, type, metadata
- Labels: person, project, concept, location
- Identity: permalink-based unique identification

**Edges (Relationships):**
- Direction: bidirectional by default
- Types: `relates_to`, `part_of`, `created_by`, `located_at`
- Properties: strength, confidence, timestamp

### Graph Algorithms

#### Path Finding
```
Entity A → Entity B → Entity C
Shortest path queries for relationship discovery
```

#### Centrality Analysis
- **Degree centrality**: Most connected entities
- **Betweenness centrality**: Bridge entities
- **Closeness centrality**: Well-connected entities

#### Community Detection
- **Clustering**: Group related entities
- **Topic modeling**: Identify subject areas
- **Subgraph extraction**: Focus on specific domains

## Implementation Details

### Link Resolution Algorithm

1. **Text Parsing**: Regex-based entity extraction
   ```
   Pattern: \\[\\[([^\\]]+)\\]\\]
   Matches: [[Entity Name]], [[Project Alpha]]
   ```

2. **Normalization**: Case-insensitive matching
   ```
   "John Smith" ≡ "john smith" ≡ "JOHN SMITH"
   ```

3. **Disambiguation**: Context-aware resolution
   ```
   [[John]] in dev team → John Developer
   [[John]] in sales team → John Sales
   ```

### Relationship Inference

#### Explicit Links
```markdown
[[Entity A]] explicitly links to Entity A
```

#### Implicit Relationships
- **Co-occurrence**: Entities mentioned together
- **Contextual**: Same section, same document
- **Temporal**: Created/updated around same time

#### Transitive Closure
```
A → B and B → C implies A → C (weaker relationship)
```

## Search Integration

### Semantic Query Expansion
```
User query: "machine learning projects"
Expanded to: "machine learning OR [[ML Project]] OR [[John Smith]] OR [[AI Initiative]]"
```

### Relevance Ranking
1. **Direct matches**: Exact term matches
2. **Entity matches**: Connected entity mentions
3. **Relationship strength**: Closer connections rank higher
4. **Recency**: Newer content slightly preferred

### Faceted Search
```
Content type: entity, note, observation
Relationship type: relates_to, part_of
Entity category: person, project, concept
Time range: recent, this week, this month
```

## Performance Optimizations

### Indexing Strategy
- **Entity index**: Fast entity lookup by name
- **Relationship index**: Bidirectional edge queries
- **Content index**: Full-text search with entity awareness
- **Metadata index**: Property-based filtering

### Caching Layers
- **Entity cache**: Recently accessed entities
- **Relationship cache**: Common relationship patterns
- **Query cache**: Frequent search results
- **Graph cache**: Computed centrality measures

## API Endpoints

### Entity Operations
```
GET    /api/entities/{id}           # Get entity details
POST   /api/entities/{id}/relations # Add relationship
DELETE /api/entities/{id}/relations # Remove relationship
GET    /api/entities/{id}/related   # Get related entities
```

### Graph Operations
```
GET    /api/graph/centrality        # Entity centrality scores
GET    /api/graph/clusters          # Community detection
GET    /api/graph/shortest-path     # Path between entities
POST   /api/graph/subgraph          # Extract subgraph
```

### Search Operations
```
GET    /api/search/semantic?q=query # Semantic search
GET    /api/search/related/{id}     # Find related content
POST   /api/search/similar           # Find similar entities
```

## Development Extensions

### Custom Relationship Types
```python
@entity_relationship("collaborates_with")
def collaboration_detector(entity_a, entity_b):
    # Custom logic for detecting collaborations
    pass
```

### Plugin Architecture
```python
class SemanticPlugin:
    def extract_entities(self, content: str) -> List[Entity]:
        # Custom entity extraction
        pass

    def infer_relationships(self, entities: List[Entity]) -> List[Relationship]:
        # Custom relationship inference
        pass
```

### External Integrations
- **WikiData**: Link to external knowledge bases
- **DBpedia**: Connect to structured data
- **Custom ontologies**: Domain-specific relationship types

## Troubleshooting

### Common Issues

**Missing Relationships**
- Check entity name consistency
- Verify link syntax: `[[Entity Name]]`
- Ensure content is synced: `sync_status()`

**Incorrect Entity Resolution**
- Use more specific names
- Add disambiguation context
- Check for typos in entity names

**Performance Degradation**
- Run graph optimization: `optimize_graph()`
- Clear caches: `clear_graph_cache()`
- Rebuild indexes: `rebuild_search_index()`

### Debug Commands
```python
# Check entity relationships
debug_entity_relations("Entity Name")

# Analyze graph structure
debug_graph_stats()

# Test relationship inference
debug_relationship_inference("content text")
```"""


def _get_claude_interaction_help(level: str) -> str:
    """Get detailed help about Claude/IDE interaction."""

    if level in ["basic", "intermediate"]:
        return """# Claude Desktop Integration

## How Basic Memory Works with Claude

Basic Memory provides **seamless AI integration** through the **Model Context Protocol (MCP)**, allowing Claude to interact with your knowledge base as naturally as having a conversation.

## Core Interaction Patterns

### Direct Commands
```
"Create a note about our project architecture"
"Find information about JWT authentication"
"What do I know about coffee brewing methods?"
```

Claude translates natural language into specific tool calls:
- **Intent recognition**: Understands what you want to do
- **Parameter extraction**: Pulls details from your request
- **Tool selection**: Chooses the right Basic Memory function
- **Result interpretation**: Presents results in natural language

### Contextual Responses
Claude maintains **conversation context** and can:
- Reference previous results
- Build on prior knowledge
- Suggest related actions
- Provide guidance based on your content

## Available Tools by Category

### Content Creation & Editing
```
write_note()     - Create new notes with metadata
edit_note()      - Update existing content
delete_note()   - Remove notes
move_note()     - Reorganize content
```

### Content Discovery
```
read_note()      - Access specific notes by title/permalink
search_notes()   - Full-text search with advanced filters
list_directory() - Browse folder structure
recent_activity() - See recent changes
```

### Knowledge Networking
```
# Automatic entity linking via [[Entity Name]] syntax
# Claude can help create semantic connections:
"Link this note to the project planning documents"
"Show me all notes related to John Smith"
```

### Import & Export
```
load_obsidian_vault()    - Import from Obsidian
load_joplin_vault()      - Import from Joplin
load_notion_export()     - Import from Notion
load_evernote_export()   - Import from Evernote
export_html_notes()      - Export with Mermaid diagrams
```

### Rich Editing
```
edit_in_typora()     - Export for professional editing
import_from_typora() - Import edited content back
```

## Effective Claude Interaction

### Natural Language Commands
**Good examples:**
```
✅ "Create a note about the new API endpoints"
❌ "Make a note or something about APIs"
```

**Claude will:**
- Extract key information
- Choose appropriate tools
- Format content properly
- Suggest additional actions

### Multi-Step Workflows
Claude can handle complex, multi-step tasks:
```
"Import my Obsidian vault, then create an overview of all projects"
1. Run import tool
2. Search for project-related content
3. Generate summary note
4. Suggest organization improvements
```

### Error Handling & Recovery
If something goes wrong, Claude will:
- Explain what happened
- Suggest fixes or alternatives
- Provide specific commands to run
- Guide you through troubleshooting

## Advanced Features

### Context Awareness
Claude remembers your conversation and can:
- Reference previous searches or notes
- Build on established context
- Make connections across topics
- Provide personalized suggestions

### Proactive Assistance
Claude can suggest improvements:
- "You might want to link this to your existing project notes"
- "This seems related to your research on topic X"
- "Would you like me to create a summary diagram?"

### Template Generation
Claude helps create structured content:
- Meeting notes with standard sections
- Project plans with checklists
- Research summaries with key findings
- Code documentation with examples

## Best Practices

### Clear Intent Communication
```
✅ "Search my notes for information about React hooks"
❌ "Find stuff about React"
```

### Specific Context
```
✅ "Create a summary of the project status"
❌ "Tell me about the project"
```

### Iterative Refinement
```
You: "Find notes about project planning"
Claude: [shows results]
You: "Now create a summary of the key milestones"
Claude: [creates summary based on found notes]
```

## Troubleshooting

### Tool Not Working
```
sync_status()  # Check if system is ready
# Claude will help interpret results
```

### Search Not Finding Content
```
"Try searching with different keywords"
"Check if the content is in a different folder"
"Use broader or more specific search terms"
```

### Import Issues
```
"Check the file format and path"
"Try importing a smaller file first"
"Verify the export was created correctly"
```

## Integration Benefits

### Accelerated Workflow
- **Instant knowledge access** without switching apps
- **Natural interaction** feels like having an assistant
- **Context preservation** across conversations
- **Multi-tool coordination** for complex tasks

### Enhanced Productivity
- **Faster content creation** with AI assistance
- **Better organization** through semantic linking
- **Improved discovery** via intelligent search
- **Professional output** with rich formatting

### Knowledge Management
- **Living documentation** that evolves with you
- **Connected thinking** across all your content
- **AI-enhanced insights** from your knowledge graph
- **Future-proof storage** in open formats

The combination of Basic Memory's structured knowledge base with Claude's natural language understanding creates a powerful system for **thinking, writing, and discovering** that enhances both human and AI capabilities."""

    else:  # advanced/expert
        return """# Advanced Claude Integration Architecture

## MCP Protocol Deep Dive

### Tool Discovery & Registration

#### Dynamic Tool Loading
```python
# In basic_memory/mcp/tools/__init__.py
@mcp.tool(description="Tool description")
async def tool_name(params) -> Result:
    # Tool implementation
    return result

# Tools auto-registered with FastMCP server
# Claude discovers capabilities at connection time
```

#### Tool Metadata
- **Descriptions**: Human-readable explanations
- **Parameters**: Type hints and validation
- **Examples**: Usage patterns in docstrings
- **Error handling**: Comprehensive failure modes

### Context Management

#### Session State
- **Conversation history**: Previous tool calls and results
- **Project context**: Current active project
- **User preferences**: Search settings, display options
- **Temporary state**: Multi-step operation progress

#### State Synchronization
- **Project switching**: Context updates on project change
- **Sync status awareness**: Tool availability based on system state
- **Error state handling**: Recovery suggestions and alternatives

### AI Interaction Layers

#### Natural Language Processing
1. **Intent Classification**: Map user requests to tool calls
   ```
   "find my notes about coffee" → search_notes(query="coffee")
   "create a meeting summary" → write_note(title="Meeting Summary", ...)
   ```

2. **Parameter Extraction**: Pull structured data from text
   ```
   "notes about the React project in docs folder"
   → search_notes(query="React", folder="docs/")
   ```

3. **Context Integration**: Use conversation history
   ```
   Previous: search_notes(query="project")
   Current: "show me the first result"
   → read_note("first-result-permalink")
   ```

#### Tool Orchestration
- **Sequential execution**: Multi-step workflows
- **Parallel processing**: Independent operations
- **Error recovery**: Alternative approaches on failure
- **Result synthesis**: Combine multiple tool outputs

## Performance Optimization

### Caching Strategies
- **Tool results**: Cache frequent queries
- **Metadata**: Pre-load commonly accessed data
- **Search indexes**: Optimize for AI query patterns
- **Context state**: Maintain session efficiency

### Async Processing
```python
# All tools are async for non-blocking operation
@mcp.tool()
async def search_notes(query: str) -> SearchResponse:
    # Async database queries
    # Async file operations
    # Async API calls
    return await perform_search(query)
```

### Resource Management
- **Connection pooling**: Database connection reuse
- **Memory limits**: Large result set pagination
- **Timeout handling**: Prevent hanging operations
- **Background processing**: Long-running tasks

## Error Handling & Recovery

### Tool Failure Modes
```python
try:
    result = await tool_call(params)
except ValidationError:
    # Parameter validation failed
    return suggest_corrections()
except PermissionError:
    # Access denied
    return request_permissions()
except NetworkError:
    # API call failed
    return retry_with_backoff()
```

### User-Friendly Error Messages
- **Context-aware**: Explain what went wrong and why
- **Actionable**: Provide specific next steps
- **Alternative suggestions**: Offer different approaches
- **Help references**: Point to relevant documentation

## Advanced AI Features

### Proactive Suggestions
- **Content recommendations**: Related notes and entities
- **Workflow optimization**: Better ways to organize
- **Missing connections**: Suggest new relationships
- **Quality improvements**: Writing and structure suggestions

### Learning & Adaptation
- **Usage patterns**: Learn preferred tools and workflows
- **Context preferences**: Remember project-specific settings
- **Search refinement**: Improve results based on feedback
- **Template generation**: Create personalized content structures

## Development Integration

### IDE Tooling
- **Inline completions**: Suggest tool calls while typing
- **Parameter hints**: Show available options and types
- **Result preview**: Display tool outputs in editor
- **Debug integration**: Step through tool execution

### API Compatibility
- **Version awareness**: Handle API changes gracefully
- **Feature detection**: Adapt to available capabilities
- **Fallback modes**: Work with limited functionality
- **Update notifications**: Alert to new features

## Security & Privacy

### Data Protection
- **Local processing**: All data stays on user's machine
- **No external calls**: Knowledge base never leaves device
- **Access control**: Project and file permission respect
- **Audit logging**: Track all operations for transparency

### Safe Execution
- **Input validation**: All parameters thoroughly checked
- **Path sanitization**: Prevent directory traversal attacks
- **Resource limits**: Prevent abuse of system resources
- **Error isolation**: Failures don't compromise other operations

## Extensibility

### Custom Tool Development
```python
@mcp.tool(description="My custom tool")
async def my_custom_tool(input: str) -> str:
    # Custom logic here
    return process_input(input)

# Tool automatically available to Claude
# No server restart required
```

### Plugin System
- **Tool packages**: Group related functionality
- **Configuration options**: Runtime behavior customization
- **Event hooks**: Extend processing pipeline
- **API extensions**: Add new capabilities

## Monitoring & Analytics

### Usage Metrics
- **Tool call frequency**: Most used capabilities
- **Success rates**: Tool reliability tracking
- **Performance metrics**: Response time analysis
- **Error patterns**: Common failure modes

### Debug Information
```python
# Enable debug mode
set_log_level("DEBUG")

# View tool execution traces
debug_tool_calls()

# Analyze conversation patterns
analyze_interactions()
```

## Future Enhancements

### Advanced AI Integration
- **Multi-modal input**: Images, audio, documents
- **Conversational memory**: Long-term context retention
- **Collaborative features**: Multi-user knowledge sharing
- **Smart automation**: Workflow creation and execution

### Enhanced Capabilities
- **Voice interaction**: Natural speech interfaces
- **Visual knowledge maps**: Graph visualization
- **Predictive suggestions**: Anticipate user needs
- **Cross-system integration**: Connect with other tools

This advanced integration creates a **symbiotic relationship** between human knowledge work and AI assistance, where each enhances the capabilities of the other."""


def _get_tools_help(level: str) -> str:
    """Get comprehensive tools reference."""

    return """# Basic Memory Tools Reference

## Complete Command Reference

### Core Note Operations

#### write_note(title, content, folder, tags)
Create new notes with automatic metadata handling.
```
Parameters:
- title: Note title (auto-sanitized for filenames)
- content: Markdown content
- folder: Optional folder path
- tags: Optional list of tags

Examples:
write_note("Meeting Notes", "# Meeting with Team\\nDiscussed Q4 goals...")
write_note("Project Plan", content, folder="projects/alpha", tags=["urgent"])
```

#### read_note(identifier, page, page_size, project)
Read notes by title, permalink, or search.
```
Parameters:
- identifier: Title, permalink, or search term
- page: Pagination page (default: 1)
- page_size: Items per page (default: 10)
- project: Optional project override

Examples:
read_note("Meeting Notes")
read_note("projects/plan")
read_note("memory://notes/meeting")
```

#### edit_note(identifier, content)
Update existing note content.
```
Parameters:
- identifier: Note to edit (title/permalink)
- content: New markdown content

Examples:
edit_note("Meeting Notes", "# Updated Meeting\\nNew content...")
```

#### delete_note(identifier)
Remove notes from the knowledge base.
```
Parameters:
- identifier: Note to delete

Examples:
delete_note("Old Meeting Notes")
```

### Search & Discovery

#### search_notes(query, page, page_size, search_type, types, entity_types, after_date, project)
Full-text search across all content with advanced filters.
```
Parameters:
- query: Search terms with boolean operators
- page: Result page (default: 1)
- page_size: Results per page (default: 10)
- search_type: "text", "title", "permalink" (default: "text")
- types: Content types to search
- entity_types: Entity categories to filter
- after_date: Date filter (ISO format or relative)
- project: Optional project override

Examples:
search_notes("machine learning")
search_notes("meeting AND project", search_type="title")
search_notes("docs/*", search_type="permalink")
search_notes("urgent", types=["entity"], after_date="1 week")
```

#### recent_activity(timeframe, project)
View recent content changes and activity.
```
Parameters:
- timeframe: Time period ("7d", "1 week", "2024-01-01")
- project: Optional project override

Examples:
recent_activity()
recent_activity("7d")
recent_activity("1 month")
```

#### list_directory(path, project)
Browse folder structure and contents.
```
Parameters:
- path: Folder path to list
- project: Optional project override

Examples:
list_directory("/")
list_directory("notes/")
list_directory("projects/alpha")
```

### Import Ecosystem

#### Obsidian Integration
```
load_obsidian_vault("path/to/vault", folder="obsidian-import")
# Import entire Obsidian vaults with link conversion

load_obsidian_canvas("canvas.json", folder="canvas-import")
# Import visual canvas files as structured notes

search_obsidian_vault("vault/path", "query", file_type="markdown")
# Search through external Obsidian exports
```

#### Joplin Integration
```
load_joplin_vault("path/to/export", folder="joplin-import")
# Import Joplin exports with metadata preservation

export_joplin_notes("output/path", folder="notes-to-export")
# Export notes in Joplin-compatible format

search_joplin_vault("export/path", "query", file_type="json")
# Search through external Joplin exports
```

#### Notion Integration
```
load_notion_export("notion-export.zip", preserve_hierarchy=True)
# Import Notion HTML/Markdown exports

export_notion_compatible("output/", notebook_name="Imported Notes")
# Export as Notion-compatible markdown

search_notion_vault("export/path", "query", file_type="html")
# Search through external Notion exports
```

#### Evernote Integration
```
load_evernote_export("notes.enex", preserve_notebooks=True, include_attachments=True)
# Import Evernote ENEX files with attachment extraction

export_evernote_compatible("output/", notebook_name="Exported Notes")
# Export as Evernote ENEX XML format

search_evernote_vault("export/path", "query", file_type="enex")
# Search through external Evernote exports
```

## Export Capabilities

### Web Publishing
```
export_html_notes("site/", folder="docs/")
# Export as HTML with live Mermaid diagram rendering

export_docsify("docs-site/")
# Create Docsify documentation sites
```

### Cross-Platform
```
export_joplin_notes("joplin/")
# Export in Joplin format for cross-platform use

export_notion_compatible("notion/")
# Export as Notion-compatible markdown

export_evernote_compatible("enex/")
# Export as Evernote ENEX XML
```

## Rich Editing

### Typora Integration
```
edit_in_typora("note-title", workspace="edits")
# Export note for professional editing in Typora

import_from_typora("note-title", workspace="edits")
# Import edited content back into Basic Memory
```

## Project Management

### Multi-Project Support
```
list_memory_projects()
# View all configured projects

switch_project("project-name")
# Change active project context

create_memory_project("name", "path", set_default)
# Create new project workspace

delete_project("name")
# Remove project configuration
```

### System Administration
```
sync_status(project)
# Check file synchronization progress

get_current_project()
# Display current project information

set_default_project(name)
# Set default project for new sessions
```

### System & Status Tools
```
status(level, focus)
# Comprehensive system status and diagnostics

help(level, topic)
# Detailed help and system information
```

## Tool Categories Summary

### Core Tools: 4 tools
- write_note, read_note, edit_note, delete_note

### Search & Discovery: 3 tools
- search_notes, recent_activity, list_directory

### Import Tools: 4 tools
- load_obsidian_vault, load_joplin_vault, load_notion_export, load_evernote_export

### Export Tools: 5 tools
- export_html_notes, export_docsify, export_joplin_notes, export_notion_compatible, export_evernote_compatible

### Search Tools: 4 tools
- search_obsidian_vault, search_joplin_vault, search_notion_vault, search_evernote_vault

### Editing Tools: 2 tools
- edit_in_typora, import_from_typora

### Project Tools: 5 tools
- list_memory_projects, switch_project, get_current_project, create_memory_project, delete_project, set_default_project

### System Tools: 2 tools
- sync_status, status, help

**Total: 31 tools** across 7 major categories, supporting comprehensive knowledge management workflows."""


def _get_import_export_help(level: str) -> str:
    """Get detailed import/export help."""

    return """# Import/Export Ecosystem in Basic Memory

## Supported Platforms & Formats

### Obsidian Integration
**Primary Format**: Markdown files with wikilinks
**Secondary**: Canvas files (JSON-based visual notes)

#### Import Capabilities
```
load_obsidian_vault("path/to/vault", folder="obsidian-archive")
# - Converts [[WikiLinks]] to Basic Memory entity links
# - Preserves folder structure
# - Handles frontmatter metadata
# - Supports image and attachment references

load_obsidian_canvas("canvas.json", folder="canvas-import")
# - Converts visual canvas nodes to structured notes
# - Preserves node connections as entity relationships
# - Handles different node types (text, files, links)
```

#### Export Options
```
# Export back to Obsidian format using standard markdown export
# Use export_html_notes() for web-viewable versions
```

#### Search Integration
```
search_obsidian_vault("vault/path", "query", file_type="markdown")
# Search through exported Obsidian content
# Supports both .md and .canvas files
# Filters by file type and content
```

### Joplin Integration
**Primary Format**: JSON metadata + Markdown content
**Structure**: Notebooks, notes, tags, attachments

#### Import Capabilities
```
load_joplin_vault("path/to/joplin-export", folder="joplin-archive")
# - Preserves notebook hierarchy as folders
# - Converts Joplin metadata to Basic Memory format
# - Handles tags and note properties
# - Supports rich text and attachments
```

#### Export Capabilities
```
export_joplin_notes("output/path", folder="notes-to-export")
# - Generates Joplin-compatible JSON + Markdown pairs
# - Preserves folder structure as notebooks
# - Includes metadata and tags
# - Ready for Joplin import
```

#### Search Integration
```
search_joplin_vault("export/path", "meeting notes", file_type="json")
# Search through Joplin export files
# Supports both metadata and content search
# Filters by notebook and tags
```

### Notion Integration
**Primary Format**: HTML exports (most comprehensive)
**Secondary**: Markdown exports (simpler)

#### Import Capabilities
```
load_notion_export("notion-export.zip", preserve_hierarchy=True)
# - Parses complex Notion HTML structure
# - Converts Notion blocks to markdown
# - Preserves page hierarchy and internal links
# - Handles databases and page properties
# - Extracts attachments and media
```

#### Export Capabilities
```
export_notion_compatible("output/", notebook_name="My Knowledge Base")
# - Generates clean markdown for Notion import
# - Preserves entity relationships as links
# - Includes frontmatter metadata
# - Compatible with Notion's import feature
```

#### Search Integration
```
search_notion_vault("export/path", "project status", file_type="html")
# Search through Notion HTML and Markdown exports
# Handles complex HTML structure
# Filters by notebooks and tags
```

### Evernote Integration
**Primary Format**: ENEX XML (Evernote's native export)
**Structure**: Notes with rich content and metadata

#### Import Capabilities
```
load_evernote_export("notes.enex", preserve_notebooks=True, include_attachments=True)
# - Parses ENEX XML format
# - Converts HTML content to clean markdown
# - Preserves notebooks, tags, and creation dates
# - Extracts base64-encoded attachments
# - Handles rich formatting and media
```

#### Export Capabilities
```
export_evernote_compatible("output/", notebook_name="Exported Notes")
# - Generates valid ENEX XML format
# - Preserves metadata and relationships
- Compatible with Evernote import
- Includes structured content sections
```

#### Search Integration
```
search_evernote_vault("export/path", "research notes", file_type="enex")
# Search through ENEX XML files
# Handles XML structure and metadata
# Filters by notebooks and tags
```

## Export Formats & Use Cases

### HTML Export with Mermaid
```
export_html_notes("site/", folder="docs/")
# - Generates standalone HTML pages
# - Renders Mermaid diagrams live
# - Includes navigation and styling
# - Perfect for documentation websites
# - Self-contained, no server required
```

### Docsify Documentation Sites
```
export_docsify("docs-site/")
# - Creates Docsify-compatible structure
# - Generates _sidebar.md for navigation
# - Includes index.html with Docsify setup
# - Supports search and themes
# - Requires web server for full functionality
```

### Cross-Platform Migration
```
# Export from Basic Memory to other tools
export_joplin_notes("migration/joplin/")
export_notion_compatible("migration/notion/")
export_evernote_compatible("migration/evernote/")

# Then import into target applications
```

## Data Preservation & Compatibility

### Content Fidelity
- **Markdown**: Preserved with full formatting
- **Links**: Converted between platform formats
- **Metadata**: Tags, dates, authors maintained
- **Structure**: Folders/notebooks preserved
- **Media**: Attachments and images handled

### Format Conversion
- **Obsidian wikilinks** → Basic Memory entity links
- **Joplin notebooks** → Basic Memory folders
- **Notion pages** → Basic Memory entities
- **Evernote notes** → Basic Memory markdown

### Relationship Mapping
- **Explicit links** preserved across platforms
- **Implicit connections** may need re-establishment
- **Cross-references** converted to appropriate syntax
- **Semantic relationships** maintained where possible

## Best Practices

### Import Strategy
1. **Selective export**: Don't export entire databases at once
2. **Test import**: Start with small subsets first
3. **Verify content**: Check imported content integrity
4. **Rebuild links**: Add semantic connections as needed

### Export Workflows
1. **Choose target format** based on use case
2. **Filter content** to avoid information overload
3. **Test import** in target application
4. **Maintain sync** if using multiple tools

### Hybrid Usage
- **Basic Memory as primary**: Enhanced features and AI integration
- **Other tools as secondary**: Specific use cases (mobile, sharing)
- **Regular sync**: Export/import to maintain consistency
- **Selective sharing**: Export only relevant content

## Troubleshooting Import/Export

### Common Import Issues
- **File encoding**: Ensure UTF-8 compatibility
- **Path separators**: Handle cross-platform paths
- **Special characters**: Check filename sanitization
- **Large files**: Split large exports if needed

### Export Compatibility
- **Target app versions**: Check supported import formats
- **File size limits**: Respect application constraints
- **Special formatting**: Verify rich content conversion
- **Link preservation**: Test cross-references work

### Performance Considerations
- **Large imports**: May take time for processing
- **Memory usage**: Monitor for large file operations
- **Disk space**: Account for attachment extraction
- **Sync delays**: Allow time for indexing completion

The import/export ecosystem makes Basic Memory a **universal knowledge hub**, allowing seamless movement of content between different tools while maintaining the richest feature set available."""


def _get_typora_help(level: str) -> str:
    """Get detailed Typora integration help."""

    return """# Typora Integration in Basic Memory

## What is Typora Integration?

Typora provides **professional rich-text editing** for markdown files. The Basic Memory integration creates a **round-trip workflow** allowing you to:

- Export notes from Basic Memory for editing in Typora
- Edit with full WYSIWYG (What You See Is What You Get) features
- Import the edited content back into Basic Memory
- Preserve all formatting, links, and metadata

## Core Workflow

### Step 1: Export for Editing
```
edit_in_typora("My Note Title", workspace="current-edits")
```
This creates a temporary markdown file in your workspace and opens it in Typora.

### Step 2: Edit in Typora
- Full rich text editing capabilities
- Live preview of markdown formatting
- Table editing, code blocks, math expressions
- Image insertion and management
- Link creation and management

### Step 3: Import Changes Back
```
import_from_typora("My Note Title", workspace="current-edits")
```
This reads the edited file and updates the note in Basic Memory.

## Detailed Commands

### Export to Typora
```
edit_in_typora(identifier, workspace="edits")
```
**Parameters:**
- `identifier`: Note title or permalink to edit
- `workspace`: Folder for temporary files (default: "typora-workspace")

**What it does:**
1. Finds the note in Basic Memory
2. Creates a temporary markdown file
3. Opens the file in Typora (if installed)
4. Creates backup of original content

**Example:**
```python
edit_in_typora("Meeting Notes", workspace="weekly-meetings")
# Creates: weekly-meetings/Meeting Notes.md
# Opens in Typora for editing
```

### Import from Typora
```
import_from_typora(identifier, workspace="edits")
```
**Parameters:**
- `identifier`: Note title or permalink to update
- `workspace`: Folder containing edited files

**What it does:**
1. Reads the edited markdown file
2. Updates the note in Basic Memory
3. Preserves all metadata and relationships
4. Cleans up temporary files (optional)

**Example:**
```python
import_from_typora("Meeting Notes", workspace="weekly-meetings")
# Updates note with edited content
# Preserves creation date, tags, etc.
```

## Workspace Management

### Organizing Edit Sessions
```
# Create workspaces for different projects
edit_in_typora("Project Plan", workspace="q4-planning")
edit_in_typora("Budget Review", workspace="q4-planning")

# Import all changes at once
import_from_typora("Project Plan", workspace="q4-planning")
import_from_typora("Budget Review", workspace="q4-planning")
```

### Cleanup Options
- **Automatic**: Temporary files removed after import
- **Manual**: Keep files for reference or further editing
- **Backup**: Original content always preserved

## Typora Features Available

### Rich Text Editing
- **Live Preview**: See formatted output as you type
- **Syntax Highlighting**: Code blocks with language support
- **Table Editing**: Click and edit tables directly
- **Math Expressions**: LaTeX math rendering
- **Emoji Support**: Visual emoji picker

### Advanced Formatting
- **Headers**: Multiple levels with auto-numbering
- **Lists**: Bulleted, numbered, and task lists
- **Blockquotes**: Multi-level quotation formatting
- **Code Blocks**: Syntax highlighting and line numbers
- **Links**: Easy URL and reference link creation

### Media & Attachments
- **Image Insertion**: Drag-and-drop or paste images
- **Image Resizing**: Visual resize handles
- **Alt Text**: Accessibility support
- **Figure Captions**: Image descriptions

## Integration Benefits

### Professional Editing Experience
- **Distraction-free writing** with clean interface
- **Immediate visual feedback** on formatting
- **Advanced typography** and layout options
- **Cross-platform consistency** (works on all OS)

### Workflow Efficiency
- **Round-trip editing** without format loss
- **Batch editing** of multiple notes
- **Workspace organization** for complex editing sessions
- **Version control integration** with Git

### Content Quality
- **Better formatting** with visual editing
- **Consistent styling** across documents
- **Professional presentation** for shared content
- **Accessibility improvements** with proper markup

## Use Cases

### Documentation Writing
1. Create initial outline in Basic Memory
2. Export to Typora for detailed writing
3. Use advanced formatting features
4. Import back with professional styling

### Meeting Notes
1. Start with basic notes during meeting
2. Export to Typora for cleanup and formatting
3. Add tables, code snippets, action items
4. Import polished version

### Technical Writing
1. Write technical content in Basic Memory
2. Use Typora for equation editing and code formatting
3. Add diagrams and complex formatting
4. Maintain in Basic Memory with enhanced presentation

### Content Review
1. Export content for stakeholder review
2. Use Typora's clean presentation
3. Make collaborative edits
4. Import approved versions

## Best Practices

### File Organization
```
# Use descriptive workspace names
edit_in_typora("API Documentation", workspace="api-v2-docs")

# Group related edits
workspace/
├── api-v2-docs/
│   ├── API Documentation.md
│   ├── Authentication Guide.md
│   └── Error Handling.md
```

### Content Workflow
1. **Draft in Basic Memory**: Capture ideas quickly
2. **Edit in Typora**: Polish formatting and structure
3. **Review and refine**: Make final adjustments
4. **Import back**: Preserve in Basic Memory

### Version Control
- **Commit before export**: Track original state
- **Backup important content**: Before major edits
- **Review changes**: Compare before/after versions
- **Document edits**: Note significant changes

## Troubleshooting

### Typora Not Opening
```
# Check Typora installation
# Verify file associations
# Try opening file manually first
edit_in_typora("note", workspace="test")
```

### Import Fails
```
# Check workspace path exists
# Verify file was edited and saved
# Ensure note still exists in Basic Memory
import_from_typora("note", workspace="test")
```

### Formatting Issues
- **Markdown compatibility**: Typora uses standard markdown
- **Special characters**: Check encoding is UTF-8
- **Complex formatting**: Some advanced features may not translate perfectly

### Performance
- **Large files**: May be slow to open in Typora
- **Many images**: Can impact editing performance
- **Complex tables**: May require manual adjustment

## Advanced Features

### Custom Workflows
```python
# Create editing pipeline
notes_to_edit = ["Doc1", "Doc2", "Doc3"]
workspace = "bulk-edit-session"

for note in notes_to_edit:
    edit_in_typora(note, workspace=workspace)

# Edit all files in Typora
# Then import all changes
for note in notes_to_edit:
    import_from_typora(note, workspace=workspace)
```

### Integration with Other Tools
- **Export after editing**: Create HTML or PDF versions
- **Version control**: Track changes in Git
- **Collaboration**: Share edited files for review
- **Publishing**: Export to other formats

## Comparison: Typora vs Basic Memory Editor

| Feature | Basic Memory | Typora |
|---------|--------------|---------|
| **Speed** | Fast capture | Rich editing |
| **Formatting** | Markdown syntax | Visual editing |
| **Links** | Entity references | Standard links |
| **Tables** | Markdown tables | Visual table editor |
| **Images** | Reference links | Inline insertion |
| **Math** | LaTeX support | Live rendering |
| **Collaboration** | AI-assisted | Visual review |

**Best Practice**: Use both - Basic Memory for knowledge networking, Typora for presentation polish."""


def _get_obsidian_help(level: str) -> str:
    """Get detailed Obsidian integration help."""

    return """# Obsidian Integration in Basic Memory

## Obsidian Overview

Obsidian is a powerful **note-taking app** that pioneered **bidirectional linking** and **graph visualization**. It uses markdown files with wikilinks (`[[Note Title]]`) and provides extensive plugin ecosystem.

## Basic Memory's Obsidian Integration

Basic Memory provides **comprehensive Obsidian compatibility** with enhanced features:

### Import Capabilities
- **Vault Import**: Full vault structure preservation
- **Link Conversion**: Wikilinks become entity relationships
- **Canvas Support**: Visual canvas files as structured notes
- **Metadata Handling**: Frontmatter and inline metadata

### Export Options
- **Markdown Export**: Standard markdown compatible with Obsidian
- **HTML Export**: Web-viewable versions with Mermaid diagrams
- **Search Integration**: Query external Obsidian content

## Detailed Import Process

### Vault Import
```
load_obsidian_vault("path/to/obsidian-vault", folder="obsidian-archive")
```

**What it does:**
1. **Scans vault structure**: Finds all markdown files
2. **Preserves folders**: Maintains directory hierarchy
3. **Converts wikilinks**: `[[Note Title]]` → Basic Memory entity links
4. **Handles frontmatter**: YAML metadata preserved
5. **Processes attachments**: Images and files referenced correctly

**Advanced options:**
```
load_obsidian_vault(
    "vault/path",
    folder="imported-notes",
    convert_links=True  # Convert wikilinks to entity references
)
```

### Canvas Import
```
load_obsidian_canvas("canvas-file.canvas", folder="canvas-imports")
```

**Canvas structure conversion:**
- **Text nodes** → Individual notes with content
- **File nodes** → References to existing content
- **Link nodes** → Entity relationships
- **Group nodes** → Folder organization

## Link Conversion Examples

### Wikilink Conversion
```
Obsidian: [[Project Alpha]] and [[Meeting Notes]]
Basic Memory: Automatic entity linking with relationships
```

### File References
```
Obsidian: ![Image](attachments/image.png)
Basic Memory: Preserved with correct relative paths
```

### Frontmatter Handling
```yaml
# Obsidian frontmatter preserved
---
tags: [project, urgent]
created: 2024-01-15
aliases: [Project Plan, Q4 Goals]
---

# Project Alpha
Content here...
```

## Search Integration

### External Vault Search
```
search_obsidian_vault("vault/path", "machine learning")
```

**Features:**
- **Full-text search** across all vault files
- **File type filtering**: Markdown, canvas, or all
- **Case sensitivity** options
- **Result limiting** for performance

**Advanced search:**
```
search_obsidian_vault(
    "vault/path",
    "project planning",
    file_type="markdown",
    case_sensitive=False,
    max_results=50
)
```

## Migration Strategies

### Complete Vault Migration
```
1. Export entire Obsidian vault
2. load_obsidian_vault("vault-backup")
3. Verify import with search_notes("vault-backup")
4. Continue using Basic Memory features
```

### Selective Import
```
1. Export specific folders from Obsidian
2. Import only needed content
3. Rebuild semantic links in Basic Memory
4. Use search to verify relationships
```

### Hybrid Workflow
```
1. Keep Obsidian for daily notes and linking
2. Use Basic Memory for AI-enhanced features
3. Sync important content between systems
4. Leverage Basic Memory's export capabilities
```

## Feature Comparison

### Linking Systems

| Feature | Obsidian | Basic Memory |
|---------|----------|--------------|
| **Link Syntax** | `[[Note Title]]` | `[[Entity Name]]` |
| **Bidirectional** | ✅ Manual graph | ✅ Automatic |
| **Transclusion** | ✅ Embed content | ❌ (by design) |
| **Graph View** | ✅ Visual | ✅ Mermaid diagrams |
| **Link Types** | Basic | Typed relationships |

### Content Features

| Feature | Obsidian | Basic Memory |
|---------|----------|--------------|
| **Plugins** | 500+ community | Built-in AI integration |
| **Themes** | Extensive | Clean, focused |
| **Mobile App** | ✅ Native | ❌ (web-first) |
| **Collaboration** | Limited | AI-assisted |
| **Search** | Full-text + links | Semantic + AI-enhanced |

## Best Practices

### Content Organization
- **Consistent naming**: Use same entity names across notes
- **Folder structure**: Logical hierarchy for discoverability
- **Tag system**: Complement folders with categorization
- **Link liberally**: Connect related concepts

### Migration Tips
1. **Start with test import**: Small vault section first
2. **Preserve links**: Use convert_links=True
3. **Verify relationships**: Check entity connections
4. **Rebuild as needed**: Add missing semantic links

### Workflow Integration
- **Obsidian for capture**: Fast note-taking and linking
- **Basic Memory for enhancement**: AI features and advanced search
- **Export for sharing**: HTML versions with diagrams
- **Regular sync**: Move content between systems

## Troubleshooting

### Import Issues

**Links not converting:**
```
# Check convert_links parameter
# Verify consistent naming
# Some links may need manual adjustment
load_obsidian_vault("vault", convert_links=True)
```

**Missing attachments:**
```
# Ensure relative paths are correct
# Check file permissions
# Verify attachment folder structure
```

**Encoding problems:**
```
# Obsidian uses UTF-8
# Check for special characters
# Some files may need manual review
```

### Search Problems

**No results found:**
```
# Check vault path is correct
# Verify file permissions
# Try different search terms
search_obsidian_vault("path", "test query")
```

**Performance issues:**
```
# Large vaults may be slow
# Use file_type filter to narrow search
# Limit max_results for faster queries
```

## Advanced Usage

### Canvas Workflow
1. **Create visual maps** in Obsidian Canvas
2. **Import to Basic Memory** as structured notes
3. **Enhance with AI** to add content and relationships
4. **Export as documentation** with Mermaid diagrams

### Plugin Integration
- **Dataview**: Structured data queries
- **Kanban**: Project management boards
- **Excalidraw**: Visual diagrams
- **Templates**: Consistent note structures

### Sync Strategies
- **Periodic export**: Move content regularly
- **Selective sync**: Important notes only
- **Bidirectional**: Manual sync when needed
- **Archive old**: Keep historical content accessible

## Compatibility Notes

### Obsidian Evolution
- **Core features stable**: Linking and markdown foundation
- **Plugin ecosystem**: Rapidly expanding
- **Mobile improvements**: Better cross-device sync

### Basic Memory Advantages
- **AI integration**: Claude Desktop connectivity
- **Rich export options**: Multiple output formats
- **Semantic networking**: Automatic relationship discovery
- **Professional editing**: Typora integration

The integration allows you to **leverage both tools' strengths**: Obsidian's flexible linking and Basic Memory's AI-enhanced knowledge management."""


def _get_joplin_help(level: str) -> str:
    """Get detailed Joplin integration help."""

    return """# Joplin Integration in Basic Memory

## Joplin Overview

Joplin is a **free, open-source note-taking app** that works across all platforms. It uses markdown with rich features and provides **end-to-end encryption** for privacy-focused users.

## Key Features
- **Cross-platform**: Windows, macOS, Linux, Android, iOS
- **End-to-end encryption**: Privacy-focused architecture
- **Rich markdown**: Tables, math, code highlighting
- **Plugin ecosystem**: Extensible functionality
- **Web clipper**: Save web content easily

## Basic Memory Integration

### Import from Joplin
```
load_joplin_vault("path/to/joplin-export", folder="joplin-archive")
```

**What it processes:**
- **JSON metadata files**: Note properties and structure
- **Markdown content**: Full formatting preservation
- **Notebook hierarchy**: Converted to folder structure
- **Tags and metadata**: Preserved in Basic Memory
- **Attachments**: Images and files extracted

### Export to Joplin
```
export_joplin_notes("output/path", folder="notes-to-export")
```

**What it creates:**
- **JSON + Markdown pairs**: Joplin's native format
- **Notebook structure**: Folders become notebooks
- **Metadata preservation**: Tags, dates, relationships
- **Ready for import**: Direct Joplin compatibility

### Search Integration
```
search_joplin_vault("export/path", "meeting notes", file_type="json")
```

**Search capabilities:**
- **Metadata search**: Title, notebook, tags
- **Content search**: Full-text across markdown
- **Type filtering**: JSON metadata or markdown content
- **Structured results**: Organized by notebook and type

## Detailed Workflow

### Migration from Joplin

#### Step 1: Export from Joplin
1. Open Joplin desktop application
2. Go to **File** → **Export** → **JSON**
3. Choose notebooks to export
4. Save to a folder

#### Step 2: Import to Basic Memory
```
load_joplin_vault("joplin-export-folder", folder="joplin-archive")
```

#### Step 3: Verify Import
```
search_notes("joplin-archive")  # Check imported content
list_directory("joplin-archive")  # Browse structure
```

#### Step 4: Enhance Content
- Add semantic links between related notes
- Use AI assistance for content improvement
- Create Mermaid diagrams for complex relationships

### Export to Joplin

#### Use Case: Mobile Access
```
# Keep primary notes in Basic Memory
export_joplin_notes("mobile-sync", folder="current-projects")
# Import to Joplin mobile app for offline access
```

#### Use Case: Team Sharing
```
# Export documentation for team
export_joplin_notes("team-docs", folder="project-docs")
# Team members can import into their Joplin instances
```

## Data Structure Mapping

### Joplin → Basic Memory

| Joplin Concept | Basic Memory Equivalent |
|----------------|------------------------|
| **Note** | Entity with markdown content |
| **Notebook** | Folder |
| **Sub-notebook** | Subfolder |
| **Tag** | Tag metadata |
| **Attachment** | File reference |
| **Todo items** | Task lists in markdown |

### Basic Memory → Joplin

| Basic Memory | Joplin Export |
|--------------|---------------|
| **Entity** | JSON metadata + Markdown file |
| **Folder** | Notebook structure |
| **Tags** | Joplin tags |
| **Relations** | Links in content |
| **Observations** | Structured metadata |

## Advanced Features

### Encryption Handling
- **Export decrypted**: Joplin exports are unencrypted
- **Security note**: Ensure secure handling of sensitive content
- **Re-encryption**: Re-encrypt in Joplin after import

### Rich Content Support
- **Code blocks**: Syntax highlighting preserved
- **Tables**: Markdown table format maintained
- **Math expressions**: LaTeX support
- **Checklists**: Task list syntax

### Metadata Preservation
- **Creation dates**: Timestamps maintained
- **Modification dates**: Update history
- **Author information**: If available
- **Custom properties**: Additional metadata

## Best Practices

### Import Strategy
1. **Selective export**: Start with specific notebooks
2. **Test conversion**: Check complex notes first
3. **Verify attachments**: Ensure media files extract correctly
4. **Preserve structure**: Use folder organization

### Organization Tips
- **Keep structure**: Maintain notebook hierarchy
- **Use tags**: Complement folders with categorization
- **Link related notes**: Add semantic connections
- **Regular sync**: Periodic export/import cycles

### Performance Considerations
- **Batch processing**: Large exports may take time
- **File size limits**: Watch for very large notebooks
- **Attachment handling**: Ensure paths are accessible

## Troubleshooting

### Import Issues

**JSON parsing errors:**
```
# Check Joplin export is valid JSON
# Ensure UTF-8 encoding
# Try exporting smaller notebooks first
```

**Missing content:**
```
# Verify export completed successfully
# Check file permissions
# Ensure all files were exported
```

**Encoding problems:**
```
# Joplin uses UTF-8
# Check for special characters
# Some content may need manual review
```

### Export Issues

**Joplin import fails:**
```
# Check generated JSON structure
# Verify markdown file references
# Try importing single notes first
```

**Missing metadata:**
```
# Check Basic Memory entity structure
# Ensure required fields are present
# Some metadata may not translate perfectly
```

## Use Cases

### Personal Knowledge Base
- **Primary storage**: Basic Memory with AI features
- **Mobile access**: Sync to Joplin for offline reading
- **Cross-device**: Access on all platforms

### Team Documentation
- **Central authoring**: Create content in Basic Memory
- **Team distribution**: Export to Joplin for sharing
- **Version control**: Track changes in both systems

### Research Management
- **Data collection**: Gather notes in Joplin (web clipper, mobile)
- **Processing**: Analyze and enhance in Basic Memory
- **Publication**: Export polished versions

## Integration Benefits

### Cross-Platform Access
- **Device flexibility**: Work on any platform
- **Offline capability**: Joplin works without internet
- **Synchronization**: Multiple sync options

### Privacy & Security
- **End-to-end encryption**: Joplin's strong privacy features
- **Local control**: Your data stays under your control
- **Open source**: Transparent security implementation

### Feature Combination
- **Joplin's reliability**: Stable, cross-platform app
- **Basic Memory's intelligence**: AI-enhanced features
- **Best of both worlds**: Comprehensive note-taking solution

The Joplin integration provides **seamless migration** and **hybrid workflow** capabilities, allowing you to leverage both tools' strengths for comprehensive knowledge management."""


def _get_notion_help(level: str) -> str:
    """Get detailed Notion integration help."""

    return """# Notion Integration in Basic Memory

## Notion Overview

Notion is a versatile **all-in-one workspace** that combines notes, databases, wikis, and project management. It uses a **block-based editor** with extensive customization options.

## Export Formats

Notion provides several export options:
- **HTML Export**: Most comprehensive, preserves all formatting
- **Markdown Export**: Simpler format, good for content migration
- **PDF Export**: Read-only format for sharing

## Basic Memory Integration

### Import from Notion
```
load_notion_export("notion-export.zip", preserve_hierarchy=True)
```

**Processing capabilities:**
- **HTML parsing**: Complex Notion page structure
- **Block conversion**: Notion blocks to markdown
- **Hierarchy preservation**: Page and subpage structure
- **Link resolution**: Internal Notion links
- **Attachment extraction**: Images and files

### Export to Notion
```
export_notion_compatible("output/", notebook_name="Imported Notes")
```

**Export features:**
- **Clean markdown**: Compatible with Notion import
- **Metadata preservation**: Properties and relationships
- **Structured content**: Maintains organization
- **Import ready**: Direct Notion compatibility

### Search Integration
```
search_notion_vault("export/path", "project status", file_type="html")
```

**Search capabilities:**
- **HTML content**: Complex page structure parsing
- **Markdown content**: Standard text search
- **Metadata filtering**: Page properties and types
- **Context preservation**: Surrounding content in results

## Detailed Import Process

### HTML Export Import
Notion's HTML exports are complex with nested div structures and custom classes.

**What gets converted:**
- **Page titles** → Note titles
- **Text blocks** → Markdown paragraphs
- **Headings** → Markdown headers (# ## ###)
- **Lists** → Markdown bullet/numbered lists
- **Tables** → Markdown table syntax
- **Links** → Markdown link syntax
- **Images** → Image references

**Advanced features:**
- **Database views** → Structured table representations
- **Toggle blocks** → Collapsible sections
- **Callouts** → Blockquote formatting
- **Math equations** → LaTeX preservation

### Hierarchy Preservation
```
Notion Structure:
Workspace
├── Project Alpha
│   ├── Planning
│   ├── Tasks
│   └── Meeting Notes
└── Project Beta
    ├── Research
    └── Documentation

Basic Memory Structure:
notion-import/
├── Project Alpha/
│   ├── Planning.md
│   ├── Tasks.md
│   └── Meeting Notes.md
└── Project Beta/
    ├── Research.md
    └── Documentation.md
```

## Content Conversion Examples

### Rich Text Formatting
```
Notion: Bold and italic text with colors
Markdown: **Bold** and *italic* text
```

### Database Tables
```
Notion Table:
| Task | Status | Owner |
|------|--------|-------|
| Design | Done | Alice |

Markdown Table:
| Task | Status | Owner |
|------|--------|-------|
| Design | Done | Alice |
```

### Complex Blocks
```
Notion Callout:
📝 This is an important note

Markdown:
> 📝 This is an important note
```

## Export to Notion Workflow

### Creating Notion-Compatible Content
1. **Write in Basic Memory** with semantic linking
2. **Add observations** for structured data
3. **Create relationships** between entities
4. **Export to markdown** compatible with Notion

### Import Process
1. **Export from Basic Memory**:
   ```python
   export_notion_compatible("notion-ready/", notebook_name="My Knowledge Base")
   ```

2. **Import to Notion**:
   - Open Notion workspace
   - Click **Import** → **Markdown & CSV**
   - Select exported files
   - Choose import location

3. **Verify import** and adjust formatting if needed

## Advanced Features

### Semantic Link Handling
When exporting to Notion, Basic Memory's semantic links are converted to:
- **Explicit links**: `[[Entity Name]]` → `[Entity Name](entity-link)`
- **Relationship preservation**: Maintains connection context
- **Cross-reference maintenance**: Links remain navigable

### Metadata Integration
- **Frontmatter conversion**: YAML metadata becomes Notion properties
- **Tag preservation**: Basic Memory tags → Notion tags
- **Date handling**: Creation/modification dates maintained
- **Author information**: Preserved where available

## Best Practices

### Import Strategy
1. **Start with test pages**: Import single pages first
2. **Verify formatting**: Check complex content conversion
3. **Preserve hierarchy**: Use preserve_hierarchy=True
4. **Handle attachments**: Ensure media files are accessible

### Content Preparation
1. **Use clean markdown**: Prepare content for Notion import
2. **Add metadata**: Include useful properties
3. **Create relationships**: Link related content
4. **Test export**: Verify import compatibility

### Migration Workflow
1. **Export from Notion**: HTML format for best fidelity
2. **Import to Basic Memory**: Process with load_notion_export
3. **Enhance content**: Add semantic links and AI assistance
4. **Re-export if needed**: Send back to Notion or share

## Troubleshooting

### Import Issues

**HTML parsing problems:**
```
# Complex Notion pages may not convert perfectly
# Some advanced blocks need manual adjustment
# Check for unsupported content types
```

**Link resolution:**
```
# Internal Notion links may not resolve correctly
# External links are preserved
# Manual link fixing may be required
```

**Formatting loss:**
```
# Some Notion-specific formatting may not translate
# Rich media content needs verification
# Complex layouts may simplify
```

### Export Issues

**Notion import failure:**
```
# Ensure clean markdown syntax
# Check file encoding (UTF-8)
# Verify file size limits
```

**Metadata problems:**
```
# Some metadata may not import to Notion
# Check Notion's import limitations
# Simplify complex property structures
```

## Use Cases

### Team Knowledge Base
1. **Create content** in Basic Memory with AI assistance
2. **Export to Notion** for team collaboration
3. **Maintain structure** with databases and pages
4. **Sync updates** between systems

### Documentation Publishing
1. **Write technical docs** in Basic Memory
2. **Add diagrams** with Mermaid support
3. **Export to Notion** for sharing
4. **Collaborate** on documentation

### Project Management
1. **Plan projects** in Basic Memory with semantic links
2. **Export to Notion** for task tracking
3. **Use Notion databases** for detailed tracking
4. **Maintain overview** in Basic Memory

## Integration Benefits

### Workflow Flexibility
- **Notion's versatility**: Databases, calendars, kanban boards
- **Basic Memory's intelligence**: AI assistance and linking
- **Best of both**: Comprehensive workspace solution

### Content Enhancement
- **AI-powered writing**: Improve content quality
- **Semantic connections**: Better organization
- **Rich visualization**: Mermaid diagrams
- **Professional editing**: Typora integration

### Migration Freedom
- **Import existing content**: Bring Notion workspaces to Basic Memory
- **Export enhanced content**: Share improvements back to Notion
- **Hybrid usage**: Use both tools for different purposes
- **Future-proofing**: Content remains accessible

The Notion integration enables **seamless content flow** between Notion's flexible workspace and Basic Memory's intelligent knowledge management, giving you the best of both worlds."""


def _get_evernote_help(level: str) -> str:
    """Get detailed Evernote integration help."""

    return """# Evernote Integration in Basic Memory

## Evernote Overview

Evernote is a **long-established note-taking service** known for its **cross-platform availability** and **rich media support**. It uses a proprietary format but provides ENEX export for data portability.

## Export Format: ENEX

Evernote's **ENEX (Evernote XML)** format is their standard export:
- **XML structure**: Hierarchical note organization
- **Rich content**: HTML formatting with embedded media
- **Metadata**: Tags, notebooks, creation dates
- **Attachments**: Base64-encoded images and files
- **Comprehensive**: Preserves all note properties

## Basic Memory Integration

### Import from Evernote
```
load_evernote_export("notes.enex", preserve_notebooks=True, include_attachments=True)
```

**ENEX processing:**
- **XML parsing**: Structured note extraction
- **HTML conversion**: Rich content to clean markdown
- **Metadata preservation**: Tags, dates, notebooks
- **Attachment extraction**: Decode and save media files
- **Relationship mapping**: Maintain note connections

### Export to Evernote
```
export_evernote_compatible("output/", notebook_name="Exported Notes")
```

**ENEX generation:**
- **Valid XML**: Evernote-compatible structure
- **Rich formatting**: HTML content blocks
- **Metadata inclusion**: Properties and tags
- **Direct import**: Ready for Evernote restoration

### Search Integration
```
search_evernote_vault("export/path", "research notes", file_type="enex")
```

**Search capabilities:**
- **XML content**: Structured data parsing
- **HTML content**: Rich text search
- **Metadata filtering**: Notebooks, tags, dates
- **Attachment context**: Related file information

## ENEX Structure Understanding

### XML Hierarchy
```xml
<en-export>
  <note>
    <title>Note Title</title>
    <content><![CDATA[HTML content]]></content>
    <created>20231201T123456Z</created>
    <updated>20231202T123456Z</updated>
    <notebook>Notebook Name</notebook>
    <tag>Tag 1</tag>
    <tag>Tag 2</tag>
    <resource>
      <data encoding="base64">...image data...</data>
      <mime>image/jpeg</mime>
      <file-name>image.jpg</file-name>
    </resource>
  </note>
</en-export>
```

### Content Conversion
Evernote's HTML content gets converted to clean markdown:
- **Rich text** → Standard markdown formatting
- **Lists and tables** → Markdown equivalents
- **Embedded images** → File references
- **Links** → Markdown link syntax

## Detailed Import Process

### Export from Evernote
1. **Open Evernote** desktop or web application
2. **Select notes** to export (individual or all)
3. **Choose ENEX format** from export options
4. **Save file** with .enex extension

### Import to Basic Memory
```
load_evernote_export("my-notes.enex", preserve_notebooks=True)
```

**What happens:**
1. **XML parsing** of ENEX structure
2. **Note extraction** with all metadata
3. **HTML processing** to clean markdown
4. **Attachment decoding** and saving
5. **Entity creation** in Basic Memory
6. **Relationship preservation** where possible

### Advanced Options
```
load_evernote_export(
    "export.enex",
    folder="evernote-archive",           # Custom import folder
    preserve_notebooks=True,             # Keep notebook structure
    include_attachments=True             # Extract media files
)
```

## Content Conversion Examples

### Rich Text Formatting
```
Evernote: <strong>Bold</strong> and <em>italic</em> text
Markdown: **Bold** and *italic* text
```

### Lists and Tasks
```
Evernote: • Task item with checkbox
Markdown: - [ ] Task item with checkbox
```

### Tables
```
Evernote Table:
| Name | Value |
|------|-------|
| Item | Data  |

Markdown Table:
| Name | Value |
|------|-------|
| Item | Data  |
```

### Attachments
```
Evernote: Embedded image with base64 data
Result: Saved as attachments/image.jpg
Markdown: ![Image](attachments/image.jpg)
```

## Export to Evernote Workflow

### Creating ENEX-Compatible Content
1. **Write in Basic Memory** with semantic enhancements
2. **Add structure** and metadata
3. **Create relationships** between entities
4. **Export to ENEX** for Evernote compatibility

### Import Process
1. **Export from Basic Memory**:
   ```python
   export_evernote_compatible("evernote-ready/", notebook_name="My Notes")
   ```

2. **Import to Evernote**:
   - Open Evernote application
   - Go to **File** → **Import Notes**
   - Select **Evernote XML (.enex)** format
   - Choose the exported .enex file
   - Select target notebook

3. **Verify import** and check formatting

## Metadata Handling

### Evernote Properties
- **Title**: Note title (preserved)
- **Created/Updated**: Timestamps (converted from ENEX format)
- **Notebook**: Organizational folder (becomes Basic Memory folder)
- **Tags**: Categorization labels (preserved)
- **Author**: Note creator (if available)

### Basic Memory Enhancements
When importing to Basic Memory:
- **Semantic links**: Convert Evernote links to entity references
- **Observation system**: Add metadata as structured observations
- **Relationship mapping**: Preserve note connections
- **Content enhancement**: AI-assisted content improvement

## Best Practices

### Import Strategy
1. **Selective export**: Start with specific notebooks
2. **Test conversion**: Check complex notes first
3. **Verify attachments**: Ensure media files extract correctly
4. **Preserve structure**: Use preserve_notebooks=True

### Content Organization
1. **Keep notebooks**: Maintain organizational structure
2. **Use tags**: Complement folders with categorization
3. **Link related notes**: Add semantic connections
4. **Clean up content**: Remove duplicate or outdated items

### Performance Tips
- **Batch processing**: Large ENEX files may take time
- **File size limits**: Watch for very large attachments
- **Memory usage**: Large files need sufficient RAM
- **Storage space**: Account for extracted attachments

## Troubleshooting

### Import Issues

**ENEX parsing errors:**
```
# Verify ENEX file is valid XML
# Check file wasn't corrupted during export
# Try exporting smaller note sets
```

**Missing attachments:**
```
# Check base64 decoding worked
# Verify file permissions for writing
# Ensure sufficient disk space
```

**Content conversion problems:**
```
# Complex HTML may not convert perfectly
# Some Evernote-specific formatting may simplify
# Manual cleanup may be needed for complex notes
```

### Export Issues

**Evernote import failure:**
```
# Check ENEX XML structure is valid
# Verify content encoding (UTF-8)
# Try importing single notes first
```

**Formatting problems:**
```
# Some markdown features may not translate perfectly
# Complex tables may need adjustment
# Rich media content needs verification
```

## Use Cases

### Personal Archive Migration
1. **Export legacy notes** from Evernote
2. **Import to Basic Memory** for modern features
3. **Enhance with AI** for better organization
4. **Keep Evernote** for mobile access if needed

### Research Management
1. **Collect research** in Evernote (web clipper, mobile)
2. **Process and organize** in Basic Memory
3. **Add semantic links** and relationships
4. **Export polished versions** back to Evernote

### Cross-Platform Sync
1. **Primary editing** in Basic Memory with AI assistance
2. **Mobile access** via Evernote for reading
3. **Sync important changes** between systems
4. **Maintain single source of truth**

## Integration Benefits

### Legacy Data Access
- **Preserve history**: Access years of accumulated notes
- **Data portability**: Move away from proprietary service
- **Content enhancement**: Add modern features to old content

### Workflow Continuity
- **Familiar interface**: Evernote for capture and mobile
- **Advanced features**: Basic Memory for processing and AI
- **Best of both**: Established workflow with modern capabilities

### Future-Proofing
- **Open formats**: ENEX provides data portability
- **Local control**: Content under your management
- **Migration freedom**: Move between tools as needed

The Evernote integration provides a **bridge from legacy note-taking** to modern, AI-enhanced knowledge management, ensuring your accumulated knowledge remains accessible and useful."""


def _get_mermaid_help(level: str) -> str:
    """Get detailed Mermaid diagram help."""

    return """# Mermaid Diagrams in Basic Memory

## What are Mermaid Diagrams?

Mermaid is a **JavaScript-based diagramming tool** that renders text definitions into visual diagrams. It supports multiple diagram types and integrates seamlessly with markdown.

## Supported Diagram Types

### Flowcharts
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[Decision]
    C -->|Yes| D[Action 1]
    C -->|No| E[Action 2]
    D --> F[End]
    E --> F
```

### Sequence Diagrams
```mermaid
sequenceDiagram
    participant User
    participant Basic Memory
    participant Claude

    User->>Basic Memory: Write note
    Basic Memory->>Claude: Process with AI
    Claude-->>Basic Memory: Enhanced content
    Basic Memory-->>User: Improved note
```

### Gantt Charts
```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Planning
    Requirements     :done, req, 2024-01-01, 2024-01-15
    Design          :active, des, 2024-01-16, 2024-02-01
    section Development
    Implementation  :impl, 2024-02-02, 2024-03-01
    Testing         :test, 2024-03-02, 2024-03-15
```

### Mind Maps
```mermaid
mindmap
  root((Knowledge Base))
    Origins
      Personal Notes
      Research
      Documentation
    Tools
      Basic Memory
      Claude AI
      Typora
    Features
      Semantic Links
      Mermaid Diagrams
      AI Enhancement
```

### ER Diagrams
```mermaid
erDiagram
    PROJECT ||--o{ TASK : contains
    USER ||--o{ PROJECT : owns
    TASK }o--|| STATUS : has
    USER {
        string username PK
        string email
        string name
    }
    PROJECT {
        int id PK
        string name
        string description
        int owner_id FK
    }
    TASK {
        int id PK
        string title
        string description
        int project_id FK
        int status_id FK
    }
    STATUS {
        int id PK
        string name
        string value
    }
```

## Basic Memory Integration

### Automatic Rendering
When you export notes to HTML, Mermaid diagrams are **automatically rendered**:

```python
export_html_notes("site/", folder="docs")
# Creates HTML with live Mermaid diagrams
```

### CDN Integration
- **Automatic loading**: Mermaid.js loaded from CDN
- **No configuration needed**: Works out of the box
- **Fast rendering**: Optimized for web viewing

### Syntax Highlighting
Mermaid code blocks are properly formatted in markdown:
```markdown
graph TD
    A --> B
    B --> C
```

## Creating Diagrams

### Basic Flowchart
```
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

### With Styling
```
graph TD
    A([Start]) --> B[Process]
    B --> C([End])

    style A fill:#e1f5fe
    style C fill:#c8e6c9
```

### Complex Relationships
```
graph LR
    subgraph "Input Sources"
        EN[Evernote]
        OB[Obsidian]
        NO[Notion]
        JO[Joplin]
    end

    subgraph "Basic Memory"
        IM[Import]
        ENH[Enhance]
        LINK[Link]
        EXP[Export]
    end

    subgraph "Output Formats"
        HT[HTML]
        MD[Markdown]
        DO[Docsify]
        TY[Typora]
    end

    EN --> IM
    OB --> IM
    NO --> IM
    JO --> IM

    IM --> ENH --> LINK --> EXP

    EXP --> HT
    EXP --> MD
    EXP --> DO
    EXP --> TY
```

## Use Cases

### Knowledge Mapping
```mermaid
graph TD
    KM[Knowledge Management] --> NT[Note Taking]
    KM --> SM[Semantic Networking]
    KM --> AI[AI Integration]

    NT --> OB[Obsidian]
    NT --> NO[Notion]
    NT --> EV[Evernote]
    NT --> JO[Joplin]

    SM --> EN[Entities]
    SM --> RE[Relationships]
    SM --> OB[Observations]

    AI --> CL[Claude Desktop]
    AI --> SE[Smart Search]
    AI --> GE[Content Generation]
```

### Project Planning
```mermaid
gantt
    title Basic Memory Enhancement Project
    dateFormat YYYY-MM-DD

    section Research
    Platform Analysis    :done, pa, 2024-01-01, 2024-01-07
    User Requirements    :done, ur, 2024-01-08, 2024-01-14

    section Development
    Core Integration     :done, ci, 2024-01-15, 2024-01-31
    Import Tools         :done, it, 2024-02-01, 2024-02-15
    Export Tools         :done, et, 2024-02-16, 2024-03-01
    AI Features          :active, af, 2024-03-02, 2024-03-15

    section Testing
    Integration Tests    :it, 2024-03-16, 2024-03-22
    User Acceptance      :uat, 2024-03-23, 2024-03-29

    section Deployment
    Documentation        :doc, 2024-03-30, 2024-04-05
    Release              :rel, 2024-04-06, 2024-04-10
```

### System Architecture
```mermaid
graph TB
    subgraph "User Interface"
        CD[Claude Desktop]
        CLI[Command Line]
        WEB[Web Interface]
    end

    subgraph "Basic Memory Core"
        MCP[MCP Server]
        API[REST API]
        DB[(SQLite Database)]
    end

    subgraph "Processing Engines"
        IMP[Import Engine]
        EXP[Export Engine]
        SEA[Search Engine]
        SYN[Sync Engine]
    end

    subgraph "External Integrations"
        OB[Obsidian]
        NO[Notion]
        EV[Evernote]
        JO[Joplin]
        TY[Typora]
    end

    CD --> MCP
    CLI --> API
    WEB --> API

    MCP --> IMP
    MCP --> EXP
    MCP --> SEA

    API --> DB
    SYN --> DB

    IMP --> OB
    IMP --> NO
    IMP --> EV
    IMP --> JO

    EXP --> TY
```

## Best Practices

### Diagram Organization
1. **Clear structure**: Use consistent layout directions
2. **Meaningful labels**: Descriptive node and edge labels
3. **Logical flow**: Top-to-bottom or left-to-right flow
4. **Color coding**: Use colors to group related elements

### Content Integration
1. **Context placement**: Put diagrams near related content
2. **Reference linking**: Link to diagram sections from text
3. **Version control**: Track diagram changes with content
4. **Responsive design**: Consider different viewing contexts

### Performance Tips
1. **Size matters**: Large diagrams may slow rendering
2. **Complexity balance**: Simpler diagrams render faster
3. **CDN reliability**: Diagrams depend on internet for rendering
4. **Fallback content**: Consider text descriptions for offline viewing

## Advanced Features

### Interactive Diagrams
Some Mermaid features support interactivity:
- **Clickable nodes**: Link to other content
- **Expandable sections**: Show/hide detail
- **Hover effects**: Additional information on hover

### Custom Styling
```mermaid
graph TD
    A[Styled Node] --> B[Another Node]

    classDef important fill:#ff9999,stroke:#ff0000,stroke-width:2px
    classDef normal fill:#e6e6e6

    class A important
    class B normal
```

### Integration with Content
```markdown
## System Architecture

Here's how Basic Memory components interact:

graph TB
    UI[User Interface] --> API[API Layer]
    API --> DB[(Database)]
    API --> AI[AI Services]

## Key Benefits

- **Modular design** for maintainability
- **API-first** approach for integrations
- **AI-enhanced** user experience
```

## Troubleshooting

### Diagram Not Rendering
- **Syntax check**: Validate Mermaid syntax
- **CDN access**: Ensure internet connection for rendering
- **Browser support**: Check for JavaScript compatibility
- **Export format**: HTML export required for live rendering

### Performance Issues
- **Large diagrams**: Break into smaller, focused diagrams
- **Complex styling**: Simplify custom CSS
- **Rendering delays**: Consider static image alternatives

### Syntax Errors
- **Validation**: Use online Mermaid editors for testing
- **Common mistakes**: Missing semicolons, incorrect brackets
- **Version differences**: Check Mermaid version compatibility

## Export & Sharing

### HTML Export with Diagrams
```python
export_html_notes("presentation/", folder="project-docs")
# Creates interactive diagram presentations
```

### Static Alternatives
For environments without JavaScript:
- **PNG export**: Static diagram images
- **SVG export**: Scalable vector graphics
- **PDF export**: Print-ready documents

### Integration Examples
- **Documentation sites**: Docsify with Mermaid
- **Presentations**: HTML slides with diagrams
- **Reports**: Rich documents with visual elements
- **Knowledge bases**: Interactive information architecture

Mermaid diagrams add **visual clarity** to your knowledge base, making complex relationships and processes easily understandable at a glance."""
