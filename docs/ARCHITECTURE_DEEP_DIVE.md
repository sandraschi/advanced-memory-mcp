# Advanced Memory MCP - Architecture Deep Dive

**Version:** 1.0.0b2  
**Purpose:** Technical architecture documentation for developers and advanced users

## System Architecture Overview

Advanced Memory MCP is built on a multi-layered architecture that separates concerns while maintaining tight integration between components.

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Desktop                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Claude UI     │  │   MCP Client    │  │   Config    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol (stdio)
┌─────────────────────▼───────────────────────────────────────┐
│                Advanced Memory MCP                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   MCP Server    │  │   FastAPI API   │  │   Sync      │ │
│  │   (FastMCP)     │  │   Layer         │  │   Service   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Tools Layer   │  │   Services      │  │   Models    │ │
│  │   (50+ tools)   │  │   Layer         │  │   (SQLAlchemy)│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ SQLite + FTS5
┌─────────────────────▼───────────────────────────────────────┐
│                   Data Layer                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   SQLite DB     │  │   File System   │  │   Search    │ │
│  │   (WAL Mode)    │  │   (Markdown)    │  │   Index     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. MCP Server Layer (FastMCP 2.12+)

The MCP server is the primary interface between Claude Desktop and Advanced Memory.

#### Key Files
- `src/advanced_memory/mcp/server.py` - Main FastMCP server
- `src/advanced_memory/mcp/tools/` - Tool implementations
- `src/advanced_memory/mcp/prompts/` - AI prompt templates

#### Architecture
```python
# FastMCP Server Structure
@mcp.tool()
async def tool_name(params) -> str:
    '''Tool description'''
    # Implementation
    return result

# Portmanteau Tools
@mcp.tool()
async def adn_content(operation: str, **kwargs) -> str:
    '''Consolidated content operations'''
    if operation == "write":
        return await _write_operation(**kwargs)
    elif operation == "read":
        return await _read_operation(**kwargs)
    # ... other operations
```

#### Tool Categories
1. **Content Management** (6 operations)
2. **Project Management** (8 operations)
3. **Search & Discovery** (5 operations)
4. **Navigation** (5 operations)
5. **Import/Export** (6 operations)
6. **Knowledge Operations** (5 operations)
7. **Editor Integration** (5 operations)

### 2. API Layer (FastAPI)

RESTful API for programmatic access and internal communication.

#### Key Files
- `src/advanced_memory/api/app.py` - FastAPI application
- `src/advanced_memory/api/routers/` - API route handlers
- `src/advanced_memory/mcp/async_client.py` - Internal HTTP client

#### API Endpoints
```python
# Project Management
GET    /projects/projects              # List projects
POST   /projects/projects              # Create project
PUT    /projects/{name}/default        # Set default
DELETE /projects/{name}                # Delete project
POST   /projects/{name}/sync           # Sync project

# Entity Management
GET    /{project}/entities            # List entities
POST   /{project}/entities            # Create entity
GET    /{project}/entities/{id}        # Get entity
PUT    /{project}/entities/{id}        # Update entity
DELETE /{project}/entities/{id}       # Delete entity

# Search
GET    /{project}/search              # Search entities
GET    /{project}/search/suggestions  # Search suggestions

# Import/Export
POST   /import/obsidian               # Import Obsidian
POST   /import/joplin                 # Import Joplin
POST   /export/pdf                    # Export PDF
POST   /export/html                   # Export HTML
```

### 3. Services Layer

Business logic and orchestration between API and data layers.

#### Key Files
- `src/advanced_memory/services/` - Service implementations
- `src/advanced_memory/repository/` - Data access layer
- `src/advanced_memory/sync/` - File synchronization

#### Service Architecture
```python
# Service Pattern
class EntityService:
    def __init__(self, entity_repo: EntityRepository):
        self.entity_repo = entity_repo
    
    async def create_entity(self, data: EntityCreate) -> Entity:
        # Business logic
        entity = await self.entity_repo.create(data)
        # Post-processing
        return entity
```

#### Key Services
1. **EntityService** - Note management
2. **ProjectService** - Project operations
3. **SearchService** - Full-text search
4. **SyncService** - File synchronization
5. **ImportService** - Data import
6. **ExportService** - Data export

### 4. Data Layer

SQLite database with full-text search capabilities.

