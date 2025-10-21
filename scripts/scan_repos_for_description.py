#!/usr/bin/env python3
"""
Scan all MCP repositories for incorrect description= pattern.

Checks each repo for @mcp.tool(description=...) and reports findings.
"""

import re
from pathlib import Path


def scan_repo(repo_path: Path) -> dict:
    """Scan a repository for description= usage.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        Dict with repo name, files with issues, and count
    """
    result = {
        "name": repo_path.name,
        "path": str(repo_path),
        "files_with_description": [],
        "total_count": 0,
    }
    
    # Find all Python files
    for py_file in repo_path.rglob("*.py"):
        if ".git" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Look for @mcp.tool( followed by description=
            pattern = r'@mcp\.tool\([^)]*description='
            matches = re.findall(pattern, content, re.DOTALL)
            
            if matches:
                result["files_with_description"].append(str(py_file.relative_to(repo_path)))
                result["total_count"] += len(matches)
                
        except Exception:
            pass  # Skip files that can't be read
    
    return result


def main():
    repos_dir = Path("D:/Dev/repos")
    
    print("🔍 Scanning all MCP repositories for description= parameter...")
    print("=" * 80)
    
    # Get all MCP repos (exclude copies and backups)
    mcp_repos = sorted([
        d for d in repos_dir.iterdir() 
        if d.is_dir() 
        and "mcp" in d.name.lower()
        and "copy" not in d.name.lower()
        and "backup" not in d.name.lower()
        and "old" not in d.name.lower()
    ])
    
    print(f"Found {len(mcp_repos)} MCP repositories\n")
    
    repos_with_issues = []
    repos_clean = []
    
    for repo in mcp_repos:
        result = scan_repo(repo)
        
        if result["total_count"] > 0:
            repos_with_issues.append(result)
            print(f"❌ {result['name']:<40} {result['total_count']:>3} issues in {len(result['files_with_description'])} files")
        else:
            repos_clean.append(result["name"])
            print(f"✅ {result['name']:<40} Clean!")
    
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  Repos with issues: {len(repos_with_issues)}")
    print(f"  Repos clean: {len(repos_clean)}")
    
    if repos_with_issues:
        print(f"\n❌ Repositories needing fixes:")
        for repo in sorted(repos_with_issues, key=lambda x: x['total_count'], reverse=True):
            print(f"\n  {repo['name']} ({repo['total_count']} issues):")
            for f in repo['files_with_description'][:5]:  # Show first 5 files
                print(f"    - {f}")
            if len(repo['files_with_description']) > 5:
                print(f"    ... and {len(repo['files_with_description']) - 5} more files")
    
    print(f"\n✅ Clean repositories: {len(repos_clean)}")
    
    print(f"\n💡 To fix repos, copy scripts/remove_description_params.py and run in each repo!")


if __name__ == "__main__":
    main()

