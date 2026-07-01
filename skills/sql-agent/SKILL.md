---
name: sql-agent
description: Write, optimize, and explain SQL queries. Use when user needs to write a query, debug slow SQL, understand a query plan, or design a schema.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [sql, database, postgres, performance, schema]
triggers: ['sql', 'query', 'database', 'optimize query', 'write sql', 'postgres', 'mysql']
---

# SQL Agent

Writes correct, performant SQL and explains what it does. Works with PostgreSQL, MySQL, SQLite, and BigQuery.

## When to Use

- "Write a query to get X"
- "This query is slow — help me optimize it"
- "What does this query plan mean?"
- "Design a schema for X"
- "How do I join these tables?"

## Writing Queries

### Step 1 — Clarify before writing

Ask if not obvious:
- What database? (PostgreSQL, MySQL, SQLite, BigQuery — syntax differs)
- Approximate row counts? (matters for optimization)
- What's the expected output format?
- Are there existing indexes?

### Step 2 — Write the query with explanation

Always provide:
1. The query itself
2. A plain-English explanation of what it does
3. What indexes it will use (or should have)

Format:
```sql
-- Gets the top 10 customers by revenue in the last 30 days
-- Uses: idx_orders_customer_id, idx_orders_created_at
SELECT 
    c.id,
    c.name,
    SUM(o.total_amount) AS revenue_30d
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE o.created_at >= NOW() - INTERVAL '30 days'
  AND o.status = 'completed'
GROUP BY c.id, c.name
ORDER BY revenue_30d DESC
LIMIT 10;
```

### Step 3 — Check for common problems

Before finalizing any query:

**N+1 patterns**: Is this query inside a loop? Rewrite to fetch in batch.

**SELECT \***: Specify columns. SELECT * on wide tables fetches data never used.

**Missing WHERE clause on updates/deletes**: Catastrophic. Always confirm the WHERE clause is intentional.

**Implicit type coercion**: `WHERE id = '123'` vs `WHERE id = 123` — coercion kills index usage.

**NULL behavior**: `NULL != NULL` in SQL. `WHERE col != 'value'` excludes NULLs. Use `IS NULL` / `IS NOT NULL` explicitly.

## Optimizing Slow Queries

### Step 1 — Get the query plan

```sql
EXPLAIN ANALYZE [your query here];
```

Key things to look for:
- **Seq Scan** on a large table = missing index
- **Hash Join** on large tables = may need index on join key
- **Nested Loop** with high estimated rows = investigate
- **actual rows >> estimated rows** = stale statistics, run `ANALYZE table_name`

### Step 2 — Common optimizations

**Add the right index**
```sql
-- Covers the common query pattern: WHERE status = ? ORDER BY created_at DESC
CREATE INDEX CONCURRENTLY idx_orders_status_created 
ON orders (status, created_at DESC);
```

**Rewrite correlated subqueries as JOINs**
```sql
-- Slow (correlated subquery runs once per row)
SELECT name, (SELECT COUNT(*) FROM orders WHERE customer_id = c.id) 
FROM customers c;

-- Fast (single pass)
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;
```

**Use CTEs for readability, window functions for efficiency**
```sql
-- Running total without subquery per row
SELECT 
    id,
    amount,
    SUM(amount) OVER (ORDER BY created_at) AS running_total
FROM payments;
```

## Schema Design Principles

1. **Normalize to 3NF** unless you have a specific denormalization reason
2. **Primary keys**: use `BIGINT` or `UUID` — never a natural key (email, username change)
3. **Timestamps**: always store in UTC; include both `created_at` and `updated_at`
4. **Soft deletes**: prefer `deleted_at TIMESTAMP NULL` over actually deleting rows
5. **Foreign keys**: declare them — the DB enforces integrity you can't always enforce in code
6. **Enum columns**: use a `CHECK` constraint or a lookup table, not magic strings

## Safety Rules

Never write or run `UPDATE` or `DELETE` without a `WHERE` clause. Always.

For bulk updates in production: use `LIMIT` and batch — never update 10M rows in a single transaction.

For schema changes in production: use `CREATE INDEX CONCURRENTLY` to avoid locking.
