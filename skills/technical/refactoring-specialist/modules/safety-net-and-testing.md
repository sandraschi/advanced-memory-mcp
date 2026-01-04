# Safety Net & Testing

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Working Effectively with Legacy Code (2025 update), pytest 8.1 Docs (2025), Approval Tests Guide (2024), Mutation Testing Reports (2024)

---

## 1. Characterization Tests

- Capture existing behavior using golden files, approval tests, snapshot testing.
- Avoid assertions on internals; focus on observable outputs.
- Build minimal harness around legacy seams to facilitate extraction.

---

## 2. Coverage Strategy

- Measure coverage (statement, branch); target critical modules first.
- Apply mutation testing (Mutmut, cosmic-ray) to ensure tests detect changes.
- Use test impact analysis to run relevant suites quickly.

---

## 3. Tooling

- pytest + fixtures for readability; parametrize edge cases.
- Use tox/nox or uv for reproducible environments.
- Integrate static analysis (ruff, mypy) to catch issues early.
- Apply continuous testing on feature branches.

---

## 4. Automation & CI

- Enforce green build before refactoring merges.
- Run smoke tests in CI after each incremental change.
- Add canary releases or feature flags when refactoring critical paths.

---

## 5. Documentation

- Maintain test catalog with coverage gaps, reliability scores.
- Record new seams created during refactoring for future work.
- Share tips/fixtures in wiki for team reuse.

---

### Checklist
- [ ] Characterization tests in place for areas under change.
- [ ] Coverage and mutation metrics monitored.
- [ ] CI enforces safety net on every refactoring slice.
- [ ] Tooling documentation updated for contributors.
- [ ] Test asset catalog maintained.

Strong safety nets enable fearless refactoring.***
