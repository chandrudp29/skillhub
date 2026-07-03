---
name: performance-optimizer
description: Systematic performance profiling and optimization for Python and web backends — measure first, fix second, verify the fix
version: 1.0.0
tags: [performance, profiling, optimization, python, backend, latency]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when a system is slow, costs too much, or fails under load. Always measure before optimizing — guessing wastes time.

## Core Rules

- **Measure first, always.** Never optimize without a profiler or benchmark showing the bottleneck
- Fix the biggest bottleneck first — fixing #2 before #1 gives partial gains at best
- Define a target before optimizing: "p99 < 200ms" not "faster"
- After every optimization, re-measure — sometimes fixes have side effects

## The Loop

```
1. Measure    → profiler, APM, benchmark (establish baseline)
2. Identify   → find the hot path (usually 1-3 functions cause 80%+ of time)
3. Hypothesize → why is this slow? (N+1 query, GIL contention, memory copy, etc.)
4. Fix        → smallest change that addresses root cause
5. Verify     → re-run benchmark — is it faster? Regressions elsewhere?
6. Repeat     → next bottleneck
```

## Python Profiling

```python
# cProfile — CPU profiling
import cProfile, pstats, io
pr = cProfile.Profile()
pr.enable()
# ... code to profile ...
pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(20)
print(s.getvalue())

# line_profiler — line-by-line (use @profile decorator)
# pip install line_profiler
# kernprof -l -v script.py

# memory_profiler — memory usage line-by-line
# pip install memory_profiler
# @profile decorator, then: python -m memory_profiler script.py

# py-spy — sampling profiler, zero-code-change, attach to running process
# pip install py-spy
# py-spy top --pid 12345
# py-spy record -o profile.svg --pid 12345
```

## Common Python Bottlenecks

```python
# ❌ String concatenation in loop — O(n²) allocations
result = ""
for item in items:
    result += str(item)  # new string object each time

# ✓ join — one allocation
result = "".join(str(item) for item in items)

# ❌ Repeated dict/set lookup in hot loop
for item in items:
    if item in some_list:  # O(n) each time if it's a list
        ...

# ✓ Convert to set once
lookup = set(some_list)  # O(1) lookup
for item in items:
    if item in lookup:
        ...

# ❌ Unnecessary object creation in loop
for i in range(1_000_000):
    temp = MyClass(i)  # constructor overhead × 1M

# ✓ Reuse or use slots
class MyClass:
    __slots__ = ['value']  # ~40% less memory, faster attribute access

# ❌ GIL-bound CPU work in threads
from threading import Thread  # threads share GIL — no real parallelism for CPU

# ✓ Use ProcessPoolExecutor for CPU-bound work
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as pool:
    results = list(pool.map(cpu_intensive_fn, items))
```

## Database Performance

```python
# ❌ N+1 query — 1 query for list + N queries for each item's relation
users = User.query.all()
for user in users:
    print(user.orders)  # each user.orders fires a new query

# ✓ Eager loading
users = User.query.options(joinedload(User.orders)).all()

# ✓ Bulk operations
# Instead of: for item in items: db.add(item)
db.bulk_insert_mappings(Item, [{'name': x} for x in items])

# EXPLAIN ANALYZE before adding indexes
# Check: Seq Scan on large table = missing index
# Check: high cost in nested loop = bad join condition

# Index selectively — write penalty for every index
# Composite index column order: most selective column first
# Partial indexes for filtered queries:
# CREATE INDEX idx_active_users ON users(email) WHERE active = true;
```

## Web API Performance

```
Latency budget for p99 < 200ms:
  Network (client → server):  ~20ms
  Auth/middleware:             ~5ms
  Business logic:              ~10ms
  Database queries:            ~100ms  ← usually the bottleneck
  Serialization:               ~5ms
  Network (server → client):  ~20ms

Tools:
  wrk / hey / k6 — load testing
  py-spy / cProfile — Python profiling
  EXPLAIN ANALYZE — PostgreSQL query plans
  DataDog / Grafana / New Relic — production APM
```

## Quick Wins Checklist

- [ ] Add indexes on all foreign keys and frequently filtered columns
- [ ] Enable connection pooling (pgBouncer for Postgres)
- [ ] Cache expensive, rarely-changing reads in Redis
- [ ] Use `select_related` / `prefetch_related` (Django) or `joinedload` (SQLAlchemy)
- [ ] Paginate all list endpoints — never return unbounded results
- [ ] Move heavy work (emails, webhooks, reports) to async workers
- [ ] Enable HTTP/2 and gzip compression at the load balancer
