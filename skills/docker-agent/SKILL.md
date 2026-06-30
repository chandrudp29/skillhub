---
name: docker-agent
description: Write optimized Dockerfiles, docker-compose configs, and debug container issues. Use when containerizing an app, fixing a broken container, or designing a multi-service local environment.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [docker, containers, dockerfile, docker-compose, devops]
---

# Docker Agent

Production-ready Dockerfiles and compose configs. Fixes common container problems fast.

## When to Use

- "Write a Dockerfile for my Python/Node/Go app"
- "My container won't start"
- "Set up docker-compose for my local dev environment"
- "My image is 2GB — help me reduce it"

## Python Dockerfile (production-ready)

```dockerfile
# Build stage — install dependencies separately for cache efficiency
FROM python:3.12-slim AS builder
WORKDIR /build

# Install build deps first (changes rarely — cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage — clean image without build tools
FROM python:3.12-slim AS runtime
WORKDIR /app

# Non-root user for security
RUN useradd --create-home appuser
USER appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy app code last (changes most often — cache invalidated last)
COPY --chown=appuser:appuser . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Node.js Dockerfile

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /build
COPY package*.json .
RUN npm ci --only=production

FROM node:20-alpine AS runtime
WORKDIR /app
RUN adduser -D appuser
USER appuser
COPY --from=builder /build/node_modules ./node_modules
COPY --chown=appuser:appuser . .
EXPOSE 3000
CMD ["node", "server.js"]
```

## docker-compose for Local Dev

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app          # hot reload in dev
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Reducing Image Size

1. **Use slim/alpine base images**: `python:3.12-slim` (150MB) vs `python:3.12` (1GB)
2. **Multi-stage builds**: compile in builder, copy artifacts to clean runtime
3. **Combine RUN commands**: each RUN is a layer
4. **Use .dockerignore**: exclude `node_modules/`, `.git/`, `__pycache__/`, `*.pyc`, `tests/`

```
# .dockerignore
.git
.gitignore
__pycache__
*.pyc
*.pyo
.env
.venv
node_modules
tests/
*.md
Dockerfile*
docker-compose*
```

4. **Don't install dev dependencies in production image**:
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt  # not requirements-dev.txt
```

## Debugging Container Issues

```bash
# Container won't start — check logs
docker logs <container_name> --tail 50

# Container exits immediately — run interactively to debug
docker run -it --entrypoint /bin/sh myimage

# Check what's inside a running container
docker exec -it <container_name> /bin/sh

# Inspect environment variables
docker exec <container_name> env

# Check network connectivity between services
docker exec <api_container> curl http://db:5432

# Check if healthcheck is passing
docker inspect <container_name> | jq '.[0].State.Health'

# Rebuild without cache (when a dependency changed)
docker-compose build --no-cache api
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running as root | Add `RUN useradd appuser && USER appuser` |
| COPY . . before installing deps | Copy requirements.txt first, install, then COPY . . |
| Hardcoded secrets in Dockerfile | Use `--build-arg` or `--secret` (BuildKit) |
| No .dockerignore | Always add one — node_modules alone adds hundreds of MB |
| `CMD python app.py` | Use `CMD ["python", "app.py"]` (exec form — proper signal handling) |
| Port exposed but not published | `EXPOSE` documents; `-p 8000:8000` publishes |

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

Or in compose:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # grace period on startup
```
