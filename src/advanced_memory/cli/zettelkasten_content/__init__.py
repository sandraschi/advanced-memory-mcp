"""
Zettelkasten content templates for Advanced Memory onboarding.

This module contains high-quality, deeply interconnected notes across
multiple categories to serve as starter content for new users.
"""

from advanced_memory.cli.zettelkasten_content.developer import DEVELOPER_TEMPLATES
from advanced_memory.cli.zettelkasten_content.knowledge_worker import KNOWLEDGE_WORKER_TEMPLATES
from advanced_memory.cli.zettelkasten_content.researcher import RESEARCHER_TEMPLATES
from advanced_memory.cli.zettelkasten_content.writer import WRITER_TEMPLATES

__all__ = [
    "DEVELOPER_TEMPLATES",
    "RESEARCHER_TEMPLATES",
    "WRITER_TEMPLATES",
    "KNOWLEDGE_WORKER_TEMPLATES",
]
