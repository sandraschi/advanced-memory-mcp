"""Delete a project from the database."""
import sqlite3
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 2:
    print("Usage: python scripts/delete_project.py <project_id>")
    sys.exit(1)

project_id = int(sys.argv[1])
db_path = r'C:\Users\sandr\.advanced-memory\memory.db'

conn = sqlite3.connect(db_path)

# Get project info
cursor = conn.execute('SELECT name, path FROM project WHERE id = ?', (project_id,))
project = cursor.fetchone()

if not project:
    print(f"ERROR: Project {project_id} not found")
    conn.close()
    sys.exit(1)

# Get entity count
cursor = conn.execute('SELECT COUNT(*) FROM entity WHERE project_id = ?', (project_id,))
entity_count = cursor.fetchone()[0]

print(f"Deleting project '{project[0]}' (id={project_id})")
print(f"  Path: {project[1]}")
print(f"  Entities: {entity_count}")

# Delete
conn.execute('DELETE FROM project WHERE id = ?', (project_id,))
conn.commit()
conn.close()

print(f"✓ Deleted!")

