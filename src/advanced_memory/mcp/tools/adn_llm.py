"""LLM management portmanteau tool for Advanced Memory MCP server.

This tool provides unified LLM management across multiple providers:
- Ollama (local models)
- LM Studio (local models via OpenAI-compatible API)
- OpenAI (hosted models)

Supports model listing, selection, loading, unloading, and status monitoring.
"""

import os
from typing import Literal

import httpx
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp

# Global state for current LLM configuration (exported for use by llm_client)
_current_provider: str | None = None
_current_model: str | None = None


@mcp.tool()
async def adn_llm(
    operation: Literal[
        "list_models",
        "list_providers",
        "select_model",
        "load_model",
        "unload_model",
        "status",
        "health",
    ],
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
) -> str:
    """Comprehensive LLM management tool for Advanced Memory.

    PORTMANTEAU PATTERN: Consolidates 7 LLM operations into one tool.

    SUPPORTED OPERATIONS:
    - list_models: List available models for a provider
    - list_providers: List available/configured providers
    - select_model: Select a model to use (doesn't load, just sets preference)
    - load_model: Load a model into memory (Ollama/LM Studio)
    - unload_model: Unload a model from memory (Ollama/LM Studio)
    - status: Get current LLM configuration and status
    - health: Check health of LLM providers

    PROVIDERS:
    - ollama: Local models via Ollama (default: http://localhost:11434)
    - lmstudio: Local models via LM Studio (default: http://localhost:1234)
    - openai: Hosted models via OpenAI API

    Args:
        operation: The operation to perform (list_models, list_providers, select_model, load_model, unload_model, status, health)
        provider: Provider name
                    * list_models, select_model, load_model, unload_model, health operations: REQUIRED - Provider name ("ollama", "lmstudio", "openai")
                    * Other operations: NOT USED
        model: Model name/identifier
                    * select_model, load_model operations: REQUIRED - Model name (e.g., "llama3", "gpt-4")
                    * unload_model operation: Optional - Specific model to unload (if not provided, unloads all)
                    * Other operations: NOT USED
        base_url: Custom base URL for provider (overrides defaults)
                    * list_models, load_model, unload_model, health operations: Optional - Custom base URL (defaults to provider default)
                    * Other operations: NOT USED
        api_key: API key (for OpenAI, or if required by provider)
                    * load_model operation: Optional - API key for OpenAI or custom providers
                    * Other operations: NOT USED

    Returns:
        Operation-specific result with model/provider information

    Examples:
        # List available providers
        adn_llm("list_providers")

        # List models for Ollama
        adn_llm("list_models", provider="ollama")

        # Load a model in Ollama
        adn_llm("load_model", provider="ollama", model="llama3")

        # Select OpenAI model
        adn_llm("select_model", provider="openai", model="gpt-4")

        # Check status
        adn_llm("status")
    """
    global _current_provider, _current_model

    try:
        if operation == "list_providers":
            return await _list_providers()

        elif operation == "list_models":
            if not provider:
                return "# Error\n\nProvider required for list_models operation.\n\nUse: adn_llm('list_models', provider='ollama')"
            return await _list_models(provider, base_url)

        elif operation == "select_model":
            if not provider or not model:
                return "# Error\n\nProvider and model required for select_model operation."
            _current_provider = provider
            _current_model = model

            # Save to persistent configuration
            try:
                from advanced_memory.config import ConfigManager

                config_manager = ConfigManager()
                config = config_manager.load_config()
                config.llm_provider = provider
                config.llm_model = model
                config_manager.save_config(config)
                logger.info(f"Saved LLM configuration: provider={provider}, model={model}")
            except Exception as e:
                logger.warning(f"Failed to save LLM configuration: {e}")

            return f"""# Model Selected

**Provider:** {provider}
**Model:** {model}

Model selection updated and saved to configuration. Use 'load_model' to load into memory (for local providers).
"""

        elif operation == "load_model":
            if not provider or not model:
                return "# Error\n\nProvider and model required for load_model operation."
            return await _load_model(provider, model, base_url, api_key)

        elif operation == "unload_model":
            if not provider:
                return "# Error\n\nProvider required for unload_model operation."
            return await _unload_model(provider, model, base_url)

        elif operation == "status":
            return await _get_status()

        elif operation == "health":
            return await _check_health(provider, base_url)

        else:
            return f"# Error\n\nUnknown operation: {operation}"

    except Exception as e:
        logger.error(f"LLM operation error: {e}", exc_info=True)
        return f"# Error\n\nFailed to execute operation: {str(e)}"


