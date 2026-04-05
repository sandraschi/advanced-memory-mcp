import asyncio
from dataclasses import dataclass
from typing import Literal


@dataclass
class Context:
    async def info(self, msg: str):
        print(f"INFO: {msg}")


async def create_memory_project(
    project_name: str, project_path: str, set_default: bool = False, ctx: Context | None = None
) -> str:
    print(f"DEBUG: ctx type: {type(ctx)}, value: {ctx}")
    if ctx:
        await ctx.info(f"Creating project: {project_name} at {project_path}")
    return f"Created {project_name}"


async def adn_project(
    operation: Literal["create"],
    name: str | None = None,
    path: str | None = None,
    set_default: bool | None = None,
    description: str | None = None,
) -> dict:
    if operation == "create":
        result = await create_memory_project(
            project_name=name, project_path=path, set_default=set_default or False
        )
        return {"success": True, "result": result}
    return {"success": False}


async def main():
    try:
        # Simulate the call that failed
        # mcp_memops_adn_project(name="chrono-glenn", operation="create", path="...", set_default=true)
        print("Running reproduction...")
        res = await adn_project(operation="create", name="test", path="path", set_default=True)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
