import asyncio
import json

from advanced_memory.mcp.async_client import client
from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.mcp.tools.utils import call_get


async def main() -> None:
    project = get_active_project(None)
    await call_get(
        client,
        f"{project.project_url}/memory/recent",
        params={"page": 1, "page_size": 5},
    )
    from advanced_memory.mcp.tools.recent_activity import recent_activity

    context = await recent_activity.fn(
        timeframe="1d",
        page=1,
        page_size=5,
        project=project.name,
    )
    print(json.dumps(context.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
