# AI Semantic Tagging - Intelligent Tag Generation

**Use AI to understand content and generate semantically relevant tags**

---

## The Vision

**Traditional tagging** (keyword matching):
```markdown
# Ophelia's Character Analysis

Discussion of Ophelia's madness scene...

Tags: ophelia  ❌ (misses: shakespeare, hamlet, tragedy, mental-health)
```

**AI semantic tagging** (understanding):
```markdown
# Ophelia's Character Analysis

Discussion of Ophelia's madness scene...

AI suggests: [shakespeare, hamlet, tragedy, character-analysis, mental-health, elizabethan-drama]
✅ (Understands context, even if words not in text!)
```

---

## How It Works

### Step 1: AI Reads Content

**Input** (your note):
```markdown
# Ophelia's Character Analysis

In Act IV, Ophelia's descent into madness represents the intersection
of patriarchal oppression and female agency in Elizabethan drama.
Her flower distribution scene employs botanical symbolism to critique
court corruption.
```

**AI analyzes**:
- Main topic: Character analysis of Ophelia
- Work: Hamlet
- Author: Shakespeare (implied)
- Themes: madness, patriarchy, symbolism, corruption
- Era: Elizabethan drama
- Genre: Tragedy
- Literary technique: symbolism

---

### Step 2: AI Generates Tags

**AI output**:
```json
{
  "suggested_tags": [
    "shakespeare",
    "hamlet",
    "ophelia",
    "tragedy",
    "character-analysis",
    "elizabethan-drama",
    "mental-health",
    "symbolism",
    "feminist-criticism",
    "patriarchy"
  ],
  "confidence": {
    "shakespeare": 0.99,
    "hamlet": 0.99,
    "ophelia": 1.0,
    "tragedy": 0.95,
    "character-analysis": 0.98,
    "elizabethan-drama": 0.92,
    "mental-health": 0.88,
    "symbolism": 0.90,
    "feminist-criticism": 0.85,
    "patriarchy": 0.87
  },
  "reasoning": "This note analyzes Ophelia's character from Hamlet. The discussion of madness, patriarchy, and symbolism suggests feminist literary criticism. Elizabethan drama context is implied by Shakespeare's era."
}
```

---

### Step 3: User Reviews and Approves

**Interactive CLI**:
```bash
advanced-memory tag suggest notes/ophelia-analysis.md

# Output:
📝 Analyzing: Ophelia's Character Analysis

🤖 AI suggests 10 tags:

High confidence (≥95%):
  ✅ shakespeare (99%)
  ✅ hamlet (99%)
  ✅ ophelia (100%)
  ✅ tragedy (95%)
  ✅ character-analysis (98%)

Medium confidence (85-94%):
  ⚠️  elizabethan-drama (92%)
  ⚠️  symbolism (90%)
  ⚠️  mental-health (88%)
  ⚠️  patriarchy (87%)
  ⚠️  feminist-criticism (85%)

Accept all? [Y/n/custom]: y

✅ Tags added to frontmatter!
```

---

### Step 4: Frontmatter Updated

**Before**:
```markdown
# Ophelia's Character Analysis

Content...
```

**After**:
```markdown
---
title: Ophelia's Character Analysis
tags: [shakespeare, hamlet, ophelia, tragedy, character-analysis, elizabethan-drama, mental-health, symbolism, feminist-criticism, patriarchy]
ai_tagged: true
ai_tagged_date: 2025-10-17T10:30:00Z
---

# Ophelia's Character Analysis

Content...
```

**Frontmatter added** with intelligent tags! ✨

---

## CLI Commands

### Command 1: `advanced-memory tag suggest`

**Purpose**: Get AI tag suggestions for a single file

**Usage**:
```bash
# Single file
advanced-memory tag suggest notes/my-note.md

# With custom prompt
advanced-memory tag suggest notes/my-note.md --prompt "Focus on technical concepts"

# Auto-accept high confidence
advanced-memory tag suggest notes/my-note.md --auto-accept 0.95

# Dry run (show suggestions, don't modify)
advanced-memory tag suggest notes/my-note.md --dry-run
```

**Options**:
- `--model`: AI model to use (claude-3-5-sonnet, gpt-4, etc.)
- `--max-tags`: Maximum tags to suggest (default: 10)
- `--min-confidence`: Minimum confidence threshold (default: 0.8)
- `--auto-accept`: Auto-accept tags above this confidence (optional)
- `--dry-run`: Show suggestions without modifying file
- `--prompt`: Custom prompt for tag generation

---

### Command 2: `advanced-memory tag batch`

**Purpose**: Tag multiple files with AI

**Usage**:
```bash
# Tag all files in folder
advanced-memory tag batch notes/

# Tag files matching query
advanced-memory tag batch --query "type:note AND tag:untagged"

# Tag recently modified
advanced-memory tag batch --query "updated:7d"

# Preview mode (show suggestions for all, don't modify)
advanced-memory tag batch notes/ --preview
```

**Options**:
- `--query`: Select files via search query
- `--folder`: Select files by folder
- `--limit`: Process only N files (for testing)
- `--preview`: Show suggestions without modifying
- `--parallel`: Process N files in parallel (default: 5)
- `--model`: AI model to use

