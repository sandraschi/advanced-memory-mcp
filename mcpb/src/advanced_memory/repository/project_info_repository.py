from advanced_memory.models.project import Project
from advanced_memory.repository.repository import Repository


class ProjectInfoRepository(Repository):
    """Repository for statistics queries."""

    def __init__(self, session_maker):
        # Initialize with Project model as a reference
        super().__init__(session_maker, Project)
