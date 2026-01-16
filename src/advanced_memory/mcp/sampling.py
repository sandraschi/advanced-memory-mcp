"""MCP 2.14.1+ Sampling Client Integration for LLM Interrogation.

This module provides unified access to FastMCP 2.14.1+ sampling capabilities,
enabling MCP servers to interrogate client LLMs for intelligent content generation,
validation, and enhancement.

PORTMANTEAU PATTERN RATIONALE:
Consolidates sampling client creation and management into a single interface
for consistent LLM interrogation across all tools.
"""

from __future__ import annotations

import os
from typing import Any, Literal

from loguru import logger
from pydantic import BaseModel


class SamplingConfig(BaseModel):
    """Configuration for LLM sampling."""
    provider: Literal["anthropic", "openai", "auto"] = "auto"
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: str | None = None
    base_url: str | None = None


class SamplingClient:
    """Unified sampling client for MCP 2.14.1+ LLM interrogation."""

    def __init__(self, config: SamplingConfig):
        self.config = config
        self._client = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the sampling client."""
        try:
            # Import FastMCP sampling components
            from advanced_memory.mcp.mcp_instance import mcp

            # Check if sampling is available (FastMCP 2.14.1+)
            if not hasattr(mcp, 'ctx') or not hasattr(mcp.ctx, 'sample'):
                logger.warning("FastMCP 2.14.1+ sampling not available")
                return False

            self._client = mcp.ctx
            self._initialized = True
            logger.info(f"Sampling client initialized with provider: {self.config.provider}")
            return True

        except ImportError as e:
            logger.error(f"Failed to import sampling components: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize sampling client: {e}")
            return False

    async def sample(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        response_format: dict[str, Any] | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs
    ) -> SamplingResult:
        """Execute sampling request using MCP context."""

        if not self._initialized or not self._client:
            raise RuntimeError("Sampling client not initialized")

        # Use configured defaults if not overridden
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature

        try:
            # Execute sampling using MCP ctx.sample()
            result = await self._client.sample(
                messages=messages,
                tools=tools or [],
                response_format=response_format,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            return SamplingResult(
                success=True,
                content=result.content,
                usage=result.usage if hasattr(result, 'usage') else None,
                finish_reason=result.finish_reason if hasattr(result, 'finish_reason') else None
            )

        except Exception as e:
            logger.error(f"Sampling request failed: {e}")
            return SamplingResult(
                success=False,
                error=str(e),
                content=""
            )

    async def sample_step(
        self,
        messages: list[dict[str, Any]],
        **kwargs
    ) -> SamplingResult:
        """Execute single sampling step for fine control."""

        if not self._initialized or not self._client:
            raise RuntimeError("Sampling client not initialized")

        try:
            # Use sample_step for fine-grained control
            result = await self._client.sample_step(
                messages=messages,
                **kwargs
            )

            return SamplingResult(
                success=True,
                content=result.content,
                usage=result.usage if hasattr(result, 'usage') else None,
                finish_reason=result.finish_reason if hasattr(result, 'finish_reason') else None
            )

        except Exception as e:
            logger.error(f"Sampling step failed: {e}")
            return SamplingResult(
                success=False,
                error=str(e),
                content=""
            )


class SamplingResult(BaseModel):
    """Result of a sampling operation."""
    success: bool
    content: str
    usage: dict[str, Any] | None = None
    finish_reason: str | None = None
    error: str | None = None


# Global sampling client instance
_sampling_client: SamplingClient | None = None


def get_sampling_client(config: SamplingConfig | None = None) -> SamplingClient | None:
    """Get or create the global sampling client instance."""

    global _sampling_client

    if _sampling_client is None:
        # Auto-configure from environment if no config provided
        if config is None:
            config = _auto_configure_sampling()

        _sampling_client = SamplingClient(config)

    return _sampling_client


def _auto_configure_sampling() -> SamplingConfig:
    """Auto-configure sampling from environment variables."""

    # Check for Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        return SamplingConfig(
            provider="anthropic",
            api_key=anthropic_key,
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        )

    # Check for OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return SamplingConfig(
            provider="openai",
            api_key=openai_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        )

    # Default fallback
    return SamplingConfig(
        provider="auto",
        model="claude-3-5-sonnet-20241022"  # Assume Anthropic by default
    )


async def initialize_sampling() -> bool:
    """Initialize the global sampling client."""

    client = get_sampling_client()
    if client:
        return await client.initialize()

    return False


async def sample_with_llm(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    config: SamplingConfig | None = None,
    **kwargs
) -> SamplingResult:
    """Convenience function for one-off sampling requests."""

    client = get_sampling_client(config)

    if not client:
        return SamplingResult(
            success=False,
            error="Sampling client not available",
            content=""
        )

    # Ensure initialized
    if not client._initialized:
        initialized = await client.initialize()
        if not initialized:
            return SamplingResult(
                success=False,
                error="Failed to initialize sampling client",
                content=""
            )

    return await client.sample(messages, tools, **kwargs)


async def validate_sampling_availability() -> dict[str, Any]:
    """Validate that sampling capabilities are available and working."""

    try:
        # Test basic sampling
        result = await sample_with_llm([
            {"role": "user", "content": "Hello, test message for sampling validation."}
        ])

        return {
            "available": True,
            "test_successful": result.success,
            "error": result.error if not result.success else None,
            "version": "2.14.1+",
            "features": [
                "ctx.sample()",
                "ctx.sample_step()",
                "Structured output",
                "Tool calling",
                "Multi-iteration workflows"
            ]
        }

    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "version": None,
            "features": []
        }