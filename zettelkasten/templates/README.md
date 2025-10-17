# Zettelkasten Templates

**Pre-built knowledge templates** for Advanced Memory onboarding

---

## Overview

This directory contains **41 high-quality zettelkasten templates** across **10 professional categories**. Each template is a complete, interconnected note demonstrating best practices for knowledge management.

---

## Categories

### Developer
**15 templates** across 10 topic groups

[Browse Developer templates →](./developer/)

### Devops
**6 templates** across 4 topic groups

[Browse Devops templates →](./devops/)

### Data Scientist
**2 templates** across 1 topic groups

[Browse Data Scientist templates →](./data-scientist/)

### Uiux Designer
**3 templates** across 2 topic groups

[Browse Uiux Designer templates →](./uiux-designer/)

### Product Manager
**1 templates** across 1 topic groups

[Browse Product Manager templates →](./product-manager/)

### Entrepreneur
**1 templates** across 1 topic groups

[Browse Entrepreneur templates →](./entrepreneur/)

### Creative
**1 templates** across 1 topic groups

[Browse Creative templates →](./creative/)

### Knowledge Worker
**2 templates** across 1 topic groups

[Browse Knowledge Worker templates →](./knowledge-worker/)

### Researcher
**7 templates** across 5 topic groups

[Browse Researcher templates →](./researcher/)

### Writer
**3 templates** across 2 topic groups

[Browse Writer templates →](./writer/)

---

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
cp zettelkasten/templates/developer/python-basics/functions.md \
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
- [example] `def greet(name): return f"Hello {name}"`
- [best-practice] Use descriptive names

## Relations
- implements [[Programming Paradigms]]
- prerequisite-for [[Advanced Python]]
```

---

## Statistics

- **Total templates**: 41
- **Categories**: 10
- **Topic groups**: 28
- **Average per category**: 4 templates

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
