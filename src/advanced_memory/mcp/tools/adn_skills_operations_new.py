"""New operations for adn_skills tool - GitHub import and distillation.

This module contains operation handlers for:
- GitHub import (SkillsMP compatible)
- Wikipedia distillation
- ArXiv distillation
- Textbook distillation
- Text distillation
- Expert distillation
"""

import os
import re

import yaml
from loguru import logger

from advanced_memory.mcp.project_session import get_active_project
from advanced_memory.services.github_skills_importer import GitHubSkillsImporter
from advanced_memory.services.skill_distiller import SkillDistiller


async def _import_from_github_operation(
    repository: str | None,
    skill_path: str | None,
    branch: str,
    category: str | None,
    project: str | None,
) -> str:
    """Import skill from GitHub repository (SkillsMP compatible).

    Args:
        repository: GitHub repository identifier (e.g., "user/repo")
        skill_path: Path to skill folder in repo (optional)
        branch: Git branch (default: "main")
        category: Category for organization (optional)
        project: Project name (optional)

    Returns:
        Formatted result string
    """
    try:
        if not repository:
            return """# Error: Missing Required Parameter

**Operation:** import_from_github

**Missing:** repository parameter

The import_from_github operation requires a GitHub repository identifier.

**Example:**
```
adn_skills(
    operation="import_from_github",
    repository="anthropics/skills",
    skill_path="skills/mcp-builder",
    category="developer-tools"
)
```

**Provide the repository parameter and try again.**"""

        active_project = get_active_project(project)
        github_token = os.getenv("GITHUB_TOKEN")  # Optional

        logger.info(f"Importing skill from GitHub: {repository} (skill_path={skill_path})")

        # Initialize importer
        importer = GitHubSkillsImporter(github_token=github_token)

        # Import skill
        skill_data = importer.import_skill_from_repo(
            repository=repository, skill_path=skill_path, branch=branch
        )

        # Parse SKILL.md content
        content = skill_data["content"]
        match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if not match:
            return f"""# Error: Invalid SKILL.md Format

**Operation:** import_from_github
**Repository:** {repository}

**Problem:** SKILL.md is missing YAML frontmatter

Claude Skills must start with YAML frontmatter. The imported file doesn't match this format.

**Check the skill's SKILL.md file in the repository.**"""

        try:
            frontmatter = yaml.safe_load(match.group(1))
        except Exception as e:
            return f"""# Error: Invalid YAML Frontmatter

**Operation:** import_from_github
**Repository:** {repository}

**Problem:** Could not parse YAML frontmatter

**Error:** {str(e)}

**Fix the YAML syntax in the repository's SKILL.md file.**"""

        skill_name = frontmatter.get("name")
        description = frontmatter.get("description")

        if not skill_name or not description:
            return f"""# Error: Missing Required Fields

**Operation:** import_from_github
**Repository:** {repository}

**Problem:** SKILL.md frontmatter missing required fields

**Required fields:**
- name: {skill_name if skill_name else "[MISSING]"}
- description: {"[OK] Present" if description else "[MISSING]"}

**Add the missing fields to SKILL.md in the repository.**"""

        # Determine category
        skill_metadata = frontmatter.get("metadata", {})
        skill_category = category or skill_metadata.get("category", "general")

        # Create skill in Advanced Memory
        folder = f"skills/{skill_category}"
        from advanced_memory.mcp.tools.write_note import write_note

        result = await write_note.fn(
            title=skill_name,
            content=content,
            folder=folder,
            tags=["claude-skill", "imported", "github", skill_category],
            entity_type="skill",
            project=active_project.name,
        )

        return f"""# Skill Imported from GitHub [OK]

{result}

**Repository:** {repository}
**Skill:** {skill_name}
**Category:** {skill_category}
**Branch:** {branch}

[OK] Successfully imported skill from GitHub! This is compatible with SkillsMP.com repositories.
"""

    except Exception as e:
        logger.error(f"Error importing from GitHub: {e}", exc_info=True)
        return f"""# Error: GitHub Import Failed

**Operation:** import_from_github
**Repository:** {repository}

**Problem:** {str(e)}

**Common issues:**
- Repository not found or private (need GITHUB_TOKEN environment variable)
- Invalid repository format (use "owner/repo")
- Network connectivity issues
- Skill path doesn't exist in repository

**How to fix:**
1. Verify repository exists and is accessible
2. Check repository format: "owner/repo-name"
3. For private repos, set GITHUB_TOKEN environment variable
4. Verify skill_path exists in the repository

**Try again with a valid repository and path.**"""


