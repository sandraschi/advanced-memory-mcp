"""
Robust markdown file validation for sync operations.

Prevents crashes from:
- Weird filenames (unicode, special chars, too long)
- Zero-size files
- Unreadable contents (encoding issues, binary)
- Broken frontmatter (malformed YAML)
- Corrupted files
- Permission issues

Usage:
    validator = FileValidator()
    result = validator.validate_file(file_path)
    
    if result.is_valid:
        # Process file safely
        content = result.content
    else:
        # Log error and skip
        logger.warning("invalid_file", errors=result.errors)
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of file validation."""
    is_valid: bool
    file_path: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    content: Optional[str] = None
    frontmatter: Optional[Dict[str, Any]] = None
    encoding: str = "utf-8"
    size_bytes: int = 0
    
    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning (doesn't invalidate)."""
        self.warnings.append(warning)


class FileValidator:
    """
    Robust file validator for markdown files.
    
    Validates:
    - Filename safety
    - File readability
    - Content encoding
    - Frontmatter syntax
    - File size constraints
    """
    
    # Maximum file size (10 MB default)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Maximum filename length (Windows limit is 260, but be conservative)
    MAX_FILENAME_LENGTH = 200
    
    # Minimum file size (0 bytes is suspicious)
    MIN_FILE_SIZE = 0  # Allow empty files but warn
    
    # Reserved Windows filenames
    WINDOWS_RESERVED = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    # Dangerous filename characters (beyond OS restrictions)
    DANGEROUS_CHARS = set('<>:"|?*\x00')
    
    # Encodings to try in order
    ENCODINGS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def __init__(
        self,
        max_file_size: int = MAX_FILE_SIZE,
        allow_empty: bool = True,
        strict_frontmatter: bool = False,
    ):
        """
        Initialize validator.
        
        Args:
            max_file_size: Maximum file size in bytes
            allow_empty: Allow empty files (will warn but not error)
            strict_frontmatter: Require valid frontmatter
        """
        self.max_file_size = max_file_size
        self.allow_empty = allow_empty
        self.strict_frontmatter = strict_frontmatter
    
    def validate_file(self, file_path: str | Path) -> ValidationResult:
        """
        Validate a markdown file completely.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            ValidationResult with details
        """
        file_path = Path(file_path)
        result = ValidationResult(
            is_valid=True,
            file_path=str(file_path)
        )
        
        # Check file exists
        if not file_path.exists():
            result.add_error(f"File does not exist: {file_path}")
            return result
        
        # Check it's a file (not directory)
        if not file_path.is_file():
            result.add_error(f"Not a file: {file_path}")
            return result
        
        # Validate filename
        self._validate_filename(file_path, result)
        
        # Validate file accessibility
        self._validate_accessibility(file_path, result)
        
        # Validate file size
        self._validate_size(file_path, result)
        
        # If basic checks failed, don't try to read content
        if not result.is_valid:
            return result
        
        # Try to read content
        self._validate_content(file_path, result)
        
        # If content read successfully, validate frontmatter
        if result.content is not None:
            self._validate_frontmatter(result)
        
        return result
    
    def _validate_filename(self, file_path: Path, result: ValidationResult):
        """Validate filename is safe."""
        filename = file_path.name
        
        # Check length
        if len(filename) > self.MAX_FILENAME_LENGTH:
            result.add_error(
                f"Filename too long ({len(filename)} > {self.MAX_FILENAME_LENGTH}): {filename}"
            )
        
        # Check for dangerous characters
        dangerous = self.DANGEROUS_CHARS & set(filename)
        if dangerous:
            result.add_error(
                f"Dangerous characters in filename: {dangerous} in {filename}"
            )
        
        # Check for Windows reserved names
        name_without_ext = file_path.stem.upper()
        if name_without_ext in self.WINDOWS_RESERVED:
            result.add_error(
                f"Reserved Windows filename: {name_without_ext}"
            )
        
        # Check for control characters
        if any(ord(c) < 32 for c in filename):
            result.add_error(
                f"Control characters in filename: {filename}"
            )
        
        # Warn about unicode characters (not an error, but worth noting)
        if not filename.isascii():
            result.add_warning(
                f"Non-ASCII characters in filename: {filename}"
            )
        
        # Warn about spaces or special chars that might cause issues
        if ' ' in filename:
            result.add_warning(
                f"Spaces in filename (consider using underscores): {filename}"
            )
        
        # Check extension
        if file_path.suffix.lower() not in ['.md', '.markdown']:
            result.add_warning(
                f"Unexpected extension: {file_path.suffix} (expected .md or .markdown)"
            )
    
    def _validate_accessibility(self, file_path: Path, result: ValidationResult):
        """Check if file can be accessed."""
        try:
            # Try to stat the file
            stats = file_path.stat()
            result.size_bytes = stats.st_size
            
            # Check read permissions
            if not os.access(file_path, os.R_OK):
                result.add_error(
                    f"No read permission: {file_path}"
                )
        
        except PermissionError as e:
            result.add_error(
                f"Permission denied: {file_path}: {e}"
            )
        
        except OSError as e:
            result.add_error(
                f"Cannot access file: {file_path}: {e}"
            )
    
    def _validate_size(self, file_path: Path, result: ValidationResult):
        """Validate file size is reasonable."""
        size = result.size_bytes
        
        # Check if empty
        if size == 0:
            if self.allow_empty:
                result.add_warning(
                    f"Empty file (0 bytes): {file_path}"
                )
            else:
                result.add_error(
                    f"Empty file not allowed: {file_path}"
                )
        
        # Check if too large
        if size > self.max_file_size:
            result.add_error(
                f"File too large ({size} > {self.max_file_size}): {file_path}"
            )
        
        # Warn if suspiciously large for markdown
        if size > 1024 * 1024:  # > 1 MB
            result.add_warning(
                f"Large markdown file ({size / 1024 / 1024:.2f} MB): {file_path}"
            )
    
    def _validate_content(self, file_path: Path, result: ValidationResult):
        """Try to read file content with multiple encodings."""
        content = None
        last_error = None
        
        for encoding in self.ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    content = f.read()
                result.encoding = encoding
                break
            
            except UnicodeDecodeError as e:
                last_error = e
                continue
            
            except Exception as e:
                result.add_error(
                    f"Failed to read file: {file_path}: {type(e).__name__}: {e}"
                )
                return
        
        if content is None:
            # Try binary read to check if it's actually binary
            try:
                with open(file_path, 'rb') as f:
                    raw = f.read(1024)  # Read first 1KB
                
                # Check for null bytes (binary indicator)
                if b'\x00' in raw:
                    result.add_error(
                        f"Binary file detected (contains null bytes): {file_path}"
                    )
                else:
                    result.add_error(
                        f"Encoding error (tried {', '.join(self.ENCODINGS)}): {file_path}: {last_error}"
                    )
            
            except Exception as e:
                result.add_error(
                    f"Cannot read file at all: {file_path}: {e}"
                )
            
            return
        
        # Successfully read content
        result.content = content
        
        # Warn if content has weird line endings
        if '\r\n' in content and '\n' in content.replace('\r\n', ''):
            result.add_warning(
                f"Mixed line endings detected: {file_path}"
            )
        
        # Warn if very long lines (might be minified/corrupted)
        lines = content.split('\n')
        max_line_len = max(len(line) for line in lines) if lines else 0
        if max_line_len > 10000:
            result.add_warning(
                f"Very long line detected ({max_line_len} chars): {file_path}"
            )
    
    def _validate_frontmatter(self, result: ValidationResult):
        """Validate YAML frontmatter if present."""
        if not result.content:
            return
        
        # Check for frontmatter markers
        if not result.content.startswith('---'):
            # No frontmatter is fine
            return
        
        # Extract frontmatter
        lines = result.content.split('\n')
        if len(lines) < 3:
            # Too short to have valid frontmatter
            if self.strict_frontmatter:
                result.add_error(
                    "Invalid frontmatter: too short"
                )
            return
        
        # Find closing marker
        end_idx = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == '---' or line.strip() == '...':
                end_idx = i
                break
        
        if end_idx is None:
            if self.strict_frontmatter:
                result.add_error(
                    "Invalid frontmatter: no closing marker"
                )
            else:
                result.add_warning(
                    "Frontmatter appears incomplete (no closing ---)"
                )
            return
        
        # Extract frontmatter content
        frontmatter_lines = lines[1:end_idx]
        frontmatter_text = '\n'.join(frontmatter_lines)
        
        # Try to parse as YAML
        if HAS_YAML:
            try:
                parsed = yaml.safe_load(frontmatter_text)
                result.frontmatter = parsed if isinstance(parsed, dict) else {}
            
            except yaml.YAMLError as e:
                if self.strict_frontmatter:
                    result.add_error(
                        f"Invalid YAML in frontmatter: {e}"
                    )
                else:
                    result.add_warning(
                        f"Malformed frontmatter YAML: {e}"
                    )
        else:
            result.add_warning(
                "Cannot validate frontmatter (PyYAML not installed)"
            )
    
    def validate_batch(
        self,
        file_paths: List[str | Path],
        on_error: str = 'continue'
    ) -> Dict[str, ValidationResult]:
        """
        Validate multiple files.
        
        Args:
            file_paths: List of files to validate
            on_error: 'continue' to keep going, 'stop' to halt on first error
            
        Returns:
            Dict mapping file paths to validation results
        """
        results = {}
        
        for file_path in file_paths:
            result = self.validate_file(file_path)
            results[str(file_path)] = result
            
            if on_error == 'stop' and not result.is_valid:
                break
        
        return results
    
    def get_summary(self, results: Dict[str, ValidationResult]) -> str:
        """Generate human-readable summary of validation results."""
        total = len(results)
        valid = sum(1 for r in results.values() if r.is_valid)
        invalid = total - valid
        
        total_errors = sum(len(r.errors) for r in results.values())
        total_warnings = sum(len(r.warnings) for r in results.values())
        
        summary = f"""
# File Validation Summary

**Total Files:** {total}
**Valid:** {valid} ({valid/total*100:.1f}%)
**Invalid:** {invalid} ({invalid/total*100:.1f}%)

**Errors:** {total_errors}
**Warnings:** {total_warnings}

## Invalid Files
"""
        
        for path, result in results.items():
            if not result.is_valid:
                summary += f"\n### {Path(path).name}\n"
                for error in result.errors:
                    summary += f"- ❌ {error}\n"
                for warning in result.warnings:
                    summary += f"- ⚠️  {warning}\n"
        
        if invalid == 0:
            summary += "\n✅ No invalid files!\n"
        
        return summary


# Convenience function for quick validation
def validate_markdown_file(file_path: str | Path) -> ValidationResult:
    """Quick validation of a single markdown file."""
    validator = FileValidator()
    return validator.validate_file(file_path)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python file_validator.py <file_or_directory>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    validator = FileValidator()
    
    if path.is_file():
        result = validator.validate_file(path)
        print(f"\n{'✅ VALID' if result.is_valid else '❌ INVALID'}: {path}")
        for error in result.errors:
            print(f"  ❌ {error}")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
    
    elif path.is_dir():
        files = list(path.rglob("*.md"))
        print(f"\nValidating {len(files)} markdown files...")
        results = validator.validate_batch(files)
        print(validator.get_summary(results))
    
    else:
        print(f"Error: {path} is not a file or directory")
        sys.exit(1)

