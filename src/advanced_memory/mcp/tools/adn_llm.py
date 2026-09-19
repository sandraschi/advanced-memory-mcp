"""LLM management portmanteau tool for Advanced Memory MCP server.

This tool provides unified LLM management across multiple providers:
- Ollama (local models)
- LM Studio (local models via OpenAI-compatible API)
- OpenAI (hosted models)

Supports model listing, selection, loading, unloading, and status monitoring.

RESPONSES:
Success: {"success": true, "operation": "...", "summary": "...", "result": {...}}
Error: {"success": false, "error": "...", "error_code": "...", "message": "...", "recovery_options": [...]}

For errors, check recovery_options for next steps.
"""

import os
from typing import Literal

import httpx
from loguru import logger

from advanced_memory.mcp.mcp_instance import mcp
from advanced_memory.mcp.tools.utils import build_error_response, build_success_response

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
) -> dict:
    """LLM Portmanteau for Advanced Memory.

    This tool consolidates the entire LLM lifecycle management, providing a
    unified interface for local and hosted model providers.

    ---------------------------------------------------------------------------
    [PORTMANTEAU PATTERN RATIONALE]
    Consolidates LLM lifecycle management into one tool to unify configuration across disparate providers.

    ---------------------------------------------------------------------------
    [SUPPORTED OPERATIONS]
    - list_models: List available models for a specific provider.
    - list_providers: Enumerate configured and detected providers.
    - select_model: Persist model selection preferences.
    - load_model: Explicitly load model into memory (for local providers).
    - unload_model: Free up system resources (for local providers).
    - status: Current configuration and active model state.
    - health: Connectivity check for all configured providers.

    ---------------------------------------------------------------------------
    [PROVIDERS]
    - ollama: Local inference via Ollama (default: localhost:11434).
    - lmstudio: Local OpenAI-compatible server (default: localhost:1234).
    - openai: Hosted API (requires OPENAI_API_KEY).

    ---------------------------------------------------------------------------
    [OPERATIONS DETAIL]

    list_models: Discovery
    - Parameters: provider (required), base_url (optional).
    - Returns: List of available model identifiers and metadata.
    - Use when: exploring available models to use.

    select_model: Configuration
    - Parameters: provider (required), model (required).
    - Function: Updates persistent configuration.
    - Use when: Switching your preferred default model.

    load_model: Resource Management
    - Parameters: provider (required), model (required).
    - Use when: Pre-warming a local model before intensive tasks.

    status: System State
    - Returns: Current active model, provider health, and config.
    - Use when: Debugging LLM connection issues.

    ---------------------------------------------------------------------------
    [PARAMETERS]
    - operation (str): The LLM operation to perform (Required).
    - provider (str): Provider identifier ("ollama", "lmstudio", "openai").
    - model (str): Model identifier (e.g., "llama3", "gpt-4").
    - base_url (str): Custom API endpoint URL.
    - api_key (str): API key for hosted providers.

    ---------------------------------------------------------------------------
    [EXAMPLES]

    - Check current status:
      adn_llm(operation="status")

    - Switch to local model:
      adn_llm(operation="select_model", provider="ollama", model="llama3:8b")

    - List OpenAI models:
      adn_llm(operation="list_models", provider="openai")

    ---------------------------------------------------------------------------
    [ERRORS]
    - Provider Required: Missing provider for list/load operations.
    - Connection Failed: Unable to reach the specified LLM service.
    - Model Not Found: Specified model does not exist on the provider.
    """
    global _current_provider, _current_model

    try:
        if operation == "list_providers":
            return await _list_providers()

        elif operation == "list_models":
            if not provider:
                return build_error_response(
                    error="Missing provider",
                    error_code="PROVIDER_REQUIRED",
                    message="Provider required for list_models operation.",
                    recovery_options=["Provide 'provider' parameter (e.g., 'ollama', 'lmstudio', 'openai')"],
                )
            return await _list_models(provider, base_url)

        elif operation == "select_model":
            if not provider or not model:
                return build_error_response(
                    error="Missing parameters",
                    error_code="MISSING_PARAMETERS",
                    message="Provider and model required for select_model operation.",
                    recovery_options=["Provide both 'provider' and 'model' parameters"],
                )
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

            summary = f"Model selection updated: {provider}/{model}"
            return build_success_response(
                operation="select_model",
                summary=summary,
                result={
                    "provider": provider,
                    "model": model,
                    "status": "selected and saved",
                },
            )

        elif operation == "load_model":
            if not provider or not model:
                return build_error_response(
                    error="Missing parameters",
                    error_code="MISSING_PARAMETERS",
                    message="Provider and model required for load_model operation.",
                    recovery_options=["Provide both 'provider' and 'model' parameters"],
                )
            return await _load_model(provider, model, base_url, api_key)

        elif operation == "unload_model":
            if not provider:
                return build_error_response(
                    error="Missing provider",
                    error_code="PROVIDER_REQUIRED",
                    message="Provider required for unload_model operation.",
                    recovery_options=["Provide 'provider' parameter"],
                )
            return await _unload_model(provider, model, base_url)

        elif operation == "status":
            return await _get_status()

        elif operation == "health":
            return await _check_health(provider, base_url)

        else:
            return build_error_response(
                error="Invalid operation",
                error_code="INVALID_OPERATION",
                message=f"Unknown operation: {operation}",
                recovery_options=[
                    "Use one of: list_models, list_providers, select_model, load_model, unload_model, status, health"
                ],
            )

    except Exception as e:
        logger.error(f"LLM operation error: {e}", exc_info=True)
        return build_error_response(
            error="Execution failed",
            error_code="EXECUTION_ERROR",
            message=str(e),
            technical_details=str(e),
        )