**Output**:
```
📊 AI Batch Tagging

Analyzing 47 files...

Progress: [████████████████████] 47/47

Results:
  ✅ 42 files tagged successfully
  ⚠️  3 files skipped (already well-tagged)
  ❌ 2 files failed (AI error)

Total tags added: 234
Average tags per file: 5.6
Total API cost: $0.12
```

---

### Command 3: `advanced-memory tag analyze`

**Purpose**: Analyze tag quality across knowledge base

**Usage**:
```bash
# Analyze all tags
advanced-memory tag analyze

# Analyze specific folder
advanced-memory tag analyze --folder research/

# Show recommendations
advanced-memory tag analyze --recommendations
```

**Output**:
```
📊 Tag Analysis

Total entities: 487
Tagged entities: 312 (64%)
Untagged entities: 175 (36%)

Tag distribution:
  • 1-3 tags: 120 entities
  • 4-6 tags: 145 entities
  • 7-10 tags: 47 entities
  • 10+ tags: 0 entities

Most common tags:
  1. python (89 entities)
  2. research (67 entities)
  3. ai (54 entities)
  4. tutorial (43 entities)
  5. web (38 entities)

Recommendations:
  ⚠️  175 entities have no tags
  💡 Run: advanced-memory tag batch --query "tag:none"

  ⚠️  67 entities have only 1 tag
  💡 Run: advanced-memory tag batch --query "tag_count:1"
```

---

### Command 4: `advanced-memory tag cleanup`

**Purpose**: Clean up redundant/inconsistent tags

**Usage**:
```bash
# Find similar tags
advanced-memory tag cleanup --find-similar

# Merge tags
advanced-memory tag cleanup --merge "python,Python,python-lang" --to "python"

# Remove unused tags
advanced-memory tag cleanup --remove-unused
```

**Example**:
```
🔍 Finding similar tags...

Similar tag groups:
  1. python, Python, python-lang, py
     → Suggest: Merge to "python"

  2. machine-learning, ml, machinelearning
     → Suggest: Merge to "machine-learning"

  3. javascript, js, JavaScript
     → Suggest: Merge to "javascript"

Merge these tags? [y/N]:
```

---

## AI Prompts

### Default Prompt

```
You are a semantic tagging expert. Analyze this markdown note and suggest relevant tags.

Rules:
1. Generate 5-10 tags that capture the note's meaning
2. Include tags for:
   - Main topics/subjects
   - Key concepts discussed
   - Related fields/domains
   - Implied context (e.g., "shakespeare" for Ophelia discussion)
3. Use lowercase, hyphen-separated (e.g., "machine-learning")
4. Be specific but not overly narrow
5. Include both explicit (mentioned) and implicit (understood) tags

Note content:
{content}

Return JSON:
{
  "suggested_tags": ["tag1", "tag2", ...],
  "confidence": {"tag1": 0.95, "tag2": 0.88, ...},
  "reasoning": "Brief explanation of tag choices"
}
```

---

### Domain-Specific Prompts

**For code/technical notes**:
```
Focus on:
- Programming languages
- Frameworks and libraries
- Concepts (e.g., async, OOP, functional)
- Patterns (e.g., singleton, MVC)
```

**For research notes**:
```
Focus on:
- Research topics
- Methodologies
- Theories
- Key researchers/authors
- Academic fields
```

**For creative writing**:
```
Focus on:
- Genres
- Themes
- Literary techniques
- Character archetypes
- Narrative structures
```

---

## Implementation

### Service: AI Tagging Service

**File**: `src/advanced_memory/services/ai_tagging_service.py`

