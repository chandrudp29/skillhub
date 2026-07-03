<div align="center">

<h1>skillhub</h1>

<p><strong>The package manager for AI agent skills.</strong><br>
Install, compose, optimize, and bridge skills across Claude, Cursor, Codex, and Gemini.</p>

[![PyPI version](https://img.shields.io/pypi/v/skillhub-ai.svg?style=flat-square&color=0066cc)](https://pypi.org/project/skillhub-ai/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/skillhub-ai?style=flat-square&color=22c55e&label=installs%2Fmonth)](https://pypi.org/project/skillhub-ai/)
[![CI](https://img.shields.io/github/actions/workflow/status/chandrudp29/skillhub/ci.yml?style=flat-square&label=CI)](https://github.com/chandrudp29/skillhub/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)

[![Ecosystems](https://img.shields.io/badge/🌐_ecosystems-13-6366f1?style=flat-square)](#the-13-ecosystems)
[![Agents](https://img.shields.io/badge/🤝_agents-4-0066cc?style=flat-square)](#install-to-any-agent)
[![Skills](https://img.shields.io/badge/📦_skills-34-22c55e?style=flat-square)](#available-skills-34)
[![Compose](https://img.shields.io/badge/🔀_only_tool_that_merges-skills-f59e0b?style=flat-square)](#compose)

```bash
pip install skillhub-ai
```

</div>

---

![skillhub compose demo](docs/compose.gif)

```bash
# Like npm install --save, but for AI skills
skillhub add python-patterns        # installs + records in skillhub.json
skillhub add security-review

# Teammates clone and reproduce your exact skill setup in one command
skillhub install                    # reads skillhub.json, installs all

# Or compose multiple skills into one expert
skillhub compose python-patterns security-review api-design -o fastapi-expert
```

---

## Why skillhub?

You install a `python-patterns` skill in Claude Code. You find a `security-review` skill in Cursor. You see a `frontend-developer` persona in agency-agents (125k stars). They all live in different files, different formats, different tools — and loading all of them burns your monthly token quota in days.

**The problems:**

- No way to combine skills — copy-pasting markdown is error-prone and tedious
- Loading all skills causes "context rot": diluted attention, 6–7 days to exhaust monthly quota
- Skills from Anthropic, OpenAI, Microsoft, Google have no common interface
- Every agent (Claude Code, Cursor, Codex, Gemini) requires a different file format
- No `package.json` equivalent — no reproducible skill setup across a team

**skillhub solves all five in one tool.**

---

## Features

### [📋 skillhub.json Manifest](#manifest) — Reproducible Skill Setups

The `package.json` for skills. `skillhub add` records what you install. `skillhub install` (no args) restores everything. Commit `skillhub.json` so teammates reproduce your exact setup in one command.

### [🔀 Compose](#compose) — The Only Tool That Merges Skills

Merge 2–10 skills from any source into one unified expert skill with automatic conflict detection. No other tool does this.

### [🤖 AI-Powered Conflict Resolution](#ai-powered-merge)

When two skills define the same `## Error Handling` section, `--strategy ai` sends both to Claude and gets back a single best-of-both version.

### [⚡ Optimize](#optimize) — Solve Context Rot

Scans all installed skills, finds duplicate sections across them, and writes a deduplicated bundle. Cuts token usage 10–30%. Directly solves the token bloat problem Microsoft named "context rot."

### [🌉 Bridge](#bridge) — AGENTS.md ↔ SKILL.md

60,000+ repos use AGENTS.md (OpenAI Codex). Claude Code doesn't read it natively. `skillhub bridge` converts in both directions — import AGENTS.md into Claude skills, or pack Claude skills into AGENTS.md for Codex teams.

### [🌐 13 Ecosystems, One Interface](#the-13-ecosystems)

Pull from Anthropic, OpenAI, GitHub Copilot, Microsoft, Google, Vercel, and 8 more — using a simple `ecosystem:skill-name` prefix. All sources resolve to the same SKILL.md format.

### [🤝 Works With Every Agent](#install-to-any-agent)

Claude Code (`.claude/commands/`), Cursor (`.cursor/rules/`), OpenAI Codex (`AGENTS.md`), Gemini CLI (`.gemini/skills/`). One skill, four agents.

---

## Quick Start

```bash
# 1. Install
pip install skillhub-ai

# 2. Add skills to your project (installs + records in skillhub.json)
skillhub add python-patterns
skillhub add security-review
skillhub add debug-agent

# 3. Teammates reproduce your setup
skillhub install           # reads skillhub.json, installs all

# 4. Optimize against token bloat
skillhub optimize          # deduplicate, save 10–30% tokens → /optimized

# 5. Compose your first expert
skillhub compose --template fastapi-expert
```

---

## Manifest

> **The `package.json` moment for AI skills.**

```bash
skillhub add python-patterns           # install + record in skillhub.json
skillhub add security-review           # add another
skillhub add anthropic:claude-api      # external sources work too

# Commit skillhub.json — teammates run:
skillhub install                       # restores all declared skills

# Already have skills installed? Pin them:
skillhub lock                          # creates skillhub.json from current installs
```

`skillhub.json` created automatically on first `add`:

```json
{
  "_skillhub": "0.4.0",
  "name": "my-project",
  "skills": {
    "python-patterns": "latest",
    "security-review": "latest",
    "anthropic:claude-api": "latest"
  },
  "composed": {}
}
```

---

## Compose

![skillhub compose demo](docs/compose.gif)

> [!IMPORTANT]
> No other tool does this. `skillhub compose` is the only way to merge multiple SKILL.md files into one unified expert skill with conflict detection and resolution.

```bash
# Simplest: registry skills
skillhub compose python-patterns security-review api-design -o fastapi-expert

# Cross-company: Anthropic + OpenAI + Google
skillhub compose anthropic:claude-api openai:aspnet-core google:agent-platform-deploy -o cloud-expert

# Mix everything: community + local + any ecosystem
skillhub compose agency-agents:frontend-developer ./my-standards.md skills.sh:react-expert -o our-expert

# Preview without writing
skillhub compose python-patterns security-review -o test --dry-run
```

**What happens when you compose:**

```
python-patterns  +  security-review  +  api-design
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                    Fetch each source
                    Parse ## sections
                    Detect conflicts
                          │
              ┌───────────┴───────────┐
       first-wins (default)         ai (Claude)
       first skill wins         merges both intelligently
              └───────────┬───────────┘
                          │
            .claude/commands/fastapi-expert.md
                          │
                  /fastapi-expert ✓
```

---

## AI-Powered Merge

![skillhub ai-compose demo](docs/ai-compose.gif)

```bash
pip install "skillhub-ai[ai]"
export ANTHROPIC_API_KEY=sk-...

skillhub compose python-patterns security-review -o secure-python --strategy ai
```

| Strategy | Speed | On conflict |
|----------|-------|-------------|
| `first-wins` (default) | Instant | First skill's section kept, conflict logged |
| `ai` | ~2s/conflict | Claude reads both, writes a unified best-of-both |

---

## Optimize

> **Solves "context rot" — the token bloat problem Microsoft named.**

Loading all your skills wastes tokens on repeated sections (`## Error Handling`, `## When to Use`, `## Code Review` — they appear in nearly every skill). Over 6–7 days, this exhausts monthly token quotas.

`skillhub optimize` deduplicates them:

```bash
skillhub optimize

# Optimizing skills for Claude Code...
#
#   Original:  6,052 tokens
#   Optimized: 4,831 tokens  (-20%, -1,221 tokens saved)
#
#   Duplicate sections merged (3 found):
#     ⊕ When to Use (in 6 skills)
#     ⊕ Error Handling (in 4 skills)
#     ⊕ Code Review Checklist (in 3 skills)
#
# ✓ Written to .claude/commands/optimized.md
#   → In Claude Code, type /optimized to load the lean bundle.
```

```bash
skillhub optimize --output team-bundle    # custom output name
skillhub optimize --agent cursor          # optimize Cursor rules
```

---

## Bridge

> **60,000+ repos use AGENTS.md. skillhub connects them to Claude, Cursor, and Gemini.**

```bash
# Import AGENTS.md → Claude/Cursor/Gemini skill files
skillhub bridge from
# ✓ my-project-rules → .claude/commands/my-project-rules.md
# → In Claude Code, type /my-project-rules to use it.

# Pack installed Claude skills → AGENTS.md for Codex teams
skillhub bridge to
# ✓ Packed 4 skill(s) into AGENTS.md
# → Codex will read them automatically.
# → Skills wrapped in skillhub markers — safe to run again.

# Custom file path
skillhub bridge from --file team/AGENTS.md
```

Round-trip safe: `bridge to` wraps skills in markers so running it again replaces, never duplicates.

---

## Diff Before You Merge

![skillhub diff demo](docs/diff.gif)

```bash
skillhub diff python-patterns security-review
```

```
Comparing: python-patterns  vs  security-review
────────────────────────────────────────────────
✅ Only in python-patterns (6):   Type Annotations, Async Patterns, Dataclasses...
✅ Only in security-review  (5):  OWASP Top 10, Input Validation, Auth Patterns...
⚠️  Conflicts (2):               Error Handling, Code Review Checklist
```

---

## Pre-Built Expert Templates

```bash
skillhub templates
skillhub compose --template fastapi-expert
skillhub compose --template ml-platform --strategy ai
```

| Template | Skills | Best for |
|----------|--------|----------|
| `fastapi-expert` | python-patterns + security-review + api-design | FastAPI backend |
| `fullstack-expert` | react-patterns + python-patterns + api-design | Full-stack |
| `ml-platform` | agent-builder + mle-workflow + llm-evaluator | ML engineers |
| `pre-pr-reviewer` | code-reviewer + security-review + test-writer | Code review |
| `research-analyst` | research-agent + rag-evaluator + doc-generator | Research |

---

## The 13 Ecosystems

> [!TIP]
> Any prefix works in `add`, `compose`, `diff`, `install`, and `info` — mix freely.

![skillhub cross-ecosystem demo](docs/cross.gif)

```bash
skillhub compose \
  anthropic:claude-api \               # Anthropic official
  openai:aspnet-core \                 # OpenAI official
  copilot:acquire-codebase-knowledge \ # GitHub Copilot official
  microsoft:skill-creator \            # Microsoft official
  google:agent-platform-deploy \       # Google official
  addyosmani:code-review-and-quality \ # Addy Osmani
  scientific:astropy \                 # K-Dense AI
  antigravity:ab-test-setup \          # Antigravity/OpenClaw
  gamedev:godot-2d-movement \          # Game Dev Skills
  tech-leads:domain-analysis \         # Tech Leads Club
  agency-agents:frontend-developer \   # Agency Agents
  debug-agent \                        # skillhub registry
  -o the-ultimate-expert
```

| Prefix | Ecosystem | Repo |
|--------|-----------|------|
| *(no prefix)* | **skillhub** registry | [chandrudp29/skillhub](https://github.com/chandrudp29/skillhub) |
| `anthropic:name` | **Anthropic** official | [anthropics/skills](https://github.com/anthropics/skills) |
| `openai:name` | **OpenAI / Codex** official | [openai/skills](https://github.com/openai/skills) |
| `copilot:name` | **GitHub Copilot** official | [github/awesome-copilot](https://github.com/github/awesome-copilot) |
| `microsoft:name` | **Microsoft** official | [microsoft/skills](https://github.com/microsoft/skills) |
| `google:name` | **Google** official | [google/skills](https://github.com/google/skills) |
| `skills.sh:name` | **Vercel** skills.sh | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| `agency-agents:name` | **Agency Agents** | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) |
| `addyosmani:name` | **Addy Osmani** | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) |
| `scientific:name` | **K-Dense AI** | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) |
| `antigravity:name` | **Antigravity** | [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) |
| `gamedev:name` | **Game Dev Skills** | [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) |
| `tech-leads:name` | **Tech Leads Club** | [tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills) |
| `claude:name` | Your **Claude Code** project | `.claude/commands/` |
| `cursor:name` | Your **Cursor** project | `.cursor/rules/` |
| `codex:name` | Your **Codex** project | `AGENTS.md` |
| `gemini:name` | Your **Gemini CLI** project | `.gemini/skills/` |
| `github:owner/repo/path` | **Any public GitHub** file | raw.githubusercontent.com |
| `./path/to/file.md` | **Local file** | — |

---

## Install to Any Agent

```bash
skillhub add debug-agent                      # Claude Code (default) + skillhub.json
skillhub install debug-agent --agent cursor   # Cursor
skillhub install debug-agent --agent codex    # OpenAI Codex
skillhub install debug-agent --agent gemini   # Gemini CLI
skillhub install debug-agent --all-agents     # all 4 at once
skillhub install debug-agent --dry-run        # preview only
```

| Agent | Where it's written | How to invoke |
|-------|-------------------|---------------|
| **Claude Code** | `.claude/commands/<name>.md` | `/<name>` in chat |
| **Cursor** | `.cursor/rules/<name>.mdc` | Always active |
| **OpenAI Codex** | `AGENTS.md` (with markers) | Auto-loaded |
| **Gemini CLI** | `.gemini/skills/<name>.md` | Always active |

---

## Cross-Ecosystem Recipes

```bash
# Ultimate Python expert — 3 sources, AI-merged
skillhub compose python-patterns security-review api-design -o python-expert --strategy ai

# Enterprise frontend — community + production-grade + patterns
skillhub compose agency-agents:frontend-developer addyosmani:code-review-and-quality \
  react-patterns -o enterprise-frontend --strategy ai

# Cloud AI expert — Anthropic + Google + Microsoft official skills
skillhub compose anthropic:claude-api google:agent-platform-deploy \
  microsoft:skill-creator -o cloud-ai-expert

# Scientific Python — K-Dense AI + skillhub registry
skillhub compose scientific:astropy python-patterns rag-evaluator -o research-scientist
```

---

## Create & Publish Your Own Skill

```bash
skillhub init our-coding-standards    # scaffold SKILL.md template
# edit SKILL.md with your team's conventions
skillhub add our-coding-standards/    # test and record locally
skillhub publish our-coding-standards/  # open PR to registry
```

<details>
<summary><b>SKILL.md format</b></summary>

```markdown
---
name: our-coding-standards
description: Backend coding standards for our team
version: 1.0.0
tags: [python, standards, backend]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when writing, reviewing, or refactoring any backend code.

## Core Rules
- All functions must have type annotations
- Use dataclasses over plain dicts for structured data

## Examples
...
```

The SKILL.md format is Anthropic's open standard — supported by 32+ AI coding tools.

</details>

---

## All Commands

<details>
<summary><b>Expand full command reference</b></summary>

```bash
# Discovery
skillhub list                              # browse all 34 skills
skillhub list --installed                  # skills in this project
skillhub search <query>                    # search by keyword
skillhub search <query> --tag <tag>        # filter by tag
skillhub info <name>                       # full preview

# Manifest (skillhub.json — like package.json for skills)
skillhub add <name>                        # install + record in skillhub.json
skillhub install                           # install all from skillhub.json
skillhub lock                              # pin current installs to skillhub.json

# Install & Manage
skillhub install <name>                    # Claude Code (default)
skillhub install <name> --agent cursor     # Cursor
skillhub install <name> --all-agents       # all 4 agents
skillhub install <name> --dry-run          # preview without writing
skillhub install <name> --overwrite        # replace existing
skillhub uninstall <name>                  # remove
skillhub update                            # update all installed

# Optimize (solve context rot / token bloat)
skillhub optimize                          # deduplicate across all installed skills
skillhub optimize --output team-bundle     # custom name
skillhub optimize --agent cursor           # optimize Cursor rules

# Bridge (AGENTS.md ↔ SKILL.md)
skillhub bridge from                       # import AGENTS.md → Claude skills
skillhub bridge to                         # pack Claude skills → AGENTS.md
skillhub bridge from --file path/AGENTS.md # custom file

# Compose
skillhub compose <a> <b> ... -o <name>              # merge (first-wins)
skillhub compose <a> <b> ... -o <name> --strategy ai  # Claude AI merge
skillhub compose --template <name>                  # pre-built template
skillhub compose --template <name> --strategy ai    # template + AI merge
skillhub compose <a> <b> -o <name> --dry-run        # preview only
skillhub templates                                  # list 5 templates

# Cross-ecosystem (any prefix works)
skillhub compose anthropic:security openai:aspnet-core -o expert
skillhub diff anthropic:claude-api openai:aspnet-core

# Diff
skillhub diff <a> <b>                      # compare section by section

# Create & Publish
skillhub init <name>                       # scaffold new SKILL.md
skillhub publish <path>                    # PR to registry
```

| Command | What it does |
|---------|-------------|
| `skillhub add <name>` | Install + record in skillhub.json |
| `skillhub install` | Install all from skillhub.json |
| `skillhub lock` | Pin current installs to skillhub.json |
| `skillhub optimize` | Deduplicate skills, save 10–30% tokens |
| `skillhub bridge from` | Import AGENTS.md → Claude/Cursor/Gemini |
| `skillhub bridge to` | Pack Claude skills → AGENTS.md |
| `skillhub diff <a> <b>` | Compare two skills section by section |
| `skillhub compose <a> <b> -o <name>` | Merge (first-wins on conflicts) |
| `skillhub compose ... --strategy ai` | Merge with Claude AI resolution |
| `skillhub compose --template <name>` | Use a pre-built expert template |
| `skillhub templates` | List all built-in templates |
| `skillhub search <query>` | Search by name, description, or tag |
| `skillhub list` | Browse all 34 skills |
| `skillhub list --installed` | Skills installed in this project |
| `skillhub info <name>` | Full details and preview |
| `skillhub install <name>` | Install for Claude Code |
| `skillhub install <name> --all-agents` | Install for all 4 agents |
| `skillhub uninstall <name>` | Remove a skill |
| `skillhub update` | Update all installed skills |
| `skillhub init <name>` | Scaffold a new SKILL.md |
| `skillhub publish <path>` | Submit to registry via PR |

</details>

---

## Available Skills (34)

<details>
<summary><b>Browse all 34 skills</b></summary>

### Research & Analysis
| Skill | Description |
|-------|-------------|
| `research-agent` | Multi-source deep research with synthesis and citations |
| `rag-evaluator` | Evaluate RAG pipelines: faithfulness, relevance, hallucination |
| `llm-evaluator` | Build evaluation frameworks for LLM outputs |

### Code Quality
| Skill | Description |
|-------|-------------|
| `code-reviewer` | Five-axis review: correctness, security, performance, readability, maintainability |
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
| `typescript-patterns` | Strict types, utility types, generics, discriminated unions, branded types |
| `nextjs-patterns` | App Router, Server Components, data fetching, caching, streaming |
| `fastapi-patterns` | Production FastAPI patterns |
| `api-design` | REST API conventions and best practices |
| `sql-agent` | Write, optimize, and explain SQL with query plans |
| `openai-patterns` | Model selection, structured outputs, function calling, retry logic, cost control |

### DevOps & Infrastructure
| Skill | Description |
|-------|-------------|
| `docker-agent` | Dockerfile optimization, multi-stage builds |
| `git-workflow` | Branching strategies, commit conventions |
| `cicd-agent` | GitHub Actions, secrets, blue-green/canary/rolling deploys |
| `kubernetes-agent` | Manifests, resource sizing, HPA, health probes, networking |
| `data-pipeline` | Idempotency, incremental loads, Airflow DAGs, data quality |
| `performance-optimizer` | Profiling methodology, Python bottlenecks, N+1 fixes, caching |

### Architecture
| Skill | Description |
|-------|-------------|
| `system-design` | RESDAC framework, scalability patterns, database selection, CAP trade-offs |

### AI / ML Engineering
| Skill | Description |
|-------|-------------|
| `agent-builder` | Build LangGraph agents: tools, memory, streaming, multi-agent |
| `prompt-optimizer` | Diagnose and improve underperforming prompts |
| `mle-workflow` | Production ML workflow: data, training, deployment |
| `cost-tracker` | Track and optimize LLM API costs |

### Career
| Skill | Description |
|-------|-------------|
| `yc-job-tracker` | Daily AI/ML job tracking at YC startups |
| `career-ops` | Global AI/ML job hunt — USA, Europe, Singapore, Dubai |

### Community (via agency-agents)
| Skill | Description |
|-------|-------------|
| `frontend-developer` | Senior frontend developer expertise |
| `backend-architect` | Senior backend architecture and system design |
| `penetration-tester` | Security testing methodology |

> Skills from all 13 external ecosystems are also available via their prefix.

</details>

---

## Contributing

skillhub is a community registry — every skill you add helps thousands of developers.

1. Fork this repo
2. Add your skill: `skillhub init <name>` then edit `skills/<name>/SKILL.md`
3. Add an entry to `registry/index.json`
4. Open a PR

Or in one command: `skillhub publish <name>/`

**What makes a good skill?** Focused on one domain, has `## When to Use` and `## Core Rules`, works well when composed with other skills, gives concrete examples over vague advice.

---

## Author

Built by [Chandrashekar DP](https://github.com/chandrudp29) — Senior AI/ML Engineer, Bengaluru.

If skillhub saves you time, **a ⭐ helps others find it.**

[![GitHub stars](https://img.shields.io/github/stars/chandrudp29/skillhub?style=for-the-badge&color=gold)](https://github.com/chandrudp29/skillhub/stargazers)
[![PyPI](https://img.shields.io/pypi/v/skillhub-ai?style=for-the-badge&color=0066cc)](https://pypi.org/project/skillhub-ai/)
[![Follow](https://img.shields.io/badge/Follow-@chandrudp29-1DA1F2?style=for-the-badge&logo=github)](https://github.com/chandrudp29)

---

## License

MIT — use it, fork it, build on it.

---

<div align="center">

**skillhub** · `pip install skillhub-ai` · [PyPI](https://pypi.org/project/skillhub-ai/) · [Issues](https://github.com/chandrudp29/skillhub/issues) · [Discussions](https://github.com/chandrudp29/skillhub/discussions)

</div>
