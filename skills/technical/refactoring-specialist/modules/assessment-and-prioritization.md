# Assessment & Prioritization

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: SEI Technical Debt Report (2025), CodeScene Behavioral Code Analysis (2024), Sonar Maintainability Metrics (2025)

---

## 1. Code Health Metrics

- Static analysis: cyclomatic complexity, maintainability index, duplication.  
- Behavioral metrics: hotspots (high churn + complexity), temporal coupling.  
- Test coverage: statement/branch coverage, mutation testing results.  
- Architecture metrics: dependency cycles, layer violations.

Use tools (SonarQube, CodeScene, CodeClimate) to gather baseline.

---

## 2. Debt Cataloging

- Identify code smells (long method, large class, feature envy, data clumps).  
- Document root causes and impacted stakeholders.  
- Categorize debt: controllable vs structural vs accidental.  
- Estimate remediation effort (story points, engineer-weeks).

---

## 3. Prioritization Framework

| Axis | Considerations |
| --- | --- |
| Impact | Customer value, developer productivity, defect reduction |
| Risk | Regression likelihood, coupling to critical systems |
| Effort | Size, dependencies, need for platform upgrades |
| Timing | Upcoming releases, team capacity |

Produce a matrix (High/Medium/Low) to guide roadmap.

---

## 4. Decision Records

- Create ADR or debt ticket per candidate with rationale and metrics.  
- Track status in debt board; assign owners and target dates.  
- Review backlog quarterly; drop stale items or reassess.

---

## 5. Metrics Tracking

- Monitor trends post-refactoring (complexity reduction, bug rate).  
- Report improvements to stakeholders (before/after metrics, ROI).  
- Feed metrics into engineering OKRs.

---

### Checklist
- [ ] Baseline metrics captured and documented.  
- [ ] Debt catalogue prioritized with impact/effort scoring.  
- [ ] Decision records created for chosen refactoring efforts.  
- [ ] Roadmap aligned with product/engineering leadership.  
- [ ] Metrics dashboard set up for ongoing tracking.

Prioritization ensures refactoring investments deliver measurable value.***

