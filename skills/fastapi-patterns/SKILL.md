---
name: fastapi-patterns
description: FastAPI production patterns — routing, dependency injection, background tasks, streaming, error handling, and async. Use when building or reviewing a FastAPI service.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [fastapi, python, api, async, pydantic, rest, streaming]
---

# FastAPI Patterns

Production FastAPI patterns. Covers the 20% of FastAPI that handles 80% of real use cases.

## When to Use

- Building a new FastAPI service
- Reviewing FastAPI code for quality or performance issues
- Adding auth, background tasks, or streaming to an existing service
- Debugging FastAPI errors you don't understand

## Project Structure

```
app/
├── main.py              # create_app(), lifespan
├── config.py            # Settings (pydantic-settings)
├── dependencies.py      # Shared dependencies (DB, auth)
├── routers/
│   ├── jobs.py
│   └── users.py
└── models/
    ├── requests.py      # Pydantic request models
    └── responses.py     # Pydantic response models
```

## App Setup with Lifespan

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB pools, load models, etc.
    app.state.db = await create_db_pool()
    app.state.model = load_ml_model()
    yield
    # Shutdown: cleanup
    await app.state.db.close()

app = FastAPI(title="My API", lifespan=lifespan)
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(users.router, prefix="/users", tags=["users"])
```

## Dependency Injection

FastAPI's `Depends` is the right way to share DB connections, auth, and config:

```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_db(request: Request) -> AsyncGenerator:
    async with request.app.state.db.acquire() as conn:
        yield conn  # connection returned to pool after request

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db),
) -> User:
    token = credentials.credentials
    user = await verify_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# routers/jobs.py — inject where needed
@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await db.fetch_jobs(user_id=current_user.id, limit=limit)
```

## Request/Response Models

```python
# models/requests.py
from pydantic import BaseModel, Field

class CreateJobRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    tags: list[str] = Field(default_factory=list, max_items=10)

# models/responses.py
from datetime import datetime

class JobResponse(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}  # allows ORM objects
```

## Streaming Responses

For LLM output, large file downloads, or real-time events:

```python
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    async def generate():
        async for chunk in llm.astream(request.messages):
            # Server-Sent Events format
            yield f"data: {chunk.content}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disables nginx buffering
        },
    )
```

## Background Tasks

For work that can happen after the response is sent:

```python
from fastapi import BackgroundTasks

@router.post("/ingest", status_code=202)
async def ingest_document(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    job_id = await create_job_record(current_user.id, request)
    background_tasks.add_task(process_document, job_id, request.url)
    return {"job_id": job_id, "status": "processing"}
```

For heavy work (minutes, not seconds) — use Celery or ARQ instead, not BackgroundTasks.

## Error Handling

Global exception handlers instead of try/except everywhere:

```python
# main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "validation_error"},
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.error("Unhandled error", exc_info=exc, extra={"path": request.url.path})
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},  # don't leak internals
    )
```

## Middleware

```python
import time

@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}s"
    return response
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Blocking I/O in async route | Use `asyncio.to_thread()` or an async library |
| Creating DB connection per request (no pool) | Use connection pool via `Depends` |
| Returning ORM objects directly | Always use Pydantic response models |
| No request size limit on uploads | Add `content_length` check in middleware |
| Secrets in `Settings` defaults | Use `pydantic-settings` with env var required, no default |
