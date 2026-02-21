import asyncio
import traceback

from advanced_memory.mcp.tools.recent_activity import recent_activity


async def main():
    try:
        # Call the tool directly exactly as it was called in the error
        result = await recent_activity(depth=1, timeframe="1 week")
        print("Success:")
        print(result)
    except Exception:
        print("Error occurred:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
