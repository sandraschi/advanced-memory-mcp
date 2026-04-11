# Development — repo tasks (`just`)

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