```python
"""AI-powered semantic tagging service."""

import json
from typing import Any

from loguru import logger

from advanced_memory.services.ai_integration import AIIntegration


class AITaggingService:
    """Service for AI-powered tag generation."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.ai = AIIntegration(model=model)
        self.default_prompt = self._load_default_prompt()

    async def suggest_tags(
        self,
        content: str,
        existing_tags: list[str] | None = None,
        max_tags: int = 10,
        min_confidence: float = 0.8,
        custom_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Generate tag suggestions for content.

        Args:
            content: Markdown content to analyze
            existing_tags: Tags already present (optional)
            max_tags: Maximum tags to suggest
            min_confidence: Minimum confidence threshold
            custom_prompt: Custom tagging instructions

        Returns:
            {
                "suggested_tags": ["tag1", "tag2", ...],
                "confidence": {"tag1": 0.95, ...},
                "reasoning": "explanation",
                "existing_preserved": ["tag1", ...]  # If any existing
            }
        """
        prompt = custom_prompt or self.default_prompt

        # Build full prompt
        full_prompt = f"""
{prompt}

Existing tags (preserve these): {existing_tags or 'none'}
Maximum new tags: {max_tags}
Minimum confidence: {min_confidence}

Note content:
{content[:2000]}  # Limit to first 2000 chars for efficiency

Return JSON with suggested_tags, confidence, and reasoning.
"""

        # Call AI
        try:
            response = await self.ai.generate_completion(full_prompt)

            # Parse JSON response
            result = json.loads(response)

            # Filter by confidence
            filtered_tags = [
                tag for tag, conf in result["confidence"].items()
                if conf >= min_confidence
            ]

            result["suggested_tags"] = filtered_tags[:max_tags]

            # Preserve existing tags
            if existing_tags:
                result["existing_preserved"] = existing_tags

            return result

        except Exception as e:
            logger.error(f"AI tagging failed: {e}")
            return {
                "suggested_tags": [],
                "confidence": {},
                "reasoning": f"Error: {str(e)}",
                "error": True
            }

    async def batch_tag(
        self,
        files: list[str],
        **kwargs
    ) -> dict[str, Any]:
        """Tag multiple files.

        Args:
            files: List of file paths to tag
            **kwargs: Passed to suggest_tags()

        Returns:
            {
                "total_files": 47,
                "successful": 42,
                "failed": 3,
                "skipped": 2,
                "total_tags_added": 234,
                "details": {...}
            }
        """
        results = {
            "total_files": len(files),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "total_tags_added": 0,
            "details": {}
        }

        for file_path in files:
            # Read file
            # Get existing tags
            # Call suggest_tags()
            # Update frontmatter
            # Track stats
            pass

        return results

    def _load_default_prompt(self) -> str:
        """Load default tagging prompt."""
        return """
You are a semantic tagging expert. Analyze this markdown note and suggest relevant tags.

Rules:
1. Generate 5-10 tags that capture the note's meaning
2. Include tags for:
   - Main topics/subjects (e.g., "ophelia" for a note about her)
   - Broader context (e.g., "shakespeare" even if not mentioned)
   - Key concepts discussed (e.g., "madness", "symbolism")
   - Related fields/domains (e.g., "elizabethan-drama", "feminist-criticism")
   - Implied context that a knowledgeable reader would recognize
3. Use lowercase, hyphen-separated (e.g., "machine-learning")
4. Be specific but not overly narrow
5. Include both explicit (mentioned in text) and implicit (understood from context) tags

Examples:
- Note about Ophelia → tags include "shakespeare", "hamlet", "tragedy"
- Note about neural networks → tags include "ai", "deep-learning", "machine-learning"
- Note about Docker → tags include "containers", "devops", "infrastructure"

Return JSON with suggested_tags, confidence scores (0-1), and brief reasoning.
"""
```

---

### CLI Command Implementation

**File**: `src/advanced_memory/cli/commands/tag.py`

```python
"""CLI commands for AI-powered tagging."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from advanced_memory.cli.app import app
from advanced_memory.config import get_project_config
from advanced_memory.services.ai_tagging_service import AITaggingService
from advanced_memory.services.file_service import FileService

# Create tag subcommand
tag_app = typer.Typer(help="AI-powered semantic tagging")
app.add_typer(tag_app, name="tag")

console = Console()


@tag_app.command("suggest")
def suggest_tags(
    file_path: Path = typer.Argument(..., help="Path to markdown file"),
    max_tags: int = typer.Option(10, help="Maximum tags to suggest"),
    min_confidence: float = typer.Option(0.8, help="Minimum confidence (0-1)"),
    auto_accept: float | None = typer.Option(None, help="Auto-accept above this confidence"),
    dry_run: bool = typer.Option(False, help="Show suggestions without modifying file"),
    model: str = typer.Option("claude-3-5-sonnet-20241022", help="AI model to use"),
):
    """Get AI tag suggestions for a single markdown file."""
    asyncio.run(_suggest_tags_async(
        file_path, max_tags, min_confidence, auto_accept, dry_run, model
    ))


async def _suggest_tags_async(
    file_path: Path,
    max_tags: int,
    min_confidence: float,
    auto_accept: float | None,
    dry_run: bool,
    model: str,
):
    """Async implementation of suggest_tags."""
    config = get_project_config()

    # Validate file exists
    full_path = config.home / file_path
    if not full_path.exists():
        console.print(f"[red]Error: File not found: {file_path}[/red]")
        raise typer.Exit(1)

    # Read content
    content = full_path.read_text(encoding="utf-8")

    # Extract existing tags
    # (parse frontmatter if present)
    from advanced_memory.file_utils import has_frontmatter, parse_frontmatter

    existing_tags = []
    if has_frontmatter(content):
        frontmatter = parse_frontmatter(content)
        existing_tags = frontmatter.get("tags", [])

    # Get AI suggestions
    console.print(f"\n📝 Analyzing: [cyan]{file_path.name}[/cyan]\n")

    tagging_service = AITaggingService(model=model)

    with console.status("[bold cyan]AI is thinking..."):
        result = await tagging_service.suggest_tags(
            content=content,
            existing_tags=existing_tags,
            max_tags=max_tags,
            min_confidence=min_confidence,
        )

    if result.get("error"):
        console.print(f"[red]Error: {result['reasoning']}[/red]")
        raise typer.Exit(1)

    # Display suggestions
    suggested = result["suggested_tags"]
    confidence = result["confidence"]
    reasoning = result["reasoning"]

    if not suggested:
        console.print("[yellow]No tags suggested above confidence threshold.[/yellow]")
        return

    console.print(f"🤖 AI suggests {len(suggested)} tags:\n")

    # Group by confidence
    high_conf = [(tag, conf) for tag, conf in confidence.items() if conf >= 0.95]
    medium_conf = [(tag, conf) for tag, conf in confidence.items() if 0.85 <= conf < 0.95]
    low_conf = [(tag, conf) for tag, conf in confidence.items() if min_confidence <= conf < 0.85]

    if high_conf:
        console.print("[bold green]High confidence (≥95%):[/bold green]")
        for tag, conf in high_conf:
            console.print(f"  ✅ {tag} ({conf*100:.0f}%)")

    if medium_conf:
        console.print("\n[bold yellow]Medium confidence (85-94%):[/bold yellow]")
        for tag, conf in medium_conf:
            console.print(f"  ⚠️  {tag} ({conf*100:.0f}%)")

    if low_conf:
        console.print(f"\n[bold]Lower confidence ({min_confidence*100:.0f}-84%):[/bold]")
        for tag, conf in low_conf:
            console.print(f"  ℹ️  {tag} ({conf*100:.0f}%)")

    console.print(f"\n[dim]Reasoning: {reasoning}[/dim]")

    # Dry run - stop here
    if dry_run:
        console.print("\n[yellow]Dry run - no changes made[/yellow]")
        return

    # Auto-accept?
    if auto_accept:
        tags_to_add = [tag for tag, conf in confidence.items() if conf >= auto_accept]
        console.print(f"\n[green]Auto-accepting {len(tags_to_add)} tags (≥{auto_accept*100:.0f}% confidence)[/green]")
    else:
        # Ask user
        choice = typer.prompt(
            "\nAccept these tags? [Y/n/custom]",
            default="Y"
        )

        if choice.lower() == "n":
            console.print("[yellow]Cancelled - no changes made[/yellow]")
            return
        elif choice.lower() == "custom":
            # Let user select individual tags
            tags_to_add = []
            for tag in suggested:
                if typer.confirm(f"  Add tag '{tag}'?", default=True):
                    tags_to_add.append(tag)
        else:
            tags_to_add = suggested

    # Update frontmatter
    # (add tags, add ai_tagged: true, ai_tagged_date)
    console.print(f"\n✅ Added {len(tags_to_add)} tags to frontmatter!")


@tag_app.command("batch")
def batch_tag(
    folder: Path | None = typer.Option(None, help="Folder to tag"),
    query: str | None = typer.Option(None, help="Search query to select files"),
    limit: int | None = typer.Option(None, help="Process only N files"),
    preview: bool = typer.Option(False, help="Preview mode (don't modify)"),
    parallel: int = typer.Option(5, help="Process N files in parallel"),
    model: str = typer.Option("claude-3-5-sonnet-20241022", help="AI model"),
):
    """Batch tag multiple files with AI."""
    console.print("📊 AI Batch Tagging\n")
    # Implementation...


@tag_app.command("analyze")
def analyze_tags(
    folder: Path | None = typer.Option(None, help="Folder to analyze"),
    recommendations: bool = typer.Option(False, help="Show recommendations"),
):
    """Analyze tag quality across knowledge base."""
    console.print("📊 Tag Analysis\n")
    # Implementation...


@tag_app.command("cleanup")
def cleanup_tags(
    find_similar: bool = typer.Option(False, help="Find similar tags"),
    merge: str | None = typer.Option(None, help="Merge tags (comma-separated)"),
    to: str | None = typer.Option(None, help="Target tag for merge"),
):
    """Clean up redundant/inconsistent tags."""
    console.print("🔍 Tag Cleanup\n")
    # Implementation...
```