async def _list_providers() -> dict:
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

    # Check Local Llama (llama.cpp server, e.g. Muse Glimmer 30B on :11435)
    local_llama_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://127.0.0.1:11435/v1/models")
            local_llama_status = "available" if response.status_code == 200 else "unavailable"
    except Exception:
        local_llama_status = "unavailable"

    providers.append(
        {
            "name": "local-llama",
            "type": "local",
            "status": local_llama_status,
            "default_url": "http://127.0.0.1:11435",
            "description": "Muse Glimmer 30B via llama.cpp (multimodal, DFlash drafter)",
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

    lines = ["# Available LLM Providers", ""]
    for p in providers:
        emoji = status_emoji.get(p["status"], "❓")
        lines.append(f"{emoji} **{p['name']}** ({p['type']})")
        lines.append(f"   Status: {p['status']}")
        lines.append(f"   URL: {p['default_url']}")
        lines.append(f"   {p['description']}")
        lines.append("")
    markdown = "\n".join(lines)

    # NOTE: must return a dict envelope, not the markdown string. FastMCP
    # validates structured_content against the `-> dict` annotation and
    # rejects bare strings (2026-09-19: "structured_content must be a dict").
    return build_success_response(
        operation="list_providers",
        summary=f"{len(providers)} providers checked",
        result={"providers": providers, "markdown": markdown},
    )


async def _list_models(provider: str, base_url: str | None = None) -> dict:
    """List available models for a provider."""
    if provider == "ollama":
        return await _list_ollama_models(base_url)
    elif provider == "lmstudio":
        return await _list_lmstudio_models(base_url)
    elif provider == "openai":
        return await _list_openai_models()
    else:
        return build_error_response(
            error="Unknown provider",
            error_code="UNKNOWN_PROVIDER",
            message=f"Unknown provider: {provider}",
            recovery_options=["Use one of: ollama, lmstudio, openai"],
        )


async def _list_ollama_models(base_url: str | None = None) -> dict:
    """List models available in Ollama."""
    url = (base_url or "http://localhost:11434") + "/api/tags"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])

                if not models:
                    return build_success_response(
                        operation="list_models",
                        summary="Ollama reachable, no models installed",
                        result={
                            "provider": "ollama",
                            "models": [],
                            "markdown": "# Ollama Models\n\nNo models found. Install models with:\n```bash\nollama pull llama3\n```",
                        },
                    )

                lines = ["# Ollama Models", ""]
                items = []
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    size_gb = size / (1024**3) if size else 0
                    modified = model.get("modified_at", "")

                    lines.append(f"**{name}**")
                    lines.append(f"  Size: {size_gb:.2f} GB")
                    if modified:
                        lines.append(f"  Modified: {modified}")
                    lines.append("")
                    items.append({"name": name, "size_bytes": size, "modified_at": modified})

                return build_success_response(
                    operation="list_models",
                    summary=f"{len(items)} Ollama models",
                    result={
                        "provider": "ollama",
                        "models": items,
                        "markdown": "\n".join(lines),
                    },
                )
            else:
                return build_error_response(
                    error="Ollama connection failed",
                    error_code="CONNECTION_FAILED",
                    message=f"Failed to connect to Ollama: HTTP {response.status_code}. Make sure Ollama is running: `ollama serve`",
                    recovery_options=[f"Start Ollama (`ollama serve`), then retry at {url}"],
                )

    except httpx.RequestError as e:
        return build_error_response(
            error="Ollama connection failed",
            error_code="CONNECTION_FAILED",
            message=f"Failed to connect to Ollama: {e!s}. Make sure Ollama is running and accessible at {url}",
            recovery_options=[f"Start Ollama (`ollama serve`), then retry at {url}"],
        )


