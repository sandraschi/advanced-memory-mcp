# Test Pyramid & Planning

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: Google Testing Blog (2025), ThoughtWorks Test Strategy Guides (2024), Martin Fowler Test Pyramid Updates (2024)

---

## 1. Test Portfolio Design

- **Unit tests**: fast, deterministic, isolate code units; target >70% critical path coverage.  
- **Component/integration tests**: validate service boundaries, contract tests.  
- **End-to-end tests**: cover user journeys; keep lean (<10% of suite).  
- **Exploratory testing**: manual or session-based to discover gaps.

---

## 2. Planning Process

- Map requirements to test types; create traceability matrix.  
- Identify high-risk features requiring additional scenarios.  
- Maintain test plans in living documentation (Confluence, Notion).

---

## 3. Shift-Left Practices

- Test-driven development (TDD) or behavior-driven development (BDD) where suitable.  
- Pair testers with developers during design to define acceptance criteria.  
- Use contract tests to prevent integration drift.

---

## 4. Test Data Management

- Generate synthetic data with tooling (Faker, Tonic).  
- Mask/anonymize production data for staging use.  
- Version test data sets; automate refresh.

---

## 5. Maintenance

- Regularly review test suites; prune obsolete tests.  
- Document ownership per suite to ensure accountability.  
- Establish test debt backlog (flaky, slow, redundant tests).

---

### Checklist
- [ ] Test pyramid tailored to product risk.  
- [ ] Requirements mapped to test types with traceability.  
- [ ] Shift-left practices adopted (TDD/BDD, contract tests).  
- [ ] Test data strategy in place.  
- [ ] Maintenance process for pruning and ownership defined.

A balanced test portfolio delivers fast feedback without sacrificing confidence.***

