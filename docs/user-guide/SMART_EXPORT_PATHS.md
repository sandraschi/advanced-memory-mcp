# Smart Export Paths - User-Friendly Defaults

**TL;DR**: No need to specify paths! Exports go to your Desktop by default.

---

## Default Export Locations

### Windows
```
C:\Users\YourName\Desktop\advanced-memory-exports\
├── pdf\
├── pandoc\
├── docsify\
├── html\
├── claude_skills\
└── archive\
```

### Mac
```
/Users/yourname/Desktop/advanced-memory-exports/
├── pdf/
├── pandoc/
├── docsify/
├── html/
├── claude_skills/
└── archive/
```

### Linux
```
/home/yourname/Desktop/advanced-memory-exports/
├── pdf/
├── pandoc/
├── docsify/
├── html/
├── claude_skills/
└── archive/
```

---

## How It Works

### Without Specifying Path

```python
# Just specify operation - path is automatic!
adn_export("pdf")
# → Desktop/advanced-memory-exports/pdf/

adn_export("docsify")
# → Desktop/advanced-memory-exports/docsify/

adn_export("claude_skills")
# → Desktop/advanced-memory-exports/claude_skills/
```

**Result**: Easy to find! Right on your Desktop!

### With Custom Path

```python
# Specify your own path
adn_export("pdf", export_path="D:/MyExports/pdfs/")
# → D:/MyExports/pdfs/

adn_export("docsify", export_path="/home/user/website/")
# → /home/user/website/
```

**Result**: Full control when you need it!

---

## Path Resolution Strategy

### Priority Order

1. **User-specified path** (if provided)
   ```python
   adn_export("pdf", export_path="C:/custom/")
   # Uses: C:/custom/
   ```

2. **Desktop/advanced-memory-exports/** (preferred)
   ```python
   adn_export("pdf")
   # Tries: Desktop/advanced-memory-exports/pdf/
   ```

3. **Documents/advanced-memory-exports/** (fallback #1)
   ```
   # If Desktop doesn't exist
   # Uses: Documents/advanced-memory-exports/pdf/
   ```

4. **Home/advanced-memory-exports/** (fallback #2)
   ```
   # If neither Desktop nor Documents exist
   # Uses: ~/advanced-memory-exports/pdf/
   ```

---

## Special Cases

### OneDrive Desktop (Windows)

**Detects**:
- Regular Desktop: `C:\Users\YourName\Desktop\`
- OneDrive Desktop: `C:\Users\YourName\OneDrive\Desktop\`

**Uses whichever exists first**

### Linux Desktop Environments

**Tries**:
1. `~/Desktop/` (standard)
2. XDG_USER_DIR for DESKTOP (if configured)
3. `~/` (fallback)

### Server/Headless Systems

**If no Desktop directory**:
- Falls back to `~/Documents/` or `~/`
- Creates `advanced-memory-exports/` there

---

## Benefits

### ✅ User-Friendly

**Before**:
```python
# User needs to know filesystem paths
adn_export("pdf", export_path="C:/Users/Sandra/Documents/exports/pdfs/output/")
```

**After**:
```python
# Just export!
adn_export("pdf")
```

**Files appear** on Desktop in clearly labeled folder!

### ✅ Organized

Each export type gets its own subfolder:
- `pdf/` - PDF exports
- `docsify/` - Website exports
- `claude_skills/` - Skills exports

**No mixing**, easy to find!

### ✅ Discoverable

**User asks**: "Where did my export go?"  
**Answer**: "Check your Desktop → `advanced-memory-exports` folder!"

Easy to remember, easy to find!

---

## Examples

### Quick Exports

```python
# PDF all notes
adn_export("pdf")
# → Desktop/advanced-memory-exports/pdf/note1.pdf, note2.pdf, ...

# Create website
adn_export("docsify")
# → Desktop/advanced-memory-exports/docsify/index.html

# Export skills
adn_export("claude_skills")
# → Desktop/advanced-memory-exports/claude_skills/category/skill/SKILL.md
```

### Custom Organization

```python
# Organize by date
from datetime import datetime
date_str = datetime.now().strftime("%Y-%m-%d")

adn_export("pdf", export_path=f"exports/{date_str}/")
# → exports/2024-10-20/note1.pdf, ...

# Organize by project
adn_export("pdf", export_path="projects/alpha/exports/")
# → projects/alpha/exports/note1.pdf, ...
```

### Portable Exports

```python
# USB drive
adn_export("html", export_path="E:/portable-site/")

# Network share
adn_export("pdf", export_path="//server/shared/exports/")

# Cloud sync folder
adn_export("docsify", export_path="~/Dropbox/knowledge-base/")
```

---

## Confirmation Messages

**After export, you'll see**:

```
✅ Export Complete!

**Export directory**: C:\Users\Sandra\Desktop\advanced-memory-exports\pdf\
**Files exported**: 15
**Errors**: 0

Successfully Exported:
- ✅ project-plan.pdf
- ✅ meeting-notes.pdf
- ✅ research-summary.pdf
... and 12 more files

Next steps:
1. Open C:\Users\Sandra\Desktop\advanced-memory-exports\pdf\ to view your PDFs
2. PDFs are ready for sharing, printing, or archiving
```

**Clear location** - you know exactly where to look!

---

## FAQ

### Q: Can I change the default export location?

**A:** Not globally yet, but you can always specify `export_path`:

```python
# Your preferred location
adn_export("pdf", export_path="D:/MyExports/")
```

**Future**: Config file setting for default export root

### Q: What if I don't have a Desktop folder?

**A:** System automatically falls back to:
1. Documents folder
2. Home directory

**You'll see** the actual path in the confirmation message!

### Q: Can exports overwrite existing files?

**A:** Yes, by operation type folder:
- Same operation → same folder
- Each export creates timestamped files (if needed)
- Or overwrites with same name

**Solution**: Use custom paths for archival exports

### Q: How do I find old exports?

**A:** All in one place:
```
Desktop/
└── advanced-memory-exports/
    ├── pdf/          (all PDF exports)
    ├── docsify/      (all website exports)
    └── ...
```

Easy to backup, easy to clean up!

---

## Summary

**Old way**:
```python
adn_export("pdf", export_path="C:/Users/Sandra/Documents/Exports/PDF/2024-10-20/output/")
```
User: "What path should I use??" 🤔

**New way**:
```python
adn_export("pdf")
```
User: "It's on my Desktop!" 😊

🎉 **Smart defaults make exports effortless!**







