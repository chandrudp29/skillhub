---
name: debug-agent
description: Systematic root cause analysis for bugs, errors, and unexpected behavior. Use when user reports something broken, an error they can't explain, or unexpected output.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [debugging, error-analysis, root-cause, testing]
triggers: ['debug', 'bug', 'error', 'broken', 'not working', 'crash', 'exception', 'fails', 'issue']
---

# Debug Agent

A discipline for finding root causes — not symptoms. Skips phases only when explicitly justified.

## When to Use

- "This is throwing an error I don't understand"
- "This worked yesterday, now it doesn't"
- "The output is wrong but I don't know why"
- "It works locally but fails in production/CI"

## Phase 1 — Build a feedback loop

**This is the skill.** Without a reproducible signal, everything else is guessing.

Build the tightest possible pass/fail test that exercises the bug:

1. Failing unit/integration test
2. CLI command with fixture input that shows the wrong output
3. Curl / HTTP request that triggers the error
4. Minimal script that reproduces the problem

The loop is ready when you can run one command and see the bug reliably.

If you can't reproduce it: ask the user for logs, a stack trace, environment details, or a way to access the failing environment. Do not hypothesize without a loop.

## Phase 2 — Gather context

Before touching code, collect:

- **Full error message and stack trace** (not "it says something about null")
- **When it started failing** (specific commit? deploy? dependency update?)
- **Environment** (OS, runtime version, env vars, cloud vs local)
- **What changed recently** (`git log --oneline -20`, recent dep updates)
- **What's expected vs what's happening** (exact expected output vs actual)

Run `git bisect` if it worked in a known past commit — narrows root cause in minutes.

## Phase 3 — Hypothesize before touching code

Generate 3–5 ranked hypotheses. Each must be falsifiable:

> "If [X] is the cause, then [changing Y] will make the bug disappear."

Show the ranked list before testing. Prevents anchoring on the first idea.

Common root cause categories (check in this order):
1. Input data is different from what's expected (null, wrong type, wrong encoding)
2. State from a previous operation is leaking (shared mutable state, unclosed connections)
3. Async/concurrency issue (race condition, missing await, callback ordering)
4. Environment difference (different versions, missing env var, path issue)
5. Off-by-one / boundary condition
6. Third-party API changed behavior (silent breaking change)

## Phase 4 — Instrument, don't guess

Add targeted instrumentation at the boundary that distinguishes your top hypotheses:

- **Use a debugger** when the env supports it — one breakpoint beats ten logs
- **Add structured logs** at the specific decision point, not everywhere
- **Tag every debug log** with a unique prefix like `[DBG-a1b2]` — easy to grep and remove
- Measure one variable at a time — changing two things at once hides which one fixed it

## Phase 5 — Fix and verify

Write a regression test before applying the fix (if a testable seam exists).

After the fix:
1. Run the Phase 1 feedback loop → it goes green
2. Run the full test suite → nothing else goes red
3. Test in the original failure environment if it was environment-specific

## Phase 6 — Clean up

- [ ] Remove all `[DBG-...]` instrumentation (grep for the prefix)
- [ ] The regression test is committed with the fix
- [ ] The commit message states what the root cause was and why the fix works
- [ ] If a design issue enabled this bug: note it for a follow-up refactor

## Common Traps

| Trap | What to do instead |
|---|---|
| "I know what the bug is" | Write the hypothesis. Test it. You're often wrong. |
| Fixing symptoms not root cause | Ask "why did this happen?" until you hit the real cause |
| Changing multiple things at once | One change per test — otherwise you learn nothing |
| Ignoring environment differences | "Works on my machine" = environment bug until proven otherwise |
| Not testing the fix thoroughly | The fix that breaks 3 other things is worse than the bug |
