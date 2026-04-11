#!/usr/bin/env python3
"""
Extract zettelkasten templates from Python files to markdown files.

This script converts templates from:
  src/advanced_memory/cli/zettelkasten_content/*.py (Python dicts)
To:
  zettelkasten/templates/*/*.md (Individual markdown files)
"""

import re
import sys
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to filesystem-safe slug"""
    # Remove special characters, replace spaces with hyphens
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def extract_templates():
    """Extract all templates from Python files to markdown"""

    # Source directory
    Path("src/advanced_memory/cli/zettelkasten_content")

    # Target directory
    target_dir = Path("zettelkasten/templates")
    target_dir.mkdir(parents=True, exist_ok=True)

    # Import all template modules
    sys.path.insert(0, str(Path.cwd() / "src"))

    from advanced_memory.cli.zettelkasten_content import (
        CREATIVE_TEMPLATES,
        DATA_SCIENTIST_TEMPLATES,
        DEVELOPER_TEMPLATES,
        DEVOPS_TEMPLATES,
        ENTREPRENEUR_TEMPLATES,
        KNOWLEDGE_WORKER_TEMPLATES,
        PRODUCT_MANAGER_TEMPLATES,
        RESEARCHER_TEMPLATES,
        UIUX_DESIGNER_TEMPLATES,
        WRITER_TEMPLATES,
    )

    # Map categories to their templates
    categories = {
        "developer": DEVELOPER_TEMPLATES,
        "devops": DEVOPS_TEMPLATES,
        "data-scientist": DATA_SCIENTIST_TEMPLATES,
        "uiux-designer": UIUX_DESIGNER_TEMPLATES,
        "product-manager": PRODUCT_MANAGER_TEMPLATES,
        "entrepreneur": ENTREPRENEUR_TEMPLATES,
        "creative": CREATIVE_TEMPLATES,
        "knowledge-worker": KNOWLEDGE_WORKER_TEMPLATES,
        "researcher": RESEARCHER_TEMPLATES,
        "writer": WRITER_TEMPLATES,
    }

    total_files = 0
    total_categories = 0
    total_topics = 0

    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print("║  📦 EXTRACTING ZETTELKASTEN TEMPLATES TO MARKDOWN! 📦      ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")

    # Process each category
    for category_name, category_templates in categories.items():
        print(f"📂 Processing category: {category_name}")

        # Create category directory
        category_dir = target_dir / category_name
        category_dir.mkdir(exist_ok=True)

        topic_count = 0
        file_count = 0

        # Process each topic group
        for topic_name, topic_templates in category_templates.items():
            # Create topic directory
            topic_slug = slugify(topic_name)
            topic_dir = category_dir / topic_slug
            topic_dir.mkdir(exist_ok=True)

            # Extract each template (templates are list of dicts)
            template_list = topic_templates if isinstance(topic_templates, list) else [topic_templates]

            for template in template_list:
                if isinstance(template, dict):
                    note_title = template.get("title", "Untitled")
                    note_content = template.get("content", "")
                else:
                    # Old format (dict[str, str])
                    note_title = template
                    note_content = topic_templates[template] if isinstance(topic_templates, dict) else template

                # Create filename
                note_slug = slugify(note_title)
                note_path = topic_dir / f"{note_slug}.md"

                # Write markdown file
                note_path.write_text(note_content, encoding="utf-8")
                file_count += 1

            topic_count += 1
            print(f"  ✓ {topic_name}: {len(template_list)} templates")

        total_categories += 1
        total_topics += topic_count
        total_files += file_count
        print(f"  📊 Total for {category_name}: {file_count} files in {topic_count} topics\n")

    # Create category READMEs
    for category_name in categories.keys():
        category_dir = target_dir / category_name
        readme_path = category_dir / "README.md"

        # Count templates in this category
        template_count = sum(len(topic_templates) for topic_templates in categories[category_name].values())

        readme_content = f"""# {category_name.replace("-", " ").title()} Templates

**Template count**: {template_count} high-quality zettelkasten notes

## Topics

