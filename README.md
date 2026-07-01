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
skillhub install debug-agent
```

---

## Install a skill in 10 seconds

![skillhub install demo](docs/discover-install.gif)

One command. Every agent gets the right file in the right place.

---

## What is a skill?

A skill is a `.md` file that teaches your AI agent **how to approach a task** — the methodology, the steps, the output format.

Without a skill, Claude figures out an approach from scratch every time. With `debug-agent` installed:

```
/debug-agent

I'm getting: TypeError: Cannot read properties of undefined (reading 'map')
```

Claude now follows a **6-phase discipline** — builds a feedback loop first, reproduces the bug before guessing, hypothesizes before touching code. Every time. Consistently.

---

## Find the right skill

![skillhub search demo](docs/search.gif)

```bash
skillhub search "security"          # search by keyword
skillhub search "react" --tag ui    # filter by tag
skillhub list                       # browse all 22 skills
skillhub info debug-agent           # preview before installing
```

---

## Compose skills — the killer feature

Merge multiple skills into one expert that applies all their knowledge at once.

![skillhub compose demo](docs/compose.gif)

```bash
# Building a FastAPI backend? Combine 3 skills into one expert:
skillhub compose python-patterns security-review api-design -o fastapi-expert
```

**What happens:**
- All sections merged intelligently
- Conflicts detected and resolved (first-writer wins, you're told what was kept)
- One file written to your agent's commands folder

```bash
# In Claude Code:
/fastapi-expert
```

Now your agent applies Python conventions, OWASP security, and REST best practices in every response — without you prompting for each.

---

## Create your own skill

![skillhub init demo](docs/init.gif)

```bash
skillhub init our-coding-standards
# Edit our-coding-standards/SKILL.md
skillhub install our-coding-standards    # test locally
skillhub publish our-coding-standards/  # share with the community
```

Encode your team's conventions once. Everyone on the team installs it. Every AI agent follows the same standards.

---

## Installation

```bash
pip install skillhub-ai
```

Requires Python 3.9+.

```bash
skillhub --help  # verify it works
```

> **Note:** Run `skillhub install` from inside your project folder, not from `/` or your home directory.

---

## Quick Start

```bash
# 1. Find a skill
skillhub list
skillhub search "debug"

# 2. Install it
skillhub install debug-agent                    # Claude Code (default)
skillhub install debug-agent --all-agents       # all 4 agents at once
skillhub install debug-agent --dry-run          # preview first

# 3. Use it in Claude Code
# Type: /debug-agent
# (Restart Claude Code if the command isn't showing yet)

# 4. Combine skills
skillhub compose research-agent code-reviewer -o smart-reviewer

# 5. Create your own
skillhub init my-skill
```

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
| `skillhub init <name>` | Scaffold a new skill locally |
| `skillhub publish <path>` | Submit your skill to the registry |

---

## Cookbook

Common copy-paste recipes → **[docs/cookbook.md](docs/cookbook.md)**

- Debug a bug you can't explain
- Code review before opening a PR
- Build a FastAPI backend with full expert context
- Give your agent your team's coding standards
- Research before building
- Install everything for all agents at once

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
│  SKILL.md                           │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Write to the correct agent path    │
│  .claude/commands/research-agent.md │
│                                     │
│  Also writes .claude/skills.json    │  lightweight index for agent routing
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

**Command not showing in Claude Code?**
```bash
# Restart Claude Code after installing
# Make sure you're in a project folder, not /
cd my-project
skillhub install <name>
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

Or use `skillhub init <name>` to scaffold the template, then `skillhub publish <name>/` to open a guided PR flow.

---

## Author

Built by [Chandrashekar DP](https://github.com/chandrudp29) — Senior AI/ML Engineer.

If skillhub saves you time, a star helps others find it.

---

## License

MIT
