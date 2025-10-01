"""Memory JSON import service for Basic Memory."""

import logging
from typing import Any, Dict, List

from basic_memory.config import get_project_config
from basic_memory.markdown.schemas import EntityFrontmatter, EntityMarkdown, Observation, Relation
from basic_memory.importers.base import Importer
from basic_memory.schemas.importer import EntityImportResult

logger = logging.getLogger(__name__)


class MemoryJsonImporter(Importer[EntityImportResult]):
    """Service for importing memory.json format data."""

    async def import_data(
        self, source_data, destination_folder: str = "", **kwargs: Any
    ) -> EntityImportResult:
        """Import entities and relations from a memory.json file.

        Args:
            source_data: Path to the memory.json file.
            destination_folder: Optional destination folder within the project.
            **kwargs: Additional keyword arguments.

        Returns:
            EntityImportResult containing statistics and status of the import.
        """
        config = get_project_config()
        try:
            # First pass - collect all relations by source entity
            entity_relations: Dict[str, List[Relation]] = {}
            entities: Dict[str, Dict[str, Any]] = {}

            # Ensure the base path exists
            base_path = config.home  # pragma: no cover
            if destination_folder:  # pragma: no cover
                base_path = self.ensure_folder_exists(destination_folder)

            # First pass - collect entities and relations
            for line in source_data:
                data = line
                if data["type"] == "entity":
                    entities[data["name"]] = data
                elif data["type"] == "relation":
                    # Store relation with its source entity
                    source = data.get("from") or data.get("from_id")
                    if source not in entity_relations:
                        entity_relations[source] = []
                    entity_relations[source].append(
                        Relation(
                            type=data.get("relationType") or data.get("relation_type"),
                            target=data.get("to") or data.get("to_id"),
                        )
                    )

            # Second pass - create and write entities
            entities_created = 0
            for name, entity_data in entities.items():
                # Ensure entity type directory exists
                entity_type_dir = base_path / entity_data["entityType"]
                entity_type_dir.mkdir(parents=True, exist_ok=True)

                entity = EntityMarkdown(
                    frontmatter=EntityFrontmatter(
                        metadata={
                            "type": entity_data["entityType"],
                            "title": name,
                            "permalink": f"{entity_data['entityType']}/{name}",
                        }
                    ),
                    content=f"# {name}\n",
                    observations=[Observation(content=obs) for obs in entity_data["observations"]],
                    relations=entity_relations.get(name, []),
                )

                # Write entity file
                file_path = base_path / f"{entity_data['entityType']}/{name}.md"
                await self.write_entity(entity, file_path)
                entities_created += 1

            relations_count = sum(len(rels) for rels in entity_relations.values())

            return EntityImportResult(
                import_count={"entities": entities_created, "relations": relations_count},
                success=True,
                entities=entities_created,
                relations=relations_count,
            )

        except Exception as e:  # pragma: no cover
            logger.exception("Failed to import memory.json")
            return self.handle_error("Failed to import memory.json", e)  # pyright: ignore [reportReturnType]
