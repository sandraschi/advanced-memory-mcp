# Profiling & Metrics

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Google SRE Book (2024), eBPF Observability Guide (2025), Chrome Web Vitals Docs (2025), Flamegraph Techniques (2024)

---

## 1. Observability Baseline

- Ensure golden signals (latency, traffic, errors, saturation) available per service.
- Enable tracing (OpenTelemetry) with sampling strategies suited to traffic volume.
- Capture business KPIs (conversion, throughput) to tie optimizations to outcomes.

---

## 2. Profiling Toolchain

| Language | Tools |
| --- | --- |
| JVM | JFR, async-profiler, YourKit, Java Mission Control |
| Python | Py-spy, scalene, cProfile, line-profiler |
| Node.js | Clinic.js, V8 CPU/heap profiler, 0x |
| Go | pprof (CPU/mem/block), go tool trace |
| Native | perf, VTune, Instruments, eBPF |

Collect flamegraphs and call stacks under realistic load.

---

## 3. Benchmarking

- Build representative workloads (wrk, k6, Locust, Gatling).
- Separate microbenchmarks (function level) from macro/system benchmarks.
- Control environment variables (CPU governor, turbo boost, network).
- Repeat runs to account for variance; report median/p95.

---

## 4. Data Analysis

- Look for hotspots consuming majority CPU/wall time.
- Identify memory churn, GC pauses, lock contention, I/O waits.
- Correlate with system metrics (CPU steal, disk latency).
- Track regressions in dashboards; implement anomaly detection.

---

## 5. Documentation

- Store profiling artifacts with timestamp, code version, environment.
- Create runbooks describing how to reproduce profiling sessions.
- Share insights via technical reports or Notion/Confluence pages.

---

### Checklist
- [ ] Observability and tracing capture necessary detail.
- [ ] Profiling tools configured per runtime with reproducible steps.
- [ ] Benchmarks defined, automated, and version-controlled.
- [ ] Analysis documented with prioritized hotspots.
- [ ] Monitoring dashboards alert on performance regressions.

Instrument first; profiling without visibility wastes time.*** End Patch
