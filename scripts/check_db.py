import sqlite3
import sys

db_path = r'C:\Users\sandr\.advanced-memory\memory.db'
conn = sqlite3.connect(db_path)

print("Projects in database:")
cursor = conn.execute('SELECT name, path FROM project')
for row in cursor:
    print(f'  {row[0]}: {row[1]}')

print("\nEntity counts by project:")
cursor = conn.execute('SELECT p.name, COUNT(e.id) FROM project p LEFT JOIN entity e ON p.id = e.project_id GROUP BY p.id')
for row in cursor:
    print(f'  {row[0]}: {row[1]} entities')

conn.close()

