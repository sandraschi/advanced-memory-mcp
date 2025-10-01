"""Path-related utility functions."""
from pathlib import Path
from typing import Union

def validate_project_path(path: str, project_path: Union[str, Path]) -> bool:
    """Ensure path stays within project boundaries.
    
    Args:
        path: The path to validate
        project_path: The base project path to validate against
        
    Returns:
        bool: True if the path is valid and within the project, False otherwise
    """
    # Convert project_path to Path if it's a string
    if isinstance(project_path, str):
        project_path = Path(project_path)
    
    # Allow empty strings as they resolve to the project root
    if not path:
        return True
    
    # Check for obvious path traversal patterns first
    if ".." in path or "~" in path:
        return False
    
    # Check for Windows-style path traversal (even on Unix systems)
    if "\\.." in path or path.startswith("\\"):
        return False
    
    # Block absolute paths and Windows drive letters
    if path.startswith("/") or (len(path) >= 2 and path[1] == ":"):
        return False
    
    # Block paths with control characters (but allow whitespace that will be stripped)
    if path.strip() and any(ord(c) < 32 and c not in [' ', '\t'] for c in path):
        return False
    
    try:
        resolved = (project_path / path).resolve()
        return resolved.is_relative_to(project_path.resolve())
    except (ValueError, OSError):
        return False
