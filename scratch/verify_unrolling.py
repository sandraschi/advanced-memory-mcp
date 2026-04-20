import os
import sys
from pathlib import Path

# Force UTF-8 for output
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

try:
    print(f"DEBUG: sys.path includes {src_path}", flush=True)
    from advanced_memory.mcp.mcp_instance import mcp
    print(f"DEBUG: mcp instance initialized: {mcp.name}", flush=True)
    
    # Import tools explicitly to ensure registration
    import advanced_memory.mcp.tools
    print(f"DEBUG: tools package imported", flush=True)
    
    import advanced_memory.mcp.tools.portmanteau_knowledge
    print(f"DEBUG: knowledge portmanteau imported", flush=True)

    print("\nRegistered Tools:", flush=True)
    
    # FastMCP typically stores tools in mcp._tools_manager._tools or mcp._tools
    tools = []
    
    # Try different FastMCP attributes (check all)
    print(f"DEBUG: mcp attributes: {[a for a in dir(mcp) if not a.startswith('__')]}", flush=True)
    
    if hasattr(mcp, "_tools"):
        tools = [t.name for t in mcp._tools.values()]
        print(f"DEBUG: found tools in _tools", flush=True)
    
    if hasattr(mcp, "tools"):
        # Some versions have a 'tools' property
        try:
            tools = [t.name for t in mcp.tools]
            print(f"DEBUG: found tools in tools property", flush=True)
        except:
            pass

    if not tools and hasattr(mcp, "_tool_manager"):
        tm = mcp._tool_manager
        print(f"DEBUG: tool_manager attributes: {dir(tm)}", flush=True)
        if hasattr(tm, "list_tools"):
            tools = [t.name for t in tm.list_tools()]
            print(f"DEBUG: found tools in tool_manager.list_tools()", flush=True)

    tool_names = sorted(list(set(tools)))
    for name in tool_names:
        print(f" - {name}", flush=True)

    # Check for specific namespaced tools
    expected = ["knowledge/create", "research/search"]
    found = [e for e in expected if e in tool_names]
    missing = [e for e in expected if e not in tool_names]
    
    print(f"\nFound: {found}", flush=True)
    
    if not missing:
        print("\n✅ Verification SUCCESS: Namespaced tools found!", flush=True)
    else:
        print(f"\n❌ Verification FAILED: Missing tools: {missing}", flush=True)

except Exception as e:
    print(f"Error during verification: {e}", flush=True)
    import traceback
    traceback.print_exc()