async def _list_lmstudio_models(base_url: str | None = None) -> dict:
    """List models available in LM Studio."""
    url = (base_url or "http://localhost:1234") + "/v1/models"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])

                if not models:
                    return build_success_response(
                        operation="list_models",
                        summary="LM Studio reachable, no models loaded",
                        result={
                            "provider": "lmstudio",
                            "models": [],
                            "markdown": "# LM Studio Models\n\nNo models loaded. Load a model in LM Studio first.",
                        },
                    )

                lines = ["# LM Studio Models", ""]
                items = []
                for model in models:
                    model_id = model.get("id", "Unknown")
                    lines.append(f"**{model_id}**")
                    items.append({"id": model_id})

                return build_success_response(
                    operation="list_models",
                    summary=f"{len(items)} LM Studio models",
                    result={
                        "provider": "lmstudio",
                        "models": items,
                        "markdown": "\n".join(lines),
                    },
                )
            else:
                return build_error_response(
                    error="LM Studio connection failed",
                    error_code="CONNECTION_FAILED",
                    message=f"Failed to connect to LM Studio: HTTP {response.status_code}. Make sure LM Studio server is running.",
                    recovery_options=[f"Start the LM Studio server, then retry at {url}"],
                )

    except httpx.RequestError as e:
        return build_error_response(
            error="LM Studio connection failed",
            error_code="CONNECTION_FAILED",
            message=f"Failed to connect to LM Studio: {e!s}. Make sure LM Studio server is running at {url}",
            recovery_options=[f"Start the LM Studio server, then retry at {url}"],
        )


