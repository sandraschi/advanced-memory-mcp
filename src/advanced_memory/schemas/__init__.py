"""Knowledge graph schema exports.

This module exports all schema classes to simplify imports.
Rather than importing from individual schema files, you can
import everything from advanced_memory.schemas.
"""

# Base types and models
from advanced_memory.schemas.base import (
    Entity,
    EntityType,
    Observation,
    Relation,
    RelationType,
)

# Delete operation models
from advanced_memory.schemas.delete import (
    DeleteEntitiesRequest,
)
from advanced_memory.schemas.directory import (
    DirectoryNode,
)
from advanced_memory.schemas.project_info import (
    ActivityMetrics,
    ProjectInfoResponse,
    ProjectStatistics,
    SystemStatus,
)

# Request models
from advanced_memory.schemas.request import (
    CreateRelationsRequest,
    GetEntitiesRequest,
    SearchNodesRequest,
)

# Response models
from advanced_memory.schemas.response import (
    DeleteEntitiesResponse,
    EntityListResponse,
    EntityResponse,
    NoteContentResponse,
    ObservationResponse,
    RelationResponse,
    SearchNodesResponse,
    SQLAlchemyModel,
)

# For convenient imports, export all models
__all__ = [
    # Base
    "Observation",
    "EntityType",
    "RelationType",
    "Relation",
    "Entity",
    # Requests
    "SearchNodesRequest",
    "GetEntitiesRequest",
    "CreateRelationsRequest",
    # Responses
    "SQLAlchemyModel",
    "ObservationResponse",
    "RelationResponse",
    "EntityResponse",
    "NoteContentResponse",
    "EntityListResponse",
    "SearchNodesResponse",
    "DeleteEntitiesResponse",
    # Delete Operations
    "DeleteEntitiesRequest",
    # Project Info
    "ProjectStatistics",
    "ActivityMetrics",
    "SystemStatus",
    "ProjectInfoResponse",
    # Directory
    "DirectoryNode",
]
