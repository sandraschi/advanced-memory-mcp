#!/usr/bin/env python3
"""Test read_latest operation."""

import asyncio

from advanced_memory.mcp.tools.content_manager import adn_content


async def test_read_latest():
    """Test the read_latest operation."""
    try:
        print("Testing read_latest...")
        result = await adn_content.fn(operation="read_latest")
        print("SUCCESS:")
        print(result)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_read_latest())
