"""Direct test of Pandoc + LaTeX PDF export."""

import subprocess
from pathlib import Path


def test_pandoc_latex():
    """Test Pandoc with LaTeX engine for PDF export."""
    print("Testing Pandoc + LaTeX PDF Export")
    print("=" * 60)

    # Create test markdown
    test_dir = Path("d:/Dev/repos/test-pdf-export")
    test_dir.mkdir(exist_ok=True)
    test_md = test_dir / "test.md"
    test_pdf = test_dir / "test.pdf"

    test_md.write_text("""# Test PDF Export

This tests Pandoc with LaTeX engine.

## Math Test

Inline: $E = mc^2$

Block:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$

## List

- Item 1
- Item 2
""")

    print(f"\n1. Created test markdown: {test_md}")

    # Try to find pandoc
    print("\n2. Finding Pandoc...")
    import shutil

    pandoc_path = shutil.which("pandoc")
    if not pandoc_path:
        # Try pypandoc
        try:
            import pypandoc

            pandoc_path = pypandoc.get_pandoc_path()
            print(f"   ✅ Found via pypandoc: {pandoc_path}")
        except Exception as e:
            print(f"   ❌ Pandoc not found: {e}")
            print("   Will try to auto-install...")
            try:
                import pypandoc

                print("   Downloading Pandoc (this may take a moment)...")
                pandoc_path = pypandoc.get_pandoc_path()
                print(f"   ✅ Auto-installed: {pandoc_path}")
            except Exception as e2:
                print(f"   ❌ Auto-install failed: {e2}")
                return
    else:
        print(f"   ✅ Found in PATH: {pandoc_path}")

    # Try to find pdflatex
    print("\n3. Finding LaTeX engine (pdflatex)...")
    pdflatex_path = shutil.which("pdflatex")
    if pdflatex_path:
        print(f"   ✅ Found: {pdflatex_path}")
    else:
        print("   ❌ pdflatex not found in PATH")
        print("   ⚠️  Need to install MiKTeX or TeX Live")
        print("   Trying anyway - Pandoc might handle it...")

    # Test export with pdflatex
    print("\n4. Testing PDF export with pdflatex...")
    try:
        cmd = [
            str(pandoc_path),
            str(test_md),
            "-o",
            str(test_pdf),
            "--pdf-engine=pdflatex",
            "-V",
            "geometry:margin=1in",
        ]
        print(f"   Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            if test_pdf.exists():
                print(f"   ✅ PDF created successfully: {test_pdf}")
                print(f"   Size: {test_pdf.stat().st_size} bytes")
            else:
                print("   ⚠️  Command succeeded but PDF not found")
        else:
            print(f"   ❌ Export failed with return code: {result.returncode}")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("   ❌ Export timed out (LaTeX compilation can take time)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback

        traceback.print_exc()

    # Test export with weasyprint (fallback)
    print("\n5. Testing PDF export with weasyprint (pure Python)...")
    test_pdf2 = test_dir / "test_weasyprint.pdf"
    try:
        cmd = [str(pandoc_path), str(test_md), "-o", str(test_pdf2), "--pdf-engine=weasyprint"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and test_pdf2.exists():
            print(f"   ✅ PDF created with weasyprint: {test_pdf2}")
            print(f"   Size: {test_pdf2.stat().st_size} bytes")
        else:
            print("   ⚠️  weasyprint export failed or not available")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ⚠️  weasyprint test error: {e}")

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    test_pandoc_latex()