async def _distill_from_wikipedia_operation(
    topic: str | None,
    depth: int,
    include_related: bool,
    quality: str | None,
    category: str | None,
    project: str | None,
) -> str:
    """Distill skill from Wikipedia article.

    Args:
        topic: Wikipedia article title
        depth: Depth of related articles (default: 0)
        include_related: Whether to include related articles (default: False)
        quality: Quality level - "basic", "comprehensive", or "expert" (default: "comprehensive")
        category: Category for organization (optional)
        project: Project name (optional)

    Returns:
        Formatted result string
    """
    try:
        if not topic:
            return """# Error: Missing Required Parameter

**Operation:** distill_from_wikipedia

**Missing:** topic parameter

The distill_from_wikipedia operation requires a Wikipedia article title.

**Example:**
```
adn_skills(
    operation="distill_from_wikipedia",
    topic="Quantum_mechanics",
    quality="comprehensive",
    category="science"
)
```

**Provide the topic parameter and try again.**"""

        active_project = get_active_project(project)
        quality_level = quality or "comprehensive"

        logger.info(f"Distilling skill from Wikipedia: {topic} (quality={quality_level})")

        # Initialize distiller
        distiller = SkillDistiller()

        # Distill skill
        skill_data = distiller.distill_from_wikipedia(
            topic=topic,
            depth=depth,
            include_related=include_related,
            quality=quality_level,
        )

        # Create skill in Advanced Memory
        skill_category = category or "general"
        folder = f"skills/{skill_category}"

        # Build SKILL.md content

        skill_name = skill_data["name"]
        description = skill_data["description"]
        content = skill_data["content"]

        frontmatter = {
            "name": skill_name,
            "description": description,
            "type": "skill",
            "metadata": {
                "category": skill_category,
                "source": skill_data.get("source", ""),
            },
        }

        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        skill_content = f"""---
{yaml_str}---

{content}
"""

        from advanced_memory.mcp.tools.write_note import write_note

        result = await write_note.fn(
            title=skill_name,
            content=skill_content,
            folder=folder,
            tags=["claude-skill", "wikipedia", "distilled", skill_category],
            entity_type="skill",
            project=active_project.name,
        )

        return f"""# Skill Distilled from Wikipedia [OK]

{result}

**Topic:** {topic}
**Quality:** {quality_level}
**Category:** {skill_category}
**Source:** {skill_data.get("source", "Wikipedia")}

[OK] Successfully created skill from Wikipedia article!
"""

    except Exception as e:
        logger.error(f"Error distilling from Wikipedia: {e}", exc_info=True)
        return f"""# Error: Wikipedia Distillation Failed

**Operation:** distill_from_wikipedia
**Topic:** {topic}

**Problem:** {str(e)}

**Common issues:**
- Article not found (check title spelling)
- Network connectivity issues
- Invalid topic format

**How to fix:**
1. Verify Wikipedia article exists: https://en.wikipedia.org/wiki/{topic.replace(" ", "_")}
2. Check topic spelling and format
3. Try with basic quality level first

**Try again with a valid Wikipedia article title.**"""


