"""Behavioral tests for adn_research llm_config / llm_generate.

Regression (2026-09-19): both ops called adn_llm operations ("configure",
"generate") that never existed, so every call failed with "Invalid operation"
— wrapped as success. llm_config must delegate to select_model; llm_generate
must generate via services.llm_client.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from advanced_memory.mcp.tools.portmanteau_research import adn_research


def _select_envelope(provider="ollama", model="llama3.1:8b"):
    return {
        "success": True,
        "message": f"Perfect! Model selection updated: {provider}/{model}",
        "operation": "select_model",
        "technical_summary": f"Model selection updated: {provider}/{model}",
        "result": {"provider": provider, "model": model, "status": "selected and saved"},
    }


class TestLlmConfig:
    @pytest.mark.asyncio
    async def test_missing_params(self):
        result = await adn_research(operation="llm_config")
        assert isinstance(result, dict)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_delegates_to_select_model(self):
        envelope = _select_envelope()
        with patch("advanced_memory.mcp.tools.adn_llm.adn_llm") as mock_tool:
            mock_tool.fn = AsyncMock(return_value=envelope)
            result = await adn_research(operation="llm_config", provider="ollama", model="llama3.1:8b")

        mock_tool.fn.assert_awaited_once_with(operation="select_model", provider="ollama", model="llama3.1:8b")
        assert result["success"] is True
        assert result["operation"] == "llm_config"
        assert result["result"]["provider"] == "ollama"
        assert result["result"]["model"] == "llama3.1:8b"

    @pytest.mark.asyncio
    async def test_propagates_inner_error(self):
        inner_error = {
            "success": False,
            "error": "Missing parameters",
            "error_code": "MISSING_PARAMETERS",
            "message": "Provider and model required",
        }
        with patch("advanced_memory.mcp.tools.adn_llm.adn_llm") as mock_tool:
            mock_tool.fn = AsyncMock(return_value=inner_error)
            result = await adn_research(operation="llm_config", provider="ollama", model="x")

        assert result["success"] is False
        assert result == inner_error


class TestLlmGenerate:
    @pytest.mark.asyncio
    async def test_missing_content(self):
        result = await adn_research(operation="llm_generate")
        assert isinstance(result, dict)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_generates_via_llm_client(self):
        fake_client = MagicMock()
        fake_client.provider = "lmstudio"
        fake_client.model = "test-model"
        fake_client.generate = AsyncMock(return_value="hello world")
        with patch("advanced_memory.services.llm_client.get_llm_client", return_value=fake_client) as mock_factory:
            result = await adn_research(operation="llm_generate", content="Say hi")

        mock_factory.assert_called_once_with(provider=None, model=None)
        fake_client.generate.assert_awaited_once_with("Say hi")
        assert result["success"] is True
        assert result["result"] == {
            "provider": "lmstudio",
            "model": "test-model",
            "text": "hello world",
        }

    @pytest.mark.asyncio
    async def test_forwards_provider_model_override(self):
        fake_client = MagicMock()
        fake_client.provider = "ollama"
        fake_client.model = "llama3.1:8b"
        fake_client.generate = AsyncMock(return_value="ok")
        with patch("advanced_memory.services.llm_client.get_llm_client", return_value=fake_client) as mock_factory:
            await adn_research(
                operation="llm_generate",
                content="hi",
                provider="ollama",
                model="llama3.1:8b",
            )

        mock_factory.assert_called_once_with(provider="ollama", model="llama3.1:8b")

    @pytest.mark.asyncio
    async def test_generation_failure_is_error_envelope(self):
        fake_client = MagicMock()
        fake_client.generate = AsyncMock(side_effect=Exception("connection refused"))
        with patch("advanced_memory.services.llm_client.get_llm_client", return_value=fake_client):
            result = await adn_research(operation="llm_generate", content="hi")

        assert result["success"] is False
        assert "connection refused" in result["message"]
        assert result["recovery_options"]


class TestRewiredBranches:
    """2026-09-19: tvtropes/rag_query/research_orchestrate passed the query
    string positionally into a required `operation` param, so every call
    failed. These lock the corrected delegation kwargs."""

    @pytest.mark.asyncio
    async def test_tvtropes_passes_operation(self):
        with patch(
            "advanced_memory.mcp.beta.adn_tvtropes_research.adn_tvtropes_research",
            new=AsyncMock(return_value={"ok": True}),
        ) as mock_fn:
            result = await adn_research(operation="tvtropes", query="hero")

        mock_fn.assert_awaited_once_with(operation="search_tropes", query="hero", max_results=5)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_rag_query_passes_operation(self):
        with patch("advanced_memory.mcp.tools.adn_rag.adn_rag", new=AsyncMock(return_value={"chunks": []})) as mock_fn:
            result = await adn_research(operation="rag_query", query="something")

        mock_fn.assert_awaited_once_with(operation="query_knowledge", query="something")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_research_orchestrate_passes_operation_topic(self):
        with patch(
            "advanced_memory.mcp.tools.research_orchestrator.research_orchestrator",
            new=AsyncMock(return_value="# plan"),
        ) as mock_fn:
            result = await adn_research(operation="research_orchestrate", query="quantum")

        mock_fn.assert_awaited_once_with(operation="research_plan", topic="quantum")
        assert result["success"] is True


class TestRegistration:
    @pytest.mark.asyncio
    async def test_adn_research_served_by_server(self):
        import advanced_memory.mcp.server  # importing registers tools
        from advanced_memory.mcp.mcp_instance import mcp

        tools = await mcp.list_tools()
        assert "adn_research" in [t.name for t in tools]
