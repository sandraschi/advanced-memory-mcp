# Advanced Memory MCP - Developer Guide

**Version:** 1.0.0b2
**Purpose:** Guide for developers contributing to Advanced Memory MCP

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Node.js (for MCPB packaging)
- SQLite 3
- Your preferred IDE (VS Code, PyCharm, etc.)

### Installation

```bash
# Clone repository
git clone https://github.com/sandraschi/advanced-memory-mcp.git
cd advanced-memory-mcp

# Install in development mode
pip install -e ".[dev]"

# Install MCPB CLI
npm install -g @anthropic-ai/mcpb

# Verify installation
python -c "import advanced_memory; print('✅ Installed')"
```

### Development Environment

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
pyright
```

---

## Project Structure

```
advanced-memory-mcp/
├── src/advanced_memory/          # Main source code
│   ├── mcp/                     # MCP server implementation
│   │   ├── tools/              # MCP tools
│   │   ├── prompts/            # AI prompts
│   │   └── server.py           # FastMCP server
│   ├── api/                     # FastAPI REST API
│   ├── models/                  # SQLAlchemy models
│   ├── services/                # Business logic
│   ├── repository/              # Data access layer
│   ├── sync/                    # File synchronization
│   ├── importers/               # Import modules
│   └── cli/                     # Command-line interface
├── tests/                        # Test suite
├── docs/                         # Documentation
├── mcpb/                         # MCPB package files
├── scripts/                      # Build and utility scripts
└── pyproject.toml               # Project configuration
```

---

## Code Style Guidelines

### Python Style

- **Line Length**: 100 characters maximum
- **Formatting**: Use `ruff format`
- **Linting**: Use `ruff check`
- **Type Hints**: Required for all functions
- **Docstrings**: Use Google style

### Example Code Style

```python
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context
from advanced_memory.mcp.server import mcp

@mcp.tool()
async def example_tool(
    param1: str,
    param2: Optional[int] = None,
    ctx: Context | None = None,
) -> str:
    """Example tool with proper type hints and docstring.

    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
        ctx: MCP context for progress reporting

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
    """
    if not param1:
        raise ValueError("param1 cannot be empty")

    # Implementation
    result = f"Processed {param1}"
    if param2:
        result += f" with {param2}"

    return result
```

### Import Order

```python
# Standard library imports
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

# Third-party imports
import httpx
from fastapi import FastAPI
from sqlalchemy import Column, Integer, String

# Local imports
from advanced_memory.models.base import Base
from advanced_memory.services.entity_service import EntityService
```

---

## Adding New MCP Tools

### 1. Create Tool File

```python
# src/advanced_memory/mcp/tools/my_new_tool.py
from typing import Any, Dict, Optional
from mcp.server.fastmcp import Context
from advanced_memory.mcp.server import mcp

@mcp.tool()
async def my_new_tool(
    param1: str,
    param2: Optional[int] = None,
    ctx: Context | None = None,
) -> str:
    """My new tool description.

    This tool does something useful for users.

    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
        ctx: MCP context for progress reporting

    Returns:
        Formatted result string

    Raises:
        ValueError: When param1 is invalid
    """
    if ctx:
        await ctx.info(f"Processing {param1}")

    try:
        # Tool implementation
        result = f"✅ Processed {param1}"
        if param2:
            result += f" with value {param2}"

        return result

    except Exception as e:
        error_msg = f"❌ Error processing {param1}: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return error_msg
```

### 2. Register Tool

```python
# src/advanced_memory/mcp/tools/__init__.py
from advanced_memory.mcp.tools.my_new_tool import my_new_tool

__all__ = [
    # ... existing tools
    "my_new_tool",
]
```

### 3. Add Tests

```python
# tests/mcp/test_my_new_tool.py
import pytest
from advanced_memory.mcp.tools.my_new_tool import my_new_tool

@pytest.mark.asyncio
async def test_my_new_tool_success():
    """Test successful tool execution."""
    result = await my_new_tool("test_param", 42)
    assert "✅ Processed test_param" in result
    assert "with value 42" in result

@pytest.mark.asyncio
async def test_my_new_tool_error():
    """Test tool error handling."""
    result = await my_new_tool("")
    assert "❌ Error" in result
    assert "invalid" in result.lower()
```

### 4. Add to Portmanteau (if applicable)

If your tool fits into an existing portmanteau:

```python
# src/advanced_memory/mcp/tools/content_manager.py
async def adn_content(operation: str, **kwargs) -> str:
    """Consolidated content operations."""

    # ... existing operations

    elif operation == "my_new_operation":
        return await _my_new_operation(**kwargs)

    else:
        return f"Invalid operation: {operation}"

