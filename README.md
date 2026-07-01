# skillhub

[![CI](https://github.com/chandrudp29/skillhub/actions/workflows/ci.yml/badge.svg)](https://github.com/chandrudp29/skillhub/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/skillhub-ai.svg)](https://pypi.org/project/skillhub-ai/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/skills-22-purple.svg)](#available-skills)

**The package manager for AI agent skills.**

Install, compose, and publish reusable prompting workflows for Claude Code, Cursor, Codex, and Gemini CLI — in one command.

```bash
pip install skillhub-ai
skillhub install research-agent
```

---

## Why skillhub?

You've been copying skill files manually:

```bash
# The old way
git clone https://github.com/someone/skills
cp skills/research-agent/SKILL.md .claude/commands/
cp skills/research-agent/SKILL.md .cursor/rules/
# repeat for every skill, every project, every agent...
```

No versioning. No search. No way to combine skills. Every agent needs different files in different places.

**skillhub fixes this:**

```bash
# The new way
skillhub install research-agent --all-agents  # Done. All 4 agents configured.
```

---

## Installation

```bash
pip install skillhub-ai
```

Requires Python 3.9+. No other dependencies needed.

**Verify installation:**
```bash
skillhub --help
```

---

## Quick Start

### Search & Discover

```bash
# Search by keyword
skillhub search "debug"

# Search by tag
skillhub search "research" --tag analysis

# List all 22 available skills
skillhub list

# Get detailed info on a skill
skillhub info research-agent
```

### Install Skills

```bash
# Install for Claude Code (default)
skillhub install research-agent

# Install for a specific agent
skillhub install debug-agent --agent cursor
skillhub install debug-agent --agent codex
skillhub install debug-agent --agent gemini

# Install for ALL agents at once
skillhub install debug-agent --all-agents

# Preview what will be installed (no changes made)
skillhub install debug-agent --dry-run
```

### Manage Installed Skills

```bash
# See what's installed in this project
skillhub list --installed

# Update all installed skills to latest
skillhub update

# Remove a skill
skillhub uninstall debug-agent
```

---

## Skill Composer (The Killer Feature)

Combine multiple skills into one unified file — conflicts resolved automatically:

```bash
skillhub compose research-agent code-reviewer security-review -o my-review-skill
```

**What it does:**
- Merges descriptions from all skills
- Combines sections without duplication
- Detects conflicts (first-writer wins)
- Reports what was merged

**Preview first:**
```bash
skillhub compose debug-agent test-writer --dry-run -o qa-skill
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

```bash
skillhub list         # See all with descriptions
skillhub info <name>  # Full details on one skill
```

---

## Supported Agents

| Agent | Install Path | Flag |
|-------|--------------|------|
| **Claude Code** | `.claude/commands/{name}.md` | default |
| **Cursor** | `.cursor/rules/{name}.mdc` | `--agent cursor` |
| **OpenAI Codex** | `AGENTS.md` (appended) | `--agent codex` |
| **Gemini CLI** | `.gemini/skills/{name}.md` | `--agent gemini` |

---

## Command Reference

| Command | Description |
|---------|-------------|
| `skillhub search <query>` | Find skills by name, description, or tag |
| `skillhub list` | Show all available skills |
| `skillhub list --installed` | Show installed skills in current project |
| `skillhub info <name>` | Detailed information about a skill |
| `skillhub install <name>` | Install a skill |
| `skillhub install <name> --dry-run` | Preview install without writing |
| `skillhub install <name> --all-agents` | Install for all 4 agents |
| `skillhub uninstall <name>` | Remove an installed skill |
| `skillhub update` | Update all installed skills |
| `skillhub compose <a> <b> -o <name>` | Merge multiple skills into one |
| `skillhub publish <path>` | Submit your skill to the registry |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKILLHUB_CACHE_TTL` | `3600` | Cache duration in seconds (1 hour) |
| `SKILLHUB_QUIET` | `0` | Set to `1` to suppress warnings |

---

## How It Works

```
skillhub install research-agent
         │
         ▼
┌─────────────────────────────────┐
│  Fetch registry from GitHub     │  (cached 1 hour)
│  registry/index.json            │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Download SKILL.md for agent    │
│  skills/research-agent/SKILL.md │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Write to correct agent path    │
│  .claude/commands/research-agent.md
└─────────────────────────────────┘
         │
         ▼
      Done! ✓
```

**Offline support:** Falls back to bundled skills when network is unavailable.

---

## Publish Your Own Skill

Have a skill that would help others? Submit it:

```bash
skillhub publish ./my-skill
```

This opens a guided PR flow. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

**Quality bar:** We review for usefulness, not quantity. One genuinely helpful skill beats ten mediocre ones.

---

## Troubleshooting

**Skill not found?**
```bash
skillhub search <partial-name>  # Find similar skills
skillhub list                   # See everything available
```

**Already installed error?**
```bash
skillhub install <name> --overwrite  # Replace existing
```

**Network issues?**
```bash
# skillhub falls back to bundled skills automatically
# To force refresh:
SKILLHUB_CACHE_TTL=0 skillhub list
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

**Quick start:**
1. Fork this repo
2. Add your skill under `skills/<your-skill-name>/SKILL.md`
3. Add entry to `registry/index.json`
4. Open a PR

---

## Author

Built by [Chandrashekar DP](https://github.com/chandrudp29) — AI/ML Engineer building open source tools for developers.

If skillhub saves you time, consider starring it — it helps others find it.

---

## License

MIT
