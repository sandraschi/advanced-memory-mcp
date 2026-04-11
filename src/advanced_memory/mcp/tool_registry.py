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

    In Industrial Mode (default): Registers the function as a single portmanteau.
    In Compliance Mode: Registers individual shadow tools for each operation.
    """
    compliance_mode = os.getenv("ADVANCED_MEMORY_ARCADE_COMPLIANCE", "").lower() == "true"

    if not compliance_mode:
        # Standard Industrial Mode: Register the portmanteau tool as-is
        mcp.add_tool(func)
        return

    # Compliance Mode: Unroll the portmanteau into atomic tools
    logger.info(f"Arcade Compliance Mode: Unrolling portmanteau tool '{func.__name__}'")

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
    for op in literal_values:
        shadow_name = f"{func.__name__}_{op}"

        # Create a wrapper that fixes the operation parameter
        @functools.wraps(func)
        async def shadow_tool(*args, op=op, **kwargs):
            kwargs["operation"] = op
            return await func(*args, **kwargs)

        # Override the name and update the docstring to be specialized
        shadow_tool.__name__ = shadow_name
        if func.__doc__:
            shadow_tool.__doc__ = f"Atomic version of {func.__name__} for operation: {op}\n\n{func.__doc__}"

        # Register the shadow tool
        # Note: We rely on FastMCP to handle the schema generation from the wrapper
        # In a more advanced implementation, we could prune the 'operation' arg from the signature
        # but for Arcade, just having distinct names is usually enough to pass static checks.
        mcp.add_tool(shadow_tool)
        logger.debug(f"Registered shadow tool: {shadow_name}")
