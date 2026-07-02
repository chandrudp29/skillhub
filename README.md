# skillhub

[![PyPI version](https://img.shields.io/pypi/v/skillhub-ai.svg)](https://pypi.org/project/skillhub-ai/)
[![CI](https://github.com/chandrudp29/skillhub/actions/workflows/ci.yml/badge.svg)](https://github.com/chandrudp29/skillhub/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Skills](https://img.shields.io/badge/skills-26-purple.svg)](#available-skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**There are 50 tools to install AI agent skills. There is exactly one tool that merges them.**

skillhub is the **skill composer** — merge skills from any source (skillhub registry, skills.sh, GitHub, local files) into one expert skill, with AI-powered conflict resolution.

```bash
pip install skillhub-ai
```

---

## The problem

You install 6 skills across Claude Code, Cursor, and Codex. Now you have:
- The same `## When to Use` section in 4 different files, all contradicting each other
- A `python-patterns` skill that conflicts with your `CLAUDE.md`
- `security-review` in Claude but not in Cursor
- No way to combine two skills without manually copy-pasting markdown

**skillhub solves all of this.**

---

## See what's in two skills before you merge them

![skillhub diff demo](docs/diff.gif)

```bash
skillhub diff python-patterns react-patterns
```

Section-by-section comparison. Green = unique to A. Yellow = conflict. Blue = unique to B.
You know exactly what will happen before you compose.

---

## Compose — the feature nobody else has built

![skillhub compose demo](docs/compose.gif)

```bash
skillhub compose python-patterns security-review api-design -o fastapi-expert
```

Three skills become one expert. All sections merged. Conflicts detected and resolved. One file written to your agent.

```
# In Claude Code:
/fastapi-expert
```

Your agent now applies Python conventions, OWASP security, and REST best practices in every response — without you prompting for each one.

---

## AI-powered merge — Claude resolves conflicts intelligently

![skillhub ai-compose demo](docs/ai-compose.gif)

```bash
pip install "skillhub-ai[ai]"        # adds the anthropic SDK
export ANTHROPIC_API_KEY=sk-...

skillhub compose python-patterns security-review -o secure-python --strategy ai
```

Two strategies:

| Strategy | What happens on conflict |
|----------|------------------------|
| `first-wins` (default) | First skill's section wins, conflict logged |
| `ai` | Claude reads both versions and writes a unified best-of-both |

When `--strategy ai` is set, conflicting sections like `## Error Handling` from two different skills get merged by Claude into a single, coherent section that preserves the best guidance from both.

---

## Pre-built expert templates

![skillhub templates demo](docs/templates.gif)

```bash
skillhub templates                                         # list all 5
skillhub compose --template fastapi-expert                 # instant expert
skillhub compose --template fastapi-expert --strategy ai   # with AI merge
```

| Template | Skills inside | What you get |
|----------|--------------|-------------|
| `fastapi-expert` | python-patterns + security-review + api-design | FastAPI backend expert |
| `fullstack-expert` | react-patterns + python-patterns + api-design | Full-stack expert |
| `ml-platform` | agent-builder + mle-workflow + llm-evaluator | ML platform engineer |
| `pre-pr-reviewer` | code-reviewer + security-review + test-writer | Pre-PR quality gate |
| `research-analyst` | research-agent + rag-evaluator + doc-generator | Research analyst |

---

## Compose from any source — not just this registry

![skillhub cross-ecosystem demo](docs/cross.gif)

```bash
# Combine this registry with addyosmani's agent-skills on GitHub
skillhub compose debug-agent \
  github:addyosmani/agent-skills/skills/code-review-and-quality/SKILL.md \
  -o super-reviewer

# Combine skills.sh (Vercel's registry) with your local team standards
skillhub compose skills.sh:react-expert ./my-team-standards.md -o team-expert

# Mix everything
skillhub compose python-patterns \
  skills.sh:typescript-expert \
  github:owner/repo/skills/custom/SKILL.md \
  ./local-style.md \
  -o polyglot-expert
```

| Source prefix | Where it fetches from |
|--------------|----------------------|
| `name` (no prefix) | skillhub registry (26 skills) |
| `skills.sh:name` | Vercel's skills.sh registry |
| `github:owner/repo/path/SKILL.md` | Any public GitHub repo |
| `./path/to/file.md` | Local file on disk |

---

## Install skills — works for all 4 agents

![skillhub install demo](docs/discover-install.gif)

```bash
skillhub install debug-agent                  # Claude Code (default)
skillhub install debug-agent --all-agents     # all 4 agents at once
skillhub install debug-agent --dry-run        # preview before writing
```

| Agent | Install Path |
|-------|-------------|
| **Claude Code** | `.claude/commands/<name>.md` |
| **Cursor** | `.cursor/rules/<name>.mdc` |
| **OpenAI Codex** | `AGENTS.md` (appended with markers) |
| **Gemini CLI** | `.gemini/skills/<name>.md` |

---

## Search and discover

![skillhub search demo](docs/search.gif)

```bash
skillhub list                          # browse all 26 skills
skillhub search "security"             # search by keyword
skillhub search "react" --tag ui       # filter by tag
skillhub info debug-agent              # full preview before installing
```

---

## Create your own skill

![skillhub init demo](docs/init.gif)

```bash
skillhub init our-coding-standards
# → creates our-coding-standards/SKILL.md with template

# Edit it, then:
skillhub install our-coding-standards      # test locally → /our-coding-standards in Claude
skillhub publish our-coding-standards/    # open a PR to add it to the registry
```

---

## How compose works

```
skillhub compose python-patterns security-review api-design -o fastapi-expert
         │
         ▼
┌──────────────────────────────────────────┐
│  Fetch each skill from its source        │
│  registry / skills.sh / GitHub / local   │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Parse all ## sections                   │
│  Detect conflicts across skills          │
└──────────────────────────────────────────┘
         │
         ├─── strategy: first-wins ──→  first skill's section kept
         │
         └─── strategy: ai ─────────→  Claude merges both intelligently
         │
         ▼
┌──────────────────────────────────────────┐
│  Write composed skill to agent path      │
│  .claude/commands/fastapi-expert.md      │
│                                          │
│  Updates .claude/skills.json index       │
└──────────────────────────────────────────┘
         │
         ▼
      /fastapi-expert ✓
```

---

## Full command reference

| Command | What it does |
|---------|-------------|
| `skillhub diff <a> <b>` | Compare two skills section by section |
| `skillhub compose <a> <b> -o <name>` | Merge skills (first-wins on conflicts) |
| `skillhub compose <a> <b> -o <name> --strategy ai` | Merge with Claude AI resolution |
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

---

## Quick start

```bash
pip install skillhub-ai

# Browse what's available
skillhub list
skillhub templates

# See what's in two skills before merging
skillhub diff debug-agent code-reviewer

# Compose a pre-built expert (5 templates available)
skillhub compose --template fastapi-expert

# Compose your own
skillhub compose debug-agent code-reviewer -o my-reviewer

# Use AI to resolve conflicts intelligently
pip install "skillhub-ai[ai]"
export ANTHROPIC_API_KEY=sk-...
skillhub compose debug-agent code-reviewer -o my-reviewer --strategy ai

# Pull from any source
skillhub compose skills.sh:react-expert python-patterns -o my-expert
```

---

## Cookbook

Copy-paste recipes for the most common workflows → **[docs/cookbook.md](docs/cookbook.md)**

---

## Contributing

1. Fork this repo
2. Add your skill under `skills/<name>/SKILL.md`
3. Add an entry to `registry/index.json`
4. Open a PR — we review for usefulness, not quantity

Or use the CLI:
```bash
skillhub init <name>
# edit the SKILL.md
skillhub publish <name>/
```

---

## Author

Built by [Chandrashekar DP](https://github.com/chandrudp29) — Senior AI/ML Engineer.

If skillhub saves you time, a ⭐ helps others find it.

---

## License

MIT