async def _list_providers() -> str:
    """List available LLM providers and their status."""
    providers = []

    # Check Ollama
    ollama_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            ollama_status = "available" if response.status_code == 200 else "unavailable"
    except Exception:
        ollama_status = "unavailable"

    providers.append(
        {
            "name": "ollama",
            "type": "local",
            "status": ollama_status,
            "default_url": "http://localhost:11434",
            "description": "Local models via Ollama",
        }
    )

    # Check LM Studio
    lmstudio_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:1234/v1/models")
            lmstudio_status = "available" if response.status_code == 200 else "unavailable"
    except Exception:
        lmstudio_status = "unavailable"

    providers.append(
        {
            "name": "lmstudio",
            "type": "local",
            "status": lmstudio_status,
            "default_url": "http://localhost:1234",
            "description": "Local models via LM Studio (OpenAI-compatible)",
        }
    )

    # Check OpenAI
    openai_status = "configured" if os.getenv("OPENAI_API_KEY") else "not_configured"
    providers.append(
        {
            "name": "openai",
            "type": "hosted",
            "status": openai_status,
            "default_url": "https://api.openai.com/v1",
            "description": "Hosted models via OpenAI API",
        }
    )

    status_emoji = {
        "available": "✅",
        "configured": "✅",
        "unavailable": "❌",
        "not_configured": "⚠️",
        "unknown": "❓",
    }

    result = "# Available LLM Providers\n\n"
    for p in providers:
        emoji = status_emoji.get(p["status"], "❓")
        result += f"{emoji} **{p['name']}** ({p['type']})\n"
        result += f"   Status: {p['status']}\n"
        result += f"   URL: {p['default_url']}\n"
        result += f"   {p['description']}\n\n"

    return result


async def _list_models(provider: str, base_url: str | None = None) -> str:
    """List available models for a provider."""
    if provider == "ollama":
        return await _list_ollama_models(base_url)
    elif provider == "lmstudio":
        return await _list_lmstudio_models(base_url)
    elif provider == "openai":
        return await _list_openai_models()
    else:
        return f"# Error\n\nUnknown provider: {provider}"


async def _list_ollama_models(base_url: str | None = None) -> str:
    """List models available in Ollama."""
    url = (base_url or "http://localhost:11434") + "/api/tags"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])

                if not models:
                    return "# Ollama Models\n\nNo models found. Install models with:\n```bash\nollama pull llama3\n```"

                result = "# Ollama Models\n\n"
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    size_gb = size / (1024**3) if size else 0
                    modified = model.get("modified_at", "")

                    result += f"**{name}**\n"
                    result += f"  Size: {size_gb:.2f} GB\n"
                    if modified:
                        result += f"  Modified: {modified}\n"
                    result += "\n"

                return result
            else:
                return f"# Error\n\nFailed to connect to Ollama: HTTP {response.status_code}\n\nMake sure Ollama is running: `ollama serve`"

    except httpx.RequestError as e:
        return f"# Error\n\nFailed to connect to Ollama: {str(e)}\n\nMake sure Ollama is running and accessible at {url}"


async def _list_lmstudio_models(base_url: str | None = None) -> str:
    """List models available in LM Studio."""
    url = (base_url or "http://localhost:1234") + "/v1/models"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])

                if not models:
                    return (
                        "# LM Studio Models\n\nNo models loaded. Load a model in LM Studio first."
                    )

                result = "# LM Studio Models\n\n"
                for model in models:
                    model_id = model.get("id", "Unknown")
                    result += f"**{model_id}**\n"

                return result
            else:
                return f"# Error\n\nFailed to connect to LM Studio: HTTP {response.status_code}\n\nMake sure LM Studio server is running."

    except httpx.RequestError as e:
        return f"# Error\n\nFailed to connect to LM Studio: {str(e)}\n\nMake sure LM Studio server is running at {url}"


async def _list_openai_models() -> str:
    """List available OpenAI models."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return """# OpenAI Models

**Status:** API key not configured

**Setup:**
1. Get API key from: https://platform.openai.com/api-keys
2. Set environment variable: `export OPENAI_API_KEY=your-key-here`

**Common Models:**
- gpt-4o (latest GPT-4)
- gpt-4-turbo
- gpt-3.5-turbo
- gpt-4
"""

    try:
        import openai

        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()

        result = "# OpenAI Models\n\n"
        gpt_models = [m for m in models.data if "gpt" in m.id.lower()]
        for model in sorted(gpt_models, key=lambda x: x.id):
            result += f"**{model.id}**\n"

        return result

    except ImportError:
        return "# Error\n\nOpenAI library not installed. Install with: `pip install openai`"
    except Exception as e:
        return f"# Error\n\nFailed to list OpenAI models: {str(e)}"


async def _load_model(
    provider: str, model: str, base_url: str | None = None, api_key: str | None = None
) -> str:
    """Load a model into memory (for local providers)."""
    if provider == "ollama":
        return await _load_ollama_model(model, base_url)
    elif provider == "lmstudio":
        return await _load_lmstudio_model(model, base_url)
    elif provider == "openai":
        return "# Info\n\nOpenAI models are hosted and don't need loading. Use 'select_model' to choose a model."
    else:
        return f"# Error\n\nUnknown provider: {provider}"


async def _load_ollama_model(model: str, base_url: str | None = None) -> str:
    """Load a model in Ollama."""
    url = (base_url or "http://localhost:11434") + "/api/generate"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Trigger model load by sending a simple generate request
            response = await client.post(
                url,
                json={"model": model, "prompt": "test", "stream": False},
            )

            if response.status_code == 200:
                return f"""# Model Loaded

