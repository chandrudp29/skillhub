---
name: api-design
description: Design REST APIs with consistent naming, error handling, versioning, and pagination. Use when designing a new API, reviewing an existing one, or writing an OpenAPI spec.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [api, rest, openapi, design, http, versioning]
triggers: ['api design', 'rest api', 'endpoint', 'routes', 'http api', 'openapi', 'swagger']
---

# API Design

Opinionated REST API design patterns. Consistent, predictable, easy to use.

## When to Use

- Designing a new REST API
- Reviewing an API for consistency issues
- Writing OpenAPI/Swagger documentation
- Deciding on URL structure, verbs, or error formats

## URL Design

**Resources are nouns, actions are HTTP verbs:**

```
# Good
GET    /users                 — list users
POST   /users                 — create user
GET    /users/{id}            — get user
PUT    /users/{id}            — replace user (full update)
PATCH  /users/{id}            — update user (partial)
DELETE /users/{id}            — delete user

GET    /users/{id}/orders     — list this user's orders
POST   /users/{id}/orders     — create order for this user

# Bad — verbs in URLs
POST   /createUser
GET    /getUser?id=123
POST   /users/delete
```

**Naming:**
- Plural for collections: `/users`, `/orders`, `/products`
- kebab-case for multi-word: `/user-profiles`, not `/userProfiles` or `/user_profiles`
- Lowercase always
- No trailing slashes: `/users` not `/users/`

**Nested resources — max 2 levels deep:**
```
/orders/{id}/items           ← fine
/users/{id}/orders/{id}/items/tags  ← too deep, use /items/{id}/tags
```

## HTTP Status Codes

Use exactly the right code — not just 200 and 500:

```
200 OK              — GET/PUT/PATCH succeeded
201 Created         — POST created a resource (include Location header)
204 No Content      — DELETE succeeded, nothing to return
400 Bad Request     — invalid request body/params (include what's wrong)
401 Unauthorized    — not authenticated (missing/invalid token)
403 Forbidden       — authenticated but not authorized
404 Not Found       — resource doesn't exist
409 Conflict        — would violate a constraint (duplicate email, etc.)
422 Unprocessable   — valid JSON but failed business validation
429 Too Many Requests — rate limited (include Retry-After header)
500 Internal Error  — your bug (never leak internals)
```

## Consistent Error Format

Pick one format. Stick to it everywhere.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      },
      {
        "field": "age",
        "message": "Must be 18 or older"
      }
    ]
  }
}
```

Rules:
- Always machine-readable `code` (SCREAMING_SNAKE_CASE)
- Human-readable `message` (not for parsing)
- `details` for field-level errors
- Never expose stack traces, SQL, or internal paths

## Pagination

Use cursor-based for large/real-time datasets, offset-based for small/static ones.

**Cursor-based (recommended):**
```json
GET /jobs?limit=20&cursor=eyJpZCI6MTAwfQ==

{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIwfQ==",
    "has_more": true,
    "limit": 20
  }
}
```

**Offset-based (simple datasets):**
```json
GET /skills?page=2&per_page=20

{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

## Versioning

Version in the URL prefix: `/v1/`, `/v2/`

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

Rules:
- v1 and v2 can coexist (never break existing integrations)
- Major version bump only for breaking changes
- Deprecate with a `Sunset` response header: `Sunset: Sat, 01 Jan 2027 00:00:00 GMT`
- Keep old versions alive ≥6 months after deprecation announcement

## Request/Response Conventions

**Dates**: always ISO 8601 in UTC: `"2026-06-30T09:00:00Z"`

**IDs**: use strings, not integers in JSON (JavaScript loses precision on large ints)
```json
{"id": "1234567890123456789"}  ← safe
{"id": 1234567890123456789}    ← dangerous in JS
```

**Boolean fields**: prefix with `is_`, `has_`, `can_`: `is_active`, `has_subscription`

**Filtering**: use query params for filtering, sorting, field selection:
```
GET /jobs?status=active&location=bangalore&sort=-created_at&fields=id,title,company
```

## OpenAPI Documentation

Document every endpoint before building it (API-first design):

```yaml
/users/{id}:
  get:
    summary: Get user by ID
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string
    responses:
      '200':
        description: User found
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      '404':
        description: User not found
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
```

## Security Checklist

- [ ] All endpoints that return or modify data require authentication
- [ ] Authorization checked on every request (not just at login)
- [ ] Rate limiting on all public endpoints
- [ ] Request size limits enforced (no unlimited file uploads)
- [ ] HTTPS only — redirect HTTP to HTTPS
- [ ] CORS configured explicitly (not `*` in production)
