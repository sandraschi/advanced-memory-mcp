"""Unified LLM client service for Advanced Memory.

This service provides a unified interface to interact with LLM providers
(Ollama, LM Studio, OpenAI) using the currently selected provider from adn_llm.
"""

import json
import os
from typing import Any

import httpx
from loguru import logger


class LLMClient:
    """Unified LLM client that works with multiple providers."""

    def __init__(
        self, provider: str | None = None, model: str | None = None, base_url: str | None = None
    ):
        """Initialize LLM client.

        Args:
            provider: Provider name (ollama, lmstudio, openai). If None, auto-detects.
            model: Model name. If None, uses default for provider.
            base_url: Custom base URL (for ollama/lmstudio).
        """
        self.provider = provider or self._auto_detect_provider()
        self.model = model or self._get_default_model()
        self.base_url = base_url

    def _auto_detect_provider(self) -> str:
        """Auto-detect available provider."""
        # Try Ollama first
        try:
            import httpx

            with httpx.Client(timeout=1.0) as client:
                response = client.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    return "ollama"
        except Exception:
            pass

        # Try LM Studio
        try:
            with httpx.Client(timeout=1.0) as client:
                response = client.get("http://localhost:1234/v1/models")
                if response.status_code == 200:
                    return "lmstudio"
        except Exception:
            pass

        # Try OpenAI
        if os.getenv("OPENAI_API_KEY"):
            return "openai"

        # Default to ollama (user can configure)
        return "ollama"

    def _get_default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            "ollama": "llama3",
            "lmstudio": "local-model",
            "openai": "gpt-3.5-turbo",
        }
        return defaults.get(self.provider, "llama3")

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using the selected LLM provider.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            Generated text
        """
        if self.provider == "ollama":
            return await self._generate_ollama(prompt, system_prompt, max_tokens, temperature)
        elif self.provider == "lmstudio":
            return await self._generate_lmstudio(prompt, system_prompt, max_tokens, temperature)
        elif self.provider == "openai":
            return await self._generate_openai(prompt, system_prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def _generate_ollama(
        self, prompt: str, system_prompt: str | None, max_tokens: int, temperature: float
    ) -> str:
        """Generate using Ollama."""
        url = (self.base_url or "http://localhost:11434") + "/api/generate"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    raise Exception(
                        f"Ollama API error: HTTP {response.status_code} - {response.text}"
                    )
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to Ollama: {str(e)}")

    async def _generate_lmstudio(
        self, prompt: str, system_prompt: str | None, max_tokens: int, temperature: float
    ) -> str:
        """Generate using LM Studio (OpenAI-compatible API)."""
        url = (self.base_url or "http://localhost:1234") + "/v1/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    raise Exception(
                        f"LM Studio API error: HTTP {response.status_code} - {response.text}"
                    )
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to LM Studio: {str(e)}")

    async def _generate_openai(
        self, prompt: str, system_prompt: str | None, max_tokens: int, temperature: float
    ) -> str:
        """Generate using OpenAI."""
        try:
            import openai

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise Exception("OPENAI_API_KEY not set")

            client = openai.AsyncOpenAI(api_key=api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content or ""

        except ImportError:
            raise Exception("OpenAI library not installed. Install with: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 2000,
        temperature: float = 0.3,
    ) -> dict[str, Any] | list[Any]:
        """Generate JSON response from LLM.

        Args:
            prompt: User prompt (should request JSON output)
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens
            temperature: Lower temperature for more structured output

        Returns:
            Parsed JSON (dict or list)
        """
        # Add JSON instruction to prompt
        json_prompt = f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."
        if system_prompt:
            json_system = f"{system_prompt}\n\nAlways respond with valid JSON."
        else:
            json_system = "Always respond with valid JSON only."

        response = await self.generate(json_prompt, json_system, max_tokens, temperature)

        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response:
                start = response.index("```json") + 7
                end = response.index("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.index("```") + 3
                end = response.index("```", start)
                response = response[start:end].strip()

            # Find JSON array or object
            if "[" in response and "]" in response:
                start = response.index("[")
                end = response.rindex("]") + 1
                return json.loads(response[start:end])
            elif "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                return json.loads(response[start:end])

            # Try parsing entire response
            return json.loads(response)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}\nResponse: {response[:200]}")
            raise Exception(f"LLM did not return valid JSON: {str(e)}")


def get_llm_client(provider: str | None = None, model: str | None = None) -> LLMClient:
    """Get LLM client instance.

    Uses global state from adn_llm if provider/model not specified.
    Falls back to config.json if global state not available.
    """
    # Import here to avoid circular dependency
    try:
        # Try to import the global state (may not be available if adn_llm not loaded)
        import sys

        if "advanced_memory.mcp.tools.adn_llm" in sys.modules:
            from advanced_memory.mcp.tools.adn_llm import _current_model, _current_provider

            if not provider:
                provider = _current_provider
            if not model:
                model = _current_model
    except (ImportError, AttributeError):
        # Module not loaded or state not available, try config.json
        try:
            from advanced_memory.config import ConfigManager

            config = ConfigManager().config
            if not provider and config.llm_provider:
                provider = config.llm_provider
            if not model and config.llm_model:
                model = config.llm_model
        except Exception:
            # Config not available, use defaults
            pass

    return LLMClient(provider=provider, model=model)
