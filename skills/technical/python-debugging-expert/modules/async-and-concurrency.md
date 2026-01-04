# Async & Concurrency

**Confidence**: 🟡 Medium
**Last validated**: 2025-11-08
**Primary sources**: Python 3.13 Asyncio Docs (2025), Trio/Nursery Patterns (2024), multiprocessing/futures Guide (2025), diagnosing deadlocks blog posts.

---

## 1. Asyncio Debugging

- Enable debug mode: `PYTHONASYNCIODEBUG=1`, `loop.set_debug(True)`.
- Use `asyncio.get_running_loop().slow_callback_duration` to detect slow coroutines.
- Inspect task traces with `asyncio.Task.print_stack()` or `asyncio.all_tasks()`.
- Monitor un-awaited coroutines warnings and resource tracker logs.

---

## 2. Concurrency Patterns

- For CPU-bound tasks, use multiprocessing or native extensions; avoid blocking event loop.
- Use `concurrent.futures` thread/process pools with proper shutdown.
- Apply synchronization primitives (`Lock`, `Semaphore`, `Event`) carefully to prevent deadlocks.

---

## 3. Deadlock & Race Detection

- Reproduce with deterministic schedulers (Trio, AnyIO) where possible.
- Insert logging around lock acquisition/release.
- Use `faulthandler.dump_traceback_later()` to capture hung threads.
- For multiprocessing, inspect child process logs and exit codes.

---

## 4. Networking & Timeouts

- Always set timeouts on I/O operations; use `asyncio.wait_for` as guard.
- Implement retries with exponential backoff.
- Monitor connection pools (httpx, aiohttp) for resource leaks.

---

## 5. Testing

- Use `pytest-asyncio`, `pytest-trio` for async tests.
- Add stress tests simulating concurrency load.
- Leverage hypothesis for race condition discovery.

---

### Checklist
- [ ] Async debug mode enabled for investigation.
- [ ] Blocking operations identified and offloaded appropriately.
- [ ] Deadlock/race detection runbooks followed.
- [ ] Timeouts/retries enforced on external calls.
- [ ] Async tests cover concurrency scenarios.

Stable async code requires vigilant debugging practices.*** End Patch*** End Patch
