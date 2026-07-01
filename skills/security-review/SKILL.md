---
name: security-review
description: Security audit focused on OWASP Top 10 — injection, auth flaws, secrets exposure, IDOR, and more. Use when reviewing code for vulnerabilities, before deploying to production, or auditing a new codebase.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [security, owasp, vulnerabilities, auth, injection, secrets]
triggers: ['security', 'vulnerability', 'owasp', 'injection', 'auth', 'secrets', 'secure']
---

# Security Review

A systematic security audit that finds real vulnerabilities — not theoretical ones. Prioritizes by blast radius.

## When to Use

- Before any code ships to production
- When adding authentication, file upload, payments, or user data handling
- Reviewing a PR that touches auth, APIs, or data access
- Auditing a new codebase you inherited

## The Audit Checklist

Work through these in order — critical first.

### 1. Secrets and Credentials

The easiest win. Scan first.

```bash
# Quick scan for likely secrets
grep -rE "(api_key|secret|password|token|credential)\s*=\s*['\"][^'\"]{8,}" . --include="*.py" --include="*.js" --include="*.ts" --include="*.env"
git log --all --full-history -- "**/*.env" "**/.env*"
```

Findings:
- [ ] No secrets hardcoded in source files
- [ ] No secrets in git history
- [ ] `.env` files are in `.gitignore`
- [ ] Secrets loaded from environment variables or a secrets manager (AWS Secrets Manager, Vault)

**Severity**: CRITICAL — hardcoded secrets are actively exploited within hours of being pushed.

### 2. Injection Vulnerabilities

**SQL Injection** — look for string concatenation in queries:
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)

# SAFE
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

**Command Injection** — look for user input in shell commands:
```python
# VULNERABLE
os.system(f"ffmpeg -i {user_filename} output.mp4")
subprocess.call(f"convert {path}", shell=True)

# SAFE
subprocess.run(["ffmpeg", "-i", user_filename, "output.mp4"])
```

**NoSQL Injection** — look for unvalidated objects passed to MongoDB queries.

**Template Injection** — look for user strings rendered as templates (Jinja2, Handlebars).

**Severity**: CRITICAL for SQL/command injection. HIGH for others.

### 3. Authentication and Authorization

**Authentication** (who are you?):
- [ ] Passwords hashed with bcrypt/argon2 (never MD5, SHA1, or plain SHA256)
- [ ] JWT secrets are strong (≥256 bits) and not hardcoded
- [ ] JWT expiry is set (exp claim checked)
- [ ] Sessions invalidated on logout
- [ ] Rate limiting on login and password reset endpoints

**Authorization** (what can you do?):
- [ ] Every API route that returns or modifies data checks the caller's permission
- [ ] No client-side-only authorization checks
- [ ] Ownership verified before returning records: `WHERE id = ? AND user_id = ?`
- [ ] Admin endpoints are protected beyond just login

**IDOR (Insecure Direct Object Reference)** — the most common auth bug:
```python
# VULNERABLE — user can request any order by guessing IDs
@app.get("/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    return db.query(Order).filter(Order.id == order_id).first()

# SAFE — user can only access their own orders
@app.get("/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    return db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id  # ownership check
    ).first()
```

### 4. Input Validation and Output Encoding

- [ ] All user inputs validated at the API boundary (type, length, format)
- [ ] File uploads: validate file type by content (magic bytes), not just extension
- [ ] File uploads: stored outside web root, with randomized names
- [ ] User-controlled content rendered as HTML is escaped (XSS prevention)
- [ ] Redirect URLs validated against an allowlist (open redirect prevention)

### 5. Sensitive Data Exposure

- [ ] PII (email, phone, address) is not logged in plaintext
- [ ] Passwords and tokens are never logged
- [ ] API responses don't leak fields the caller shouldn't see (over-fetching)
- [ ] Error messages don't expose stack traces, SQL, or internal paths to users
- [ ] HTTPS enforced (no HTTP fallback for auth or data endpoints)

### 6. Dependency Vulnerabilities

```bash
# Python
pip-audit  # or: safety check

# Node.js
npm audit

# Check for known CVEs in direct dependencies
```

Update any dependency with a HIGH or CRITICAL CVE. Pin versions in production.

### 7. Rate Limiting and Abuse Prevention

- [ ] Login endpoint: max 5 attempts per minute per IP
- [ ] Password reset: rate limited, tokens expire in ≤15 minutes
- [ ] File upload: size limit enforced server-side
- [ ] API endpoints: rate limited per user/IP to prevent scraping or DoS

## Output Format

```
Security Review — [file or PR]

🔴 CRITICAL
  [Finding]: [What the vulnerability is]
  [Location]: [file:line]
  [Impact]: [What an attacker can do]
  [Fix]: [Specific code change needed]

🟠 HIGH
  ...

🟡 MEDIUM
  ...

✅ SECURE
  [What was done correctly — be specific]

SUMMARY
  [2–3 sentences: overall posture, biggest risk, ship/revise recommendation]
```

## What NOT to Flag

- Theoretical attacks with no realistic path
- Issues already mitigated by the framework
- Style preferences (use HTTPS everywhere is a real finding; "prefer fstrings" is not)
