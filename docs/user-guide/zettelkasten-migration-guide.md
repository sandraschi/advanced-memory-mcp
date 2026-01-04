# Zettelkasten Migration Guide - Python to Markdown Templates

**Migration Version**: v1.0.0b2 → v1.0.0b3+
**Date**: October 2025
**Breaking Changes**: No (backward compatible)

---

## Overview

Advanced Memory has migrated zettelkasten templates from Python dictionaries embedded in source code to **markdown files** in the `zettelkasten/templates/` directory.

**Why this matters**:
- ✅ Templates are now human-readable markdown
- ✅ Users can browse/edit templates directly
- ✅ No Python knowledge needed to customize
- ✅ Templates are part of your repository, not hidden in code
- ✅ Version control friendly

**Impact on users**: **None** - migration is automatic and transparent.

---

## What Changed

### Before (v1.0.0b2 and earlier)

**Templates stored in**:
```
src/advanced_memory/cli/zettelkasten_content/
├── developer.py          # Python dictionary
├── researcher.py         # Python dictionary
├── writer.py             # Python dictionary
└── knowledge_worker.py   # Python dictionary
```

**Structure**:
```python
DEVELOPER_TEMPLATES = {
    "python-core": [
        {
            "title": "Python Fundamentals",
            "folder": "developer/python",
            "content": "# Python Fundamentals\n\n...",
        }
    ]
}
```

**Access**: Only via code (hidden from users)

---

### After (v1.0.0b3+)

**Templates stored in**:
```
zettelkasten/templates/
├── developer/
│   ├── python/
│   │   ├── python-fundamentals.md
│   │   ├── python-advanced.md
│   │   └── ...
│   ├── git/
│   └── testing/
├── researcher/
├── writer/
└── knowledge-worker/
```

**Structure**:
```markdown
# Python Fundamentals

> **Category:** developer/python
> **Topic:** python-core

## Overview

Python is a high-level programming language...
```

**Access**:
- Browse directly in file system
- Edit with any text editor
- Version control with Git
- Share as files

---

## Migration Process

### For End Users

**No action required.** The migration happens automatically:

1. On first run of v1.0.0b3+, Advanced Memory:
   - Detects new `zettelkasten/templates/` directory
   - Loads templates from markdown files
   - Falls back to Python templates if markdown not found (backward compatible)

2. Your existing notes are **not affected**

3. New notes use markdown-based templates

---

### For Developers/Contributors

If you've added custom templates to Python files:

**Step 1**: Extract your templates to markdown

```bash
# Run extraction script (included in repo)
python scripts/extract_templates.py
```

**Step 2**: Review extracted templates

```bash
# Templates extracted to:
zettelkasten/templates/<category>/<topic>/<title>.md
```

**Step 3**: Edit/customize as needed

```bash
# Edit any template
nano zettelkasten/templates/developer/python/python-fundamentals.md
```

**Step 4**: Commit to repo

```bash
git add zettelkasten/templates/
git commit -m "Add custom zettelkasten templates"
```

---

## New Directory Structure

### Complete Layout

```
zettelkasten/
├── README.md                    # Main guide
├── templates/                   # Pre-built templates (read-only recommended)
│   ├── developer/
│   │   ├── python/
│   │   │   ├── python-fundamentals.md
│   │   │   ├── python-advanced.md
│   │   │   └── ...
│   │   ├── git/
│   │   ├── testing/
│   │   └── architecture/
│   ├── researcher/
│   ├── writer/
│   ├── knowledge-worker/
│   ├── devops/
│   ├── data-scientist/
│   ├── uiux-designer/
│   ├── product-manager/
│   ├── entrepreneur/
│   └── creative/
├── user-templates/              # Your custom templates (create your own!)
│   └── .gitkeep
├── inbox/                       # Drop files here for processing
│   ├── README.md
│   └── .gitkeep
└── converted/                   # Converted documents stored here
    └── .gitkeep
```

---

## Template Format

### Markdown Template Structure

**File**: `zettelkasten/templates/developer/python/python-fundamentals.md`

