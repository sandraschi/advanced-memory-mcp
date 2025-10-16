import sqlite3
conn = sqlite3.connect(r"C:\Users\sandr\.advanced-memory\memory.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM entity WHERE project_id = (SELECT id FROM project WHERE name = 'advanced-memory-mcp')")
count = cur.fetchone()[0]
print(f"{count}")
conn.close()

