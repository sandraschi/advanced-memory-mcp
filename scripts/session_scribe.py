"""Session scribe v1 - auto-capture Claude session digests into the vault.

Created 2026-07-17. Fixes the recurring failure mode where dev sessions end
without notes (10-day backlog reconstructed by hand that same day).

What it does, each run:
1. Scans Claude transcript jsonl files (Cowork local-agent-mode-sessions +
   Claude Code ~/.claude/projects) modified since the last run.
2. Builds a compact per-session digest: time range, message/tool counts,
   user-intent lines (what Sandra actually asked).
3. Optionally asks the local LLM (LLMClient -> Ollama) for a bullet summary;
   degrades gracefully to the raw digest if no LLM is reachable.
4. Writes ONE timestamped digest note into the vault inbox/ folder (the watch
   service indexes it) and a copy into aiwatcher-mcp's data/inbox/.

State: ~/.advanced-memory/scribe_state.json (last_run ISO). Safe to run any
time; no transcripts modified since last run -> exits quietly without a note.

Run:      uv run --directory D:\\Dev\\repos\\advanced-memory-mcp python scripts/session_scribe.py
Schedule: hourly via Windows scheduled task 'advanced-memory-session-scribe'.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
STATE_FILE = HOME / ".advanced-memory" / "scribe_state.json"
VAULT_INBOX = HOME / ".advanced-memory" / "vault" / "inbox"
AIWATCHER_INBOX = Path(r"D:\Dev\repos\aiwatcher-mcp\data\inbox")

TRANSCRIPT_ROOTS = [
    HOME / ".claude" / "projects",
    HOME / "AppData" / "Roaming" / "Claude" / "local-agent-mode-sessions",
]

MAX_SESSIONS_PER_RUN = 20
MAX_INTENT_LINES = 12
MAX_INTENT_CHARS = 240
DEFAULT_LOOKBACK_HOURS = 24  # first run / missing state


def _now() -> datetime:
    return datetime.now(UTC)


def _load_state() -> dict:
    """State: last_run ISO + per-session seen user-message counts (dedupe, v2)."""
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if "last_run" in data:
            data.setdefault("sessions", {})
            return data
    except Exception:
        pass
    return {
        "last_run": (_now() - timedelta(hours=DEFAULT_LOOKBACK_HOURS)).isoformat(),
        "sessions": {},
    }


def _save_state(ts: datetime, sessions: dict[str, int]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    trimmed = dict(sorted(sessions.items())[-200:])  # bound the map
    STATE_FILE.write_text(
        json.dumps({"last_run": ts.isoformat(), "sessions": trimmed}), encoding="utf-8"
    )


def _find_transcripts(since: datetime) -> list[Path]:
    since_ts = since.timestamp()
    found: list[Path] = []
    for root in TRANSCRIPT_ROOTS:
        if not root.is_dir():
            continue
        try:
            for p in root.rglob("*.jsonl"):
                try:
                    if p.stat().st_mtime > since_ts and p.stat().st_size > 500:
                        found.append(p)
                except OSError:
                    continue
        except OSError:
            continue
    # newest first, cap
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found[:MAX_SESSIONS_PER_RUN]


def _extract_text_items(content) -> list[str]:
    """Pull text blocks out of a message content list/str."""
    texts: list[str] = []
    if isinstance(content, str):
        texts.append(content)
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
    return texts


def _digest_session(path: Path, seen: int = 0) -> dict | None:
    """Digest a transcript; only user messages beyond `seen` are included (dedupe)."""
    user_lines: list[str] = []
    n_user = n_assistant = n_tools = 0
    first_ts = last_ts = None

    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(entry, dict):
                    continue
                ts = entry.get("timestamp")
                if ts:
                    first_ts = first_ts or ts
                    last_ts = ts
                etype = entry.get("type")
                msg = entry.get("message") or {}
                content = msg.get("content") if isinstance(msg, dict) else None
                if etype == "user":
                    texts = _extract_text_items(content)
                    real = [
                        t.strip()
                        for t in texts
                        if t.strip()
                        and not t.startswith("<")  # skip system-reminder/tool blocks
                        and "tool_result" not in t[:60]
                    ]
                    if real:
                        n_user += 1
                        if n_user > seen and len(user_lines) < MAX_INTENT_LINES:
                            user_lines.append(real[0][:MAX_INTENT_CHARS].replace("\n", " "))
                elif etype == "assistant":
                    n_assistant += 1
                    if isinstance(content, list):
                        n_tools += sum(
                            1
                            for i in content
                            if isinstance(i, dict) and i.get("type") == "tool_use"
                        )
    except OSError:
        return None

    if n_user == 0 or n_user <= seen:
        return None  # nothing new since last digest (dedupe)
    return {
        "path": str(path),
        "session": path.stem[:12],
        "kind": "cowork" if "local-agent-mode-sessions" in str(path) else "claude-code",
        "first_ts": first_ts,
        "last_ts": last_ts,
        "n_user": n_user - seen,
        "n_user_total": n_user,
        "n_assistant": n_assistant,
        "n_tools": n_tools,
        "user_lines": user_lines,
    }


MAX_LLM_SESSIONS = 6  # cap per-run LLM calls (v2, 2026-07-17)


def _detect_repos(digests: list[dict]) -> list[str]:
    """Auto-tag: repo names actually mentioned in the sessions (v2)."""
    import re

    text = " ".join(" ".join(d["user_lines"]) for d in digests).lower()
    names = set(re.findall(r"[a-z0-9][a-z0-9_]*(?:-[a-z0-9_]+)*-mcp\b", text))
    repos_root = Path(r"D:\Dev\repos")
    if repos_root.is_dir():
        try:
            for p in repos_root.iterdir():
                if p.is_dir() and len(p.name) > 3 and p.name.lower() in text:
                    names.add(p.name.lower())
        except OSError:
            pass
    return sorted(names)[:10]


def _llm_bullets(digests: list[dict]) -> dict[str, str]:
    """Best-effort per-session bullet summaries via local LLM (v2).

    Returns {session_id: bullets} for up to MAX_LLM_SESSIONS newest sessions;
    empty dict if no LLM is reachable. Never raises.
    """
    summaries: dict[str, str] = {}
    try:
        import asyncio

        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        from advanced_memory.services.llm_client import get_llm_client

        llm = get_llm_client()

        async def _one(d: dict) -> None:
            material = "\n".join(f"- {line}" for line in d["user_lines"])
            prompt = (
                f"User requests from one dev session ({d['n_user']} messages, "
                f"{d['n_tools']} tool calls). Summarize the work in 3-5 terse "
                "bullet points naming repos/tools mentioned. Bullets only, no preamble.\n\n"
                + material[:4000]
            )
            out = await llm.generate(
                prompt=prompt,
                system_prompt="Terse dev-log summarizer.",
                max_tokens=300,
                temperature=0.2,
            )
            out = (out or "").strip()
            if out:
                summaries[d["session"]] = out

        async def _all() -> None:
            for d in digests[:MAX_LLM_SESSIONS]:
                try:
                    await _one(d)
                except Exception:
                    continue

        asyncio.run(_all())
    except Exception:
        pass
    return summaries


def main() -> int:
    started = _now()
    state = _load_state()
    last_run = datetime.fromisoformat(state["last_run"])
    seen_map: dict[str, int] = state.get("sessions", {})
    transcripts = _find_transcripts(last_run)

    digests = []
    new_seen = dict(seen_map)
    for t in transcripts:
        d = _digest_session(t, seen=seen_map.get(str(t), 0))
        if d:
            digests.append(d)
            new_seen[d["path"]] = d["n_user_total"]

    if not digests:
        _save_state(started, new_seen)
        print("scribe: no new session activity since", last_run.isoformat(), file=sys.stderr)
        return 0

    local_now = datetime.now().astimezone()
    stamp = local_now.strftime("%Y-%m-%d %H:%M")
    fname_stamp = local_now.strftime("%Y-%m-%d_%H-%M")
    title = f"{stamp} session scribe digest"

    repo_tags = _detect_repos(digests)
    summaries = _llm_bullets(digests)

    lines = [
        "---",
        f"title: {title}",
        "type: note",
        "tags:",
        "- session-scribe",
        "- auto-capture",
        "- review",
        *[f"- {r}" for r in repo_tags],
        "---",
        "",
        f"# {title}",
        "",
        f"Auto-captured by session_scribe.py. Window: {last_run.isoformat()} -> {started.isoformat()}.",
        f"{len(digests)} active session(s). REVIEW: promote real work to proper project notes, then delete this.",
        "",
        "## Sessions",
        "",
    ]
    for d in digests:
        lines += [
            f"### {d['session']} ({d['kind']}) - {d['n_user']} new user msgs "
            f"(of {d['n_user_total']}), {d['n_assistant']} assistant turns, "
            f"{d['n_tools']} tool calls",
            "",
        ]
        bullets = summaries.get(d["session"])
        if bullets:
            lines += ["**LLM summary (local model):**", "", bullets, "", "**Raw intents:**", ""]
        lines += [f"- {line}" for line in d["user_lines"]]
        lines.append("")
    summary = bool(summaries)

    note_text = "\n".join(lines)

    VAULT_INBOX.mkdir(parents=True, exist_ok=True)
    vault_file = VAULT_INBOX / f"{fname_stamp}_session-scribe.md"
    vault_file.write_text(note_text, encoding="utf-8")

    try:
        AIWATCHER_INBOX.mkdir(parents=True, exist_ok=True)
        (AIWATCHER_INBOX / vault_file.name).write_text(note_text, encoding="utf-8")
    except OSError as exc:
        print(f"scribe: aiwatcher inbox copy failed: {exc}", file=sys.stderr)

    _save_state(started, new_seen)
    print(f"scribe: wrote {vault_file} ({len(digests)} sessions, llm={'yes' if summary else 'no'})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
