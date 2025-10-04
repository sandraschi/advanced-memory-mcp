"""Knowledge graph schema exports.

This module exports all schema classes to simplify imports.
Rather than importing from individual schema files, you can
import everything from advanced_memory.schemas.
"""

# Base types and models
from advanced_memory.schemas.base import (
    Observation,
    EntityType,
    RelationType,
    Relation,
    Entity,
)

# Delete operation models
from advanced_memory.schemas.delete import (
    DeleteEntitiesRequest,
)

# Request models
from advanced_memory.schemas.request import (
    SearchNodesRequest,
    GetEntitiesRequest,
    CreateRelationsRequest,
)

# Response models
from advanced_memory.schemas.response import (
    SQLAlchemyModel,
    ObservationResponse,
    RelationResponse,
    EntityResponse,
    EntityListResponse,
    SearchNodesResponse,
    DeleteEntitiesResponse,
)

from advanced_memory.schemas.project_info import (
    ProjectStatistics,
    ActivityMetrics,
    SystemStatus,
    ProjectInfoResponse,
)

from advanced_memory.schemas.directory import (
    DirectoryNode,
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
