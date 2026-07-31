"""Test fpdf2 for lightweight PDF export - NO LaTeX needed!"""

from pathlib import Path

try:
    from fpdf import FPDF

    print("✅ fpdf2 imported successfully")
except ImportError:
    print("❌ fpdf2 not installed - run: pip install fpdf2")
    exit(1)


class MarkdownPDF(FPDF):
    """PDF generator that handles basic markdown."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    @staticmethod
    def _sanitize(text: object) -> str:
        """Replace characters the core fonts (latin-1) cannot encode."""
        s = str(text)
        try:
            s.encode("latin-1")
            return s
        except UnicodeEncodeError:
            return "".join(c if ord(c) < 256 else "?" for c in s)

    def cell(self, *args, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = self._sanitize(kwargs["text"])
        elif len(args) >= 3 and isinstance(args[2], str):
            args = (*args[:2], self._sanitize(args[2]), *args[3:])
        return super().cell(*args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = self._sanitize(kwargs["text"])
        elif len(args) >= 3 and isinstance(args[2], str):
            args = (*args[:2], self._sanitize(args[2]), *args[3:])
        return super().multi_cell(*args, **kwargs)

    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "Advanced Memory Export", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_markdown(self, md_content: str):
        """Add markdown content to PDF."""
        lines = md_content.split("\n")
        in_code_block = False
        code_lines = []

        for line in lines:
            # Code blocks
            if line.strip().startswith("```"):
                if in_code_block:
                    # End code block
                    self.set_font("Courier", "", 10)
                    self.set_fill_color(240, 240, 240)
                    self.multi_cell(0, 5, "\n".join(code_lines), border=0, fill=True)
                    code_lines = []
                    in_code_block = False
                    self.ln(2)
                else:
                    # Start code block
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # Headers
            if line.startswith("# "):
                self.set_font("Arial", "B", 24)
                self.cell(0, 12, line[2:].strip(), ln=1)
                self.ln(2)
            elif line.startswith("## "):
                self.set_font("Arial", "B", 18)
                self.cell(0, 10, line[3:].strip(), ln=1)
                self.ln(2)
            elif line.startswith("### "):
                self.set_font("Arial", "B", 14)
                self.cell(0, 8, line[4:].strip(), ln=1)
                self.ln(1)
            # Lists
            elif line.strip().startswith("- ") or line.strip().startswith("* "):
                self.set_font("Arial", "", 12)
                self.cell(10)
                self.cell(0, 6, "- " + line.strip()[2:], ln=1)
            # Regular text
            elif line.strip():
                self.set_font("Arial", "", 12)
                # Handle basic formatting
                text = line.strip()
                text = text.replace("**", "")  # Remove bold markers for now
                text = text.replace("__", "")  # Remove italic markers
                self.multi_cell(0, 6, text, align="L")
                self.ln(1)
            else:
                # Empty line
                self.ln(2)


def test_fpdf2_export():
    """Test fpdf2 PDF generation."""
    print("=" * 60)
    print("Testing fpdf2 PDF Export (Pure Python, No LaTeX!)")
    print("=" * 60)

    # Create test markdown
    test_md = """# Test PDF Export with fpdf2

This is a test document using **fpdf2** - pure Python, no LaTeX!

## Features

- Pure Python library
- Minimal dependencies
- No 2GB LaTeX bullshit
- Works immediately

### Code Example

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(40, 10, 'Hello World')
pdf.output('hello.pdf')
```

## Math (as plain text for now)

E = mc²

∫ e^(-x²) dx = √π

## Conclusion

fpdf2 is lightweight and works!
"""

    # Create PDF
    print("\n1. Creating PDF with fpdf2...")
    pdf = MarkdownPDF()
    pdf.add_page()
    pdf.add_markdown(test_md)

    # Save
    output_dir = Path("d:/Dev/repos/test-pdf-export")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_fpdf2.pdf"

    pdf.output(str(output_path))

    if output_path.exists():
        size = output_path.stat().st_size
        print(f"   ✅ PDF created: {output_path}")
        print(f"   Size: {size:,} bytes ({size / 1024:.1f} KB)")
        print(f"\n   📄 Open: {output_path}")
    else:
        print("   ❌ PDF not created!")

    print("\n" + "=" * 60)
    print("Test complete! fpdf2 works without LaTeX! 🎉")
    print("=" * 60)


if __name__ == "__main__":
    test_fpdf2_export()
