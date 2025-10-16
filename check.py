import sqlite3
c = sqlite3.connect(r'C:\Users\sandr\.advanced-memory\memory.db')
r = c.execute('SELECT COUNT(*) FROM entity WHERE project_id = (SELECT id FROM project WHERE name = "advanced-memory-mcp")').fetchone()[0]
print(f'advanced-memory-mcp: {r} files')
c.close()