**Provider:** Ollama
**Model:** {model}

Model is now loaded and ready to use.
"""
            else:
                error_text = response.text
                return (
                    f"# Error\n\nFailed to load model: HTTP {response.status_code}\n\n{error_text}"
                )

    except httpx.RequestError as e:
        return f"# Error\n\nFailed to connect to Ollama: {str(e)}\n\nMake sure Ollama is running."


async def _load_lmstudio_model(model: str, base_url: str | None = None) -> str:
    """Load a model in LM Studio."""
    # LM Studio loads models through its UI, but we can check if it's available
    url = (base_url or "http://localhost:1234") + "/v1/models"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("id") for m in data.get("data", [])]

                if model in models:
                    return f"""# Model Available

**Provider:** LM Studio
**Model:** {model}

Model is loaded and ready to use in LM Studio.
"""
                else:
                    return f"""# Model Not Loaded

**Provider:** LM Studio
**Model:** {model}

**Status:** Model not currently loaded

**To load:**
1. Open LM Studio
2. Select the model from the sidebar
3. Click "Start Server"
4. The model will be available for use

**Available models:** {", ".join(models) if models else "None"}
"""
            else:
                return f"# Error\n\nFailed to connect to LM Studio: HTTP {response.status_code}"

    except httpx.RequestError as e:
        return f"# Error\n\nFailed to connect to LM Studio: {str(e)}\n\nMake sure LM Studio server is running."


async def _unload_model(
    provider: str, model: str | None = None, base_url: str | None = None
) -> str:
    """Unload a model from memory (for local providers)."""
    if provider == "ollama":
        # Ollama doesn't have an explicit unload, but we can note it
        return """# Info

Ollama automatically manages memory. Models are unloaded when not in use.

**To free memory:**
- Stop using the model (it will be unloaded automatically)
- Or restart Ollama: `ollama serve`
"""
    elif provider == "lmstudio":
        return """# Info

LM Studio manages model loading through its UI.

**To unload:**
1. Open LM Studio
2. Click "Stop Server" in the sidebar
3. The model will be unloaded from memory
"""
    elif provider == "openai":
        return "# Info\n\nOpenAI models are hosted and don't need unloading."
    else:
        return f"# Error\n\nUnknown provider: {provider}"


async def _get_status() -> str:
    """Get current LLM configuration and status."""
    global _current_provider, _current_model

    result = "# LLM Status\n\n"

    # Check both in-memory state and persistent config
    from advanced_memory.config import ConfigManager

    config = ConfigManager().config
    active_provider = _current_provider or config.llm_provider
    active_model = _current_model or config.llm_model

    if active_provider and active_model:
        result += "**Current Configuration:**\n"
        result += f"- Provider: {active_provider}\n"
        result += f"- Model: {active_model}\n"
        if _current_provider and _current_model:
            result += "- **Status:** Active (in-memory)\n"
        elif config.llm_provider and config.llm_model:
            result += "- **Status:** Loaded from config (will be active on next use)\n"
        result += "\n"
    else:
        result += "**Current Configuration:** None\n"
        result += "**Status:** No LLM provider configured. Use `adn_llm('select_model', ...)` to configure.\n\n"

    result += "**Provider Status:**\n"
    result += await _list_providers()

    return result


async def _check_health(provider: str | None = None, base_url: str | None = None) -> str:
    """Check health of LLM providers."""
    if provider:
        providers_to_check = [provider]
    else:
        providers_to_check = ["ollama", "lmstudio", "openai"]

    result = "# LLM Provider Health Check\n\n"

    for prov in providers_to_check:
        if prov == "ollama":
            url = (base_url or "http://localhost:11434") + "/api/tags"
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        result += f"✅ **Ollama**: Healthy (connected to {url})\n"
                    else:
                        result += f"❌ **Ollama**: Unhealthy (HTTP {response.status_code})\n"
            except Exception as e:
                result += f"❌ **Ollama**: Unavailable ({str(e)})\n"

        elif prov == "lmstudio":
            url = (base_url or "http://localhost:1234") + "/v1/models"
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        result += f"✅ **LM Studio**: Healthy (connected to {url})\n"
                    else:
                        result += f"❌ **LM Studio**: Unhealthy (HTTP {response.status_code})\n"
            except Exception as e:
                result += f"❌ **LM Studio**: Unavailable ({str(e)})\n"

        elif prov == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                result += "✅ **OpenAI**: Configured (API key present)\n"
            else:
                result += "⚠️ **OpenAI**: Not configured (no API key)\n"

    return result
