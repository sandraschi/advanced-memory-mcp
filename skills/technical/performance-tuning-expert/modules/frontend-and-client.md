# Frontend & Client Optimization

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Google Web Vitals 2025, Chrome Aurora Program Updates (2025), iOS/macOS Instruments Performance Guide (2024), Android Perfetto Docs (2025)

---

## 1. Performance Budgets

- Define budgets for LCP, FID, INP, CLS, TTFB, bundle size, API latency.
- Track budgets in CI (Lighthouse CI, Calibre, SpeedCurve); fail builds on regressions.
- Communicate budgets with product/design to balance UX and performance.

---

## 2. Web Optimization

- Split bundles via code splitting and dynamic imports.
- Use HTTP/3, server push/103 Early Hints, CDN caching.
- Optimize images (responsive, AVIF/WebP, lazy loading).
- Preload critical assets, inline critical CSS, defer non-critical JS.
- Reduce render-blocking resources; use web workers for heavy computation.

---

## 3. Mobile/Desktop Apps

- Profile with Xcode Instruments, Android Profiler, Perfetto.
- Optimize rendering loops, reduce overdraw, avoid main-thread blocking.
- Cache data locally with TTL; ensure offline resilience.
- Monitor battery/network impact; use background tasks thoughtfully.

---

## 4. Network & API

- Minimize round trips (batch requests, GraphQL persisted queries).
- Compress payloads (brotli/gzip), use ETags/cache headers.
- Implement client-side retries with exponential backoff.
- Monitor CDN and edge performance; evaluate geolocation distribution.

---

## 5. Monitoring & Feedback

- Deploy Real User Monitoring (RUM) for Web Vitals; segment by device/network.
- Establish feedback loop with support/UX for qualitative insights.
- Run A/B tests to ensure improvements correlate with user satisfaction.

---

### Checklist
- [ ] Performance budgets defined and enforced via CI/RUM.
- [ ] Bundles optimized, critical rendering path minimized.
- [ ] Mobile clients profiled with platform tools; hotspots addressed.
- [ ] Network requests minimized and optimized.
- [ ] Real user metrics monitored with alerts and dashboards.

Fast client experiences drive retention—treat performance as a product feature.*** End Patch
