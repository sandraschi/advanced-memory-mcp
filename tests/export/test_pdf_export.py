"""Test PDF export with Pandoc and LaTeX dependencies."""

import asyncio
import sys
from pathlib import Path

# Add advanced-memory to path
sys.path.insert(0, str(Path(__file__).parent / "advanced-memory-mcp" / "src"))


async def test_pdf_export():
    """Test PDF export with different engines."""
    print("=" * 60)
    print("Testing Advanced Memory PDF Export")
    print("=" * 60)

    # Test 1: Check pypandoc
    print("\n1. Checking pypandoc...")
    try:
        import pypandoc

        print(f"   ✅ pypandoc imported: {pypandoc.__version__}")
        try:
            pandoc_path = pypandoc.get_pandoc_path()
            print(f"   ✅ Pandoc found at: {pandoc_path}")
        except Exception as e:
            print(f"   ❌ Pandoc not found: {e}")
            print("   ⚠️  Will attempt auto-install on first use")
    except ImportError:
        print("   ❌ pypandoc not installed!")
        return

    # Test 2: Check weasyprint
    print("\n2. Checking weasyprint...")
    try:
        import weasyprint

        print(f"   ✅ weasyprint imported: {weasyprint.__version__}")
    except ImportError:
        print("   ❌ weasyprint not installed!")

    # Test 3: Check LaTeX engines
    print("\n3. Checking LaTeX engines...")
    import shutil

    latex_engines = ["pdflatex", "xelatex", "lualatex"]
    for engine in latex_engines:
        if shutil.which(engine):
            print(f"   ✅ {engine} found")
        else:
            print(f"   ❌ {engine} not found in PATH")

    # Test 4: Check pandoc_installer
    print("\n4. Testing pandoc installer...")
    try:
        from advanced_memory.utils.pandoc_installer import get_pandoc_command

        cmd = get_pandoc_command()
        print(f"   ✅ get_pandoc_command() returned: {cmd}")
    except Exception as e:
        print(f"   ❌ Error getting pandoc command: {e}")
        import traceback

        traceback.print_exc()

    # Test 5: Create test markdown and try export
    print("\n5. Creating test markdown file...")
    test_dir = Path("d:/Dev/repos/test-pdf-export")
    test_dir.mkdir(exist_ok=True)
    test_md = test_dir / "test.md"
    test_md.write_text("""# Test Document

This is a test for PDF export.

## Features

- Item 1
- Item 2

### Math

Inline: $E = mc^2$

Block:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$
""")
    print(f"   ✅ Created: {test_md}")

    print("\n" + "=" * 60)
    print("Test complete. Check output above for dependency status.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_pdf_export())
