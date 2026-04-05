import asyncio
import os
import sys

# Ensure project root is in path
project_root = os.path.dirname(os.path.abspath(__file__))
# Add 'src' to path
sys.path.append(os.path.join(project_root, "src"))

async def check_tools():
    print("Checking FastMCP 3.2 SOTA Modernization...")
    # Import the server mcp instance
    from advanced_memory.mcp.server import mcp
    
    # FastMCP 3.2: list_tools is an async method
    tools = await mcp.list_tools()
    
    print(f"\nTotal Tools Found: {len(tools)}")
    
    meta_tools = [t for t in tools if t.name in ["Discover", "Execute"]]
    print("\nMeta-Tools (Code Mode):")
    for t in meta_tools:
        print(f" - ✅ {t.name}: {t.description[:80]}...")
            
    print("\nIndividual Tool Samples (Stable):")
    stable_tools = [t for t in tools if "adn_" in t.name or "help" == t.name]
    for t in stable_tools[:5]:
        print(f" - {t.name}")
        
    print("\nBeta Tool Samples:")
    beta_tools = [t for t in tools if t.name in ["adn_arxiv_research", "adn_github_research", "adn_visualize"]]
    for t in beta_tools:
        print(f" - {t.name}")
        
    if any(t.name == "Discover" for t in tools):
        print("\n🏆 Verification Successful: FastMCP 3.2 Code Mode Active!")
    else:
        print("\n❌ Verification Failed: Code Mode not detected.")

if __name__ == "__main__":
    asyncio.run(check_tools())