```markdown
# Python Fundamentals

> **Category:** developer/python
> **Topic:** python-core
> **Level:** Beginner

## Overview

Python is a high-level programming language known for its readability and versatility.

## Key Concepts

### 1. Variables and Data Types

Python supports several built-in data types:
- `int` - integers
- `float` - floating-point numbers
- `str` - strings
- `bool` - booleans

### 2. Control Flow

\`\`\`python
if condition:
    do_something()
elif other_condition:
    do_other_thing()
else:
    do_default()
\`\`\`

## Observations

- [language-feature] Dynamic typing allows flexible code
- [best-practice] Follow PEP 8 style guide
- [performance] Use list comprehensions for efficiency

## Relations

- prerequisite_for [[Python Advanced Topics]]
- relates_to [[Programming Fundamentals]]
- used_in [[Data Science with Python]]

## References

- Official Documentation: https://docs.python.org/3/
- Python Tutorial: https://docs.python.org/3/tutorial/
- PEP 8: https://peps.python.org/pep-0008/
```

---

### Required Frontmatter (Optional)

You can add YAML frontmatter for metadata:

```markdown
---
title: "Python Fundamentals"
category: "developer"
topic: "python-core"
level: "beginner"
tags: ["programming", "python", "fundamentals"]
created: "2025-10-17"
---

# Python Fundamentals

Content here...
```

---

## Customization

### Option 1: Edit Existing Templates

**Not recommended** (updates will overwrite):

```bash
# Edit pre-built template
nano zettelkasten/templates/developer/python/python-fundamentals.md
```

**Risk**: Next update might overwrite your changes.

---

### Option 2: Create User Templates (Recommended)

**Create your own**:

```bash
# Create custom template
mkdir -p zettelkasten/user-templates/my-domain
nano zettelkasten/user-templates/my-domain/my-template.md
```

**Benefits**:
- Not overwritten by updates
- Fully customizable
- Version controlled separately

**Usage**:
```python
# Reference in your own scripts
from advanced_memory.services.template_loader import TemplateLoader

loader = TemplateLoader()
my_template = loader.load_template("user-templates/my-domain/my-template.md")
```

---

### Option 3: Fork and Modify

**For advanced users**:

1. Fork the Advanced Memory repository
2. Modify templates in `zettelkasten/templates/`
3. Keep your fork up to date with upstream
4. Merge updates carefully

---

## Backward Compatibility

### Python Templates Still Work

The old Python-based templates are **still included** for backward compatibility:

```python
# This still works (v1.0.0b3+)
from advanced_memory.cli.zettelkasten_content import DEVELOPER_TEMPLATES

# But now also works:
from advanced_memory.services.template_loader import get_content_templates

templates = get_content_templates()  # Loads from markdown first, falls back to Python
```

---

### Fallback Behavior

**Loading order**:
1. Try loading from `zettelkasten/templates/` (markdown)
2. If not found, fall back to Python dictionaries
3. If neither, return empty

**This means**:
- Old code continues working
- New code uses markdown
- Gradual migration supported

---

## API Changes

### Old API (Still Works)

```python
from advanced_memory.cli.zettelkasten_content import DEVELOPER_TEMPLATES

templates = DEVELOPER_TEMPLATES["python-core"]
```

---

### New API (Recommended)

```python
from advanced_memory.services.template_loader import get_template_loader

loader = get_template_loader()
templates = loader.load_topic("developer", "python-core")
```

Or:

```python
from advanced_memory.services.template_loader import get_content_templates

templates = get_content_templates()  # All templates, all categories
developer_templates = templates["developer"]["python-core"]
```

---

## For Package Maintainers

### Including Templates in Distribution

**pyproject.toml** already updated:

```toml
[tool.hatch.build.targets.wheel.force-include]
"zettelkasten" = "advanced_memory/zettelkasten"
```

This ensures `zettelkasten/` directory is included in PyPI distribution.

---

### Installing from PyPI

```bash
pip install advanced-memory>=1.0.0b3
```

Templates are installed to:
```
site-packages/advanced_memory/zettelkasten/templates/
```

---

## Troubleshooting

### Problem: Templates not found after upgrade

