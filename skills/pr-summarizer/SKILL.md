---
name: pr-summarizer
description: Generate clear, complete pull request descriptions from a diff or commit list. Use when user needs to write a PR description, wants to document a change, or asks for a commit summary.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [git, pull-request, documentation, changelog]
---

# PR Summarizer

Writes PR descriptions that reviewers actually read — context-first, not diff-first.

## When to Use

- "Write a PR description for this"
- "Summarize what these commits do"
- "Help me document this change"
- Before opening any non-trivial PR

## What a Good PR Description Does

It answers the questions a reviewer has before they look at the diff:

1. **Why does this change exist?** (the problem, not the solution)
2. **What did you change?** (the approach, not every file)
3. **How do I know it works?** (test plan, screenshots, benchmark)
4. **What should I watch out for?** (risks, known limitations, follow-up needed)

A PR description is not a diff summary. "Changed X in file Y" is what git already shows. The PR description should explain what the reviewer cannot see from the diff.

## Workflow

### Step 1 — Read the diff and commits

Before writing anything, understand:
- What problem does this solve? (if not obvious, ask)
- What was the approach taken (and what alternatives were considered)?
- What's the blast radius — what could break?
- Are there any TODOs, hacks, or known limitations in the code?

### Step 2 — Write the description

```markdown
## What and Why

[1–3 sentences: the problem this solves and why it needed to be solved now.
Not "this PR adds X" — that's in the title. Why does X need to exist?]

## How

[The approach taken. Not every file changed — the mental model a reviewer 
needs to understand the diff. Include key design decisions and any 
alternatives considered and rejected.]

## Test Plan

- [ ] [Specific test: what you ran, what you verified]
- [ ] [Edge case tested]
- [ ] [Screenshot or link to demo if UI change]
- [ ] [Performance numbers if perf-sensitive change]

## Risks and Notes

[What could go wrong? What didn't you test? What follow-up is needed?
Leave blank if genuinely none — don't write "None" as a placeholder.]
```

### Step 3 — Write the title

Format: `[type]: [imperative verb] [what]`

Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`

Good titles:
- `feat: add streaming support to chat completions`
- `fix: handle null user in session middleware`
- `perf: replace O(n²) dedup with hash set`

Bad titles:
- `update stuff`
- `fixes`
- `WIP`

## Calibrating Length

Match description depth to change size:
- **Trivial fix** (typo, config change): 2–3 sentences is enough
- **Normal feature**: Full template above
- **Large refactor or risky change**: Add "Architecture Notes" section explaining the before/after design

## What NOT to Include

- Exhaustive file-by-file change lists (that's what the diff is for)
- Generic statements ("This PR improves code quality")
- Explanations of code that's self-evident from reading it
- Detailed commit history (squash or use `git log` instead)
