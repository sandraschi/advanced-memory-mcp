import sys
from pathlib import Path

# Add src to sys.path
src_path = Path("src").absolute()
sys.path.insert(0, str(src_path))

tools_dir = src_path / "advanced_memory" / "mcp" / "tools"
print(f"Scanning tools in {tools_dir}")

for file in tools_dir.glob("adn_*.py"):
    module_name = f"advanced_memory.mcp.tools.{file.stem}"
    print(f"Testing import of {module_name}...")
    try:
        __import__(module_name)
        print(f"SUCCESS: {module_name}")
    except SyntaxError as e:
        print(f"SYNTAX ERROR in {module_name}: {e}")
        print(f"  File: {e.filename}, Line: {e.lineno}, Offset: {e.offset}, Text: {e.text}")
    except Exception as e:
        print(f"IMPORT ERROR in {module_name}: {type(e).__name__}: {e}")

print("Done.")