**Solution**:
```bash
# Verify templates directory exists
ls zettelkasten/templates/

# If missing, clone from repo
git clone https://github.com/sandraschi/advanced-memory-mcp
cp -r advanced-memory-mcp/zettelkasten/templates/ zettelkasten/
```

---

### Problem: Old Python templates still loading

**This is normal**. Python templates are fallback for backward compatibility.

**To force markdown**:
```python
loader = TemplateLoader()
loader.load_topic("developer", "python-core")  # Only loads from markdown
```

---

### Problem: Custom templates not detected

**Solution**:
```bash
# Check file structure
zettelkasten/user-templates/
└── my-category/
    └── my-template.md

# Load explicitly
loader = TemplateLoader()
template = loader.load_template("user-templates/my-category/my-template.md")
```

---

## Benefits of Migration

### For Users

**1. Visibility**
- Templates are no longer hidden in Python code
- Browse with any text editor or file manager
- Understand template structure by reading markdown

**2. Customization**
- Edit templates without Python knowledge
- Create custom templates easily
- Share templates as files

**3. Version Control**
- Templates tracked in Git
- See history of template changes
- Fork and customize

---

### For Developers

**4. Maintainability**
- Easier to add new templates (markdown vs Python)
- No code changes needed for content updates
- Separate content from logic

**5. Community Contributions**
- Contributors can add templates without coding
- Pull requests are simpler (markdown diffs)
- Community-driven template library

**6. Extensibility**
- Template system is now pluggable
- Users can add custom loaders
- Future: Template marketplace

---

## Future Enhancements

### Planned Features

**1. Template Marketplace** (Phase 5)
- Community-contributed templates
- Rating and review system
- One-click template import

**2. Template Generator** (Phase 2 - Completed)
- AI-generated templates for any topic
- Quality levels (quick, standard, comprehensive)
- Caching for performance

**3. Template Versioning**
- Track template versions
- Update notifications
- Diff between versions

**4. Template Inheritance**
- Base templates with variants
- Override sections selectively
- Template composition

---

## Migration Checklist

**For End Users**:
- [ ] Upgrade to v1.0.0b3+ (`pip install --upgrade advanced-memory`)
- [ ] Verify templates load: `advanced-memory onboard`
- [ ] (Optional) Browse templates: `ls zettelkasten/templates/`
- [ ] Continue using Advanced Memory (no changes needed!)

**For Developers/Contributors**:
- [ ] Run extraction script: `python scripts/extract_templates.py`
- [ ] Review extracted templates: `zettelkasten/templates/`
- [ ] Update custom code to use new API
- [ ] Test template loading: `python -m pytest tests/`
- [ ] Commit templates to repo

**For Package Maintainers**:
- [ ] Verify `pyproject.toml` includes `zettelkasten/`
- [ ] Test package build: `python -m build`
- [ ] Test installation: `pip install dist/*.whl`
- [ ] Verify templates installed: `python -c "from advanced_memory.services.template_loader import get_template_loader; print(get_template_loader().templates_dir)"`

---

## Getting Help

**Issues after migration?**

1. Check [GitHub Issues](https://github.com/sandraschi/advanced-memory-mcp/issues)
2. Review [Troubleshooting Section](#troubleshooting)
3. Ask in Discussions
4. File a bug report

**Questions?**

- Docs: [README.md](../../README.md)
- User Guide: [docs/user-guide/](../)
- Templates: [zettelkasten/README.md](../../zettelkasten/README.md)

---

## Summary

**Migration is**:
- ✅ Automatic
- ✅ Backward compatible
- ✅ Transparent to users
- ✅ Beneficial for developers
- ✅ Non-breaking

**You should**:
- ✅ Upgrade to v1.0.0b3+
- ✅ Browse the new `zettelkasten/` directory
- ✅ Consider customizing templates
- ✅ Contribute templates back to community

**You don't need to**:
- ❌ Manually migrate anything
- ❌ Change your existing notes
- ❌ Learn new APIs (old ones still work)

**Welcome to the new template system!** 🎉

---

*Last updated: October 17, 2025*
