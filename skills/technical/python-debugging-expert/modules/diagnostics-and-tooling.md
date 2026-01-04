# Diagnostics & Tooling

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Python 3.13 Debugging Enhancements (2025), debugpy Docs (2025), PyCharm/VSCode Debugging Guides (2025), structlog/rich Logging Patterns (2024)

---

## 1. Debuggers

- `pdb` / `ipdb`: built-in CLI debugging; use `breakpoint()` for quick entry.
- `debugpy`: VSCode/remote debugging; supports attach to running process.
- PyCharm Professional debugger: advanced breakpoints, async support.
- `pudb`, `pdb++`: enhanced terminal debuggers with UI.

Best practice: avoid leaving breakpoints in production; use conditional breakpoints.

---

## 2. Logging & Tracing

- Configure structured logging (structlog, loguru) with context variables.
- Use logging levels consistently; trace ID propagation (contextvars).
- Integrate with observability stack (OpenTelemetry tracing).
- Mask secrets and PII; follow compliance policies.

---

## 3. Error Tracking

- Capture exceptions with Sentry, Rollbar, Honeybadger.
- Include breadcrumbs (user actions, request IDs).
- Setup alerting thresholds; correlate with deployment events.

---

## 4. Dynamic Inspection

- Use `sys.settrace`, `faulthandler`, `tracemalloc` to inspect runtime state.
- Enable `PYTHONWARNINGS=error` to surface deprecations.
- For C extensions, use `gdb` with `python-gdb.py` helpers.

---

## 5. Automation

- Create reusable debug scripts (invoke, doit) for attaching debuggers.
- Provide VSCode/IDE launch configurations, Docker compose dev containers.
- Document common commands in project README or onboarding guide.

---

### Checklist
- [ ] Logging structured and contextualized.
- [ ] Debugger setup documented for local and remote scenarios.
- [ ] Error tracking integrated with alerting.
- [ ] Dynamic inspection tools available for difficult bugs.
- [ ] Automation scripts/configs maintained.

Effective diagnostics reduce mean-time-to-resolution for Python issues.***