---

## MCP Tool Integration

### Portmanteau Tool: `adn_tagger`

```python
@mcp.tool()
async def adn_tagger(
    operation: Literal["suggest", "batch", "analyze", "cleanup"],
    # ... parameters
) -> str:
    """
    AI-powered semantic tagging for your knowledge base.

    Operations:
    - suggest: Get AI tag suggestions for a file
    - batch: Tag multiple files at once
    - analyze: Analyze tag quality
    - cleanup: Clean up redundant tags

    Examples:
    - adn_tagger("suggest", identifier="my-note")
    - adn_tagger("batch", query="tag:none", limit=50)
    - adn_tagger("analyze", folder="research")
    """
```

---

## Example Workflows

### Workflow 1: Tag New Notes

```bash
# You create a note manually (no tags)
vim notes/quantum-computing-intro.md

# Get AI suggestions
advanced-memory tag suggest notes/quantum-computing-intro.md

# Output:
🤖 AI suggests:
  ✅ quantum-computing (99%)
  ✅ physics (98%)
  ✅ computer-science (95%)
  ⚠️  qubits (92%)
  ⚠️  superposition (88%)
  ⚠️  quantum-mechanics (87%)

Accept all? [Y/n]: y

✅ Tags added!

# Sync
advanced-memory sync
```

---

### Workflow 2: Bulk Tag Old Notes

```bash
# You have 200 old notes without tags
advanced-memory tag batch notes/ --preview

# Output:
Analyzing 200 files...
[Progress bar...]

Preview:
  • notes/note1.md → 6 tags suggested
  • notes/note2.md → 5 tags suggested
  • ...

Estimated cost: $0.50 (200 files × $0.0025)

Proceed? [y/N]: y

[Processing...]

✅ 200 files tagged successfully
Total tags added: 1,234
Total cost: $0.48
```

---

### Workflow 3: Improve Existing Tags

```bash
# Check tag quality
advanced-memory tag analyze

# Output:
175 entities have no tags
67 entities have only 1 tag

# Tag the untagged
advanced-memory tag batch --query "tag:none" --auto-accept 0.95

# Enhance poorly-tagged
advanced-memory tag batch --query "tag_count:1" --max-tags 5
```

