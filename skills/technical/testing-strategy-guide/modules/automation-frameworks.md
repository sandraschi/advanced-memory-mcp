# Automation Frameworks

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Selenium/WebDriver BiDi (2025), Playwright 1.50 Docs (2025), Cypress Component Testing Guide (2025), pytest 8.1 Docs

---

## 1. Framework Selection

- UI: Playwright, Cypress, Selenium WebDriver BiDi.
- API: pytest + requests/httpx, Postman/newman, Karate.
- Mobile: Appium, Detox.
- Contract: Pact, Hoverfly.
- Choose based on language ecosystem, team skills, CI compatibility.

---

## 2. Architecture & Patterns

- Adopt page object/screenplay or component object pattern for UI tests.
- Modularize helpers and fixtures; avoid duplication.
- Use dependency injection for test data and services.
- Ensure tests stateless and parallelizable.

---

## 3. Infrastructure

- Containerize test runners; use Docker compose for environment parity.
- For UI tests, use cloud grids (BrowserStack, Sauce Labs) or Selenium Grid.
- Manage test environments via IaC, enabling ephemeral environments per PR.

---

## 4. Maintainability

- Enforce coding standards (linting) on test code.
- Track flake rate; quarantine flaky tests with auto-retry + ticket.
- Review automation code in pull requests just like production code.
- Provide onboarding docs and templates for new tests.

---

## 5. Data & Secrets

- Store credentials in vaults; inject via CI secrets.
- Reset data between tests; use fixtures for isolation.
- Use feature flags to expose test hooks safely.

---

### Checklist
- [ ] Frameworks selected with clear criteria; documented architecture.
- [ ] Automation codebase modular, maintainable, and linted.
- [ ] Test infrastructure automated and scalable.
- [ ] Flakiness monitored with suppression & fix process.
- [ ] Secrets/test data handled securely.

Well-architected automation prevents brittle suites and supports rapid feedback.***
