"""AI integration service for Advanced Memory MCP.

This module provides integration with AI APIs (Claude, OpenAI, etc.)
for dynamic content generation and analysis.
"""

import json
import os
from typing import Any

from loguru import logger


class AIIntegration:
    """AI integration service for template generation and analysis."""

    def __init__(self, api_key: str | None = None, provider: str = "anthropic"):
        """Initialize AI integration.

        Args:
            api_key: API key for the provider (defaults to env var)
            provider: AI provider ('anthropic' or 'openai')
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()

    def _get_api_key(self) -> str | None:
        """Get API key from environment variables."""
        if self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        return None

    async def generate_templates(self, prompt: str, max_tokens: int = 8000) -> list[dict[str, Any]]:
        """Generate templates using AI.

        Args:
            prompt: Generation prompt
            max_tokens: Maximum tokens for response

        Returns:
            List of generated template dictionaries

        Raises:
            NotImplementedError: When API key is not configured
        """
        if not self.api_key:
            raise NotImplementedError(
                f"AI generation requires {self.provider.upper()}_API_KEY environment variable. "
                "Set it with: export ANTHROPIC_API_KEY=your-key-here\n\n"
                "For now, use pre-built templates with: "
                "adn_zettelmaker('generate', category='developer', topic='python-core')"
            )

        # In production, this would call the actual API
        # For Phase 2 implementation:
        if self.provider == "anthropic":
            return await self._generate_with_anthropic(prompt, max_tokens)
        elif self.provider == "openai":
            return await self._generate_with_openai(prompt, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _generate_with_anthropic(self, prompt: str, max_tokens: int) -> list[dict[str, Any]]:
        """Generate templates using Anthropic Claude API.

        Args:
            prompt: Generation prompt
            max_tokens: Maximum tokens for response

        Returns:
            List of generated template dictionaries
        """
        try:
            # Import anthropic library
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            # Call Claude API
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text content
            response_text = message.content[0].text

            # Parse JSON response
            # Look for JSON array in response
            if "[" in response_text and "]" in response_text:
                start = response_text.index("[")
                end = response_text.rindex("]") + 1
                json_str = response_text[start:end]
                templates = json.loads(json_str)
                return templates
            else:
                logger.error("No JSON array found in Claude response")
                raise ValueError("Claude response did not contain valid JSON array")

        except ImportError as e:
            raise NotImplementedError(
                "Anthropic library not installed. Install with: pip install anthropic"
            ) from e
        except Exception as e:
            logger.error(f"Error generating with Claude: {e}")
            raise

    async def _generate_with_openai(self, prompt: str, max_tokens: int) -> list[dict[str, Any]]:
        """Generate templates using OpenAI API.

        Args:
            prompt: Generation prompt
            max_tokens: Maximum tokens for response

        Returns:
            List of generated template dictionaries
        """
        try:
            # Import openai library
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key)

            # Call OpenAI API
            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text content
            response_text = response.choices[0].message.content

            # Parse JSON response
            if "[" in response_text and "]" in response_text:
                start = response_text.index("[")
                end = response_text.rindex("]") + 1
                json_str = response_text[start:end]
                templates = json.loads(json_str)
                return templates
            else:
                logger.error("No JSON array found in OpenAI response")
                raise ValueError("OpenAI response did not contain valid JSON array")

        except ImportError as e:
            raise NotImplementedError(
                "OpenAI library not installed. Install with: pip install openai"
            ) from e
        except Exception as e:
            logger.error(f"Error generating with OpenAI: {e}")
            raise