---

## AI Model Selection

### Claude 3.5 Sonnet (Recommended)

**Pros**:
- ✅ Excellent semantic understanding
- ✅ Understands implicit context (Ophelia → Shakespeare)
- ✅ Good at reasoning
- ✅ Fast responses

**Cost**: ~$0.003 per file (200-word note)

**Example**:
```bash
advanced-memory tag suggest note.md --model claude-3-5-sonnet-20241022
```

---

### GPT-4 Turbo

**Pros**:
- ✅ Good understanding
- ✅ Cheaper than Claude
- ✅ Fast

**Cost**: ~$0.002 per file

**Example**:
```bash
advanced-memory tag suggest note.md --model gpt-4-turbo
```

---

### GPT-3.5 Turbo (Budget)

**Pros**:
- ✅ Very cheap
- ✅ Very fast

**Cons**:
- ⚠️ Less sophisticated (might miss implicit context)
- ⚠️ May suggest generic tags

**Cost**: ~$0.0005 per file (4x cheaper than GPT-4)

**Good for**: Large batches where cost matters

---

## Cost Analysis

### Batch Tagging 1000 Notes

| Model | Cost per File | Total Cost | Quality |
|-------|---------------|------------|---------|
| Claude 3.5 Sonnet | $0.003 | **$3.00** | ⭐⭐⭐⭐⭐ |
| GPT-4 Turbo | $0.002 | **$2.00** | ⭐⭐⭐⭐ |
| GPT-3.5 Turbo | $0.0005 | **$0.50** | ⭐⭐⭐ |

**Recommendation**:
- **Small batches** (< 100): Use Claude (best quality)
- **Large batches** (> 500): Use GPT-3.5 (cost-effective)
- **Important notes**: Use Claude (worth the cost)

---

## Tag Quality Examples

### Example 1: Literature Note

**Content**:
```markdown
# The Green Light Symbolism

In The Great Gatsby, the green light at the end of Daisy's dock
represents Gatsby's hopes and dreams. It symbolizes the American
Dream's promise and ultimate futility.
```

**AI suggests**:
```
High confidence:
  ✅ great-gatsby (99%)
  ✅ fitzgerald (98%)
  ✅ symbolism (98%)
  ✅ american-literature (96%)
  ✅ american-dream (95%)

Medium confidence:
  ⚠️  1920s (92%)
  ⚠️  modernism (88%)
  ⚠️  literary-analysis (87%)
```

**Note**: Even though "Fitzgerald" isn't mentioned, AI knows Great Gatsby → Fitzgerald!

---

### Example 2: Technical Note

**Content**:
```markdown
# Async/Await in Python

The async/await syntax allows concurrent execution without threads.
Event loops handle task scheduling. Useful for I/O-bound operations.
```

**AI suggests**:
```
High confidence:
  ✅ python (99%)
  ✅ async (99%)
  ✅ concurrency (97%)
  ✅ asyncio (96%)

Medium confidence:
  ⚠️  event-loop (93%)
  ⚠️  coroutines (90%)
  ⚠️  io-bound (88%)
  ⚠️  programming (85%)
```

---

### Example 3: Concept Note

**Content**:
```markdown
# Zettelkasten Method

A note-taking system where each note captures one idea and links
to related notes. Promotes emergent insights through connections.
Luhmann created 90,000 notes using this method.
```

**AI suggests**:
```
High confidence:
  ✅ zettelkasten (100%)
  ✅ note-taking (98%)
  ✅ pkm (97%)  # Personal Knowledge Management
  ✅ luhmann (96%)

Medium confidence:
  ⚠️  knowledge-management (92%)
  ⚠️  linking (90%)
  ⚠️  emergent-thinking (88%)
  ⚠️  slip-box (85%)
```

**Note**: "PKM" and "slip-box" not in text, but AI understands context!

---

## Advanced Features

### Feature 1: Hierarchical Tags

**AI can suggest hierarchical tags**:
```
technology/python/async
literature/shakespeare/hamlet
research/ai/machine-learning/neural-networks
```

**Benefit**: Better organization, precise filtering

---

### Feature 2: Tag Synonyms

**AI recognizes synonyms**:
```
Note about "ML" → suggests: machine-learning, ml, artificial-intelligence
Note about "JS" → suggests: javascript, js, web-programming
```

**Benefit**: Consistent tagging across knowledge base

---

### Feature 3: Domain Detection

**AI detects domain and adjusts tags**:

**Code note** → Focus on: languages, frameworks, concepts
**Research note** → Focus on: topics, methodologies, authors
**Creative note** → Focus on: themes, genres, techniques

**Benefit**: Domain-appropriate tags

---

### Feature 4: Tag Relationships

**AI understands tag relationships**:
```
If tagged "neural-networks", should also suggest:
  - deep-learning (parent concept)
  - ai (grandparent)
  - machine-learning (parent)
  - transformers (sibling concept)
```

**Benefit**: Complete context, better discoverability

---

### Feature 5: Quality Control & Error Detection

**AI detects quality issues and flags them!**

**Example 1: Gibberish Detection**

**Your note**:
```markdown
# Quantm Computng Fundamentls

Qubits are the goblahoy of quantum systms. They utiliz
superpostion to achive paralelism.
```

