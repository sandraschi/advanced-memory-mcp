from httpx import ASGITransport, AsyncClient, Timeout
from loguru import logger

from advanced_memory.api.app import app as fastapi_app
from advanced_memory.config import ConfigManager

# Prevent indefinite hangs: entity create/update can involve file I/O, DB, search indexing
DEFAULT_REQUEST_TIMEOUT = 120.0

_client_instance: AsyncClient | None = None


def create_client() -> AsyncClient:
    """Create an HTTP client based on configuration.

    Returns:
        AsyncClient configured for either local ASGI or remote HTTP transport
    """
    config_manager = ConfigManager()
    config = config_manager.load_config()
    timeout = Timeout(DEFAULT_REQUEST_TIMEOUT)

    if config.api_url:
        logger.info(f"Creating HTTP client for remote Advanced Memory API: {config.api_url}")
        return AsyncClient(base_url=config.api_url, timeout=timeout)
    else:
        from advanced_memory.api.app import app as fastapi_app

        logger.debug("Creating ASGI client for local Advanced Memory API")
        return AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test", timeout=timeout)


class _LazyClient:
    _instance: AsyncClient | None = None

    def __getattr__(self, name):
        if self._instance is None:
            self._instance = create_client()
        return getattr(self._instance, name)


client: AsyncClient = _LazyClient()  # type: ignore[assignment]
