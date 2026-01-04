# Research Checklist

Review every 6 months or when major Python releases land.

## 1. Source Refresh
- [ ] Read Python release notes (https://docs.python.org/3/whatsnew/).
- [ ] Monitor PyCon/PyData talks on debugging and tooling.
- [ ] Track IDE/debugger updates (VSCode, PyCharm, Wing).
- [ ] Follow asyncio, Trio, and concurrency SIG updates.

## 2. Tooling Audit
- [ ] Verify debugger versions and compatibility (debugpy, pdb, IDE).
- [ ] Review logging formats and redaction policies.
- [ ] Ensure profiling tools (scalene, py-spy) support current Python version.
- [ ] Update Docker dev containers or VSCode settings.

## 3. Documentation
- [ ] Refresh debugging quickstart guides and onboarding docs.
- [ ] Update incident response templates with recent examples.
- [ ] Archive root cause analyses for recurring issues.

## 4. Metrics
- [ ] Analyze error tracking trends; identify top recurring issues.
- [ ] Measure mean-time-to-detect/resolve for debugging incidents.
- [ ] Review flake rate in CI; adjust tooling accordingly.

## 5. Source Log
| Date | Source | Notes |
| --- | --- | --- |
| 2025-11-08 | Python 3.13 Release Notes | Debugging improvements, specializing interpreter |
| 2025-11-08 | PyCon 2025 Debugging Track | Async debugging best practices |
| 2025-11-08 | Real Python Advanced Debugging Guide | Structured logging + remote debugging |
| 2025-11-08 | PEP 760 Draft | Asyncio task introspection updates |

> Tip: Start with `adn_skills("distill_from_wikipedia", topic="Debugging")` for baseline refresh, then inspect debugger changes directly via `adn_skills("import_from_github", repository="python/cpython", path="Lib/pdb.py")`.***