#### Database Schema
```sql
-- Core Tables
CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL,
    permalink TEXT UNIQUE NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE entity (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    file_path TEXT NOT NULL,
    permalink TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project (id),
    UNIQUE(project_id, file_path)
);

CREATE TABLE observation (
    id INTEGER PRIMARY KEY,
    entity_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES entity (id) ON DELETE CASCADE
);

CREATE TABLE relation (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES entity (id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES entity (id) ON DELETE CASCADE,
    UNIQUE(source_id, target_id, relation_type)
);

-- Full-Text Search Tables
CREATE VIRTUAL TABLE fts_entity USING fts5(
    title, content, 
    content='entity', 
    content_rowid='id'
);

CREATE VIRTUAL TABLE fts_observation USING fts5(
    content, 
    content='observation', 
    content_rowid='id'
);
```

#### Database Features
- **WAL Mode**: Concurrent read/write access
- **Connection Pooling**: Optimized for MCP usage
- **FTS5**: Full-text search engine
- **Automatic Vacuum**: Maintenance and optimization
- **Foreign Key Constraints**: Data integrity
- **Indexes**: Optimized query performance

### 5. Sync Layer

Real-time file synchronization and change detection.

#### Components
```python
# File Watcher
class WatchService:
    def __init__(self, config: Config):
        self.config = config
        self.observer = Observer()
    
    def start_watching(self):
        # Monitor all active projects
        for project in self.active_projects:
            self.observer.schedule(
                FileHandler(project.path),
                project.path,
                recursive=True
            )
        self.observer.start()

# Background Sync
class BackgroundSyncService:
    async def sync_changes(self, changes: List[FileChange]):
        # Process file changes
        for change in changes:
            if change.type == "added":
                await self.index_file(change.path)
            elif change.type == "modified":
                await self.update_file(change.path)
            elif change.type == "deleted":
                await self.remove_file(change.path)
```

#### Sync Features
- **Real-time Monitoring**: File system events
- **Debounced Processing**: 1-second delay after last change
- **Multi-project Support**: Monitor all active projects
- **Smart Filtering**: Ignore `node_modules/`, `.git/`, etc.
- **Conflict Resolution**: Handle concurrent modifications
- **Error Recovery**: Retry failed operations

---

## Data Flow Architecture

### 1. Note Creation Flow

```
User Input → MCP Tool → API Endpoint → Service Layer → Repository → Database
     ↓
File System ← Sync Service ← Background Process ← Change Detection
```

### 2. Search Flow

```
Search Query → MCP Tool → Search Service → FTS5 Index → Results → Ranking
```

### 3. Import Flow

```
External Data → Import Tool → Parser → Entity Service → Database → File System
```

### 4. Export Flow

```
Database Query → Export Service → Formatter → Output File
```

---

## Portmanteau Tool Architecture

### Design Pattern

Portmanteau tools use a **command pattern** with **operation routing**:

```python
@mcp.tool()
async def adn_content(operation: str, **kwargs) -> str:
    '''Consolidated content operations'''
    
    # Route to appropriate operation
    if operation == "write":
        return await _write_operation(**kwargs)
    elif operation == "read":
        return await _read_operation(**kwargs)
    elif operation == "edit":
        return await _edit_operation(**kwargs)
    # ... other operations
    else:
        return f"Invalid operation: {operation}"

# Individual operation handlers
async def _write_operation(title: str, content: str, folder: str) -> str:
    # Implementation
    pass
```

### Benefits
1. **Reduced Complexity**: 8 tools instead of 50+
2. **Consistent API**: Same parameter patterns
3. **Better UX**: Easier to remember and use
4. **Cursor IDE Optimized**: Fewer tools in autocomplete
5. **Maintainable**: Centralized operation logic

---

## Import/Export Architecture

### Parser Architecture

Each import format has a dedicated parser:

```python
class BaseImporter(ABC):
    @abstractmethod
    async def parse(self, source_path: str) -> List[Entity]:
        pass
    
    @abstractmethod
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        pass

class ObsidianImporter(BaseImporter):
    async def parse(self, source_path: str) -> List[Entity]:
        # Parse Obsidian vault
        # Convert [[WikiLinks]] to relations
        # Extract frontmatter
        pass
```

### Export Architecture

Exporters use a **template-based** approach:

```python
class BaseExporter(ABC):
    @abstractmethod
    async def export(self, entities: List[Entity], output_path: str):
        pass

class PDFExporter(BaseExporter):
    async def export(self, entities: List[Entity], output_path: str):
        # Generate LaTeX
        # Compile to PDF
        # Include TOC and metadata
        pass
```

---

## Configuration Architecture

### Configuration Hierarchy

```
Environment Variables (highest priority)
    ↓
User Config File (~/.advanced-memory/config.json)
    ↓
Default Configuration (lowest priority)
```

