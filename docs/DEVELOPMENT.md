# Development â€” repo tasks (`just`)

This project uses a [Just](https://github.com/casey/just) file for linting, tests, and packaging. From the **repository root**, run:

```
just
```

Shows the recipe dashboard (PowerShell on Windows).

## Common recipes

| Command     | Purpose              |
| :---------- | :------------------- |
| `just lint` | Ruff lint            |
| `just fix`  | Ruff fix + format    |
| `just test` | Run tests            |
| `just pack` | Build `.mcpb` package |

See the `Justfile` in the repo root for the full list.

[README](../README.md)
---

## Sync Service Architecture

`src/advanced_memory/sync/sync_service.py` — core sync loop.

### Performance rules (learned the hard way)

**`handle_move` must not call `index_entity` for path-only moves.**
The FTS trigram indexer re-reads the full file and rebuilds stems — O(content length).
On Windows, the first sync after files were indexed on Linux/Mac produces thousands of
`/` → `\` path-separator "moves". Each one must go through the cheap
`search_service.update_entity_path()` path, not `index_entity`.

Only call `index_entity` from `handle_move` when `content_changed=True` (i.e.
`update_permalinks_on_move` caused a real file rewrite with a new checksum).

**`resolve_relations` must not call `index_entity`.**
Relation resolution only writes `to_id`/`to_name` to the relation row — it does not
change file content. The search index for entity content is already correct. Adding
`index_entity` here re-indexes every relation target on every sync, which dominated
wall-clock time on large vaults (~21 min for 3,000 entities).

### When `index_entity` IS appropriate

- `sync_file` — new or modified files (content changed, must re-index)
- `handle_move` with `content_changed=True` — permalink rewrite changed file content

### Search index update methods

| Method | Cost | When to use |
|--------|------|-------------|
| `search_service.index_entity(entity)` | High — reads file, rebuilds stems | Content changed |
| `search_service.update_entity_path(id, path)` | Low — single SQL UPDATE | Path-only rename |