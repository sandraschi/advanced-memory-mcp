"""Test script for repo export functionality."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from advanced_memory.mcp.tools.adn_export import _repo_export
from advanced_memory.utils.export_paths import format_export_path


async def main():
    """Test repo export."""
    repo_path = "d:/dev/repos/llm-txt-mcp"
    
    # Use default export path
    export_path = format_export_path("repo", None)
    
    print(f"Exporting repository: {repo_path}")
    print(f"Export path: {export_path}")
    print()
    
    try:
        result = await _repo_export(export_path, repo_path, show_after_export=True)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

































