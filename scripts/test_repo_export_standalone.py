"""Standalone test script for repo export functionality."""
import asyncio
import os
import sys
import zipfile
from pathlib import Path

try:
    from pathspec import PathSpec
    from pathspec.patterns import GitWildMatchPattern
except ImportError:
    print("Error: pathspec not installed. Install with: pip install pathspec>=0.12.0")
    sys.exit(1)


async def export_repo(repo_path: str, export_path: str):
    """Export repository as ZIP, respecting .gitignore."""
    repo_root = Path(repo_path).resolve()
    
    if not repo_root.exists():
        print(f"Error: Repository path not found: {repo_root}")
        return
    
    if not repo_root.is_dir():
        print(f"Error: Repository path is not a directory: {repo_root}")
        return
    
    print(f"Exporting repository: {repo_root}")
    print(f"Export path: {export_path}")
    
    # Ensure export path is a ZIP file
    export_path_obj = Path(export_path)
    if export_path_obj.suffix.lower() != ".zip":
        export_path_obj = export_path_obj.with_suffix(".zip")
    
    # Collect all .gitignore files
    gitignore_files = list(repo_root.rglob(".gitignore"))
    print(f"Found {len(gitignore_files)} .gitignore file(s)")
    
    # Build a map of directory -> patterns (like the actual implementation)
    ignore_specs = {}  # Maps directory (relative to repo_root) -> PathSpec
    
    # Parse root .gitignore
    root_gitignore = repo_root / ".gitignore"
    root_patterns = []
    if root_gitignore.exists():
        try:
            with open(root_gitignore, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        root_patterns.append(line)
        except Exception as e:
            print(f"Warning: Failed to read root .gitignore: {e}")
    
    if root_patterns:
        ignore_specs[Path(".")] = PathSpec.from_lines(GitWildMatchPattern, root_patterns)
        print(f"Root .gitignore: {len(root_patterns)} patterns")
    
    # Parse nested .gitignore files
    for gitignore_file in gitignore_files:
        if gitignore_file == root_gitignore:
            continue
        gitignore_dir = gitignore_file.parent.relative_to(repo_root)
        try:
            with open(gitignore_file, "r", encoding="utf-8") as f:
                patterns = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
                if patterns:
                    ignore_specs[gitignore_dir] = PathSpec.from_lines(GitWildMatchPattern, patterns)
                    print(f"Nested .gitignore at {gitignore_dir}: {len(patterns)} patterns")
        except Exception as e:
            print(f"Warning: Failed to read .gitignore at {gitignore_file}: {e}")
    
    # Check if ZIP64 is needed
    needs_zip64 = False
    total_size_check = 0
    files_to_include = []
    ignored_count = 0
    
    # Walk repository and collect files
    print("Scanning files...")
    sample_ignored = []
    for file_path in repo_root.rglob("*"):
        if not file_path.is_file():
            continue
        
        rel_path = file_path.relative_to(repo_root)
        rel_path_str = str(rel_path).replace("\\", "/")
        rel_path_obj = Path(rel_path_str)
        
        # Check if file matches .gitignore (same logic as actual implementation)
        should_ignore = False
        
        # Check root .gitignore patterns
        if Path(".") in ignore_specs:
            if ignore_specs[Path(".")].match_file(rel_path_str):
                should_ignore = True
        
        # Check nested .gitignore patterns
        if not should_ignore:
            for gitignore_dir, spec in ignore_specs.items():
                if gitignore_dir == Path("."):
                    continue
                try:
                    if rel_path_obj.is_relative_to(gitignore_dir) or gitignore_dir in rel_path_obj.parents:
                        rel_to_gitignore = rel_path_obj.relative_to(gitignore_dir)
                        rel_to_gitignore_str = str(rel_to_gitignore).replace("\\", "/")
                        if spec.match_file(rel_to_gitignore_str):
                            should_ignore = True
                            break
                except ValueError:
                    continue
        
        if should_ignore:
            ignored_count += 1
            if len(sample_ignored) < 5:
                sample_ignored.append(rel_path_str)
            continue
        
        file_size = file_path.stat().st_size
        total_size_check += file_size
        if file_size > 4 * 1024 * 1024 * 1024:
            needs_zip64 = True
        
        files_to_include.append((file_path, rel_path_str))
    
    if not needs_zip64 and total_size_check > 4 * 1024 * 1024 * 1024:
        needs_zip64 = True
    
    print(f"Files to include: {len(files_to_include)}")
    print(f"Files ignored: {ignored_count}")
    if sample_ignored:
        print(f"Sample ignored files: {sample_ignored[:5]}")
    print(f"Total size: {total_size_check / (1024**2):.2f} MB")
    print(f"ZIP64 needed: {needs_zip64}")
    
    # Create ZIP archive
    export_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    zipf = zipfile.ZipFile(
        export_path_obj,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
        allowZip64=needs_zip64,
    )
    
    try:
        file_count = 0
        for file_path, rel_path_str in files_to_include:
            try:
                zipf.write(file_path, rel_path_str)
                file_count += 1
                if file_count % 100 == 0:
                    print(f"  Added {file_count}/{len(files_to_include)} files...")
            except Exception as e:
                print(f"Warning: Failed to add {rel_path_str}: {e}")
    finally:
        zipf.close()
    
    # Verify ZIP
    try:
        test_zip = zipfile.ZipFile(export_path_obj, "r")
        test_zip.close()
        print(f"\nSuccess! ZIP archive created and verified: {export_path_obj}")
        print(f"  Files: {file_count}")
        print(f"  Size: {export_path_obj.stat().st_size / (1024**2):.2f} MB")
        print(f"  ZIP64: {needs_zip64}")
    except zipfile.BadZipFile as e:
        print(f"\nError: Created ZIP file is invalid: {e}")
        return
    
    # Open file explorer
    try:
        if os.name == "nt":  # Windows
            os.startfile(export_path_obj.parent)
        elif sys.platform == "darwin":  # macOS
            os.system(f'open "{export_path_obj.parent}"')
        else:  # Linux
            os.system(f'xdg-open "{export_path_obj.parent}"')
    except Exception as e:
        print(f"Note: Could not open file explorer: {e}")


def main():
    """Main function."""
    repo_path = "d:/dev/repos/llm-txt-mcp"
    
    # Default export path
    desktop = Path.home() / "Desktop"
    export_dir = desktop / "advanced-memory-exports" / "repo"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / f"{Path(repo_path).name}.zip"
    
    asyncio.run(export_repo(repo_path, str(export_path)))


if __name__ == "__main__":
    main()

