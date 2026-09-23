# MyAI Subproject Launchers Repaired, /apps Hub Working (11/11)

**Date:** 2026-09-22
**Repo:** myai
**Status:** Fixed, verified live, committed and pushed (10 commits)

---

## Problem

Booting `bob_and_alice` from the myai master webapp (`:10888/apps`) failed with
`No module named pip`. Investigation showed four distinct root causes, plus
two more found while bringing the other subprojects up. All 11 enabled apps
now boot through the hub and answer health checks.

## Root causes and fixes

1. **Root venv had no pip.** `myai/.venv` lost pip entirely. Repaired via
   `ensurepip --upgrade`, then upgraded to 26.2.1.
2. **Corrupted pip in 7 subproject venvs.** Partially-removed pip
   (`ModuleNotFoundError: pip._internal.operations.build`, a botched upgrade
   leaving half a tree). Repaired the same way in bob, document_viewer x2,
   future_you, gemini_tools, teams_debate x2. `teams_debate/venv` was fully
   dead (base Python 3.11 removed) and was deleted.
3. **BUG-037 class: unescaped parens in run.bat.** `echo ... (PID: %%a),
   stopping...` inside a `for`/`if` block makes cmd abort the whole batch
   with `stopping... was unexpected at this time.` before app.py ever runs.
   The 2026-09-14 fleet audit covered `starts/*.bat` only and missed project
   `run.bat` launchers; 5 more found in myai and fixed with paren-free text
   (`[PID: %%a]`). BUG-037 entry extended. Verified by test: bare echo aborts
   (exit 255), quoted `call :log` is safe.
4. **Naked `python` not on PATH.** All launchers called `python`; only `py -3`
   resolves here. Fixed across 8 launchers (run.bat trio, document_viewer,
   talking_avatar, gemini, 4 dual-stack backends).
5. **bridge.py launched PowerShell 5.1.** gemini's `start_local.ps1` requires
   7.0. Bridge now prefers pwsh, passes `-ExecutionPolicy Bypass`, sets cwd,
   checks both `.venv` and `venv`, returns pid, probes health with 8s timeout.
6. **App-level bugs:** `document_viewer` logs.py included its own router
   (AssertionError); character_conversation called `gr.mount_gradio_app` on
   Flask (ASGI-only) - split to Flask :5190 + Gradio :5191; talking_avatar and
   character requirements contained uninstallable packages on 3.13 (basicsr,
   Coqui TTS) - commented out with notes, backends degrade gracefully.
7. **Registry mismatches:** future_you and document_viewer health paths were
   `/health`, apps serve `/api/health`. Fixed in config.json.

## Verification

`POST /api/platform/apps/<id>/start` for all 11, each answering its health
endpoint. `tsc`, `ruff`, `mypy`, `bandit`, `biome` green on touched files.
`apps.tsx` now polls `/api/platform/status` every 5s with live badges.

## Commits (myai main, pushed)

765fcc8, 6baeb18, f884824, e2a6764, 58ab076, 4332c49, 7852f6f,
eabaf6a (11 files: mypy import-graph consistency forced the size),
b5cf359, 72d69d5. Pre-commit hook required re-stage/retry cycles
(trailing-whitespace and end-of-file fixers); safety snapshot taken first
per BUG-043. Unrelated README.md change in sandraschi/ left uncommitted.
