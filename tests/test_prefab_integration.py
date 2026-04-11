import pytest

from advanced_memory.repository.entity_repository import EntityRepository
from advanced_memory.repository.observation_repository import ObservationRepository


@pytest.mark.asyncio
async def test_prefab_standard_loading(prefab_standard, session_maker, file_service):
    """Verify that the standard prefab is correctly loaded with entities and observations."""
    # 1. Check Entities
    entity_repo = EntityRepository(session_maker, project_id=1)  # Assume project_id 1
    entities = await entity_repo.find_all()

    titles = [e.title for e in entities]
    assert "Project Glenn" in titles
    assert "FastMCP" in titles
    assert "Sandra Schipal" in titles

    # 2. Check Filesystem
    project_glenn_file = file_service.base_path / "projects" / "Project_Glenn.md"
    assert project_glenn_file.exists()
    content = project_glenn_file.read_text()
    assert "# Project Glenn" in content

    # 3. Check Observations
    obs_repo = ObservationRepository(session_maker, project_id=1)
    # Find Project Glenn entity
    glenn = next(e for e in entities if e.title == "Project Glenn")
    observations = await obs_repo.find_by_entity(glenn.id)

    obs_contents = [o.content for o in observations]
    assert "Uses SOTA 2026 patterns" in obs_contents
    assert "Managed by Sandra Schipal" in obs_contents


@pytest.mark.asyncio
async def test_prefab_manager_clear(prefab_manager, prefab_standard, session_maker, file_service):
    """Verify that clearing the environment actually wipes it."""
    # Clear it
    await prefab_manager.clear_environment("test-project")

    # Check Entities
    entity_repo = EntityRepository(session_maker, project_id=1)
    entities = await entity_repo.find_all()
    assert len(entities) == 0

    # Check Filesystem
    project_root = file_service.base_path
    items = list(project_root.iterdir())
    # Should only have .advanced-memory or be empty
    visible_items = [i for i in items if not i.name.startswith(".")]
    assert len(visible_items) == 0
