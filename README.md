<div align="center">

```
███████╗██╗  ██╗██╗██╗     ██╗     ██╗  ██╗██╗   ██╗██████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██║  ██║██║   ██║██╔══██╗
███████╗█████╔╝ ██║██║     ██║     ███████║██║   ██║██████╔╝
╚════██║██╔═██╗ ██║██║     ██║     ██╔══██║██║   ██║██╔══██╗
███████║██║  ██╗██║███████╗███████╗██║  ██║╚██████╔╝██████╔╝
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝
```

### The skill composer for AI agents

**Merge skills from Anthropic · OpenAI · GitHub Copilot · Microsoft · Google · Vercel and 8 more ecosystems**
**into one expert skill — with AI-powered conflict resolution.**

<br>

[![PyPI version](https://img.shields.io/pypi/v/skillhub-ai.svg?style=for-the-badge&color=0066cc)](https://pypi.org/project/skillhub-ai/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/skillhub-ai?style=for-the-badge&color=22c55e&label=installs%2Fmonth)](https://pypi.org/project/skillhub-ai/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/chandrudp29/skillhub/actions/workflows/ci.yml/badge.svg?style=for-the-badge)](https://github.com/chandrudp29/skillhub/actions/workflows/ci.yml)

<br>

```bash
pip install skillhub-ai
```

<br>

> **There are 50+ tools to install AI agent skills.**
> **There is exactly one tool that merges them. This is it.**

<br>

</div>

---

## Why skillhub?

Every AI coding tool has its own skill/rules format. Skills live scattered across:
- `.claude/commands/` in Claude Code
- `.cursor/rules/` in Cursor
- `AGENTS.md` in OpenAI Codex
- Dozens of GitHub repos from Anthropic, OpenAI, Microsoft, Google...

You end up with skills that **conflict**, **duplicate**, and **can't talk to each other.**

**skillhub solves this in one command:**

```bash
# Turn 3 skills into 1 expert — from 3 different companies
skillhub compose anthropic:security-hardening \
               openai:aspnet-core \
               google:agent-platform-deploy \
               -o my-cloud-security-expert
```

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [The 13 Ecosystems](#the-13-ecosystems--source-prefix-table)
- [Compose — The Killer Feature](#compose--the-killer-feature)
- [AI-Powered Merge](#ai-powered-merge)
- [Diff Before You Merge](#diff-before-you-merge)
- [Pre-Built Expert Templates](#pre-built-expert-templates)
- [Install to Any Agent](#install-to-any-agent)
- [Search & Discover](#search--discover)
- [How Compose Works](#how-compose-works-under-the-hood)
- [All Commands](#all-commands)
- [Available Skills (26)](#available-skills-26)
- [Create & Publish Your Own Skill](#create--publish-your-own-skill)
- [Contributing](#contributing)

---

## Features

| | What it does |
|---|---|
| 🔀 **Compose** | Merge 2–10 skills from any ecosystem into one unified expert skill |
| 🤖 **AI Merge** | Claude resolves section conflicts intelligently (no manual editing) |
| 🔍 **Diff** | See exactly what will conflict before composing |
| 🌐 **13 Ecosystems** | Pull skills from Anthropic, OpenAI, Copilot, Microsoft, Google, and 8 more |
| 🤝 **4 Agents** | Claude Code, Cursor, OpenAI Codex, Gemini CLI — all supported |
| 📦 **Templates** | 5 pre-built expert configurations, ready to use in one command |
| 🔌 **Local + Remote** | Mix registry skills, GitHub URLs, and local `.md` files freely |
| 🏗️ **Scaffold** | `skillhub init` creates a proper SKILL.md template in seconds |

---

## Quick Start

```bash
# Install
pip install skillhub-ai

# Browse what's available
skillhub list
skillhub search "security"

# See what's inside a skill before installing
skillhub info debug-agent

# Install a skill (writes to .claude/commands/ by default)
skillhub install debug-agent

# Install for ALL agents at once
skillhub install debug-agent --all-agents

# Compare two skills section by section
skillhub diff python-patterns security-review

# Compose a pre-built expert template
skillhub compose --template fastapi-expert

# Compose your own from any ecosystem
skillhub compose anthropic:claude-api openai:aspnet-core -o my-cloud-expert
```

---

## The 13 Ecosystems — Source Prefix Table

> [!TIP]
> Any prefix below works anywhere a skill name is accepted: `compose`, `diff`, `install`, `info`.

```bash
# Pull from 13 different ecosystems in a single compose command
skillhub compose \
  anthropic:claude-api \          # Anthropic's official skill
  openai:aspnet-core \            # OpenAI's official skill
  copilot:acquire-codebase-knowledge \ # GitHub Copilot's official skill
  microsoft:skill-creator \       # Microsoft's official skill
  google:agent-platform-deploy \  # Google's official skill (auto-searches categories)
  addyosmani:code-review-and-quality \ # Addy Osmani's production skills
  scientific:astropy \            # K-Dense AI scientific skills
  antigravity:ab-test-setup \     # Antigravity/OpenClaw community skills
  gamedev:godot-2d-movement \     # Game dev skills (auto-searches engines)
  tech-leads:domain-analysis \    # Tech Leads Club validated skills
  agency-agents:frontend-developer \ # Role-based expert personas
  skills.sh:typescript-expert \   # Vercel's skills.sh registry
  debug-agent \                   # skillhub's own registry (no prefix)
  -o the-ultimate-expert
```

| Prefix | Ecosystem | GitHub Repo | Skills |
|--------|-----------|-------------|--------|
| *(no prefix)* | **skillhub** registry | [chandrudp29/skillhub](https://github.com/chandrudp29/skillhub) | 26 curated |
| `anthropic:name` | **Anthropic** official | [anthropics/skills](https://github.com/anthropics/skills) | Claude-native |
| `openai:name` | **OpenAI / Codex** official | [openai/skills](https://github.com/openai/skills) | Codex-native |
| `copilot:name` | **GitHub Copilot** official | [github/awesome-copilot](https://github.com/github/awesome-copilot) | Copilot-native |
| `microsoft:name` | **Microsoft** official | [microsoft/skills](https://github.com/microsoft/skills) | Enterprise |
| `google:name` | **Google** official | [google/skills](https://github.com/google/skills) | Cloud/Ads/Analytics |
| `skills.sh:name` | **Vercel** skills.sh | [vercel-labs/skills](https://github.com/vercel-labs/skills) | 857K installs |
| `agency-agents:name` | **Agency Agents** | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | Role personas |
| `addyosmani:name` | **Addy Osmani** | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production-grade |
| `scientific:name` | **K-Dense AI** | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | Research/Science |
| `antigravity:name` | **Antigravity** | [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) | Community |
| `gamedev:name` | **Game Dev Skills** | [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) | Unity/Godot/more |
| `tech-leads:name` | **Tech Leads Club** | [tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills) | Architecture/Cloud |
| `claude:name` | Your **Claude Code** project | `.claude/commands/` | Local |
| `cursor:name` | Your **Cursor** project | `.cursor/rules/` | Local |
| `codex:name` | Your **Codex** project | `AGENTS.md` | Local |
| `gemini:name` | Your **Gemini CLI** project | `.gemini/skills/` | Local |
| `github:owner/repo/path` | **Any public GitHub** file | raw.githubusercontent.com | Unlimited |
| `./path/to/file.md` | **Local file** on disk | — | Unlimited |

---

## Compose — The Killer Feature

![skillhub compose demo](docs/compose.gif)

> [!IMPORTANT]
> No other tool does this. `skillhub compose` is the only way to merge multiple SKILL.md files into one unified expert skill with conflict detection and resolution.

```bash
# The simplest case — 3 skills become 1 expert
skillhub compose python-patterns security-review api-design -o fastapi-expert

# Cross-company compose — Anthropic + OpenAI + Google in one command
skillhub compose anthropic:claude-api openai:aspnet-core google:agent-platform-deploy -o cloud-expert

# Mix everything — local files, GitHub raw URLs, any ecosystem
skillhub compose \
  agency-agents:frontend-developer \
  skills.sh:typescript-expert \
  ./my-team-standards.md \
  -o our-frontend-expert

# Preview the output without writing any files
skillhub compose python-patterns security-review -o test --dry-run
```

**What happens when you compose:**

```
Input skills:          python-patterns  +  security-review  +  api-design
                              │                  │                  │
                    ┌─────────┴──────────────────┴──────────────────┘
                    │
                    ▼
            Parse all ## sections
            Detect duplicate headings (conflicts)
                    │
              ┌─────┴──────────────────────┐
              │                            │
        strategy: first-wins         strategy: ai
        (default, instant)          (Claude resolves each conflict)
              │                            │
              └─────────────┬──────────────┘
                            │
                            ▼
              Write to .claude/commands/fastapi-expert.md
              Update .claude/skills.json
                            │
                            ▼
                    /fastapi-expert  ✓
```

---

## AI-Powered Merge

![skillhub ai-compose demo](docs/ai-compose.gif)

```bash
pip install "skillhub-ai[ai]"       # one-time: adds the anthropic SDK
export ANTHROPIC_API_KEY=sk-...

# Now conflicts are resolved by Claude, not by "first wins"
skillhub compose python-patterns security-review -o secure-python --strategy ai
```

Two strategies — pick what fits:

| Strategy | Speed | What happens when two skills have the same `## Error Handling` section |
|----------|-------|-------------------------------------------------------------------------|
| `first-wins` | Instant | First skill's version is kept; conflict is logged |
| `ai` | ~2s/conflict | Claude reads both versions and writes a unified best-of-both |

When you use `--strategy ai`, Claude reads both conflicting sections and generates a single, coherent section that preserves the best guidance from each. No more choosing which skill to trust.

---

## Diff Before You Merge

![skillhub diff demo](docs/diff.gif)

```bash
# See exactly what's in each skill and what will conflict before composing
skillhub diff python-patterns security-review
```

Output:
```
Comparing: python-patterns  vs  security-review
────────────────────────────────────────────────
✅ Only in python-patterns (6):  Type Annotations, Async Patterns, Dataclasses...
✅ Only in security-review  (5):  OWASP Top 10, Input Validation, Auth Patterns...
⚠️  Conflicts (2):               Error Handling, Code Review Checklist
```

You know exactly what you're getting before a single file is written.

---

## Pre-Built Expert Templates

![skillhub templates demo](docs/templates.gif)

```bash
skillhub templates                                         # list all 5
skillhub compose --template fastapi-expert                 # instant expert
skillhub compose --template ml-platform --strategy ai      # with AI merge
```

| Template | Skills inside | Best for |
|----------|--------------|----------|
| `fastapi-expert` | python-patterns + security-review + api-design | FastAPI/Python backend |
| `fullstack-expert` | react-patterns + python-patterns + api-design | Full-stack developers |
| `ml-platform` | agent-builder + mle-workflow + llm-evaluator | ML platform engineers |
| `pre-pr-reviewer` | code-reviewer + security-review + test-writer | Pre-PR quality gate |
| `research-analyst` | research-agent + rag-evaluator + doc-generator | Research & analysis |

---

## Install to Any Agent

![skillhub install demo](docs/discover-install.gif)

```bash
skillhub install debug-agent                  # Claude Code (default)
skillhub install debug-agent --agent cursor   # Cursor
skillhub install debug-agent --agent codex    # OpenAI Codex
skillhub install debug-agent --agent gemini   # Gemini CLI
skillhub install debug-agent --all-agents     # all 4 at once
skillhub install debug-agent --dry-run        # preview only
```

| Agent | Skill File Path | How to Use |
|-------|----------------|------------|
| **Claude Code** | `.claude/commands/<name>.md` | Type `/<name>` in Claude |
| **Cursor** | `.cursor/rules/<name>.mdc` | Active in every chat |
| **OpenAI Codex** | `AGENTS.md` (with markers) | Auto-loaded by Codex |
| **Gemini CLI** | `.gemini/skills/<name>.md` | Active in every session |

---

## Search & Discover

![skillhub search demo](docs/search.gif)

```bash
skillhub list                          # browse all 26 skills
skillhub list --installed              # skills active in this project
skillhub search "security"             # search by keyword
skillhub search "react" --tag ui       # filter by tag
skillhub info debug-agent              # full preview before installing
```

---

## How Compose Works Under the Hood

```
skillhub compose python-patterns security-review api-design -o fastapi-expert
         │
         ├─ Step 1: Fetch ──────────────────────────────────────────────────
         │          Each source is resolved independently.
         │          Registry skills: fetched from GitHub CDN
         │          anthropic:, openai:, copilot:, google:, ... → GitHub raw
         │          ./local.md → read from disk
         │          All are normalized to SKILL.md format.
         │
         ├─ Step 2: Parse ──────────────────────────────────────────────────
         │          YAML frontmatter is extracted (name, description, tags)
         │          Markdown body is split into ## sections
         │          Sections become a merge dictionary
         │
         ├─ Step 3: Merge ──────────────────────────────────────────────────
         │          Unique sections: kept as-is (with attribution comment)
         │          Duplicate sections:
         │            --strategy first-wins → first skill wins, conflict logged
         │            --strategy ai → Claude reads both, writes unified version
         │
         ├─ Step 4: Write ──────────────────────────────────────────────────
         │          Combined frontmatter with all tags merged
         │          composed_from: [python-patterns, security-review, api-design]
         │          Written to agent-specific path
         │
         └─ Step 5: Done ───────────────────────────────────────────────────
                    /fastapi-expert is now active in Claude Code
```

---

## All Commands

```bash
# ── Discovery ──────────────────────────────────────────────────────────────
skillhub list                              # all 26 registry skills
skillhub list --installed                  # skills in this project
skillhub search <query>                    # search by keyword
skillhub search <query> --tag <tag>        # filter by tag
skillhub info <name>                       # full preview

# ── Install & Manage ───────────────────────────────────────────────────────
skillhub install <name>                    # install for Claude Code
skillhub install <name> --agent cursor     # install for Cursor
skillhub install <name> --all-agents       # install for all 4 agents
skillhub install <name> --dry-run          # preview without writing
skillhub install <name> --overwrite        # replace existing
skillhub uninstall <name>                  # remove a skill
skillhub update                            # update all installed skills

# ── Compose ────────────────────────────────────────────────────────────────
skillhub compose <a> <b> ... -o <name>             # merge (first-wins)
skillhub compose <a> <b> ... -o <name> --strategy ai  # merge with Claude AI
skillhub compose --template <name>                 # use a pre-built template
skillhub compose --template <name> --strategy ai   # template + AI merge
skillhub compose <a> <b> -o <name> --dry-run       # preview without writing
skillhub compose <a> <b> -o <name> --no-install    # return content only
skillhub templates                                 # list all 5 templates

# ── Cross-ecosystem compose (any prefix works) ─────────────────────────────
skillhub compose anthropic:security-hardening openai:aspnet-core -o expert
skillhub compose copilot:codebase-knowledge microsoft:skill-creator -o expert
skillhub compose addyosmani:code-review scientific:astropy -o expert
skillhub compose agency-agents:frontend-developer skills.sh:react-expert -o expert
skillhub compose github:owner/repo/path/SKILL.md ./local.md -o expert

# ── Diff ───────────────────────────────────────────────────────────────────
skillhub diff <a> <b>                      # compare two skills
skillhub diff anthropic:security openai:aspnet-core  # cross-ecosystem diff

# ── Create & Publish ───────────────────────────────────────────────────────
skillhub init <name>                       # scaffold a new SKILL.md
skillhub publish <path>                    # open a PR to add it to the registry
```

**Full reference:**

| Command | What it does |
|---------|-------------|
| `skillhub diff <a> <b>` | Compare two skills section by section |
| `skillhub compose <a> <b> -o <name>` | Merge skills (first-wins on conflicts) |
| `skillhub compose ... --strategy ai` | Merge with Claude AI resolution |
| `skillhub compose --template <name>` | Use a pre-built expert template |
| `skillhub templates` | List all built-in templates |
| `skillhub search <query>` | Search by name, description, or tag |
| `skillhub list` | Browse all 26 skills |
| `skillhub list --installed` | Show skills installed in this project |
| `skillhub info <name>` | Full details and preview |
| `skillhub install <name>` | Install for Claude Code |
| `skillhub install <name> --all-agents` | Install for all 4 agents |
| `skillhub install <name> --dry-run` | Preview without writing files |
| `skillhub install <name> --overwrite` | Replace existing installation |
| `skillhub uninstall <name>` | Remove a skill |
| `skillhub update` | Update all installed skills to latest |
| `skillhub init <name>` | Scaffold a new SKILL.md template |
| `skillhub publish <path>` | Submit to the registry via GitHub PR |

---

## Available Skills (26)

### Research & Analysis
| Skill | Description |
|-------|-------------|
| `research-agent` | Multi-source deep research with synthesis and citations |
| `rag-evaluator` | Evaluate RAG pipelines: faithfulness, relevance, hallucination |
| `llm-evaluator` | Build evaluation frameworks for LLM outputs |

### Code Quality
| Skill | Description |
|-------|-------------|
| `code-reviewer` | Five-axis code review: correctness, security, performance, readability, maintainability |
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
| `penetration-tester` | Security testing and penetration testing methodology |

> [!NOTE]
> Skills from 13 external ecosystems (Anthropic, OpenAI, Copilot, Microsoft, Google, and more)
> are available via their source prefix — see the [13 Ecosystems table](#the-13-ecosystems--source-prefix-table) above.

---

## Create & Publish Your Own Skill

```bash
# 1. Scaffold a new skill
skillhub init our-coding-standards
# → creates our-coding-standards/SKILL.md with full template

# 2. Edit it with your team's conventions
# The SKILL.md format is Anthropic's open standard — supported by 32+ tools

# 3. Test it locally
skillhub install our-coding-standards/
# → type /our-coding-standards in Claude Code to verify

# 4. Submit it to the registry
skillhub publish our-coding-standards/
# → opens a GitHub PR — we review for usefulness, not quantity
```

**SKILL.md format:**

```markdown
---
name: our-coding-standards
description: Company coding standards for backend engineers
version: 1.0.0
tags: [python, standards, backend]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when writing, reviewing, or refactoring any backend code.

## Core Rules
- All functions must have type annotations
- Use dataclasses over plain dicts for structured data
- ...

## Examples
...
```

---

## Cross-Ecosystem Recipes

Copy-paste these into your terminal:

```bash
# ── The Ultimate Python Expert ──────────────────────────────────────────────
skillhub compose python-patterns security-review api-design -o python-expert --strategy ai

# ── Enterprise Frontend ─────────────────────────────────────────────────────
skillhub compose \
  agency-agents:frontend-developer \
  addyosmani:code-review-and-quality \
  react-patterns \
  -o enterprise-frontend --strategy ai

# ── AI/ML Platform Engineer ─────────────────────────────────────────────────
skillhub compose --template ml-platform --strategy ai

# ── Cloud Architecture Expert (3 companies' best practices) ─────────────────
skillhub compose \
  anthropic:claude-api \
  google:agent-platform-deploy \
  microsoft:skill-creator \
  -o cloud-ai-expert

# ── Security-First Developer ────────────────────────────────────────────────
skillhub compose security-review python-patterns addyosmani:code-review-and-quality \
  -o security-first

# ── Scientific Python Research ──────────────────────────────────────────────
skillhub compose scientific:astropy python-patterns rag-evaluator -o research-scientist

# ── Game Dev + Web Stack ─────────────────────────────────────────────────────
skillhub compose gamedev:godot-2d-movement react-patterns python-patterns \
  -o gamedev-web

# ── Pre-PR Code Review Gate ──────────────────────────────────────────────────
skillhub compose --template pre-pr-reviewer --strategy ai
```

---

## Contributing

skillhub is a community registry. Every skill you add helps thousands of developers.

```bash
# Fork → add skill → PR
skillhub init <your-skill-name>
# edit SKILL.md
skillhub publish <your-skill-name>/
```

**What makes a good skill?**
- Focused on one domain or role
- Has clear `## When to Use` and `## Core Rules` sections
- Works well when composed with other skills
- Concrete examples, not vague advice

Skills are reviewed for **usefulness**, not quantity. One great skill beats ten generic ones.

---

## Author

Built by [Chandrashekar DP](https://github.com/chandrudp29) — Senior AI/ML Engineer, Bengaluru.

**If skillhub saves you time, a ⭐ helps others find it.**

[![GitHub stars](https://img.shields.io/github/stars/chandrudp29/skillhub?style=for-the-badge&color=gold)](https://github.com/chandrudp29/skillhub/stargazers)
[![PyPI](https://img.shields.io/pypi/v/skillhub-ai?style=for-the-badge&color=0066cc)](https://pypi.org/project/skillhub-ai/)

---

## License

MIT — use it, fork it, build on it.

---

<div align="center">

**skillhub** — the skill composer for AI agents

`pip install skillhub-ai`

[PyPI](https://pypi.org/project/skillhub-ai/) · [GitHub](https://github.com/chandrudp29/skillhub) · [Issues](https://github.com/chandrudp29/skillhub/issues)

</div>
