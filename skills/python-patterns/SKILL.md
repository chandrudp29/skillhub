---
name: python-patterns
description: Python best practices — type hints, async/await, dataclasses, error handling, and performance patterns. Use when writing new Python code, reviewing Python, or modernizing legacy code.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [python, async, type-hints, patterns, performance, best-practices]
triggers: ['python', 'best practices', 'type hints', 'dataclass', 'async python', 'pythonic']
---

# Python Patterns

Modern Python (3.10+) patterns for production code. Specific, opinionated, actionable.

## When to Use

- Writing new Python modules or services
- Reviewing Python code for quality
- Modernizing Python 2-era or early Python 3 code
- Debugging subtle Python behavior

## Type Hints

Always type hint public functions. It's documentation that tools can check.

```python
# Good — clear what goes in and what comes out
def chunk_text(text: str, max_tokens: int = 512) -> list[str]:
    ...

# Good — complex types use type aliases
from typing import TypeAlias
JsonDict: TypeAlias = dict[str, "JsonValue"]
JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | JsonDict

# Good — use | for unions (Python 3.10+), not Optional
def find_user(user_id: int) -> User | None:
    ...

# Good — use dataclass for structured data, not plain dicts
from dataclasses import dataclass, field

@dataclass
class EmbeddingResult:
    text: str
    vector: list[float]
    model: str
    token_count: int
    metadata: dict[str, str] = field(default_factory=dict)
```

## Async Patterns

Use async for I/O-bound work. Don't use it for CPU-bound work.

```python
import asyncio
import httpx

# Good — concurrent I/O with asyncio.gather
async def fetch_all(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    return [r.json() for r in responses if not isinstance(r, Exception)]

# Good — async context manager for resource cleanup
class DatabasePool:
    async def __aenter__(self):
        self._conn = await connect()
        return self._conn

    async def __aexit__(self, *args):
        await self._conn.close()

# Good — async generator for streaming
async def stream_llm_response(prompt: str):
    async with client.stream("POST", "/completions", json={"prompt": prompt}) as r:
        async for chunk in r.aiter_lines():
            if chunk:
                yield chunk

# BAD — blocking I/O in async code
async def bad_example():
    import requests
    result = requests.get(url)  # blocks the event loop for everyone
```

## Error Handling

Be specific. Catch the error you expect, not `Exception`.

```python
# Good — specific exceptions with context
from contextlib import contextmanager

@contextmanager
def db_transaction(conn):
    try:
        yield conn
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Constraint violation: {e}") from e
    except Exception:
        conn.rollback()
        raise

# Good — custom exceptions for domain errors
class EmbeddingError(Exception):
    """Raised when embedding generation fails."""

class TokenLimitError(EmbeddingError):
    def __init__(self, text_length: int, limit: int):
        super().__init__(f"Text too long: {text_length} tokens, limit is {limit}")
        self.text_length = text_length
        self.limit = limit

# BAD — swallowing exceptions
try:
    result = process(data)
except Exception:
    pass  # never do this

# BAD — catching Exception for expected errors
try:
    result = int(user_input)
except Exception:  # should be ValueError
    result = 0
```

## Dataclasses and Pydantic

Use `dataclass` for internal data structures. Use `pydantic.BaseModel` for API boundaries (validation + serialization).

```python
# Internal data — dataclass
@dataclass(frozen=True)  # frozen = immutable = safe to share
class ChunkMetadata:
    source: str
    page: int
    chunk_index: int

# API boundary — Pydantic
from pydantic import BaseModel, Field, validator

class IngestRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100_000)
    source: str = Field(..., pattern=r"^[a-z0-9-]+$")
    chunk_size: int = Field(default=512, ge=64, le=2048)

    @validator("text")
    def text_must_not_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("text must not be empty or whitespace only")
        return v
```

## Performance Patterns

```python
# Use generators for large sequences — don't build the whole list in memory
def read_chunks(filepath: str, size: int = 8192):
    with open(filepath, "rb") as f:
        while chunk := f.read(size):
            yield chunk

# Use sets for membership testing — O(1) not O(n)
VALID_MODELS = {"gpt-4o", "claude-sonnet-4-6", "gemini-1.5-pro"}
if model_name not in VALID_MODELS:  # set lookup, not list scan
    raise ValueError(f"Unknown model: {model_name}")

# Use lru_cache for pure functions called repeatedly with same args
from functools import lru_cache

@lru_cache(maxsize=1024)
def get_tokenizer(model_name: str):  # expensive to init, cheap to cache
    return AutoTokenizer.from_pretrained(model_name)

# Prefer list comprehensions over map/filter for readability
scores = [score_document(doc) for doc in documents if doc.is_valid]

# Use walrus operator for combined check + assign
if (match := PATTERN.search(text)) is not None:
    process(match.group(1))
```

## Module Structure

```
mypackage/
├── __init__.py          # public API only — re-export from submodules
├── models.py            # dataclasses, Pydantic models
├── exceptions.py        # custom exception classes
├── config.py            # settings (use pydantic-settings)
└── core/
    ├── __init__.py
    ├── embedder.py
    └── retriever.py
```

`__init__.py` should only re-export what external callers need:
```python
# __init__.py
from .core.embedder import Embedder
from .core.retriever import Retriever
from .models import EmbeddingResult, SearchResult
__all__ = ["Embedder", "Retriever", "EmbeddingResult", "SearchResult"]
```
