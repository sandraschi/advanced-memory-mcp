"""Direct PDF export test - bypasses pytest for quick verification."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from advanced_memory.mcp.tools.export_pdf_native import MarkdownPDF, _export_single_note_pdf

# Test 1: Basic PDF creation
print("Test 1: Basic PDF creation")
pdf = MarkdownPDF(title="Test PDF")
pdf.add_page()
pdf.add_markdown("# Test\n\nContent here.")
test_dir = Path("d:/Dev/repos/test-pdf-export")
test_dir.mkdir(parents=True, exist_ok=True)
output_file = test_dir / "test_basic.pdf"
pdf.output(str(output_file))
print(f"✅ Created: {output_file} ({output_file.stat().st_size} bytes)")

# Test 2: Multiple notes
print("\nTest 2: Multiple notes export")
notes = [
    {
        "title": "Note 1: Introduction",
        "content": "# Introduction\n\nThis is the first note.",
        "permalink": "notes/note-1",
    },
    {
        "title": "Note 2: Details",
        "content": "# Details\n\nThis is the second note.\n\n- Item 1\n- Item 2",
        "permalink": "notes/note-2",
    },
    {
        "title": "Note 3: Conclusion",
        "content": "# Conclusion\n\nFinal thoughts here.",
        "permalink": "notes/note-3",
    },
]

import asyncio


async def test_multiple():
    for note in notes:
        result = await _export_single_note_pdf(note, test_dir)
        if result:
            print(f"✅ Exported: {Path(result).name} ({Path(result).stat().st_size} bytes)")


asyncio.run(test_multiple())

# Test 3: Edge cases
print("\nTest 3: Edge cases")

edge_cases = [
    {
        "title": "Empty Note",
        "content": "",
        "permalink": "test/empty",
    },
    {
        "title": "Special Characters: @#$%",
        "content": "# Special\n\nTesting: @#$%^&*()",
        "permalink": "test/special",
    },
    {
        "title": "Unicode: 中文 🎉",
        "content": "# Unicode\n\n中文 content\n\n🎉 Emojis!",
        "permalink": "test/unicode",
    },
    {
        "title": "Code Blocks",
        "content": """# Code

```python
def hello():
    print("Hello!")
```
""",
        "permalink": "test/code",
    },
    {
        "title": "Complex Markdown",
        "content": """# Complex

## Headers
### Level 3

## Lists
- Item 1
- Item 2

1. First
2. Second

**Bold** and *italic*

---

More content.
""",
        "permalink": "test/complex",
    },
]


async def test_edge_cases():
    for note in edge_cases:
        try:
            result = await _export_single_note_pdf(note, test_dir)
            if result:
                size = Path(result).stat().st_size
                print(f"✅ {note['title'][:30]:30s} -> {Path(result).name} ({size} bytes)")
        except Exception as e:
            print(f"❌ {note['title'][:30]:30s} -> ERROR: {e}")


asyncio.run(test_edge_cases())

# Summary
pdf_files = list(test_dir.glob("*.pdf"))
print(f"\n📊 Summary: {len(pdf_files)} PDF files created")
for pdf_file in sorted(pdf_files):
    print(f"   - {pdf_file.name} ({pdf_file.stat().st_size:,} bytes)")

print("\n✅ All tests completed!")
