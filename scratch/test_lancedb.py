import os
from pathlib import Path

import lancedb

db_path = Path("scratch_db")
os.makedirs(db_path, exist_ok=True)
db = lancedb.connect(db_path)

print(f"Db type: {type(db)}")
print(f"Directory: {dir(db)}")

if hasattr(db, "table_names"):
    try:
        res = db.table_names()
        print(f"table_names (sync): {res}")
    except Exception as e:
        print(f"table_names (sync) failed: {e}")

if hasattr(db, "list_tables"):
    try:
        res = db.list_tables()
        print(f"list_tables (sync): {res}")
    except Exception as e:
        print(f"list_tables (sync) failed: {e}")


async def test_async():
    import lancedb

    db_async = await lancedb.connect_async("scratch_db_async")
    print(f"Async Db type: {type(db_async)}")
    print(f"Async Directory: {dir(db_async)}")
    # In async connection, we use table_names() usually or list_tables()
    try:
        res = await db_async.table_names()
        print(f"async table_names: {res}")
    except Exception as e:
        print(f"async table_names failed: {e}")


import asyncio

try:
    asyncio.run(test_async())
except Exception as e:
    print(f"Async test failed: {e}")

shutil_path = Path("scratch_db")
import shutil

shutil.rmtree(shutil_path)
