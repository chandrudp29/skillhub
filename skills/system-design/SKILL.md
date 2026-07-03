---
name: system-design
description: Production system design — scalability patterns, trade-off analysis, database selection, caching strategy, API design, and architecture decisions
version: 1.0.0
tags: [system-design, architecture, scalability, distributed-systems, backend]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when designing new systems, reviewing architecture decisions, preparing for system design interviews, or evaluating trade-offs between approaches.

## Framework: RESDAC

Use this order for every system design problem:

1. **R**equirements — functional (what it does) vs non-functional (scale, latency, availability)
2. **E**stimations — DAU, QPS, storage, bandwidth. Back-of-envelope before any architecture
3. **S**torage — what data model, which database, why
4. **D**ata flow — how does data move through the system
5. **A**rchitecture — high-level components, then drill into bottlenecks
6. **C**onsistency — what CAP trade-offs, where eventual vs strong consistency

## Estimation Shortcuts

```
Traffic:
  1M DAU × 10 requests/day = 10M requests/day = ~120 QPS
  Peak = 3–5× average → 360–600 QPS

Storage:
  1 tweet = 140 chars + metadata ≈ 500 bytes
  500M tweets/day × 500 bytes = 250 GB/day
  250 GB × 365 = ~90 TB/year

Bandwidth:
  Read-heavy: 1B reads/day × 10 KB/read = 10 TB/day = ~1 GB/s
```

## Database Selection

| Need | Choice | Why |
|------|--------|-----|
| Transactions, relations | PostgreSQL | ACID, mature, great for most systems |
| High-write throughput | Cassandra | Wide-column, no joins, linear scale |
| Flexible schema | MongoDB | Document model, good for hierarchical data |
| Key-value, low latency | Redis | In-memory, microsecond reads |
| Full-text search | Elasticsearch | Inverted index, relevance ranking |
| Time-series | TimescaleDB / InfluxDB | Optimized for append-only time data |
| Graph relationships | Neo4j | Native graph traversal |

## Caching Strategy

```
Levels (fastest to slowest):
  L1: In-process (application memory) — microseconds, evicted on restart
  L2: Distributed cache (Redis) — sub-millisecond, survives restarts
  L3: CDN — geographic edge, for static/quasi-static content
  L4: Database cache (pgBouncer, read replicas) — database-level

Cache patterns:
  Cache-aside: App reads cache → miss → reads DB → writes cache
  Write-through: App writes cache AND DB simultaneously
  Write-behind: App writes cache → async write to DB (risk: data loss)
  Read-through: Cache handles DB reads transparently

TTL strategy: match TTL to data freshness requirements, not convenience
Cache invalidation: tag-based (preferred), time-based, event-based
```

## Scalability Patterns

```
Horizontal scaling:
  Stateless services → easy to scale, just add instances
  Stateful services → need session affinity or external state (Redis)

Database scaling:
  Read replicas → scale reads (most traffic is reads)
  Sharding → scale writes; shard key choice is critical
  CQRS → separate read/write models for very high scale

Async processing:
  Message queues (Kafka, SQS) for decoupling and buffering spikes
  Rule: if the user doesn't need an immediate result, make it async

Rate limiting:
  Token bucket (bursty traffic OK), sliding window (smooth), fixed window (simple)
  Apply at: API gateway > service > database

Circuit breaker:
  Closed → Open (on failure threshold) → Half-open (probe)
  Prevents cascade failures when downstream services fail
```

## API Design for Scale

- Cursor-based pagination over offset — offset breaks under concurrent inserts
- Idempotency keys for all mutation endpoints — safe to retry
- Versioning via URL path (`/v1/`) not headers — easier to cache, debug
- Async endpoints with `202 Accepted` + polling or webhooks for long operations

## CAP Trade-offs

```
Consistency + Partition tolerance (CP): strong consistency, may reject writes
  → Use for: banking, inventory, anything where stale = wrong

Availability + Partition tolerance (AP): always available, may serve stale data
  → Use for: social feeds, product catalogs, anything where stale = acceptable

Real-world: most systems are tunable; choose per data type, not per system
```

## Common Bottlenecks & Solutions

| Bottleneck | Signal | Fix |
|-----------|--------|-----|
| DB connection exhaustion | Latency spikes under load | Connection pool (pgBouncer) |
| Hot shard | One DB node at 100% CPU | Reshard with better key, or add range splitting |
| N+1 queries | Slow list endpoints | Eager loading, DataLoader pattern |
| Large payload | High bandwidth cost | Pagination, field selection, compression |
| Single point of failure | Any critical path with one instance | Add replica, health check, load balancer |