async def _my_new_operation(param1: str, **kwargs) -> str:
    """Handle my new operation."""
    # Implementation
    pass
```

---

## Adding New Portmanteau Tools

### 1. Create Portmanteau Tool

```python
# src/advanced_memory/mcp/tools/my_portmanteau.py
from typing import Any, Dict, Optional
from mcp.server.fastmcp import Context
from advanced_memory.mcp.server import mcp

@mcp.tool()
async def adn_my_portmanteau(
    operation: str,
    ctx: Context | None = None,
    **kwargs: Any,
) -> str:
    """Consolidated my operations.

    SUPPORTED OPERATIONS:
    - operation1: Description of operation1
    - operation2: Description of operation2
    - operation3: Description of operation3

    Args:
        operation: Operation to perform
        ctx: MCP context for progress reporting
        **kwargs: Additional parameters for specific operations

    Returns:
        Formatted result string
    """
    if ctx:
        await ctx.info(f"Executing {operation} operation")

    # Route to appropriate operation
    if operation == "operation1":
        return await _operation1(**kwargs)
    elif operation == "operation2":
        return await _operation2(**kwargs)
    elif operation == "operation3":
        return await _operation3(**kwargs)
    else:
        return f"# Error\n\nInvalid operation '{operation}'. Supported operations: operation1, operation2, operation3"

async def _operation1(param1: str, **kwargs) -> str:
    """Handle operation1."""
    # Implementation
    return f"✅ Operation1 completed with {param1}"

async def _operation2(param2: int, **kwargs) -> str:
    """Handle operation2."""
    # Implementation
    return f"✅ Operation2 completed with {param2}"

async def _operation3(**kwargs) -> str:
    """Handle operation3."""
    # Implementation
    return "✅ Operation3 completed"
```

### 2. Register Portmanteau Tool

```python
# src/advanced_memory/mcp/tools/__init__.py
from advanced_memory.mcp.tools.my_portmanteau import adn_my_portmanteau

__all__ = [
    # ... existing tools
    "adn_my_portmanteau",
]
```

### 3. Update Documentation

```python
# src/advanced_memory/mcp/tools/__init__.py
__all__ = [
    # Complete portmanteau tool suite (9 tools total)
    "adn_content",      # Content management
    "adn_project",      # Project management
    "adn_search",       # Search & discovery
    "adn_navigation",   # Knowledge graph navigation
    "adn_import",       # Import from platforms
    "adn_export",       # Export to formats
    "adn_knowledge",    # Advanced knowledge management
    "adn_editor",       # External editor integration
    "adn_my_portmanteau", # My new portmanteau tool
    # ... legacy tools
]
```

---

## Database Development

### Adding New Models

```python
# src/advanced_memory/models/my_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from advanced_memory.models.base import Base

class MyModel(Base):
    """My new model."""

    __tablename__ = "my_model"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    entity_id = Column(Integer, ForeignKey("entity.id"))
    created_at = Column(DateTime, nullable=False)

    # Relationships
    entity = relationship("Entity", back_populates="my_models")
```

### Creating Migrations

```bash
# Create new migration
just migration "Add my_model table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Repository Pattern

```python
# src/advanced_memory/repository/my_model_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from advanced_memory.models.my_model import MyModel
from advanced_memory.repository.repository import Repository

class MyModelRepository(Repository[MyModel]):
    """Repository for MyModel."""

    def __init__(self, db: Session):
        super().__init__(MyModel, db)

    async def find_by_name(self, name: str) -> Optional[MyModel]:
        """Find model by name."""
        return self.db.query(MyModel).filter(MyModel.name == name).first()

    async def find_by_entity_id(self, entity_id: int) -> List[MyModel]:
        """Find models by entity ID."""
        return self.db.query(MyModel).filter(MyModel.entity_id == entity_id).all()
```

---

## API Development

### Adding New Endpoints

```python
# src/advanced_memory/api/routers/my_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from advanced_memory.schemas.my_model import MyModelCreate, MyModelResponse
from advanced_memory.services.my_model_service import MyModelService
from advanced_memory.deps import get_db

router = APIRouter(prefix="/my-models", tags=["my-models"])

@router.post("/", response_model=MyModelResponse)
async def create_my_model(
    data: MyModelCreate,
    service: MyModelService = Depends(),
) -> MyModelResponse:
    """Create a new my model."""
    try:
        model = await service.create(data)
        return MyModelResponse.from_orm(model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[MyModelResponse])
async def list_my_models(
    service: MyModelService = Depends(),
) -> List[MyModelResponse]:
    """List all my models."""
    models = await service.list_all()
    return [MyModelResponse.from_orm(model) for model in models]
```

