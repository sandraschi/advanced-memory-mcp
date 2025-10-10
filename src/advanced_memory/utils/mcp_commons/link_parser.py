"""
Robust link parser for markdown notes.

Prevents failures from:
- Very large notes (> 1 MB)
- Many links (> 1000)
- Complex/nested link patterns
- Malformed link syntax
- Catastrophic regex backtracking
- Memory exhaustion

Usage:
    parser = LinkParser()
    result = parser.parse_links(content)
    
    if result.is_valid:
        links = result.links
    else:
        # Handle gracefully
        logger.warning("link_parse_failed", errors=result.errors)
"""

import re
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
import logging

logger = logging.getLogger(__name__)


@dataclass
class Link:
    """Represents a parsed link."""
    type: str  # 'wikilink', 'markdown', 'url', 'image'
    target: str
    text: Optional[str] = None
    start_pos: int = 0
    end_pos: int = 0
    raw: str = ""


@dataclass
class LinkParseResult:
    """Result of link parsing."""
    is_valid: bool
    content: str
    links: List[Link] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    parse_time_ms: float = 0
    
    def add_error(self, error: str):
        """Add parse error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add parse warning."""
        self.warnings.append(warning)


class LinkParser:
    """
    Robust link parser for markdown content.
    
    Handles:
    - Wikilinks: [[Page]] or [[Page|Display]]
    - Markdown links: [text](url)
    - Images: ![alt](url)
    - Raw URLs: http://example.com
    - Large files with many links
    - Malformed syntax
    """
    
    # Maximum content size to parse (10 MB default)
    MAX_CONTENT_SIZE = 10 * 1024 * 1024
    
    # Maximum links to extract (prevents memory exhaustion)
    MAX_LINKS = 10000
    
    # Maximum time for parsing (seconds)
    MAX_PARSE_TIME = 5.0
    
    # Warn if more than this many links
    WARN_LINK_COUNT = 1000
    
    # Regex patterns (non-greedy to prevent catastrophic backtracking)
    WIKILINK_PATTERN = re.compile(
        r'\[\[([^\[\]]+?)\]\]',  # Non-greedy, no nested brackets
        re.MULTILINE
    )
    
    MARKDOWN_LINK_PATTERN = re.compile(
        r'\[([^\[\]]+?)\]\(([^\(\)]+?)\)',  # Non-greedy
        re.MULTILINE
    )
    
    IMAGE_PATTERN = re.compile(
        r'!\[([^\[\]]*?)\]\(([^\(\)]+?)\)',  # Non-greedy
        re.MULTILINE
    )
    
    # Simple URL pattern (more permissive, less complex)
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+',
        re.MULTILINE
    )
    
    def __init__(
        self,
        max_content_size: int = MAX_CONTENT_SIZE,
        max_links: int = MAX_LINKS,
        max_parse_time: float = MAX_PARSE_TIME,
        extract_urls: bool = False,  # Disabled by default (expensive)
    ):
        """
        Initialize link parser.
        
        Args:
            max_content_size: Maximum content size in bytes
            max_links: Maximum links to extract
            max_parse_time: Maximum parsing time in seconds
            extract_urls: Extract raw URLs (expensive, off by default)
        """
        self.max_content_size = max_content_size
        self.max_links = max_links
        self.max_parse_time = max_parse_time
        self.extract_urls = extract_urls
    
    def parse_links(self, content: str) -> LinkParseResult:
        """
        Parse all links in markdown content.
        
        Args:
            content: Markdown content to parse
            
        Returns:
            LinkParseResult with extracted links or errors
        """
        start_time = time.time()
        result = LinkParseResult(
            is_valid=True,
            content=content
        )
        
        # Check content size
        content_size = len(content.encode('utf-8'))
        if content_size > self.max_content_size:
            result.add_error(
                f"Content too large for link parsing "
                f"({content_size / 1024 / 1024:.2f} MB > "
                f"{self.max_content_size / 1024 / 1024:.2f} MB)"
            )
            return result
        
        try:
            # Parse different link types
            self._parse_wikilinks(content, result, start_time)
            self._parse_images(content, result, start_time)
            self._parse_markdown_links(content, result, start_time)
            
            # Optionally parse raw URLs (expensive)
            if self.extract_urls:
                self._parse_raw_urls(content, result, start_time)
            
            # Check if too many links
            if len(result.links) >= self.max_links:
                result.add_warning(
                    f"Maximum links reached ({self.max_links}), "
                    f"some links may be missing"
                )
            
            # Warn if many links
            if len(result.links) > self.WARN_LINK_COUNT:
                result.add_warning(
                    f"Large number of links ({len(result.links)}) "
                    f"may impact performance"
                )
            
            # Calculate parse time
            result.parse_time_ms = (time.time() - start_time) * 1000
            
            logger.debug("link_parsing_complete",
                        link_count=len(result.links),
                        parse_time_ms=result.parse_time_ms)
            
        except Exception as e:
            result.add_error(f"Link parsing failed: {type(e).__name__}: {e}")
            logger.error("link_parsing_exception",
                        error=str(e),
                        error_type=type(e).__name__)
        
        return result
    
    def _check_timeout(self, start_time: float, result: LinkParseResult) -> bool:
        """Check if parsing has exceeded timeout."""
        elapsed = time.time() - start_time
        if elapsed > self.max_parse_time:
            result.add_error(
                f"Link parsing timeout ({elapsed:.2f}s > {self.max_parse_time}s)"
            )
            return True
        return False
    
    def _check_link_limit(self, result: LinkParseResult) -> bool:
        """Check if link limit reached."""
        return len(result.links) >= self.max_links
    
    def _parse_wikilinks(
        self,
        content: str,
        result: LinkParseResult,
        start_time: float
    ):
        """Parse wikilinks: [[Page]] or [[Page|Display]]."""
        try:
            for match in self.WIKILINK_PATTERN.finditer(content):
                # Check limits
                if self._check_timeout(start_time, result):
                    return
                if self._check_link_limit(result):
                    return
                
                raw_link = match.group(1)
                
                # Parse [[target|text]] format
                if '|' in raw_link:
                    target, text = raw_link.split('|', 1)
                else:
                    target = raw_link
                    text = None
                
                link = Link(
                    type='wikilink',
                    target=target.strip(),
                    text=text.strip() if text else None,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    raw=match.group(0)
                )
                
                result.links.append(link)
        
        except re.error as e:
            result.add_warning(f"Wikilink regex error: {e}")
        except Exception as e:
            result.add_warning(f"Wikilink parsing error: {e}")
    
    def _parse_images(
        self,
        content: str,
        result: LinkParseResult,
        start_time: float
    ):
        """Parse image links: ![alt](url)."""
        try:
            for match in self.IMAGE_PATTERN.finditer(content):
                # Check limits
                if self._check_timeout(start_time, result):
                    return
                if self._check_link_limit(result):
                    return
                
                alt_text = match.group(1)
                url = match.group(2)
                
                link = Link(
                    type='image',
                    target=url.strip(),
                    text=alt_text.strip() if alt_text else None,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    raw=match.group(0)
                )
                
                result.links.append(link)
        
        except re.error as e:
            result.add_warning(f"Image regex error: {e}")
        except Exception as e:
            result.add_warning(f"Image parsing error: {e}")
    
    def _parse_markdown_links(
        self,
        content: str,
        result: LinkParseResult,
        start_time: float
    ):
        """Parse markdown links: [text](url)."""
        try:
            # Skip positions already covered by images
            image_positions = {
                (link.start_pos, link.end_pos)
                for link in result.links
                if link.type == 'image'
            }
            
            for match in self.MARKDOWN_LINK_PATTERN.finditer(content):
                # Check limits
                if self._check_timeout(start_time, result):
                    return
                if self._check_link_limit(result):
                    return
                
                # Skip if this is an image (starts with !)
                if match.start() > 0 and content[match.start() - 1] == '!':
                    continue
                
                text = match.group(1)
                url = match.group(2)
                
                link = Link(
                    type='markdown',
                    target=url.strip(),
                    text=text.strip() if text else None,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    raw=match.group(0)
                )
                
                result.links.append(link)
        
        except re.error as e:
            result.add_warning(f"Markdown link regex error: {e}")
        except Exception as e:
            result.add_warning(f"Markdown link parsing error: {e}")
    
    def _parse_raw_urls(
        self,
        content: str,
        result: LinkParseResult,
        start_time: float
    ):
        """Parse raw URLs: http://example.com."""
        try:
            # Skip positions already covered by other links
            existing_ranges = {
                range(link.start_pos, link.end_pos)
                for link in result.links
            }
            
            for match in self.URL_PATTERN.finditer(content):
                # Check limits
                if self._check_timeout(start_time, result):
                    return
                if self._check_link_limit(result):
                    return
                
                # Skip if URL is inside another link
                pos = match.start()
                if any(pos in r for r in existing_ranges):
                    continue
                
                url = match.group(0)
                
                link = Link(
                    type='url',
                    target=url.strip(),
                    text=None,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    raw=url
                )
                
                result.links.append(link)
        
        except re.error as e:
            result.add_warning(f"URL regex error: {e}")
        except Exception as e:
            result.add_warning(f"URL parsing error: {e}")
    
    def extract_unique_targets(self, links: List[Link]) -> Set[str]:
        """Extract unique link targets."""
        return {link.target for link in links}
    
    def group_by_type(self, links: List[Link]) -> Dict[str, List[Link]]:
        """Group links by type."""
        groups: Dict[str, List[Link]] = {}
        for link in links:
            if link.type not in groups:
                groups[link.type] = []
            groups[link.type].append(link)
        return groups
    
    def get_statistics(self, result: LinkParseResult) -> Dict[str, Any]:
        """Get parsing statistics."""
        groups = self.group_by_type(result.links)
        
        return {
            "total_links": len(result.links),
            "wikilinks": len(groups.get('wikilink', [])),
            "markdown_links": len(groups.get('markdown', [])),
            "images": len(groups.get('image', [])),
            "raw_urls": len(groups.get('url', [])),
            "unique_targets": len(self.extract_unique_targets(result.links)),
            "parse_time_ms": result.parse_time_ms,
            "errors": len(result.errors),
            "warnings": len(result.warnings),
        }


def parse_links_safe(content: str) -> LinkParseResult:
    """
    Safe link parsing with default settings.
    
    Returns valid result even if parsing fails.
    """
    parser = LinkParser()
    try:
        return parser.parse_links(content)
    except Exception as e:
        result = LinkParseResult(
            is_valid=False,
            content=content
        )
        result.add_error(f"Catastrophic link parsing failure: {e}")
        logger.error("link_parsing_catastrophic_failure",
                    error=str(e),
                    error_type=type(e).__name__)
        return result


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python link_parser.py <file>")
        sys.exit(1)
    
    from pathlib import Path
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    content = file_path.read_text(encoding='utf-8')
    
    parser = LinkParser()
    result = parser.parse_links(content)
    
    print(f"\n{'✅ SUCCESS' if result.is_valid else '❌ FAILED'}")
    print(f"\nStatistics:")
    stats = parser.get_statistics(result)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  ❌ {error}")
    
    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
    
    if result.links:
        print(f"\nFirst 10 links:")
        for link in result.links[:10]:
            print(f"  [{link.type}] {link.target}")

