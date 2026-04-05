import fastmcp
import os

def search_fastmcp(target):
    print(f"Searching for '{target}' in fastmcp source...")
    path = os.path.dirname(fastmcp.__file__)
    found = False
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        if target in f.read():
                            relative_path = os.path.relpath(file_path, path)
                            module_name = relative_path.replace(os.path.sep, ".").replace(".py", "")
                            if module_name.endswith(".__init__"):
                                module_name = module_name[:-9]
                            print(f"Found {target} in module: fastmcp.{module_name}")
                            found = True
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    if not found:
        print(f"'{target}' not found in any .py files in {path}")

if __name__ == "__main__":
    search_fastmcp("CodeMode")
    search_fastmcp("FileSystemProvider")