### Service Layer

```python
# src/advanced_memory/services/my_model_service.py
from typing import List, Optional
from advanced_memory.models.my_model import MyModel
from advanced_memory.repository.my_model_repository import MyModelRepository
from advanced_memory.schemas.my_model import MyModelCreate, MyModelUpdate
from advanced_memory.services.service import Service

class MyModelService(Service[MyModel]):
    """Service for MyModel operations."""

    def __init__(self, repository: MyModelRepository):
        super().__init__(repository)
        self.repository = repository

    async def create(self, data: MyModelCreate) -> MyModel:
        """Create a new my model."""
        # Business logic
        model = MyModel(**data.dict())
        return await self.repository.create(model)

    async def update(self, id: int, data: MyModelUpdate) -> MyModel:
        """Update a my model."""
        model = await self.repository.get(id)
        if not model:
            raise ValueError(f"MyModel with id {id} not found")

        # Update fields
        for field, value in data.dict(exclude_unset=True).items():
            setattr(model, field, value)

        return await self.repository.update(model)
```

---

## Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_models.py      # Model tests
│   ├── test_services.py    # Service tests
│   └── test_tools.py       # Tool tests
├── integration/            # Integration tests
│   ├── test_api.py         # API tests
│   ├── test_sync.py        # Sync tests
│   └── test_import.py      # Import tests
├── mcp/                    # MCP tests
│   ├── test_portmanteau.py # Portmanteau tests
│   └── test_individual.py  # Individual tool tests
└── fixtures/               # Test data
    ├── sample_notes.md     # Sample markdown files
    └── test_config.json    # Test configuration
```

### Writing Tests

```python
# tests/unit/test_my_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from advanced_memory.services.my_service import MyService
from advanced_memory.models.my_model import MyModel

@pytest.fixture
def mock_repository():
    """Mock repository for testing."""
    return AsyncMock()

@pytest.fixture
def service(mock_repository):
    """Service instance with mocked repository."""
    return MyService(mock_repository)

@pytest.mark.asyncio
async def test_create_success(service, mock_repository):
    """Test successful creation."""
    # Arrange
    data = {"name": "test", "description": "test description"}
    expected_model = MyModel(id=1, **data)
    mock_repository.create.return_value = expected_model

    # Act
    result = await service.create(data)

    # Assert
    assert result.id == 1
    assert result.name == "test"
    mock_repository.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_error(service, mock_repository):
    """Test creation error."""
    # Arrange
    data = {"name": "", "description": "test"}
    mock_repository.create.side_effect = ValueError("Name cannot be empty")

    # Act & Assert
    with pytest.raises(ValueError, match="Name cannot be empty"):
        await service.create(data)
```

### Integration Tests

```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from advanced_memory.api.app import app

@pytest.fixture
async def client():
    """Test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_entity(client):
    """Test entity creation via API."""
    data = {
        "title": "Test Entity",
        "content": "# Test\n\nThis is a test entity.",
        "file_path": "test.md"
    }

    response = await client.post("/main/entities", json=data)
    assert response.status_code == 200

    result = response.json()
    assert result["title"] == "Test Entity"
    assert result["content"] == data["content"]
```

---

## Import/Export Development

### Adding New Importers

```python
# src/advanced_memory/importers/my_importer.py
from typing import List, Dict, Any
from pathlib import Path
from advanced_memory.importers.base import BaseImporter
from advanced_memory.models.entity import Entity

class MyImporter(BaseImporter):
    """Importer for My format."""

    def __init__(self):
        super().__init__()
        self.supported_extensions = [".my", ".myformat"]

    async def parse(self, source_path: str) -> List[Entity]:
        """Parse My format files."""
        entities = []
        source = Path(source_path)

        if source.is_file():
            entities.extend(await self._parse_file(source))
        elif source.is_dir():
            for file_path in source.rglob("*.my"):
                entities.extend(await self._parse_file(file_path))

        return entities

    async def _parse_file(self, file_path: Path) -> List[Entity]:
        """Parse a single My format file."""
        # Implementation
        content = file_path.read_text(encoding="utf-8")

        # Extract metadata
        metadata = self._extract_metadata(content)

        # Create entity
        entity = Entity(
            title=metadata.get("title", file_path.stem),
            content=content,
            file_path=str(file_path),
            project_id=self.project_id
        )

        return [entity]

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from content."""
        # Implementation
        return {"title": "Extracted Title"}
