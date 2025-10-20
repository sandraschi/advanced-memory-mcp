"""Clean up duplicate/old projects from database."""

import sqlite3
import sys

db_path = r"C:\Users\sandr\.advanced-memory\memory.db"
conn = sqlite3.connect(db_path)

print("Current projects:")
cursor = conn.execute("SELECT id, name, path FROM project")
projects = cursor.fetchall()
for p in projects:
    print(f"  [{p[0]}] {p[1]}: {p[2]}")

print("\nEntity counts:")
cursor = conn.execute(
    "SELECT p.id, p.name, COUNT(e.id) FROM project p LEFT JOIN entity e ON p.id = e.project_id GROUP BY p.id"
)
for row in cursor:
    print(f"  [{row[0]}] {row[1]}: {row[2]} entities")

print("\n" + "=" * 70)
print("CLEANUP RECOMMENDATIONS")
print("=" * 70)

# Find empty or nearly empty projects
cursor = conn.execute("""
    SELECT p.id, p.name, p.path, COUNT(e.id) as entity_count
    FROM project p
    LEFT JOIN entity e ON p.id = e.project_id
    GROUP BY p.id
    HAVING entity_count < 10
""")
small_projects = cursor.fetchall()

if small_projects:
    print("\nProjects with < 10 entities (candidates for deletion):")
    for p in small_projects:
        print(f"  [{p[0]}] {p[1]}: {p[3]} entities at {p[2]}")

    print("\nTo delete a project:")
    print("  python scripts/cleanup_duplicate_projects.py --delete <project_id>")

# Find duplicate paths
cursor = conn.execute("""
    SELECT path, GROUP_CONCAT(name, ', ') as projects, COUNT(*) as count
    FROM project
    GROUP BY path
    HAVING count > 1
""")
dupes = cursor.fetchall()

if dupes:
    print("\nDuplicate paths (multiple projects pointing to same folder):")
    for d in dupes:
        print(f"  {d[0]}")
        print(f"    Projects: {d[1]}")

    print("\nRecommendation: Keep the one with most entities, delete the others")

conn.close()

# Handle command line args
if len(sys.argv) > 1 and sys.argv[1] == "--delete":
    if len(sys.argv) < 3:
        print("\nUsage: python scripts/cleanup_duplicate_projects.py --delete <project_id>")
        sys.exit(1)

    project_id = int(sys.argv[2])

    # Confirm
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT name, path FROM project WHERE id = ?", (project_id,))
    project = cursor.fetchone()

    if not project:
        print(f"ERROR: Project {project_id} not found")
        conn.close()
        sys.exit(1)

    print(f"\nWARNING: This will DELETE project '{project[0]}' (id={project_id})")
    print(f"  Path: {project[1]}")

    # Check entity count
    cursor = conn.execute("SELECT COUNT(*) FROM entity WHERE project_id = ?", (project_id,))
    entity_count = cursor.fetchone()[0]
    print(f"  Entities: {entity_count}")

    if entity_count > 100:
        print(f"\nERROR: Project has {entity_count} entities! Too dangerous to delete.")
        print("Only projects with < 100 entities can be deleted with this script.")
        conn.close()
        sys.exit(1)

    confirm = input("\nType the project name to confirm deletion: ")
    if confirm != project[0]:
        print("Cancelled.")
        conn.close()
        sys.exit(0)

    # Delete
    conn.execute("DELETE FROM project WHERE id = ?", (project_id,))
    conn.commit()
    print(f"\n✓ Deleted project '{project[0]}' (id={project_id})")
    print("Note: Entities and relations were also deleted (cascade)")

    conn.close()
