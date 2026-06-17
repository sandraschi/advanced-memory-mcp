"""Full Advanced Memory vector reindex via API — use with just rag-gpu (venv python, not uv run)."""

from __future__ import annotations

import os
import sys


def main() -> int:
    import httpx

    base = os.environ.get("ADVANCED_MEMORY_API_URL", "http://127.0.0.1:8000").rstrip("/")
    url = f"{base}/search/reindex"
    print(f"[rag] POST {url}")
    try:
        with httpx.Client(timeout=7200.0) as client:
            resp = client.post(url)
            resp.raise_for_status()
            print(resp.json())
    except Exception as exc:
        print(
            f"[rag] API reindex failed: {exc}\n"
            "Start Advanced Memory API (webapp backend) and retry, or run: advanced-memory sync",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
