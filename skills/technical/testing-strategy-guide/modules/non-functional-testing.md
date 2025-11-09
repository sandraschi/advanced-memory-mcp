# Non-Functional Testing

**Confidence**: 🟡 Medium  
**Last validated**: 2025-11-08  
**Primary sources**: k6 Performance Testing Handbook (2024), OWASP ASVS NFR Section, Google Accessibility Guidelines (2025), AWS FIS Chaos Testing Docs (2025)

---

## 1. Performance & Load

- Define SLAs/SLOs; design load, stress, soak, and spike tests.  
- Tools: k6, Gatling, Locust, JMeter.  
- Automate with CI for critical endpoints; store results in dashboards.  
- Include capacity planning and cost analysis in findings.

---

## 2. Security Testing

- Integrate security scans (SAST/DAST/IAST) into pipeline.  
- Run penetration tests or red teaming annually/after major releases.  
- Use dependency vulnerability scanning and container image scanning.

---

## 3. Accessibility

- Adopt WCAG 2.2 AA compliance.  
- Tools: axe-core, Lighthouse, Pa11y; augment with manual audits.  
- Include accessibility checks in CI; provide remediation backlog.

---

## 4. Resilience & Chaos

- Inject failures via chaos engineering (Gremlin, Litmus, AWS FIS).  
- Verify fallback behavior, retries, auto-healing.  
- Document learnings and update runbooks.

---

## 5. Internationalization & Localization

- Test with varied locales/timezones/charsets.  
- Validate right-to-left layouts, currency formats.  
- Automate locale smoke tests.

---

### Checklist
- [ ] Performance tests aligned with SLOs and automated.  
- [ ] Security testing integrated (automation + manual).  
- [ ] Accessibility audits scheduled with CI checks.  
- [ ] Chaos/resilience experiments planned and executed.  
- [ ] Localization scenarios covered for supported locales.

Non-functional testing protects user experience and reliability beyond basic functionality.***

