---
name: data-pipeline
description: Production data pipeline patterns — ETL/ELT design, orchestration with Airflow/Prefect, idempotency, incremental loads, and data quality
version: 1.0.0
tags: [data-engineering, etl, pipeline, airflow, python, analytics]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when building, reviewing, or debugging data pipelines, ETL jobs, or data orchestration workflows.

## Core Rules

- All pipelines must be **idempotent** — running twice gives the same result as running once
- Prefer **ELT over ETL** — load raw first, transform in the warehouse (cheaper to re-transform than re-extract)
- Always use **incremental loads** over full loads for tables > 100K rows
- Fail fast and loudly — a silent partial load is worse than a visible failure
- Test transformations with fixed fixtures, not prod data samples

## Idempotency Patterns

```python
# ❌ Non-idempotent — double run = double rows
def load_events(conn, events):
    for event in events:
        conn.execute("INSERT INTO events VALUES (?)", event)

# ✓ Idempotent — delete-then-insert by partition
def load_events(conn, events, date: str):
    conn.execute("DELETE FROM events WHERE date = ?", date)
    conn.executemany("INSERT INTO events VALUES (?)", events)

# ✓ UPSERT — idempotent by natural key
def upsert_users(conn, users):
    conn.executemany("""
        INSERT INTO users (id, email, name, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET
          email = excluded.email,
          name = excluded.name,
          updated_at = excluded.updated_at
    """, users)
```

## Incremental Load Pattern

```python
from datetime import datetime, timedelta

def get_last_watermark(conn, table: str) -> datetime:
    row = conn.execute(
        "SELECT MAX(watermark) FROM pipeline_state WHERE table_name = ?", table
    ).fetchone()
    return row[0] or datetime(2020, 1, 1)

def update_watermark(conn, table: str, watermark: datetime):
    conn.execute("""
        INSERT INTO pipeline_state (table_name, watermark)
        VALUES (?, ?)
        ON CONFLICT (table_name) DO UPDATE SET watermark = excluded.watermark
    """, (table, watermark))

def load_incremental(source_conn, dest_conn, table: str):
    last = get_last_watermark(dest_conn, table)
    new_watermark = datetime.utcnow()

    rows = source_conn.execute(
        f"SELECT * FROM {table} WHERE updated_at > ?", last
    ).fetchall()

    upsert_rows(dest_conn, table, rows)
    update_watermark(dest_conn, table, new_watermark)
```

## Airflow DAG Pattern

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
}

with DAG(
    dag_id='user_events_pipeline',
    default_args=default_args,
    schedule='0 */6 * * *',   # every 6 hours
    start_date=datetime(2024, 1, 1),
    catchup=False,             # don't backfill missed runs on first deploy
    tags=['events', 'incremental'],
) as dag:

    extract = PythonOperator(
        task_id='extract_events',
        python_callable=extract_events_from_source,
    )

    validate = PythonOperator(
        task_id='validate_events',
        python_callable=run_data_quality_checks,
    )

    load = PythonOperator(
        task_id='load_to_warehouse',
        python_callable=load_events_incremental,
    )

    extract >> validate >> load  # explicit dependency chain
```

## Data Quality Checks

```python
# Run these before loading to prod — fail the pipeline, not silently skip
def validate(df):
    checks = [
        (df['user_id'].notna().all(),        "user_id has nulls"),
        (df['event_time'].notna().all(),     "event_time has nulls"),
        (df['event_type'].isin(VALID_TYPES).all(), "unknown event_type values"),
        (len(df) > 0,                         "empty result — no events extracted"),
        ((df['amount'] >= 0).all(),           "negative amounts"),
    ]
    failures = [msg for passed, msg in checks if not passed]
    if failures:
        raise ValueError(f"Data quality failed: {', '.join(failures)}")
```

## Pipeline Monitoring

- Emit row counts at each stage — alert on drops > 20% vs same window last week
- Track pipeline duration — alert if > 2× historical average
- Dead-letter queue for rows that fail transformation — don't silently drop
- Log: extract_count, transform_count, load_count, rejected_count, duration_seconds
- Idempotency test: run pipeline twice on same data, result must be identical
