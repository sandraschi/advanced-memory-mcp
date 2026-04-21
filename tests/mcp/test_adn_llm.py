"""Tests for adn_llm tool."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.mcp.tool_invoker import mcp_fn

from advanced_memory.mcp.tools.adn_llm import adn_llm


class TestAdnLLM:
    """Test adn_llm tool functionality."""

    @pytest.mark.asyncio
    async def test_list_providers(self):
        """Test listing LLM providers."""
        with patch("httpx.AsyncClient") as mock_client:
            # Mock Ollama unavailable
            mock_response_ollama = MagicMock()
            mock_response_ollama.status_code = 500
            # Mock LM Studio unavailable
            mock_response_lmstudio = MagicMock()
            mock_response_lmstudio.status_code = 500

            async def mock_get(url, **kwargs):
                if "11434" in url:
                    return mock_response_ollama
                elif "1234" in url:
                    return mock_response_lmstudio

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=mock_get)

            result = await mcp_fn(adn_llm)(operation="list_providers")
            assert "LLM Providers" in result
            assert "ollama" in result.lower()
            assert "lmstudio" in result.lower()
            assert "openai" in result.lower()

    @pytest.mark.asyncio
    async def test_list_models_ollama(self):
        """Test listing Ollama models."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [{"name": "llama3", "size": 1000000000, "modified_at": "2024-01-01"}]
            }
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await mcp_fn(adn_llm)(operation="list_models", provider="ollama")
            assert "Ollama Models" in result
            assert "llama3" in result

    @pytest.mark.asyncio
    async def test_select_model(self, app_config, config_manager):
        """Test selecting a model."""
        result = await mcp_fn(adn_llm)(operation="select_model", provider="ollama", model="llama3")
        assert "Model Selected" in result
        assert "ollama" in result
        assert "llama3" in result

        # Verify it's saved to config
        config = config_manager.load_config()
        assert config.llm_provider == "ollama"
        assert config.llm_model == "llama3"

    @pytest.mark.asyncio
    async def test_status(self, app_config, config_manager):
        """Test getting LLM status."""
        # Set config
        app_config.llm_provider = "ollama"
        app_config.llm_model = "llama3"
        config_manager.save_config(app_config)

        result = await mcp_fn(adn_llm)(operation="status")
        assert "LLM Status" in result
        assert "ollama" in result.lower()
        assert "llama3" in result.lower()

    @pytest.mark.asyncio
    async def test_health(self):
        """Test health check."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await mcp_fn(adn_llm)(operation="health")
            assert "Health Check" in result

    @pytest.mark.asyncio
    async def test_invalid_operation(self):
        """Test invalid operation."""
        result = await mcp_fn(adn_llm)(operation="invalid_operation")
        assert "Error" in result
        assert "Unknown operation" in result

    @pytest.mark.asyncio
    async def test_list_models_missing_provider(self):
        """Test list_models without provider."""
        result = await mcp_fn(adn_llm)(operation="list_models")
        assert "Error" in result
        assert "Provider required" in result

    @pytest.mark.asyncio
    async def test_select_model_missing_params(self):
        """Test select_model with missing parameters."""
        result = await mcp_fn(adn_llm)(operation="select_model")
        assert "Error" in result
        assert "Provider and model required" in result