**AI detects**:
- ❌ Multiple typos: "Quantm", "Computng", "Fundamentls"
- ❌ Nonsense word: "goblahoy"
- ❌ More typos: "systms", "utiliz", "superpostion", "achive", "paralelism"

**AI suggests**:
```json
{
  "suggested_tags": [
    "quantum-computing",  // Corrected from "Quantm Computng"
    "qubits",
    "physics"
  ],
  "quality_flags": [
    "needs-review",
    "contains-typos",
    "contains-gibberish"
  ],
  "errors_detected": {
    "typos": ["Quantm→Quantum", "Computng→Computing", "Fundamentls→Fundamentals",
              "systms→systems", "utiliz→utilize", "superpostion→superposition",
              "achive→achieve", "paralelism→parallelism"],
    "gibberish": ["goblahoy"],
    "confidence": 0.95
  },
  "severity": "medium",
  "recommendation": "Review and fix typos before publishing"
}
```

**Frontmatter updated**:
```yaml
---
title: Quantum Computing Fundamentals
tags: [quantum-computing, qubits, physics, needs-review, contains-typos, contains-gibberish]
quality_score: 0.4  # Low score due to errors
ai_detected_errors: true
needs_review: true
---
```

**User alerted**:
```bash
advanced-memory tag suggest notes/quantum.md

⚠️  Quality Issues Detected!
   • 8 typos found
   • 1 nonsense word: "goblahoy"

Suggested corrections:
   Quantm → Quantum
   goblahoy → (unknown - needs review)

Add quality flag tags? [Y/n]: y

✅ Added tags: [needs-review, contains-typos, contains-gibberish]
```

---

**Example 2: Incomplete Content Detection**

**Your note**:
```markdown
# Docker Tutorial

TODO: write this section

Remember to explain:
- containers
- images
-
```

**AI detects**:
- ❌ Incomplete content (mostly TODOs)
- ❌ Empty bullet point
- ❌ No substantive information

**AI suggests**:
```json
{
  "suggested_tags": ["docker", "containers"],
  "quality_flags": [
    "incomplete",
    "draft",
    "needs-content"
  ],
  "quality_score": 0.2,
  "severity": "high",
  "recommendation": "Note is mostly placeholders - add actual content"
}
```

---

**Example 3: Contradictory Information**

**Your note**:
```markdown
# Python Version Guide

Python 3.8 was released in 2019.

The latest version is Python 3.11, released in 2019.

Python 3.12 came out before 3.11.
```

**AI detects**:
- ❌ Contradiction: Python 3.11 can't be from 2019 if 3.8 was 2019
- ❌ Logic error: 3.12 can't come before 3.11

**AI suggests**:
```json
{
  "suggested_tags": ["python", "python-versions"],
  "quality_flags": [
    "contains-contradictions",
    "needs-fact-check"
  ],
  "errors_detected": {
    "contradictions": [
      "Python 3.11 release date conflicts with Python 3.8 date",
      "Version ordering error: 3.12 before 3.11 is impossible"
    ]
  },
  "severity": "medium",
  "recommendation": "Verify Python release dates and version order"
}
```

---

**Example 4: Low-Quality Content**

**Your note**:
```markdown
# AI Stuff

AI is cool. It does things. Machine learning is part of AI.
Neural networks are used. Deep learning exists.

That's all I know.
```

**AI detects**:
- ❌ Extremely vague content
- ❌ No depth or detail
- ❌ Self-admission of limited knowledge

**AI suggests**:
```json
{
  "suggested_tags": ["ai", "machine-learning"],
  "quality_flags": [
    "low-quality",
    "needs-expansion",
    "superficial"
  ],
  "quality_score": 0.3,
  "severity": "low",
  "recommendation": "Expand with specific details, examples, or delete if not useful"
}
```

---

**Example 5: Outdated Information**

**Your note**:
```markdown
# Web Development Best Practices

Always use jQuery for DOM manipulation.
Internet Explorer 6 is the dominant browser.
Flash is the best way to add interactivity.
```

**AI detects**:
- ❌ Severely outdated (jQuery, IE6, Flash all deprecated)
- ❌ Advice is harmful in 2025

**AI suggests**:
```json
{
  "suggested_tags": ["web-development"],
  "quality_flags": [
    "outdated",
    "historical",
    "not-current-best-practice"
  ],
  "quality_score": 0.2,
  "severity": "high",
  "recommendation": "This advice is outdated (circa 2010). Update or mark as historical reference."
}
```

---

**Benefit**: AI doesn't just tag topics - it **quality-checks your knowledge base!**

---

## Quality Control Commands

### Command: `advanced-memory tag check-quality`

**Purpose**: Find notes with quality issues

**Usage**:
```bash
# Find all notes with errors
advanced-memory tag check-quality

# Find specific issues
advanced-memory tag check-quality --type typos
advanced-memory tag check-quality --type gibberish
advanced-memory tag check-quality --type incomplete
advanced-memory tag check-quality --type contradictions

# Show detailed report
advanced-memory tag check-quality --detailed
```

