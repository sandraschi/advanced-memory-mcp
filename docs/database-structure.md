# Database Structure

This document describes the database schema for the Basic Memory application.

## Overview

The Basic Memory application uses SQLite as its database engine with SQLAlchemy as the ORM. The database is designed to store knowledge entities, their relationships, and project information.

## Tables

### Project

Represents a collection of knowledge entities that are grouped together. Projects provide context for all knowledge operations.

**Table Name:** `project`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Project name (unique) |
| permalink | String | URL-friendly identifier (unique) |
| description | Text | Project description |
| path | String | Filesystem path to the project |
| is_active | Boolean | Whether the project is active |
| is_default | Boolean | Whether this is the default project |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `entities`: One-to-many relationship with Entity

### Entity

Core entity in the knowledge graph representing semantic nodes maintained by the AI layer.

**Table Name:** `entity`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| entity_type | String | Type of entity (e.g., 'note', 'document', 'person') |
| title | String | Display name of the entity |
| permalink | String | URL-friendly identifier |
| file_path | String | Relative path to the file on disk |
| content_type | String | MIME type of the content |
| checksum | String | Hash of the file content for change detection |
| metadata | JSON | Additional metadata about the entity |
| project_id | Integer | Foreign key to Project |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Relationships:**
- `project`: Many-to-one relationship with Project
- `observations`: One-to-many relationship with Observation
- `incoming_relations`: One-to-many relationship with Relation (where this is the target)
- `outgoing_relations`: One-to-many relationship with Relation (where this is the source)

### Observation

An observation represents an atomic fact or note about an entity.

**Table Name:** `observation`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| entity_id | Integer | Foreign key to Entity |
| category | String | Category of the observation |
| content | Text | The observation content |
| created_at | DateTime | Creation timestamp |

**Relationships:**
- `entity`: Many-to-one relationship with Entity

### Relation

Represents a directed relationship between two entities.

**Table Name:** `relation`

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| from_id | Integer | Foreign key to source Entity |
| to_id | Integer | Foreign key to target Entity (nullable) |
| to_name | String | Name of target entity (used when to_id is null) |
| relation_type | String | Type of relationship |
| metadata | JSON | Additional metadata about the relationship |
| created_at | DateTime | Creation timestamp |

**Relationships:**
- `from_entity`: Many-to-one relationship with Entity (source)
- `to_entity`: Many-to-one relationship with Entity (target, optional)

## Indexes

- `project`:
  - `ix_project_name`: Index on name (unique)
  - `ix_project_permalink`: Index on permalink (unique)

- `entity`:
  - `ix_entity_type`: Index on entity_type
  - `ix_entity_permalink`: Index on permalink
  - `ix_entity_file_path`: Index on file_path
  - `ix_entity_project_id`: Index on project_id (foreign key)

- `observation`:
  - `ix_observation_entity_id`: Index on entity_id (foreign key)
  - `ix_observation_category`: Index on category

- `relation`:
  - `uix_relation_from_id_to_id`: Unique constraint on (from_id, to_id, relation_type)
  - `uix_relation_from_id_to_name`: Unique constraint on (from_id, to_name, relation_type)
  - `ix_relation_type`: Index on relation_type
  - `ix_relation_from_id`: Index on from_id (foreign key)
  - `ix_relation_to_id`: Index on to_id (foreign key)

## Database Initialization

The database is initialized using SQLAlchemy's async engine. The application supports both in-memory and file-based SQLite databases.

### Connection URL Format
- In-memory: `sqlite+aiosqlite://`
- File-based: `sqlite+aiosqlite:///path/to/database.db`

### Database Migrations

Database schema changes should be managed using Alembic migrations. The migration scripts are located in the `migrations` directory.

## Best Practices

1. **Foreign Keys**: Always use foreign key constraints to maintain referential integrity.
2. **Indexes**: Add indexes for frequently queried columns and foreign keys.
3. **Timestamps**: All tables include `created_at` and `updated_at` timestamps for auditing.
4. **Soft Deletes**: Consider implementing soft deletes for important data.
5. **Migrations**: Always use migrations for schema changes to support different environments.
