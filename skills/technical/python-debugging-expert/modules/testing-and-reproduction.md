# Testing & Reproduction

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: pytest 8.1 Docs (2025), Hypothesis Property Testing Guide (2025), tox/uv Environment Management (2025), Docker Compose Debug Patterns (2024)

---

## 1. Reproduction Harness

- Create minimal failing test using pytest; isolate dependencies with `tox` or `uv run`.
- Use reproducible environments (Docker, virtualenv + requirements lock).
- Capture input fixtures (JSON, DB snapshots) for exact reproduction.

---

## 2. Property-Based Testing

- Leverage Hypothesis to generate edge cases; shrink failing examples automatically.
- Combine with custom strategies for domain-specific data.
- Use to guard against regressions that arise from unexpected inputs.

---

## 3. CI Integration

- Add failing test to CI pipeline; mark xfail with linked issue if fix pending.
- Ensure deterministic tests (set random seeds, avoid clock dependencies).
- Run slow or flaky tests in nightly jobs; track flake rate metrics.

---

## 4. Cross-Environment Verification

- Test on multiple Python versions (tox, nox).
- Validate on OS matrix (Linux, Windows, macOS) when bug may be platform-specific.
- For distributed systems, spin up dependent services with docker-compose or test containers.

---

## 5. Documentation

- Record reproduction steps, fixtures, and environment in issue tracker.
- Update README or CONTRIBUTING with debugging tips for the project.
- After fix, leave regression test with descriptive name referencing issue ID.

---

### Checklist
- [ ] Minimal reproduction established and version-controlled.
- [ ] Property-based or targeted tests prevent recurrence.
- [ ] CI pipeline enforces regression coverage.
- [ ] Multi-version/platform tests executed if relevant.
- [ ] Documentation updated with reproduction steps and resolution.

Reliable reproduction is the foundation of effective debugging.***
