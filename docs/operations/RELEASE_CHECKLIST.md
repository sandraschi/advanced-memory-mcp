# Release checklist (PyPI + MCPB)

Use this when cutting a stable tag (for example **v1.8.1**). Adapt the version string everywhere below.

## 1. Version alignment

Confirm the same semantic version in:

| File | Field |
| :--- | :--- |
| `pyproject.toml` | `[project].version` |
| `src/advanced_memory/__init__.py` | `__version__` |
| `manifest.json` | `version` (MCPB / Claude extension manifest) |
| `mcpb.json` | `version` (local MCPB metadata) |

Optional catalog metadata: `glama.json` (tool counts, description).

## 2. Changelog and docs

- [ ] `CHANGELOG.md` has a section for this version.
- [ ] `docs/PRD.md` and top-level `README.md` badges match.

## 3. Build MCPB (`.mcpb`)

From the repository root (PowerShell):

```powershell
Set-Location D:\Dev\repos\advanced-memory-mcp
if (-not (Test-Path dist)) { New-Item -ItemType Directory -Path dist | Out-Null }
npx --yes @anthropic-ai/mcpb@latest validate manifest.json
npx --yes @anthropic-ai/mcpb@latest pack . "dist/advanced-memory-mcp.mcpb"
```

Or install [just](https://github.com/casey/just) and run `just pack` (same commands).

**Output:** `dist/advanced-memory-mcp.mcpb` (the `dist/` directory is gitignored). Copy the **shasum** line from the `mcpb pack` log and record **SHA256** for GitHub release notes:

```powershell
Get-FileHash .\dist\advanced-memory-mcp.mcpb -Algorithm SHA256
```

## 4. Quality gate (before tag)

```powershell
Set-Location D:\Dev\repos\advanced-memory-mcp
uv run ruff check .
uv run pytest -q tests\test_search_rag_extra_helpers.py
```

Run the full suite when practical (`just test-unit` if `just` is available).

## 5. Git tag and GitHub release

1. Commit all release files (including `manifest.json`, `mcpb.json`, version bumps).
2. Create an annotated tag:

```powershell
git tag -a v1.8.1 -m "Release v1.8.1"
git push origin main
git push origin v1.8.1
```

3. On GitHub: **Releases → Draft a new release** → choose tag **v1.8.1** → paste the **CHANGELOG** section for this version → attach **`dist/advanced-memory-mcp.mcpb`** as a release asset (rebuild the file if the tag moved).

## 6. `just release` (Linux / Git Bash only)

The recipe `just release v1.8.1` in the root `justfile` runs `just check`, bumps `__init__.py`, commits, tags, and pushes. It expects **bash**, a **clean** `git status`, and branch **main**. On Windows-only shells, use the manual steps above instead.

## 7. PyPI

Stable tags drive publishing only if your `.github/workflows` release job is configured and secrets (for example `PYPI_API_TOKEN`) are set. See [PYPI_PUBLISHING_COMPLETE_GUIDE.md](PYPI_PUBLISHING_COMPLETE_GUIDE.md).
