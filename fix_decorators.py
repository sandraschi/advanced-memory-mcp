import os

root_dir = r"d:\Dev\repos\advanced-memory-mcp\src"

for root, _dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, encoding="utf-8") as f:
                content = f.read()

            if "@mcp.tool()" in content:
                new_content = content.replace("@mcp.tool()", "@mcp.tool")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"FIXED: {path}")
