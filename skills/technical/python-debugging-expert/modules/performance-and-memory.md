# Performance & Memory

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Python 3.13 Specialization Docs (2025), Scalene Profiler Paper (2024), tracemalloc Enhancements (2025), Memory Leak Detection with objgraph (2024)

---

## 1. CPU Profiling

- Use `scalene`, `py-spy`, `yappi`, or `cProfile` for CPU hotspots.
- Generate flamegraphs for visualization (`py-spy record -o flame.svg`).
- Benefit from Python 3.13 specialization—inspect bytecode with `dis` to ensure hot loops optimized.

---

## 2. Memory Analysis

- Track allocations with `tracemalloc` snapshots; compare before/after operations.
- Use `objgraph` to analyze reference cycles; integrate with `gc.collect()` for diagnosis.
- Detect leaks in long-running services by monitoring RSS via psutil/prometheus.

---

## 3. GC & Reference Cycles

- Understand generational GC thresholds; tune `gc.set_threshold`.
- Avoid reference cycles with `weakref` or context managers.
- For async applications, ensure tasks cleaned up (`task.cancel()` + await).

---

## 4. Native Extensions & CFFI

- Verify GIL release for CPU-bound C extensions.
- Check for reference leaks using `PYTHONMALLOC=debug` and `pytest --leak-check`.
- Use Valgrind or AddressSanitizer for native memory debugging.

---

## 5. Validation

- Add performance regression tests (pytest-benchmark).
- Monitor production metrics after fix (latency, memory usage).
- Document findings and update performance budgets.

---

### Checklist
- [ ] Profilers run and hotspots documented.
- [ ] Memory usage analyzed with tracemalloc/objgraph.
- [ ] GC settings reviewed and tuned if necessary.
- [ ] Native extension behavior verified.
- [ ] Regression tests and metrics confirm improvement.

Performance-aware debugging prevents recurrence of costly issues.***
