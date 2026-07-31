"""Tests for LLM client service."""

import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from advanced_memory.services.llm_client import LLMClient, get_llm_client


class TestLLMClient:
    """Test LLM client functionality."""

    def test_llm_client_init_defaults(self):
        """Test LLM client initialization with defaults."""
        client = LLMClient()
        assert client.provider in ["ollama", "lmstudio", "openai"]
        assert client.model is not None

    def test_llm_client_init_with_provider(self):
        """Test LLM client initialization with explicit provider."""
        with patch.object(LLMClient, "_check_provider_available", return_value=True):
            client = LLMClient(provider="ollama", model="llama3")
        assert client.provider == "ollama"
        assert client.model == "llama3"

    @pytest.mark.asyncio
    async def test_generate_ollama(self):
        """Test Ollama generation."""
        with patch.object(LLMClient, "_check_provider_available", return_value=True):
            client = LLMClient(provider="ollama", model="llama3", base_url="http://localhost:11434")

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "Test response"}
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            result = await client.generate("Test prompt")
            assert result == "Test response"

    @pytest.mark.asyncio
    async def test_generate_lmstudio(self):
        """Test LM Studio generation."""
        with patch.object(LLMClient, "_check_provider_available", return_value=True):
            client = LLMClient(provider="lmstudio", model="local-model", base_url="http://localhost:1234")

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            result = await client.generate("Test prompt")
            assert result == "Test response"

    @pytest.mark.asyncio
    async def test_generate_openai(self):
        """Test OpenAI generation."""
        import os

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):  # pragma: allowlist secret
            # openai is an optional dependency; inject a fake module so the
            # import inside _generate_openai resolves without it being installed
            fake_openai = ModuleType("openai")
            fake_openai.AsyncOpenAI = MagicMock()
            with patch.dict(sys.modules, {"openai": fake_openai}):
                client = LLMClient(provider="openai", model="gpt-3.5-turbo")

                with patch("openai.AsyncOpenAI") as mock_openai:
                    mock_response = MagicMock()
                    mock_response.choices = [MagicMock()]
                    mock_response.choices[0].message.content = "Test response"
                    mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

                    result = await client.generate("Test prompt")
                    assert result == "Test response"

    @pytest.mark.asyncio
    async def test_generate_json(self):
        """Test JSON generation."""
        client = LLMClient(provider="ollama", model="llama3", base_url="http://localhost:11434")

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": '{"key": "value"}'}
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            result = await client.generate_json("Test prompt")
            assert result == {"key": "value"}

    def test_get_llm_client_with_params(self):
        """Test get_llm_client with explicit parameters."""
        with patch.object(LLMClient, "_check_provider_available", return_value=True):
            client = get_llm_client(provider="ollama", model="llama3")
        assert client.provider == "ollama"
        assert client.model == "llama3"

    def test_get_llm_client_from_config(self, app_config, monkeypatch):
        """Test get_llm_client loading from config."""
        app_config.llm_provider = "ollama"
        app_config.llm_model = "llama3"

        # Ensure the adn_llm global state path is not taken (config fallback is
        # what this test exercises), and mock where ConfigManager is imported
        monkeypatch.delitem(sys.modules, "advanced_memory.mcp.tools.adn_llm", raising=False)
        with patch("advanced_memory.config.ConfigManager") as mock_config:
            mock_config.return_value.config = app_config
            with patch.object(LLMClient, "_check_provider_available", return_value=True):
                client = get_llm_client()
            assert client.provider == "ollama"
            assert client.model == "llama3"