async def _distill_from_arxiv_operation(
    query: str | None,
    max_papers: int,
    synthesis_level: str | None,
    category: str | None,
    project: str | None,
) -> str:
    """Distill skill from arXiv research papers.

    Args:
        query: Search query or paper ID
        max_papers: Maximum papers to synthesize (default: 5)
        synthesis_level: Synthesis level - "summary", "synthesis", or "comprehensive" (default: "comprehensive")
        category: Category for organization (optional)
        project: Project name (optional)

    Returns:
        Formatted result string
    """
    try:
        if not query:
            return """# Error: Missing Required Parameter

**Operation:** distill_from_arxiv

**Missing:** query parameter

The distill_from_arxiv operation requires a search query or paper ID.

**Example:**
```
adn_skills(
    operation="distill_from_arxiv",
    query="transformer architecture attention mechanism",
    max_papers=5,
    synthesis_level="comprehensive"
)
```

**Provide the query parameter and try again.**"""

        active_project = get_active_project(project)
        synthesis = synthesis_level or "comprehensive"

        logger.info(f"Distilling skill from arXiv: {query} (synthesis={synthesis})")

        # Initialize distiller
        distiller = SkillDistiller()

        # Distill skill
        skill_data = distiller.distill_from_arxiv(
            query=query, max_papers=max_papers, synthesis_level=synthesis
        )

        # Create skill in Advanced Memory
        skill_category = category or "research"
        folder = f"skills/{skill_category}"

        # Build SKILL.md content
        skill_name = skill_data["name"]
        description = skill_data["description"]
        content = skill_data["content"]

        frontmatter = {
            "name": skill_name,
            "description": description,
            "type": "skill",
            "metadata": {
                "category": skill_category,
                "source": skill_data.get("source", ""),
            },
        }

        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        skill_content = f"""---
{yaml_str}---

{content}
"""

        from advanced_memory.mcp.tools.write_note import write_note

        result = await write_note.fn(
            title=skill_name,
            content=skill_content,
            folder=folder,
            tags=["claude-skill", "arxiv", "distilled", skill_category],
            entity_type="skill",
            project=active_project.name,
        )

        return f"""# Skill Distilled from arXiv [OK]

{result}

**Query:** {query}
**Papers:** {len(skill_data.get("papers", []))}
**Synthesis Level:** {synthesis}
**Category:** {skill_category}

[OK] Successfully created skill from arXiv research papers!
"""

    except Exception as e:
        logger.error(f"Error distilling from arXiv: {e}", exc_info=True)
        return f"""# Error: ArXiv Distillation Failed

**Operation:** distill_from_arxiv
**Query:** {query}

**Problem:** {str(e)}

**Common issues:**
- No papers found for query
- Network connectivity issues
- Invalid query format

**How to fix:**
1. Try a different search query
2. Use paper ID format: "arxiv:1706.03762"
3. Check network connectivity
4. Verify arxiv package is installed

**Try again with a valid search query or paper ID.**"""


