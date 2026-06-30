---
name: git-workflow
description: Git branching, commit conventions, rebase vs merge, conflict resolution, and release tagging. Use when setting up a git workflow, writing commits, resolving conflicts, or preparing a release.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [git, branching, commits, workflow, collaboration, release]
---

# Git Workflow

Opinionated, practical Git patterns for teams that ship. Skip the theory — here's what to actually do.

## When to Use

- Starting a new feature or fix
- Writing a commit message
- Resolving a merge conflict
- Preparing a release
- Cleaning up a messy branch history

## Branching Strategy

Use **GitHub Flow** for most teams (continuous delivery):

```
main  ← always deployable, protected
  ├── feat/add-rag-pipeline
  ├── fix/null-session-middleware
  └── chore/bump-langchain-deps
```

Branch naming: `feat/` `fix/` `chore/` `refactor/` `docs/` + short-kebab-description.

**When to use GitFlow instead**: only if you ship versioned releases (mobile apps, SDKs, libraries) with defined release cycles. For web services and APIs, GitFlow adds process with no benefit.

## Commit Messages

Format: `type: imperative verb + what changed`

```
feat: add streaming support to chat completions
fix: handle null user in session middleware
refactor: replace O(n²) dedup with hash set
chore: bump langchain from 0.2.1 to 0.3.0
docs: add RAG evaluation guide to README
test: add edge cases for empty query handling
```

**Rules:**
- Imperative mood: "add", "fix", "remove" — not "added", "fixing", "removes"
- Under 72 characters for the subject line
- If you need to explain WHY, add a blank line then a paragraph body
- Never: "WIP", "fix stuff", "update", "changes"

**When to add a body:**
```
fix: prevent session token from expiring mid-request

The token refresh was happening after the auth check instead of before,
causing a race condition when tokens expired between 0-500ms of the check.
Moved refresh to happen before any auth validation.
```

## Rebase vs Merge

**Use rebase** for feature branches before merging to main:
```bash
git fetch origin
git rebase origin/main    # replay your commits on top of latest main
git push --force-with-lease  # safe force push (fails if someone else pushed)
```

**Use merge** only for: merging main into a long-running branch, or when you want to preserve the exact history of a collaborative branch.

**Never rebase** shared branches (anything others have pulled).

## Conflict Resolution

When `git rebase` hits a conflict:

```bash
# See what conflicts exist
git status

# For each conflicted file:
# 1. Open the file — look for <<<<<<, =======, >>>>>>>
# 2. Understand BOTH sides before choosing
# 3. Edit to the correct result (may be a combination of both)
# 4. Remove the conflict markers entirely

# Mark resolved and continue
git add <resolved-file>
git rebase --continue

# If you're lost and want to start over
git rebase --abort
```

Never blindly accept "ours" or "theirs" — read what changed on both sides first.

## Cleaning Up History Before PR

Squash "WIP" commits before opening a PR:
```bash
# Interactive rebase to squash last 4 commits
git rebase -i HEAD~4
# Mark commits as 's' (squash) to merge into the one above
# Edit the combined commit message
```

Use `git commit --amend` to fix the most recent commit (message or content) before pushing.

## Tagging a Release

```bash
git tag -a v1.2.0 -m "Release v1.2.0 — adds skill composer"
git push origin v1.2.0
```

Use semantic versioning: `vMAJOR.MINOR.PATCH`
- MAJOR: breaking change
- MINOR: new feature, backwards compatible
- PATCH: bug fix

## Common Mistakes

| Mistake | Fix |
|---|---|
| Committed to main directly | `git reset HEAD~1`, make a branch, recommit |
| Pushed sensitive data | Rotate the credential immediately, then use `git filter-repo` to scrub history |
| Merge conflict you don't understand | `git rebase --abort` and ask — never guess |
| Giant PR that's impossible to review | Split it; one concern per PR |
| Force pushed a shared branch | Coordinate with the team, they'll need to `git reset --hard` |
