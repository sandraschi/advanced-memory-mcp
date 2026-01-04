# Refactoring Patterns

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Refactoring 3rd Edition (2024), Working Effectively with Legacy Code (2025 update), IDE Refactoring Tools Guides (2025)

---

## 1. Tactical Techniques

- **Extract Method/Class**: break down long functions/classes.
- **Introduce Parameter Object**: consolidate parameter lists.
- **Replace Conditional with Polymorphism**: use strategy pattern.
- **Encapsulate Field/Collection**: enforce invariants.
- **Move Method/Field**: align behavior with owning class.
- **Inline Variable/Method**: remove indirection.

Use IDE refactorings (PyCharm, IntelliJ, VSCode) for safety.

---

## 2. Legacy Code Rescue

- Establish seams using dependency injection or parameterization.
- Apply Sprout Method/Class to add features without altering legacy code.
- Use characterization tests before modification.
- Gradually migrate global state to injectable dependencies.

---

## 3. Modularization Patterns

- Extract package/module; create new namespace.
- Introduce anti-corruption layers when interfacing with legacy modules.
- Use strangler fig: route traffic to new module via feature flag or proxy.
- Break cycles with interface extraction or event-driven collaboration.

---

## 4. Data & Schema Refactoring

- Use expand-and-contract: add new fields/tables, migrate data, remove legacy.
- Employ database views or dual writes during transition.
- Maintain backward-compatible APIs until consumers updated.

---

## 5. Tooling

- Leverage automated refactoring tools (Rope for Python, Sourcery).
- Configure static analysis autofixes (ruff, eslint --fix).
- Use search-and-replace with AST tooling (codemods, LibCST, jscodeshift).

---

### Checklist
- [ ] Selected patterns documented with rationale.
- [ ] IDE/tooling configured for safe automated transformations.
- [ ] Characterization tests in place before large moves.
- [ ] Data/schema changes follow expand-contract.
- [ ] Refactoring steps captured for knowledge sharing.

Choosing the right pattern minimizes risk and accelerates delivery.***
