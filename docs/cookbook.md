# skillhub Cookbook

Concrete recipes for the most common workflows. Each recipe is a copy-paste sequence you can run right now.

---

## 1. Debug a bug you can't explain

You have an error. You've been staring at it for 20 minutes. Install the debug-agent skill and let your AI agent follow a disciplined root-cause process instead of guessing.

```bash
skillhub install debug-agent
```

Then in Claude Code, open the file with the bug and type:

```
/debug-agent

I'm getting this error:
TypeError: Cannot read properties of undefined (reading 'map')
  at UserList (UserList.jsx:12)

Here's the component:
[paste your code]
```

**What changes:** Without the skill, Claude guesses. With `debug-agent`, it builds a feedback loop first (adds logging, checks assumptions), hypothesizes before touching code, and won't suggest a fix until it's reproduced the bug.

---

## 2. Code review before you open a PR

Two skills work together here: `code-reviewer` for the five-axis review, and `security-review` to catch OWASP issues.

**Option A — Just code quality:**
```bash
skillhub install code-reviewer
```

**Option B — Code quality + security (recommended for APIs):**
```bash
skillhub install code-reviewer
skillhub install security-review
```

**Option C — Compose into one expert reviewer:**
```bash
skillhub compose code-reviewer security-review -o pre-pr-reviewer
```

Then in Claude Code:
```
/pre-pr-reviewer

Review this before I open the PR:
[paste your diff or file]
```

**What you get:** Scores per axis (1–5), critical issues that must be fixed, nice-to-have suggestions, and one thing done well — in a consistent format every time.

---

## 3. Build a FastAPI backend with full expert context

Instead of switching between tabs for Python style, security, and REST design — compose all three into one skill your agent carries throughout the project.

```bash
skillhub compose python-patterns security-review api-design -o fastapi-expert
```

Then start any session with:
```
/fastapi-expert

Building a POST /users endpoint. Here's my current plan:
[describe or paste]
```

Your agent now applies Python typing conventions, OWASP checks, and REST best practices in every response — without you prompting for each one.

**Tip:** Reuse the composed skill across the project. Install once, use everywhere.

---

## 4. Give your agent your team's coding standards

Every team has conventions that aren't in any public skill. Create one for yours.

```bash
skillhub init our-standards
```

Edit `our-standards/SKILL.md`:

```markdown
---
name: our-standards
description: Acme Corp coding standards — TypeScript, naming, error handling, logging
version: 1.0.0
agents: [claude, cursor]
tags: [standards, typescript, company]
triggers: ['our standards', 'company style', 'follow our conventions']
author: your-github-username
---

# Acme Corp Standards

## TypeScript

- Prefer `interface` over `type` for object shapes
- All async functions must have explicit return types
- No `any` — use `unknown` and narrow

## Error handling

- Use Result<T, E> pattern from our `@acme/core` package
- Never throw in service layer — return errors
- Always log with structured fields: `{ userId, action, error }`

## Naming

- Components: PascalCase
- Hooks: camelCase, prefix `use`
- API routes: kebab-case, plural nouns

## What to check on every PR

1. No secrets in code
2. All DB queries use parameterized inputs
3. Rate limiting on new public endpoints
```

Install and test locally:
```bash
skillhub install our-standards
# In Claude Code: /our-standards
```

Share with your team:
```bash
# Add to .gitignore if internal:
echo "our-standards/" >> .gitignore

# Or commit the skill directory for team use:
git add our-standards/ && git commit -m "add team skill"
```

---

## 5. Research before building

Before starting any non-trivial feature, use `research-agent` to compare approaches, understand tradeoffs, and get citations — so your implementation decision is informed.

```bash
skillhub install research-agent
```

In Claude Code:
```
/research-agent

Research: what's the best approach for rate limiting in a Node.js API?
Compare: in-memory (express-rate-limit) vs Redis-backed vs API gateway level.
Context: we have 50k daily active users, single region, Express + PostgreSQL stack.
```

**What you get:** Structured comparison across multiple sources, tradeoffs per option, a recommendation with reasoning, and citations so you can verify.

---

## 6. Install everything for all your agents at once

Working across Claude Code, Cursor, and Codex? Install once for all of them:

```bash
skillhub install debug-agent --all-agents
skillhub install code-reviewer --all-agents
skillhub install research-agent --all-agents
```

Each skill lands in the right place automatically:
- Claude Code → `.claude/commands/<name>.md`
- Cursor → `.cursor/rules/<name>.mdc`
- Codex → `AGENTS.md` (appended with markers)
- Gemini CLI → `.gemini/skills/<name>.md`

---

## 7. Keep skills up to date

```bash
skillhub update          # update all installed skills for Claude Code
skillhub update --agent cursor  # update for a specific agent
```

---

## 8. Preview before installing

Not sure what a skill does? Check before writing any files:

```bash
skillhub info security-review        # metadata + description
skillhub install security-review --dry-run   # shows where files would go
```

---

## Common patterns

**Start a new project:**
```bash
mkdir my-project && cd my-project
skillhub install debug-agent
skillhub install code-reviewer
skillhub install test-writer
```

**Before shipping a feature:**
```bash
skillhub compose code-reviewer security-review -o ship-check --dry-run
skillhub compose code-reviewer security-review -o ship-check
# In Claude: /ship-check — review everything before I open the PR
```

**Onboard a new teammate:**
```bash
# They run once in their project:
skillhub install debug-agent --all-agents
skillhub install code-reviewer --all-agents
# Done — same skills, same methodology, consistent team output
```
