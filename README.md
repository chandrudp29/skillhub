# skillhub

[![CI](https://github.com/chandrudp29/skillhub/actions/workflows/ci.yml/badge.svg)](https://github.com/chandrudp29/skillhub/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/skillhub-ai.svg)](https://pypi.org/project/skillhub-ai/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/skills-22-purple.svg)](#available-skills-22)

**The package manager for AI agent skills.**

Stop copying `.md` files between projects. Install, compose, and publish reusable AI workflows for Claude Code, Cursor, Codex, and Gemini CLI — in one command.

```bash
pip install skillhub-ai
skillhub install research-agent
```

---

## Demo

![skillhub demo](docs/demo.gif)

---

## What is a Skill?

A **skill** is a `.md` file that tells your AI agent *how* to approach a specific type of task — the methodology, the steps, the output format.

Without a skill, Claude Code figures it out from scratch every time. With a skill, it follows a proven workflow consistently.

**Example — what `code-reviewer` looks like inside:**

```markdown
---
name: code-reviewer
description: Five-axis code review for correctness, security, performance,
             readability, and maintainability
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [code-quality, review, security]
---

# Code Reviewer

You are an expert code reviewer. When asked to review code, always evaluate
across five axes:

## Review Axes

**Correctness** — Does it do what it's supposed to do? Are there edge cases
that break it? Off-by-one errors? Null handling?

**Security** — OWASP Top 10. SQL injection, XSS, insecure deserialization,
hardcoded secrets, improper auth.

**Performance** — N+1 queries, unnecessary loops, blocking I/O, missing indexes.

**Readability** — Can a new engineer understand this in 5 minutes?

**Maintainability** — Will this be painful to change in 6 months?

## Output Format

For each file reviewed, output:
1. A summary score per axis (1–5)
2. Critical issues (must fix before merge)
3. Suggestions (nice to have)
4. One thing done well
```

When you run `skillhub install code-reviewer`, this file lands in exactly the right place for your agent — `.claude/commands/code-reviewer.md` for Claude Code, `.cursor/rules/code-reviewer.mdc` for Cursor, and so on.

Now every time you say **"review this PR"**, your agent follows this exact methodology. Every project. Every teammate.

---

## Why skillhub?

Before skillhub, using a skill meant this:

```bash
# Find the skill on GitHub...
# Clone the repo...
# Figure out the right path for your agent...
cp skills/research-agent.md .claude/commands/
cp skills/research-agent.md .cursor/rules/research-agent.mdc
# Switch projects → do it all again
# New teammate → send them the link → they do it all again
```

No versioning. No search. No way to combine skills. Every agent needs files in different places.

**skillhub fixes this:**

```bash
skillhub install research-agent --all-agents
# ✓ Claude Code  → .claude/commands/research-agent.md
# ✓ Cursor       → .cursor/rules/research-agent.mdc
# ✓ Codex        → AGENTS.md
# ✓ Gemini CLI   → .gemini/skills/research-agent.md
```

One command. Every agent. Every project.

---

## Installation

```bash
pip install skillhub-ai
```

Requires Python 3.9+.

```bash
skillhub --help  # verify it works
```

---

## Quick Start

### 1. Find a skill

```bash
skillhub search "debug"           # search by keyword
skillhub search "react" --tag ui  # filter by tag
skillhub list                     # browse all 22 skills
skillhub info research-agent      # full details on one skill
```

### 2. Install it

```bash
# For Claude Code (default)
skillhub install research-agent

# For a specific agent
skillhub install react-patterns --agent cursor

# For ALL agents at once
skillhub install debug-agent --all-agents

# Preview before writing any files
skillhub install security-review --dry-run
```

### 3. Use it

Open your agent and use the skill by name. In Claude Code, type `/research-agent`. In Cursor, the rule activates automatically based on context.

### 4. Manage skills

```bash
skillhub list --installed    # what's installed in this project
skillhub update              # pull latest versions
skillhub uninstall debug-agent
```

---

## Skill Composer

The killer feature. Merge multiple skills into one unified file:

```bash
skillhub compose research-agent code-reviewer security-review -o deep-review
```

**What happens:**
- Descriptions are merged
- Sections are combined without duplication
- Conflicts detected and resolved (first-writer wins, reported to you)
- One file written to your agent's path

**Preview before composing:**
```bash
skillhub compose debug-agent test-writer --dry-run -o qa-skill
```

**Real example:** Building a FastAPI backend?

```bash
skillhub compose python-patterns security-review api-design -o fastapi-expert
```

Now your agent has expertise in Python conventions, OWASP security, and REST best practices — in a single command.

---

## Available Skills (22)

### Research & Analysis
| Skill | Description |
|-------|-------------|
| `research-agent` | Multi-source deep research with synthesis and citations |
| `rag-evaluator` | Evaluate RAG pipelines: faithfulness, relevance, hallucination |
| `llm-evaluator` | Build evaluation frameworks for LLM outputs |

### Code Quality
| Skill | Description |
|-------|-------------|
| `code-reviewer` | Five-axis code review (correctness, security, performance, readability, maintainability) |
| `debug-agent` | Systematic root cause analysis — feedback loop first |
| `refactor-agent` | Safe, incremental refactoring with verification |
| `test-writer` | Write meaningful tests that actually catch bugs |
| `security-review` | OWASP-based security auditing |

### Documentation
| Skill | Description |
|-------|-------------|
| `doc-generator` | README, API docs, docstrings, changelogs |
| `pr-summarizer` | Generate PR descriptions: what, why, how, risks |

### Development Patterns
| Skill | Description |
|-------|-------------|
| `python-patterns` | Modern Python best practices (typing, async, dataclasses) |
| `react-patterns` | React 18+ patterns (hooks, suspense, server components) |
| `fastapi-patterns` | Production FastAPI patterns |
| `api-design` | REST API conventions and best practices |
| `sql-agent` | Write, optimize, and explain SQL with query plans |

### DevOps
| Skill | Description |
|-------|-------------|
| `docker-agent` | Dockerfile optimization, multi-stage builds |
| `git-workflow` | Branching strategies, commit conventions |

### AI/ML Engineering
| Skill | Description |
|-------|-------------|
| `agent-builder` | Build LangGraph agents with proper patterns |
| `prompt-optimizer` | Diagnose and improve underperforming prompts |
| `mle-workflow` | Production ML workflow: data, training, deployment |
| `cost-tracker` | Track and optimize LLM API costs |

### Career
| Skill | Description |
|-------|-------------|
| `yc-job-tracker` | Daily AI/ML job tracking at YC startups |

```bash
skillhub info <name>  # see full skill content before installing
```

---

## Supported Agents

| Agent | Install Path | Flag |
|-------|--------------|------|
| **Claude Code** | `.claude/commands/{name}.md` | `--agent claude` (default) |
| **Cursor** | `.cursor/rules/{name}.mdc` | `--agent cursor` |
| **OpenAI Codex** | `AGENTS.md` (appended with markers) | `--agent codex` |
| **Gemini CLI** | `.gemini/skills/{name}.md` | `--agent gemini` |

---

## Command Reference

| Command | What it does |
|---------|-------------|
| `skillhub search <query>` | Find skills by name, description, or tag |
| `skillhub list` | Show all 22 skills |
| `skillhub list --installed` | Show skills installed in this project |
| `skillhub info <name>` | Full details + preview of a skill |
| `skillhub install <name>` | Install for Claude Code |
| `skillhub install <name> --all-agents` | Install for all 4 agents |
| `skillhub install <name> --dry-run` | Preview without writing files |
| `skillhub install <name> --overwrite` | Replace existing installation |
| `skillhub uninstall <name>` | Remove a skill |
| `skillhub update` | Update all installed skills to latest |
| `skillhub compose <a> <b> -o <name>` | Merge multiple skills into one |
| `skillhub publish <path>` | Submit your skill to the registry |

---

## How It Works

```
skillhub install research-agent
         │
         ▼
┌─────────────────────────────────────┐
│  Fetch registry/index.json          │  cached 1 hour · falls back to bundled
│  github.com/chandrudp29/skillhub    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Download skills/research-agent/    │  falls back to bundled if offline
│  SKILL.md (or agent-specific file)  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Write to the correct agent path    │
│  .claude/commands/research-agent.md │
└─────────────────────────────────────┘
         │
         ▼
      Done! ✓
```

Works offline — skillhub bundles all 22 skills locally and falls back automatically when the network is unavailable.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKILLHUB_CACHE_TTL` | `3600` | Registry cache duration in seconds |
| `SKILLHUB_QUIET` | `0` | Set to `1` to suppress warnings |

---

## Publish Your Own Skill

Have a skill that saves you time? Share it:

```bash
skillhub publish ./my-skill-folder
```

This opens a guided GitHub PR flow. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide and quality bar.

A skill needs one file — `SKILL.md` with YAML frontmatter:

```markdown
---
name: my-skill
description: What this skill makes your agent do
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [relevant, tags]
author: your-github-username
---

# My Skill

Your methodology here...
```

---

## Troubleshooting

**Skill not found?**
```bash
skillhub search <partial-name>   # skillhub suggests similar names automatically
skillhub list                    # browse everything
```

**Already installed?**
```bash
skillhub install <name> --overwrite
```

**Network issues?**
```bash
# skillhub falls back to bundled skills automatically
# Force a fresh registry fetch:
SKILLHUB_CACHE_TTL=0 skillhub list
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork this repo
2. Add your skill under `skills/<name>/SKILL.md`
3. Add the entry to `registry/index.json`
4. Open a PR — we review for usefulness, not quantity

---

## Author

Built by [Chandrashekar DP](https://github.com/chandrudp29) — Senior AI/ML Engineer.

If skillhub saves you time, a star helps others find it.

---

## License

MIT
