---
name: code-reviewer
description: Structured code review across five axes — correctness, security, performance, maintainability, and test coverage. Use when user asks to review code, check a PR, or audit a diff.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [code-review, security, quality, testing, pull-request]
triggers: ['review', 'code review', 'pr review', 'check code', 'audit code', 'review this']
---

# Code Reviewer

Five-axis structured code review. Finds what matters, ignores what doesn't, and produces actionable feedback — not a style lecture.

## When to Use

- "Review this code"
- "Check my PR"
- "Is this safe to merge?"
- "What could go wrong here?"
- Before merging any non-trivial change

## The Five Axes

Review in this order. Stop at critical findings — don't bury them.

### Axis 1 — Correctness

Does the code do what it claims?

- Does it handle the happy path correctly?
- What about empty inputs, null values, zero, negative numbers?
- Are there off-by-one errors in loops/slices?
- Are async operations awaited correctly?
- Are there race conditions if called concurrently?
- Do error paths clean up resources (files, connections, locks)?

**Severity**: Any correctness bug is at minimum MEDIUM. Incorrect behavior in production = CRITICAL.

### Axis 2 — Security

Does the code introduce vulnerabilities?

Checklist:
- [ ] SQL/NoSQL injection (string concatenation in queries)
- [ ] Command injection (user input in shell commands)
- [ ] Path traversal (user-controlled file paths)
- [ ] XSS (unsanitized user content rendered as HTML)
- [ ] Secrets in code (API keys, passwords, tokens hardcoded)
- [ ] Insecure deserialization (pickle, eval, exec on user data)
- [ ] Authentication bypass (missing auth checks on routes)
- [ ] Overly permissive CORS or CSP
- [ ] Sensitive data in logs

**Severity**: Any security finding is CRITICAL or HIGH. Flag immediately, don't bury in a list.

### Axis 3 — Performance

Will this code be fast enough at scale?

- N+1 queries (DB query inside a loop)
- Missing database indexes for the query pattern
- Blocking I/O in async code
- Unnecessary data fetching (SELECT * when 2 columns needed)
- Memory leaks (event listeners not removed, caches unbounded)
- Expensive operations in hot paths (JSON parse per request, etc.)

Only flag if the code will actually run at meaningful scale. Don't micro-optimize cold paths.

### Axis 4 — Maintainability

Will the next engineer understand this?

- Is the logic expressed clearly, or does it require decoding?
- Are variable and function names accurate?
- Is complexity justified? (cyclomatic complexity > 10 = explain or refactor)
- Are magic numbers / strings explained or extracted to constants?
- Does this duplicate logic that already exists elsewhere?
- Are error messages helpful to the person who'll debug this at 2am?

### Axis 5 — Test Coverage

Is the change tested?

- Does the diff include tests?
- Do the tests exercise the actual change, or just existing behavior?
- Are error paths tested, not just the happy path?
- Would tests catch a regression if someone refactored this?

If there are no tests: note it. If the code is inherently hard to test, note that too — it's a design signal.

## Output Format

```
## Code Review: [filename or PR title]

### 🔴 CRITICAL
[Issue]: [Exact description — what can go wrong]
[Location]: [file:line]
[Fix]: [Specific recommendation]

### 🟠 HIGH
...

### 🟡 MEDIUM
...

### 🔵 LOW / Nit
...

### ✅ Looks Good
[What was done well — be specific, not generic]

### Summary
[2–3 sentences: overall assessment, biggest concern, recommendation to merge/revise]
```

Only include sections that have findings. An empty HIGH section is noise.

## What NOT to Review

- Style preferences not covered by the project's linter
- Rewrites of working code with no bug to fix
- Hypothetical performance issues on code that runs once
- Naming bikeshedding that doesn't affect clarity

## Severity Definitions

| Severity | Meaning |
|---|---|
| CRITICAL | Will cause data loss, security breach, or crash in production |
| HIGH | Will cause incorrect behavior under realistic conditions |
| MEDIUM | Will cause problems under edge cases or at scale |
| LOW | Worth fixing but doesn't block merge |
| Nit | Style/preference, reviewer discretion |