**Output**:
```
🔍 Knowledge Base Quality Report

Total entities: 487

Quality Issues Found:
  ⚠️  23 notes with typos
  ⚠️  8 notes with gibberish
  ⚠️  45 incomplete notes (drafts, TODOs)
  ⚠️  3 notes with contradictions
  ⚠️  12 outdated notes

Overall quality score: 82% (400 high-quality, 87 need review)

Notes needing immediate attention:
  1. notes/quantum.md - contains gibberish ("goblahoy")
  2. notes/web-dev.md - severely outdated (jQuery, Flash)
  3. notes/python.md - contradictory information

Run 'advanced-memory tag check-quality --detailed' for full report
```

---

### Quality Flag Tags (Standard Set)

**Error tags**:
- `contains-typos` - Spelling/grammar errors detected
- `contains-gibberish` - Nonsense words detected (e.g., "goblahoy")
- `needs-spell-check` - Many minor errors

**Content quality tags**:
- `incomplete` - Note is a stub or draft
- `needs-expansion` - Too brief, lacks depth
- `superficial` - Surface-level only
- `needs-examples` - Could use code/examples
- `low-quality` - Overall poor quality

**Factual accuracy tags**:
- `contains-contradictions` - Self-contradictory statements
- `needs-fact-check` - Questionable claims
- `outdated` - Information no longer current
- `historical` - Correct for its time, but dated

**Review tags**:
- `needs-review` - General flag for review
- `needs-content` - Missing substantive information
- `needs-citations` - Claims without sources

---

### Finding Notes with Issues

**Search by quality flags**:
```bash
# All notes needing review
advanced-memory tool search-notes "tag:needs-review"

# All notes with typos
advanced-memory tool search-notes "tag:contains-typos"

# All notes with gibberish
advanced-memory tool search-notes "tag:contains-gibberish"

# Multiple issues
advanced-memory tool search-notes "tag:incomplete AND tag:needs-expansion"
```

**Batch fix workflow**:
```bash
# 1. Find problematic notes
advanced-memory tag check-quality --type gibberish

# Output:
# notes/quantum.md - contains "goblahoy"
# notes/experiment.md - contains "xyzqwerty"

# 2. Review and fix
vim notes/quantum.md  # Fix "goblahoy" → "foundation"

# 3. Re-tag (AI removes quality flags)
advanced-memory tag suggest notes/quantum.md

# Output:
# ✅ No errors detected!
# Tags: [quantum-computing, qubits, physics]
# (Quality flags removed automatically)
```

---

### Auto-Fix Suggestions

**AI can suggest corrections**:
```bash
advanced-memory tag suggest notes/quantum.md --auto-fix

# Output:
⚠️  Errors detected! AI suggests fixes:

Typos:
  Line 3: "Quantm" → "Quantum" [Fix]
  Line 5: "goblahoy" → ??? (unknown word, manual review needed)
  Line 7: "paralelism" → "parallelism" [Fix]

Apply auto-fixes? [y/N]: y

✅ Fixed 7 typos automatically
⚠️  1 unknown word needs manual review: "goblahoy"

File updated. Review changes and run sync.
```

---

## Integration with Existing Features

### Combine with Zettelmaker

```bash
# Generate note from template
advanced-memory tool adn_zettelmaker generate python async --quality advanced

# AI auto-tags the generated note
advanced-memory tag suggest zettelkasten/developer/python/async-await.md --auto-accept 0.95

# Result: Note has intelligent tags from creation!
```

---

### Combine with Import

```bash
# Import Obsidian vault (no tags)
advanced-memory project add obsidian ~/Documents/ObsidianVault
advanced-memory sync

# AI tag all imported notes
advanced-memory tag batch --query "tag:none" --model gpt-3.5-turbo

# Result: Entire vault intelligently tagged!
```

---

### Combine with Search

```bash
# AI tags notes
advanced-memory tag batch notes/

# Now search with semantic tags
advanced-memory tool search-notes "tag:shakespeare"
# Finds ALL notes about Shakespeare, Hamlet, etc.
```

---

## Privacy & Cost Controls

### Local vs. API

**API-based** (current proposal):
- Sends content to Claude/OpenAI
- Costs money ($0.002-0.003 per file)
- High quality results

**Future: Local models** (optional):
```bash
# Use local LLM (no API cost, slower, lower quality)
advanced-memory tag suggest note.md --model local/mistral-7b
```

**Trade-off**: Free vs. Quality

---

### Cost Limits

**Config option**:
```json
{
  "ai_tagging": {
    "daily_cost_limit": 5.00,
    "monthly_cost_limit": 50.00,
    "warn_at_cost": 1.00
  }
}
```

**Behavior**:
```bash
advanced-memory tag batch notes/  # Starts processing

⚠️  Cost warning: $1.05 spent today (limit: $5.00)

Continue? [y/N]:
```

---

## Roadmap

### Phase 1: Core Feature (2-3 weeks)

**Deliverables**:
- ✅ `AITaggingService` (tag suggestion logic)
- ✅ `tag suggest` CLI command (single file)
- ✅ Claude integration
- ✅ Frontmatter update logic
- ✅ Tests

**Timeline**: 2-3 weeks

---

### Phase 2: Batch Operations (1-2 weeks)

**Deliverables**:
- ✅ `tag batch` CLI command
- ✅ Parallel processing
- ✅ Progress tracking
- ✅ Cost estimation and limits

**Timeline**: 1-2 weeks

---

### Phase 3: Analysis & Cleanup (1 week)

