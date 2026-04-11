"""API routers."""

from . import knowledge_router as knowledge
from . import management_router as management
from . import memory_router as memory
from . import project_router as project
from . import prompt_router as prompt
from . import resource_router as resource
from . import search_router as search
from . import tests_router as tests_router

__all__ = [
    "knowledge",
    "management",
    "memory",
    "project",
    "prompt",
    "resource",
    "search",
    "tests_router",
]
