import json
import shutil
from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from advanced_memory.markdown.entity_parser import EntityParser
from advanced_memory.repository.entity_repository import EntityRepository
from advanced_memory.repository.observation_repository import ObservationRepository
from advanced_memory.repository.project_repository import ProjectRepository
from advanced_memory.repository.relation_repository import RelationRepository
from advanced_memory.repository.search_repository import SearchRepository
from advanced_memory.schemas.base import Entity as EntitySchema
from advanced_memory.services.entity_service import EntityService
from advanced_memory.services.file_service import FileService
from advanced_memory.services.link_resolver import LinkResolver
from advanced_memory.services.search_service import SearchService
from advanced_memory.utils import generate_permalink


class PrefabManager:
    """Manages pre-fabricated test environments (Prefabs).

    A prefab is a folder containing a state.json and optional associated files.
    This manager handles:
    1. Loading prefab data.
    2. Seeding the database.
    3. Populating the filesystem.
    """

    def __init__(
        self,
        prefabs_dir: Path,
        session_maker: async_sessionmaker[AsyncSession],
        file_service: FileService,
        app_config: Any,
    ):
        self.prefabs_dir = prefabs_dir
        self.session_maker = session_maker
        self.file_service = file_service
        self.app_config = app_config
        self.project_repo = ProjectRepository(session_maker)

    async def load_prefab(self, name: str, project_name: str = "test-project") -> None:
        """Load a prefab by name into the specified project."""
        prefab_path = self.prefabs_dir / name
        state_file = prefab_path / "state.json"

        if not state_file.exists():
            raise FileNotFoundError(f"Prefab state file not found: {state_file}")

        with open(state_file) as f:
            data = json.load(f)

        # 1. Ensure project exists
        project = await self.project_repo.get_by_name(project_name)
        if not project:
            project = await self.project_repo.create(
                {"name": project_name, "path": str(self.file_service.base_path), "is_active": True}
            )

        # 2. Setup Repositories and Services
        entity_repo = EntityRepository(self.session_maker, project_id=project.id)
        obs_repo = ObservationRepository(self.session_maker, project_id=project.id)
        rel_repo = RelationRepository(self.session_maker, project_id=project.id)
        search_repo = SearchRepository(self.session_maker, project_id=project.id)

        # Initialize search service and link resolver for smart resolution
        from advanced_memory.repository.vector_repository import VectorRepository

        db_path = self.app_config.database_path
        vector_repo = VectorRepository(db_path=str(db_path.parent / "vectors"))

        search_service = SearchService(
            search_repository=search_repo,
            entity_repository=entity_repo,
            vector_repository=vector_repo,
            file_service=self.file_service,
            app_config=self.app_config,
        )
        link_resolver = LinkResolver(
            entity_repository=entity_repo,
            search_service=search_service,
        )

        # We use EntityService to handle file creation and DB insertion in sync
        # Note: We'll need a way to bypass full sync if we want to be fast,
        # but for now EntityService is safe.
        entity_parser = EntityParser(base_path=self.file_service.base_path)

        entity_service = EntityService(
            entity_parser=entity_parser,
            entity_repository=entity_repo,
            observation_repository=obs_repo,
            relation_repository=rel_repo,
            file_service=self.file_service,
            link_resolver=link_resolver,
        )

        # 3. Seed Entities
        entities_data = data.get("entities", [])
        created_entities = {}  # permalink -> entity

        for ent_data in entities_data:
            observations = ent_data.pop("observations", [])
            relations = ent_data.pop("relations", [])

            # Create entity (and its file)
            entity_schema = EntitySchema(**ent_data)
            entity, _ = await entity_service.create_or_update_entity(entity_schema)
            created_entities[entity.permalink] = entity

            # Add observations
            for obs_data in observations:
                await obs_repo.create({"entity_id": entity.id, "project_id": project.id, **obs_data})

            # Save relations for second pass
            ent_data["_pending_relations"] = relations

        # 4. Second pass: Seed Relations
        for ent_data in entities_data:
            entity = created_entities.get(
                ent_data.get("permalink") or generate_permalink(f"{ent_data['folder']}/{ent_data['title']}.md")
            )
            if not entity:
                continue

            relations = ent_data.get("_pending_relations", [])
            for rel_data in relations:
                target_permalink = rel_data.get("to_id")
                target_entity = created_entities.get(target_permalink)

                # Resolve IDs and Name
                to_id = target_entity.id if target_entity else None
                to_name = target_entity.title if target_entity else target_permalink

                await rel_repo.create(
                    {
                        "from_id": entity.id,
                        "to_id": to_id,
                        "to_name": to_name,
                        "relation_type": rel_data.get("relation_type"),
                        "context": rel_data.get("context"),
                        "project_id": project.id,
                    }
                )

        # 5. Copy static files if any
        files_dir = prefab_path / "files"
        if files_dir.exists():
            for item in files_dir.iterdir():
                dest = self.file_service.base_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        logger.info(f"Loaded prefab '{name}' into project '{project_name}'")

    async def clear_environment(self, project_name: str = "test-project") -> None:
        """Wipe DB and FS for the test project."""
        project = await self.project_repo.get_by_name(project_name)
        if not project:
            return

        # 1. Wipe DB records for this project
        async with self.session_maker() as session:
            from sqlalchemy import delete

            from advanced_memory.models.knowledge import Entity

            # Cascade delete from Entity handles Observation and Relation
            await session.execute(delete(Entity).where(Entity.project_id == project.id))
            await session.commit()

        # 2. Wipe FS (contents of project root)
        root_path = Path(project.path)
        if root_path.exists():
            for item in root_path.iterdir():
                if item.name == ".advanced-memory":  # Keep config if present
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        logger.info(f"Cleared environment for project '{project_name}'")
