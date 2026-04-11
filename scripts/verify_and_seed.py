import asyncio
import sys

# Try to import httpx for async calls
try:
    import httpx
except ImportError:
    print("Error: 'httpx' library not found. Please run 'pip install httpx'.")
    sys.exit(1)

# We use the internal ASGI app directly via httpx.AsyncClient(app=app)
# This bypasses the stdio transport entirely.
try:
    from advanced_memory.api.app import app
except ImportError:
    print("Error: Could not import 'advanced_memory.api.app'. Ensure you are running from the repo root.")
    sys.exit(1)

# Project Configuration
PROJECT_NAME = "chrono-glenn"
PROJECT_PATH = r"c:\Users\sandr\.gemini\antigravity\playground\chrono-glenn"


async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        print(f"--- Synchronizing Project: {PROJECT_NAME} ---")

        # 1. Register/Switch to the project
        # Endpoint: POST /projects/projects
        # Payload: ProjectInfoRequest (name, path, set_default)
        reg_payload = {"name": PROJECT_NAME, "path": PROJECT_PATH, "set_default": True}

        print(f"Registering project at {PROJECT_PATH}...")
        resp = await client.post("/projects/projects", json=reg_payload)

        if resp.status_code in (200, 201):
            print(f"SUCCESS: Project '{PROJECT_NAME}' is now active and default.")
        elif resp.status_code == 400 and "exists" in resp.text:
            print(f"INFO: Project '{PROJECT_NAME}' already registered. Proceeding...")
        else:
            print(f"ERROR registering project: {resp.status_code}")
            print(resp.text)
            return

        # 2. Verify List
        print("\n--- Verifying Project List ---")
        list_resp = await client.get("/projects/projects")
        if list_resp.status_code == 200:
            data = list_resp.json()
            projects = data.get("projects", [])
            default_project = data.get("default_project", "None")
            print(f"Active Projects: {[p['name'] for p in projects]}")
            print(f"Current Default: {default_project}")
        else:
            print(f"Error listing projects: {list_resp.text}")

        # 3. Create Seedling Zettel
        # Path: /{project}/knowledge/entities
        print(f"\n--- Seeding '{PROJECT_NAME}' with initial Zettel ---")

        zettel_payload = {
            "title": "Chrono-Glenn Paradox Hypothesis",
            "content": """# Chrono-Glenn Paradox Hypothesis

This note acts as the technical seed for the [[chrono-glenn]] project.
The hypothesis posits that temporal drift in a localized "Glenn-field"
is inversely proportional to the empirical data-density of the observer.

## Core Observations
- [hypothesis] Temporal drift is linked to data entropy #temporal #glenn #reductionism
- [note] Need to cross-reference with [[General AI]] drift prediction models #todo

## Methodology
The initial research vector focuses on the 1974 'Glenn-Event' trace data,
deconstructed through the lens of modern materialist/reductionist physics.
""",
            "folder": "seedlings",
            "tags": "temporal,glenn,seedling,paradox,reductionism",
            "entity_type": "zettel",
        }

        # Note: The project name in the URL must match the registered name (slugified)
        entity_url = f"/{PROJECT_NAME}/knowledge/entities"
        entity_resp = await client.post(entity_url, json=zettel_payload)

        if entity_resp.status_code in (200, 201):
            print("SUCCESS: Initial Zettel created.")
            result = entity_resp.json()
            print(f"Created Path: {result.get('path', 'unknown')}")
        else:
            print(f"ERROR creating Zettel: {entity_resp.status_code}")
            print(entity_resp.text)


if __name__ == "__main__":
    asyncio.run(main())