### Configuration Classes

```python
@dataclass
class Config:
    projects: Dict[str, str]
    default_project: str
    sync_changes: bool
    sync_delay: int
    database_path: str
    
    @classmethod
    def load(cls) -> 'Config':
        # Load from file, environment, defaults
        pass
```

---

## Security Architecture

### Data Protection
- **File System Access**: Restricted to configured project paths
- **Database Security**: SQLite with proper permissions
- **Input Validation**: Pydantic models for all inputs
- **Path Traversal Protection**: Sanitized file paths

### Authentication
- **MCP Protocol**: Secure stdio communication
- **API Security**: Internal API only (no external access)
- **File Permissions**: Respect system file permissions

---

## Performance Architecture

### Optimization Strategies

#### Database Optimization
- **Connection Pooling**: Reuse database connections
- **WAL Mode**: Concurrent read/write access
- **Indexes**: Optimized for common queries
- **Query Optimization**: Efficient SQL queries

#### File System Optimization
- **Debounced Sync**: Reduce file system calls
- **Smart Filtering**: Skip unnecessary files
- **Batch Operations**: Process multiple changes together
- **Caching**: Cache frequently accessed data

#### Memory Optimization
- **Lazy Loading**: Load data on demand
- **Streaming**: Process large files in chunks
- **Garbage Collection**: Proper cleanup of resources

---

## Error Handling Architecture

### Error Hierarchy

```python
class AdvancedMemoryError(Exception):
    """Base exception for Advanced Memory"""

class ProjectError(AdvancedMemoryError):
    """Project-related errors"""

class EntityError(AdvancedMemoryError):
    """Entity-related errors"""

class SyncError(AdvancedMemoryError):
    """Synchronization errors"""

class ImportError(AdvancedMemoryError):
    """Import-related errors"""
```

### Error Recovery

```python
async def robust_operation():
    try:
        return await operation()
    except DatabaseError:
        # Retry with backoff
        await asyncio.sleep(1)
        return await operation()
    except FileSystemError:
        # Log and continue
        logger.error("File system error")
        return None
```

---

## Testing Architecture

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_tools.py
├── integration/          # Integration tests
│   ├── test_api.py
│   ├── test_sync.py
│   └── test_import.py
├── mcp/                 # MCP tool tests
│   ├── test_portmanteau.py
│   └── test_individual.py
└── fixtures/            # Test data
    ├── sample_notes.md
    └── test_config.json
```

### Test Patterns

```python
@pytest.fixture
async def test_db():
    # In-memory SQLite database
    db = create_test_database()
    yield db
    await db.close()

@pytest.mark.asyncio
async def test_create_entity(test_db):
    # Test entity creation
    entity = await create_entity(test_db, {...})
    assert entity.title == "Test Note"
```

---

## Deployment Architecture

### MCPB Package Structure

```
advanced-memory-mcp.mcpb/
├── manifest.json         # Package metadata
├── requirements.txt      # Python dependencies
├── src/                  # Source code
│   └── advanced_memory/
├── data/                 # Sample data
└── README.md            # Package documentation
```

### Installation Methods

1. **PyPI**: `pip install advanced-memory-mcp`
2. **MCPB**: Drag `.mcpb` file to Claude Desktop
3. **Development**: `pip install -e ".[dev]"`

---

## Monitoring & Observability

### Logging Architecture

```python
# Structured logging with loguru
logger.add(
    "advanced-memory.log",
    rotation="1 day",
    retention="30 days",
    format="{time} | {level} | {message}",
    level="INFO"
)
```

### Metrics Collection

- **Database Statistics**: Entity counts, sync status
- **Performance Metrics**: Response times, memory usage
- **Error Tracking**: Error rates, failure patterns
- **Usage Analytics**: Tool usage, project activity

---

## Future Architecture Considerations

### Scalability
- **Database Migration**: PostgreSQL for larger datasets
- **Distributed Sync**: Multi-machine synchronization
- **Caching Layer**: Redis for performance
- **API Gateway**: External API access

### Extensibility
- **Plugin System**: Custom importers/exporters
- **Custom Tools**: User-defined MCP tools
- **Template System**: Customizable export formats
- **Webhooks**: External integrations

### Performance
- **Async Processing**: Background task queues
- **CDN Integration**: Asset delivery
- **Compression**: Data compression
- **Indexing**: Advanced search capabilities

---

This architecture provides a solid foundation for Advanced Memory MCP while maintaining flexibility for future enhancements and scalability requirements.
