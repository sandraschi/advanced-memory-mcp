import inspect
import re

from advanced_memory.mcp.tools.content_manager import adn_content

fn = adn_content.fn if hasattr(adn_content, "fn") else adn_content
d = inspect.getdoc(fn)
print("len", len(d or ""), "has Args", "Args:" in (d or ""))
m = re.search(r"Args:\s*\n", d)
lines = []
if m:
    lines = d[m.end() :].split("\n")[:5]
    for i, line in enumerate(lines):
        print(i, repr(line[:60]))

# Test regex
for line in lines:
    m8 = re.match(r"^\s{8}(\w+):\s*(.*)$", line)
    m4 = re.match(r"^\s{4}(\w+):\s*(.*)$", line)
    print("line", repr(line[:40]), "m8", bool(m8), "m4", bool(m4))