**Deliverables**:
- ✅ `tag analyze` CLI command
- ✅ `tag cleanup` CLI command
- ✅ Tag quality metrics

**Timeline**: 1 week

---

### Phase 4: Advanced Features (2-3 weeks)

**Deliverables**:
- ✅ Hierarchical tags
- ✅ Domain detection
- ✅ Tag relationships
- ✅ Local model support
- ✅ MCP tool `adn_tagger`

**Timeline**: 2-3 weeks

---

## Success Metrics

**Adoption**:
- % of entities with AI-generated tags
- User satisfaction with tag quality
- Reduction in manual tagging time

**Quality**:
- Tag precision (relevant tags)
- Tag recall (comprehensive tags)
- User acceptance rate

**Cost**:
- Average cost per file
- Total monthly spend
- ROI (time saved vs. cost)

---

## Killer Use Cases

### Use Case 1: "Tag My 500 Old Notes"

**Before**: Hours of manual tagging work
**After**:
```bash
advanced-memory tag batch notes/ --model gpt-3.5-turbo
# 5 minutes, $0.25 cost, 2,500 tags added
```

---

### Use Case 2: "Find All Shakespeare Notes"

**Before**: Hope you remembered to tag them
**After**: AI tagged automatically
```bash
advanced-memory tool search-notes "tag:shakespeare"
# Finds all notes about Hamlet, Ophelia, sonnets, etc.
```

---

### Use Case 3: "Organize Research Papers"

**Before**: Manual categorization
**After**: AI understands context
```bash
advanced-memory tag batch research/ --auto-accept 0.95
# AI tags by topic, methodology, field
```

---

## Summary

**Your brilliant ideas**:
1. ✨ AI reads content and generates intelligent tags (semantic understanding!)
2. 🛡️ AI detects errors and quality issues (auto quality control!)

**Key features**:
- ✅ Semantic understanding (Ophelia → Shakespeare)
- ✅ Implicit tagging (understands context)
- ✅ Error detection (typos, gibberish, contradictions)
- ✅ Quality scoring (0-1 score for each note)
- ✅ Batch processing (tag 1000s of notes)
- ✅ Cost controls (budget limits)
- ✅ Auto-fix suggestions (correct typos)
- ✅ Compatible with Obsidian, GitHub (YAML frontmatter)

**Impact**:
- 📚 Better organization (comprehensive tags)
- 🔍 Better search (semantic tags)
- 🛡️ Better quality (error detection)
- ⏱️ Time saved (automated tagging + QC)
- 🧠 Smarter knowledge base (AI understands AND validates your notes)

**This is a killer feature!** 🌟

Would take Advanced Memory from "good" to "magical" - true AI-powered knowledge management with built-in quality control! 🙏⚡

---

## Quality Control Use Cases

### Use Case 1: "Find All My Gibberish Notes"

```bash
advanced-memory tool search-notes "tag:contains-gibberish"

# Results:
# 1. notes/quantum.md - contains "goblahoy"
# 2. notes/experiment.md - contains "xyzqwerty"
# 3. notes/draft.md - contains "asdfghjkl"

# Fix them one by one
vim notes/quantum.md
# Change "goblahoy" to proper word

# Re-tag (AI removes flag)
advanced-memory tag suggest notes/quantum.md
# ✅ No errors! Quality flag removed
```

---

### Use Case 2: "Clean Up Before Publishing"

```bash
# Check quality of entire folder
advanced-memory tag check-quality --folder blog-posts/

# Output:
# ⚠️  3 posts with typos
# ⚠️  1 post with outdated info
# ✅ 15 posts are high-quality

# Fix issues
advanced-memory tag check-quality --type typos --auto-fix

# Publish only high-quality
advanced-memory export pdf blog-posts/ --exclude "tag:needs-review"
```

---

### Use Case 3: "Knowledge Base Health Check"

```bash
# Monthly quality audit
advanced-memory tag check-quality --detailed > quality-report-2025-10.txt

# Fix top issues
advanced-memory tool search-notes "tag:contains-gibberish"
# Fix gibberish notes

advanced-memory tool search-notes "tag:outdated"
# Update or archive outdated notes

# Re-check
advanced-memory tag check-quality
# Quality score improved: 82% → 94%! 🎉
```

---

## Standard Quality Flags

### The "Goblahoy" Tag Family

**`contains-gibberish`**: Nonsense words detected
- "goblahoy", "xyzqwerty", "asdfghjkl", etc.
- Indicator: Random character sequences, made-up words

**`contains-typos`**: Common spelling errors
- "Quantm", "paralelism", "occured"
- Indicator: Words not in dictionary, close to valid words

**`needs-spell-check`**: Many minor errors
- Multiple small typos throughout
- Indicator: High error density

**Usage**:
```bash
# Find all notes with any errors
advanced-memory tool search-notes "tag:contains-gibberish OR tag:contains-typos"

# Quality control workflow
advanced-memory tag batch notes/ --detect-errors
# AI tags all notes with quality flags

advanced-memory tool search-notes "tag:contains-gibberish"
# Fix the gibberish

advanced-memory tag batch notes/ --detect-errors
# Re-run to remove flags from fixed notes
```

---

*Proposal created: 2025-10-17*
*Status: Ready for implementation*
*Priority: HIGH (game-changing feature)*