async def _distill_from_textbook_operation(
    pdf_path: str | None,
    chapters: list[int] | None,
    level: str | None,
    category: str | None,
    project: str | None,
) -> str:
    """Distill skill from textbook PDF.

    Args:
        pdf_path: Path to textbook PDF
        chapters: Specific chapters to process (optional)
        level: Skill level - "beginner", "intermediate", or "advanced" (default: "intermediate")
        category: Category for organization (optional)
        project: Project name (optional)

    Returns:
        Formatted result string
    """
    try:
        if not pdf_path:
            return """# Error: Missing Required Parameter

**Operation:** distill_from_textbook

**Missing:** pdf_path parameter

The distill_from_textbook operation requires a path to a textbook PDF file.

**Example:**
```
adn_skills(
    operation="distill_from_textbook",
    pdf_path="D:/books/intro-to-linear-algebra.pdf",
    chapters=[1, 2, 3],
    level="beginner"
)
```

**Provide the pdf_path parameter and try again.**"""

        active_project = get_active_project(project)
        skill_level = level or "intermediate"

        logger.info(f"Distilling skill from textbook: {pdf_path} (level={skill_level})")

        # Initialize distiller
        distiller = SkillDistiller()

        # Distill skill
        skill_data = distiller.distill_from_textbook(
            pdf_path=pdf_path, chapters=chapters, level=skill_level
        )

        # Create skill in Advanced Memory
        skill_category = category or "education"
        folder = f"skills/{skill_category}"

        # Build SKILL.md content
        skill_name = skill_data["name"]
        description = skill_data["description"]
        content = skill_data["content"]

        frontmatter = {
            "name": skill_name,
            "description": description,
            "type": "skill",
            "metadata": {
                "category": skill_category,
                "level": skill_level,
                "source": skill_data.get("source", ""),
            },
        }

        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        skill_content = f"""---
{yaml_str}---

{content}
"""

        from advanced_memory.mcp.tools.write_note import write_note

        result = await write_note.fn(
            title=skill_name,
            content=skill_content,
            folder=folder,
            tags=["claude-skill", "textbook", "distilled", skill_category, skill_level],
            entity_type="skill",
            project=active_project.name,
        )

        return f"""# Skill Distilled from Textbook [OK]

{result}

**Textbook:** {pdf_path}
**Level:** {skill_level}
**Chapters:** {chapters or "All"}
**Category:** {skill_category}

[OK] Successfully created skill from textbook!
"""

    except Exception as e:
        logger.error(f"Error distilling from textbook: {e}", exc_info=True)
        return f"""# Error: Textbook Distillation Failed

**Operation:** distill_from_textbook
**PDF Path:** {pdf_path}

**Problem:** {str(e)}

**Common issues:**
- PDF file not found
- PDF parsing libraries not installed (pypdf, pdfplumber)
- Corrupted or encrypted PDF
- Invalid file path

**How to fix:**
1. Verify PDF file exists at the specified path
2. Install PDF libraries: pip install pypdf pdfplumber
3. Check file is not password-protected
4. Use absolute path if relative path fails

**Try again with a valid PDF file path.**"""


async def _distill_from_text_operation(
    text_path: str | None,
    focus: str | None,
    context_level: str | None,
    category: str | None,
    project: str | None,
) -> str:
    """Distill skill from famous text or document.

    Args:
        text_path: Path to text file or PDF
        focus: What to distill - "principles", "examples", "methodology", or "all" (default: "principles")
        context_level: Historical context level - "basic", "comprehensive", or "detailed" (default: "basic")
        category: Category for organization (optional)
        project: Project name (optional)

    Returns:
        Formatted result string
    """
    try:
        if not text_path:
            return """# Error: Missing Required Parameter

**Operation:** distill_from_text

**Missing:** text_path parameter

The distill_from_text operation requires a path to a text file or PDF.

**Example:**
```
adn_skills(
    operation="distill_from_text",
    text_path="D:/texts/plato-republic.pdf",
    focus="principles",
    context_level="comprehensive"
)
```

**Provide the text_path parameter and try again.**"""

        active_project = get_active_project(project)
        focus_type = focus or "principles"
        context = context_level or "basic"

        logger.info(f"Distilling skill from text: {text_path} (focus={focus_type})")

        # Initialize distiller
        distiller = SkillDistiller()

        # Distill skill
        skill_data = distiller.distill_from_text(
            text_path=text_path, focus=focus_type, context_level=context
        )

        # Create skill in Advanced Memory
        skill_category = category or "philosophy"
        folder = f"skills/{skill_category}"

        # Build SKILL.md content
        skill_name = skill_data["name"]
        description = skill_data["description"]
        content = skill_data["content"]

        frontmatter = {
            "name": skill_name,
            "description": description,
            "type": "skill",
            "metadata": {
                "category": skill_category,
                "focus": focus_type,
                "source": skill_data.get("source", ""),
            },
        }

        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        skill_content = f"""---
{yaml_str}---

{content}
"""

        from advanced_memory.mcp.tools.write_note import write_note

        result = await write_note.fn(
            title=skill_name,
            content=skill_content,
            folder=folder,
            tags=["claude-skill", "text", "distilled", skill_category],
            entity_type="skill",
            project=active_project.name,
        )

        return f"""# Skill Distilled from Text [OK]

{result}

**Text:** {text_path}
**Focus:** {focus_type}
**Context Level:** {context}
**Category:** {skill_category}

[OK] Successfully created skill from text!
"""

    except Exception as e:
        logger.error(f"Error distilling from text: {e}", exc_info=True)
        return f"""# Error: Text Distillation Failed

**Operation:** distill_from_text
**Text Path:** {text_path}

**Problem:** {str(e)}

**Common issues:**
- File not found
- Unsupported file format
- Encoding issues with text files
- PDF parsing errors

**How to fix:**
1. Verify file exists at the specified path
2. For PDFs, install PDF libraries: pip install pdfplumber pypdf
3. Check file encoding (UTF-8 recommended)
4. Use absolute path if relative path fails

**Try again with a valid text file or PDF path.**"""


