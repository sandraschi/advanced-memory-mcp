"""
MCP Tool Registry for Portmanteau and Compliance modes.

This module provides utilities for registering portmanteau tools in a way
that supports dynamic flattening into atomic tools for static scanners
like Arcade ToolBench.
"""

import functools
import os
from collections.abc import Callable
from typing import Literal, get_args, get_type_hints

from fastmcp import FastMCP
from loguru import logger


def register_portmanteau_tool(mcp: FastMCP, func: Callable) -> None:
    """
    Register a tool as either a consolidated portmanteau or a set of atomic tools.

    SOTA 2026 Mode (default): Registers individual shadow tools for each operation (Namespaced).
    Reduced Mode: Registers the function as a single portmanteau.
    """
    # Invert the logic: Default to unrolling (SOTA) unless Reduced Mode is explicitly requested
    reduced_mode = os.getenv("ADVANCED_MEMORY_REDUCED_MODE", "").lower() == "true"

    if reduced_mode:
        # Reduced Mode: Register the portmanteau tool as-is (Switch-Case view)
        mcp.add_tool(func)
        return

    # SOTA 2026 Mode: Unroll the portmanteau into namespaced atomic tools
    # This improves BM25 discovery in Cursor and ToolBench rankings.
    logger.info(f"SOTA Mode: Unrolling portmanteau tool '{func.__name__}'")

    # 1. Identify the 'operation' parameter and its Literal values
    type_hints = get_type_hints(func, include_extras=True)
    operation_hint = type_hints.get("operation")

    if not operation_hint:
        logger.warning(f"Tool '{func.__name__}' has no 'operation' parameter. Registering as-is.")
        mcp.add_tool(func)
        return

    # Extract Literal values from the hint (might be nested in Annotated)
    literal_values = []

    # Handle Annotated[Literal[...], Field(...)]
    if hasattr(operation_hint, "__metadata__"):
        actual_type = operation_hint.__origin__
        if hasattr(actual_type, "__origin__") and actual_type.__origin__ is Literal:
            literal_values = get_args(actual_type)
    elif hasattr(operation_hint, "__origin__") and operation_hint.__origin__ is Literal:
        literal_values = get_args(operation_hint)

    if not literal_values:
        logger.warning(f"Could not extract Literal values for 'operation' in '{func.__name__}'. Registering as-is.")
        mcp.add_tool(func)
        return

    # 2. For each operation, create and register a shadow tool
    prefix = func.__name__.replace("adn_", "")
    for op in literal_values:
        # Use SLASH separator for optimal BM25 tokenization in Cursor
        shadow_name = f"{prefix}/{op}"

        # Create a wrapper that fixes the operation parameter
        @functools.wraps(func)
        async def shadow_tool(*args, op=op, **kwargs):
            kwargs["operation"] = op
            return await func(*args, **kwargs)

        # Override the name and update the docstring to be specialized
        shadow_tool.__name__ = shadow_name
        if func.__doc__:
            # Strip the generic portmanteau header if present
            clean_doc = func.__doc__.split("For full documentation")[0].strip()
            shadow_tool.__doc__ = f"Atomic operation: {op}\n\n{clean_doc}"

        # Register the namespaced shadow tool
        mcp.add_tool(shadow_tool)
        logger.debug(f"Registered namespaced tool: {shadow_name}")
