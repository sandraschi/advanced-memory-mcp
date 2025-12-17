"""Quick test to verify fpdf2 installation and PDF export availability."""

import sys
from pathlib import Path

# Add advanced-memory to path
sys.path.insert(0, str(Path(__file__).parent / "advanced-memory-mcp" / "src"))

print("=" * 60)
print("Testing fpdf2 Installation and PDF Export")
print("=" * 60)

# Test 1: Import fpdf2
print("\n1. Testing fpdf2 import...")
try:
    import fpdf
    print(f"   ✓ fpdf2 imported successfully")
    print(f"   Version: {fpdf.__version__}")
except ImportError as e:
    print(f"   ✗ fpdf2 import failed: {e}")
    sys.exit(1)

# Test 2: Create a simple PDF
print("\n2. Testing PDF creation...")
try:
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Test PDF from fpdf2", ln=1)
    
    test_pdf_path = Path(__file__).parent / "test_fpdf2_output.pdf"
    pdf.output(str(test_pdf_path))
    
    if test_pdf_path.exists():
        print(f"   ✓ PDF created successfully: {test_pdf_path}")
        print(f"   Size: {test_pdf_path.stat().st_size} bytes")
    else:
        print(f"   ✗ PDF file not created")
except Exception as e:
    print(f"   ✗ PDF creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check Advanced Memory PDF export module
print("\n3. Testing Advanced Memory PDF export module...")
try:
    from advanced_memory.mcp.tools.export_pdf_native import FPDF_AVAILABLE, export_pdf_native
    print(f"   ✓ Module imported successfully")
    print(f"   FPDF_AVAILABLE: {FPDF_AVAILABLE}")
    if FPDF_AVAILABLE:
        print("   ✓ PDF export is ready to use!")
    else:
        print("   ✗ PDF export not available (fpdf2 not detected)")
except Exception as e:
    print(f"   ✗ Module import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