async def _distill_from_expert_operation(
    expert_name: str | None,
    source_types: list[str] | None,
    focus_area: str | None,
    category: str | None,
    project: str | None,
) -> str:
    """Distill skill from expert/SOTA thinker's work.

    Args:
        expert_name: Name of expert/thinker
        source_types: List of sources to search - "arxiv", "papers", "lectures" (optional)
        focus_area: Specific domain/focus area (optional)
        category: Category for organization (optional)
        project: Project name (optional)

    Returns:
        Formatted result string
    """
    try:
        if not expert_name:
            return """# Error: Missing Required Parameter

**Operation:** distill_from_expert

**Missing:** expert_name parameter

The distill_from_expert operation requires the name of an expert or SOTA thinker.

**Example:**
```
adn_skills(
    operation="distill_from_expert",
    expert_name="Yoshua Bengio",
    source_types=["arxiv", "papers"],
    focus_area="deep learning"
)
```

**Provide the expert_name parameter and try again.**"""

        active_project = get_active_project(project)

        logger.info(f"Distilling skill from expert: {expert_name} (focus_area={focus_area})")

        # Initialize distiller
        distiller = SkillDistiller()

        # Distill skill
        skill_data = distiller.distill_from_expert(
            expert_name=expert_name, source_types=source_types, focus_area=focus_area
        )

        # Create skill in Advanced Memory
        skill_category = category or "expert"
        folder = f"skills/{skill_category}"

        # Build SKILL.md content
        skill_name = skill_data["name"]
        description = skill_data["description"]
        content = skill_data["content"]

        frontmatter = {
            "name": skill_name,
            "description": description,
            "type": "skill",
            "metadata": {
                "category": skill_category,
                "expert": expert_name,
                "focus_area": focus_area,
                "source": skill_data.get("source", ""),
            },
        }

        yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        skill_content = f"""---
{yaml_str}---

{content}
"""

        from advanced_memory.mcp.tools.write_note import write_note

        result = await write_note.fn(
            title=skill_name,
            content=skill_content,
            folder=folder,
            tags=["claude-skill", "expert", "distilled", skill_category],
            entity_type="skill",
            project=active_project.name,
        )

        return f"""# Skill Distilled from Expert [OK]

{result}

**Expert:** {expert_name}
**Focus Area:** {focus_area or "General"}
**Sources:** {", ".join(source_types) if source_types else "arxiv"}
**Category:** {skill_category}

[OK] Successfully created skill from expert's work!
"""

    except Exception as e:
        logger.error(f"Error distilling from expert: {e}", exc_info=True)
        return f"""# Error: Expert Distillation Failed

**Operation:** distill_from_expert
**Expert:** {expert_name}

**Problem:** {str(e)}

**Common issues:**
- No content found for expert
- Network connectivity issues
- Invalid expert name format
- Source types not available

**How to fix:**
1. Verify expert name spelling
2. Try different source types: ["arxiv", "papers"]
3. Check network connectivity
4. Verify arxiv package is installed for arXiv searches

**Try again with a valid expert name.**"""