```

### Adding New Exporters

```python
# src/advanced_memory/exporters/my_exporter.py
from typing import List
from pathlib import Path
from advanced_memory.models.entity import Entity
from advanced_memory.exporters.base import BaseExporter

class MyExporter(BaseExporter):
    """Exporter to My format."""

    def __init__(self):
        super().__init__()
        self.output_extension = ".my"

    async def export(
        self,
        entities: List[Entity],
        output_path: str,
        **kwargs
    ) -> str:
        """Export entities to My format."""
        output = Path(output_path)
        output.mkdir(parents=True, exist_ok=True)

        for entity in entities:
            await self._export_entity(entity, output)

        return f"Exported {len(entities)} entities to {output_path}"

    async def _export_entity(self, entity: Entity, output_dir: Path):
        """Export a single entity."""
        # Convert to My format
        my_content = self._convert_to_my_format(entity)

        # Write file
        output_file = output_dir / f"{entity.title}.my"
        output_file.write_text(my_content, encoding="utf-8")

    def _convert_to_my_format(self, entity: Entity) -> str:
        """Convert entity to My format."""
        # Implementation
        return f"# {entity.title}\n\n{entity.content}"
```

---

## MCPB Package Development

### Building MCPB Package

```bash
# Validate manifest
cd mcpb
mcpb validate manifest.json

# Build package
mcpb pack . ../dist/

# Test package
# Drag .mcpb file to Claude Desktop
```

### Manifest Configuration

```json
{
  "mcpb_version": "0.1",
  "name": "advanced-memory-mcp",
  "version": "1.0.0b2",
  "description": "Advanced Memory MCP Server",
  "author": {
    "name": "Sandra Schi",
    "email": "sandra@sandraschi.dev"
  },
  "server": {
    "type": "python",
    "entry_point": "src/advanced_memory/mcp/server.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "PYTHONPATH": "src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  },
  "capabilities": {
    "tools": true,
    "resources": true,
    "prompts": true
  }
}
```

---

## Performance Optimization

### Database Optimization

```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Optimize queries
async def get_entities_optimized(db: Session, limit: int = 100):
    """Optimized entity query."""
    return (
        db.query(Entity)
        .options(joinedload(Entity.observations))
        .options(joinedload(Entity.relations))
        .limit(limit)
        .all()
    )
```

### Async Optimization

```python
# Use asyncio.gather for concurrent operations
async def process_multiple_files(file_paths: List[str]):
    """Process multiple files concurrently."""
    tasks = [process_file(path) for path in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Use async context managers
async def with_database():
    """Use database with proper cleanup."""
    async with get_db_session() as db:
        # Database operations
        yield db
```

---

## Debugging

### Debug Tools

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Profile performance
import cProfile
cProfile.run('your_function()')
```

### Common Debug Patterns

```python
# Debug MCP tools
@mcp.tool()
async def debug_tool(param: str, ctx: Context | None = None) -> str:
    """Debug tool with logging."""
    if ctx:
        await ctx.info(f"Debug: Processing {param}")

    try:
        # Implementation
        result = f"Processed {param}"
        if ctx:
            await ctx.info(f"Debug: Result = {result}")
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Debug: Error = {str(e)}")
        raise
```

---

## Contributing Guidelines

### Code Review Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Write Tests**
   - Unit tests for new functionality
   - Integration tests for API changes
   - Update existing tests if needed

3. **Run Quality Checks**
   ```bash
   ruff check .
   ruff format .
   pyright
   pytest
   ```

4. **Create Pull Request**
   - Clear description of changes
   - Reference related issues
   - Include test results

### Commit Message Format

```
type(scope): description

Detailed description of changes.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

### Release Process

1. **Update Version**
   ```bash
   # Update pyproject.toml version
   # Create git tag
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Build Package**
   ```bash
   # Build MCPB package
   cd mcpb
   mcpb pack . ../dist/
   ```

3. **Create Release**
   - GitHub release with changelog
   - Upload MCPB package
   - Update documentation

---

This developer guide provides comprehensive information for contributing to Advanced Memory MCP. Follow these guidelines to ensure consistent, high-quality contributions.