"""

        # List all topic directories
        for topic_dir in sorted(category_dir.iterdir()):
            if topic_dir.is_dir():
                topic_name = topic_dir.name.replace("-", " ").title()
                md_count = len(list(topic_dir.glob("*.md")))
                readme_content += f"- **{topic_name}** ({md_count} templates)\n"

        readme_content += f"""
## How to Use

### Via CLI
```bash
advanced-memory onboard
# Select "{category_name.replace("-", " ").title()}" category
```

### Via MCP
```python
adn_zettelmaker("generate", category="{category_name}", topic="<topic-name>")
```

### Customize
```bash
# Copy template to user-templates/
cp zettelkasten/templates/{category_name}/<topic>/<note>.md \\
   zettelkasten/user-templates/my-custom-template.md

# Edit and use
```

---

**Category**: {category_name.replace("-", " ").title()}
**Templates**: {template_count}
**Updated**: October 17, 2025
"""

        readme_path.write_text(readme_content, encoding="utf-8")

    # Create main templates README
    main_readme = target_dir / "README.md"
    main_readme_content = f"""# Zettelkasten Templates

**Pre-built knowledge templates** for Advanced Memory onboarding

---

## Overview

This directory contains **{total_files} high-quality zettelkasten templates** across **{total_categories} professional categories**. Each template is a complete, interconnected note demonstrating best practices for knowledge management.

---

## Categories

"""

    for category_name, category_templates in categories.items():
        template_count = sum(len(t) for t in category_templates.values())
        topic_count = len(category_templates)
        category_title = category_name.replace("-", " ").title()

        main_readme_content += f"""### {category_title}
**{template_count} templates** across {topic_count} topic groups

[Browse {category_title} templates →](./{category_name}/)

"""

    main_readme_content += f"""---

## How to Use

### Generate Templates

**Via CLI**:
```bash
advanced-memory onboard
```

**Via MCP**:
```python
adn_zettelmaker("generate", category="developer", topic="Python Basics")
```

---

### Customize Templates

1. **Copy template** to user-templates/
2. **Modify** for your needs
3. **Generate** from custom template

```bash
cp zettelkasten/templates/developer/python-basics/functions.md \\
   zettelkasten/user-templates/my-python-notes.md
```

---

## Template Structure

Each template includes:
- **Title** (H1) - Main concept
- **Concept** (H2) - Core explanation
- **Observations** (bulleted with [categories])
- **Relations** (wikilinks to related concepts)
- **Examples** (code or practical examples)
- **Diagrams** (Mermaid visualizations)

**Example**:
```markdown
# Python Functions

## Concept
A function is a reusable block of code...

## Observations
- [definition] Functions encapsulate behavior
- [example] `def greet(name): return f"Hello {{name}}"`
- [best-practice] Use descriptive names

## Relations
- implements [[Programming Paradigms]]
- prerequisite-for [[Advanced Python]]
```

---

## Statistics

- **Total templates**: {total_files}
- **Categories**: {total_categories}
- **Topic groups**: {total_topics}
- **Average per category**: {total_files // total_categories} templates

---

## See Also

- **Main README**: [../README.md](../README.md)
- **Inbox**: [../inbox/README.md](../inbox/README.md)
- **User Templates**: [../user-templates/README.md](../user-templates/README.md)
- **Source Code**: Original templates in `src/advanced_memory/cli/zettelkasten_content/`

---

**Extracted**: October 17, 2025
**From**: Python dictionaries in source code
**Format**: Individual markdown files
**Editable**: Yes! (but will be overwritten on update)
"""

    main_readme.write_text(main_readme_content, encoding="utf-8")

    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║  ✅ EXTRACTION COMPLETE! ✅                                ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    print("📊 Statistics:")
    print(f"  Categories: {total_categories}")
    print(f"  Topics: {total_topics}")
    print(f"  Templates: {total_files}")
    print("  Location: zettelkasten/templates/")
    print("\n✅ All templates extracted successfully!\n")


if __name__ == "__main__":
    try:
        extract_templates()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