async def _list_openai_models() -> dict:
    """List available OpenAI models."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return build_error_response(
            error="OpenAI API key not configured",
            error_code="NOT_CONFIGURED",
            message="OpenAI API key not configured. Get one at https://platform.openai.com/api-keys and set OPENAI_API_KEY.",
            recovery_options=[
                "Set the OPENAI_API_KEY environment variable",
                "Use a local provider instead (ollama / lmstudio)",
            ],
        )

    try:
        import openai

        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()

        lines = ["# OpenAI Models", ""]
        items = []
        gpt_models = [m for m in models.data if "gpt" in m.id.lower()]
        for model in sorted(gpt_models, key=lambda x: x.id):
            lines.append(f"**{model.id}**")
            items.append({"id": model.id})

        return build_success_response(
            operation="list_models",
            summary=f"{len(items)} OpenAI models",
            result={
                "provider": "openai",
                "models": items,
                "markdown": "\n".join(lines),
            },
        )

    except ImportError:
        return build_error_response(
            error="OpenAI library not installed",
            error_code="MISSING_DEPENDENCY",
            message="OpenAI library not installed. Install with: `pip install openai`",
            recovery_options=["Install the openai package, or use a local provider"],
        )
    except Exception as e:
        return build_error_response(
            error="OpenAI listing failed",
            error_code="EXECUTION_ERROR",
            message=f"Failed to list OpenAI models: {e!s}",
        )


async def _load_model(provider: str, model: str, base_url: str | None = None, api_key: str | None = None) -> dict:
    """Load a model into memory (for local providers)."""
    if provider == "ollama":
        return await _load_ollama_model(model, base_url)
    elif provider == "lmstudio":
        return await _load_lmstudio_model(model, base_url)
    elif provider == "openai":
        return build_success_response(
            operation="load_model",
            summary="OpenAI models are hosted, nothing to load",
            result={
                "provider": provider,
                "model": model,
                "loaded": False,
                "markdown": "# Info\n\nOpenAI models are hosted and don't need loading. Use 'select_model' to choose a model.",
            },
        )
    else:
        return build_error_response(
            error="Unknown provider",
            error_code="UNKNOWN_PROVIDER",
            message=f"Unknown provider: {provider}",
            recovery_options=["Use one of: ollama, lmstudio, openai"],
        )


async def _load_ollama_model(model: str, base_url: str | None = None) -> dict:
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
                return build_success_response(
                    operation="load_model",
                    summary=f"Ollama model loaded: {model}",
                    result={
                        "provider": "ollama",
                        "model": model,
                        "loaded": True,
                        "markdown": f"# Model Loaded\n\n**Provider:** Ollama\n**Model:** {model}\n\nModel is now loaded and ready to use.",
                    },
                )
            else:
                return build_error_response(
                    error="Ollama load failed",
                    error_code="LOAD_FAILED",
                    message=f"Failed to load model: HTTP {response.status_code}\n\n{response.text}",
                    recovery_options=["Check the model name (`ollama list`), then retry"],
                )

    except httpx.RequestError as e:
        return build_error_response(
            error="Ollama connection failed",
            error_code="CONNECTION_FAILED",
            message=f"Failed to connect to Ollama: {e!s}. Make sure Ollama is running.",
        )


async def _load_lmstudio_model(model: str, base_url: str | None = None) -> dict:
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
                    return build_success_response(
                        operation="load_model",
                        summary=f"LM Studio model available: {model}",
                        result={
                            "provider": "lmstudio",
                            "model": model,
                            "loaded": True,
                            "markdown": f"# Model Available\n\n**Provider:** LM Studio\n**Model:** {model}\n\nModel is loaded and ready to use in LM Studio.",
                        },
                    )
                else:
                    available = ", ".join(models) if models else "None"
                    return build_error_response(
                        error="Model not loaded",
                        error_code="MODEL_NOT_LOADED",
                        message=f"Model not currently loaded in LM Studio: {model}. Available models: {available}",
                        recovery_options=[
                            "Open LM Studio, select the model from the sidebar, click Start Server",
                        ],
                    )
            else:
                return build_error_response(
                    error="LM Studio connection failed",
                    error_code="CONNECTION_FAILED",
                    message=f"Failed to connect to LM Studio: HTTP {response.status_code}",
                )

    except httpx.RequestError as e:
        return build_error_response(
            error="LM Studio connection failed",
            error_code="CONNECTION_FAILED",
            message=f"Failed to connect to LM Studio: {e!s}. Make sure LM Studio server is running.",
        )


async def _unload_model(provider: str, model: str | None = None, base_url: str | None = None) -> dict:
    """Unload a model from memory (for local providers)."""
    notes = {
        "ollama": "# Info\n\nOllama automatically manages memory. Models are unloaded when not in use.\n\n**To free memory:**\n- Stop using the model (it will be unloaded automatically)\n- Or restart Ollama: `ollama serve`",
        "lmstudio": '# Info\n\nLM Studio manages model loading through its UI.\n\n**To unload:**\n1. Open LM Studio\n2. Click "Stop Server" in the sidebar\n3. The model will be unloaded from memory',
        "openai": "# Info\n\nOpenAI models are hosted and don't need unloading.",
    }
    if provider in notes:
        return build_success_response(
            operation="unload_model",
            summary=f"Unload is managed by the provider ({provider}), nothing to do",
            result={
                "provider": provider,
                "model": model,
                "loaded": False,
                "markdown": notes[provider],
            },
        )
    return build_error_response(
        error="Unknown provider",
        error_code="UNKNOWN_PROVIDER",
        message=f"Unknown provider: {provider}",
        recovery_options=["Use one of: ollama, lmstudio, openai"],
    )


async def _get_status() -> dict:
    """Get current LLM configuration and status."""
    global _current_provider, _current_model

    lines = ["# LLM Status", ""]

    # Check both in-memory state and persistent config
    from advanced_memory.config import ConfigManager

    config = ConfigManager().config
    active_provider = _current_provider or config.llm_provider
    active_model = _current_model or config.llm_model

    if active_provider and active_model:
        lines.append("**Current Configuration:**")
        lines.append(f"- Provider: {active_provider}")
        lines.append(f"- Model: {active_model}")
        if _current_provider and _current_model:
            lines.append("- **Status:** Active (in-memory)")
        elif config.llm_provider and config.llm_model:
            lines.append("- **Status:** Loaded from config (will be active on next use)")
        lines.append("")
        configured_text = f"{active_provider}/{active_model}"
    else:
        lines.append("**Current Configuration:** None")
        lines.append("**Status:** No LLM provider configured. Use `adn_llm('select_model', ...)` to configure.")
        lines.append("")
        configured_text = "none"

    lines.append("**Provider Status:**")
    lines.append("")
    providers_resp = await _list_providers()
    providers_payload = providers_resp.get("result", {}) if isinstance(providers_resp, dict) else {}
    lines.append(providers_payload.get("markdown", ""))

    return build_success_response(
        operation="status",
        summary=f"LLM status (configured: {configured_text})",
        result={
            "provider": active_provider,
            "model": active_model,
            "providers": providers_payload.get("providers", []),
            "markdown": "\n".join(lines),
        },
    )


async def _check_health(provider: str | None = None, base_url: str | None = None) -> dict:
    """Check health of LLM providers."""
    if provider:
        providers_to_check = [provider]
    else:
        providers_to_check = ["ollama", "lmstudio", "openai"]

    lines = ["# LLM Provider Health Check", ""]
    entries = []

    for prov in providers_to_check:
        if prov == "ollama":
            url = (base_url or "http://localhost:11434") + "/api/tags"
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        # NOTE: /api/tags 200 proves the daemon answers, NOT that
                        # inference works (2026-09-19: tags OK while every
                        # /api/chat 500'd with llama-server.exe missing).
                        # /api/ps is a cheap second signal for loaded models.
                        loaded: list = []
                        try:
                            ps = await client.get((base_url or "http://localhost:11434") + "/api/ps")
                            if ps.status_code == 200:
                                loaded = [m.get("name") for m in ps.json().get("models", [])]
                        except Exception:
                            pass
                        state, emoji = "healthy", "✅"
                        detail = f"Reachable ({url})"
                        if loaded:
                            detail += f"; loaded: {', '.join(loaded)}"
                        else:
                            detail += "; nothing loaded (tags OK != inference OK)"
                    else:
                        state, emoji = f"unhealthy_http_{response.status_code}", "❌"
                        detail = f"HTTP {response.status_code} from {url}"
            except Exception as e:
                state, emoji = "unavailable", "❌"
                detail = f"Unavailable ({e!s})"
            lines.append(f"{emoji} **Ollama**: {detail}")
            entries.append({"provider": "ollama", "state": state, "detail": detail})

        elif prov == "lmstudio":
            url = (base_url or "http://localhost:1234") + "/v1/models"
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        state, emoji = "healthy", "✅"
                        detail = f"Healthy (connected to {url})"
                    else:
                        state, emoji = f"unhealthy_http_{response.status_code}", "❌"
                        detail = f"Unhealthy (HTTP {response.status_code})"
            except Exception as e:
                state, emoji = "unavailable", "❌"
                detail = f"Unavailable ({e!s})"
            lines.append(f"{emoji} **LM Studio**: {detail}")
            entries.append({"provider": "lmstudio", "state": state, "detail": detail})

        elif prov == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                state, emoji, detail = "configured", "✅", "Configured (API key present)"
            else:
                state, emoji, detail = "not_configured", "⚠️", "Not configured (no API key)"
            lines.append(f"{emoji} **OpenAI**: {detail}")
            entries.append({"provider": "openai", "state": state, "detail": detail})

    return build_success_response(
        operation="health",
        summary=f"Health checked: {len(entries)} providers",
        result={"checks": entries, "markdown": "\n".join(lines)},
    )
