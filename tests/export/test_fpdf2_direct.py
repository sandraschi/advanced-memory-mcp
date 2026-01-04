"""Direct test of fpdf2 export - bypasses MCP server."""

import sys
from pathlib import Path

# Add advanced-memory to path
sys.path.insert(0, str(Path(__file__).parent / "advanced-memory-mcp" / "src"))

from fpdf import FPDF


class MarkdownPDF(FPDF):
    """Simple PDF generator for markdown."""

    def __init__(self, title: str = "Test"):
        super().__init__()
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, self.title, 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_markdown(self, md_content: str):
        """Add markdown content."""
        lines = md_content.split("\n")
        for line in lines:
            if line.startswith("# "):
                self.set_font("Arial", "B", 24)
                self.cell(0, 12, line[2:].strip(), ln=1)
                self.ln(2)
            elif line.startswith("## "):
                self.set_font("Arial", "B", 18)
                self.cell(0, 10, line[3:].strip(), ln=1)
                self.ln(2)
            elif line.strip().startswith("- "):
                self.set_font("Arial", "", 12)
                self.cell(10)
                self.cell(0, 6, "• " + line.strip()[2:], ln=1)
            elif line.strip():
                self.set_font("Arial", "", 12)
                text = line.strip().replace("**", "")
                self.multi_cell(0, 6, text, align="L")
                self.ln(1)
            else:
                self.ln(2)


# Test markdown
test_md = """# Test PDF Export

This tests fpdf2 - pure Python, no LaTeX!

## Features

- Pure Python
- No dependencies
- Works immediately

## Conclusion

fpdf2 is ready!
"""

# Create PDF
print("Creating PDF with fpdf2...")
pdf = MarkdownPDF(title="Test Export")
pdf.add_page()
pdf.add_markdown(test_md)

output_path = Path("d:/Dev/repos/test-pdf-export/test_fpdf2_direct.pdf")
pdf.output(str(output_path))

if output_path.exists():
    size = output_path.stat().st_size
    print(f"✅ PDF created: {output_path}")
    print(f"   Size: {size:,} bytes")
else:
    print("❌ PDF not created!")
