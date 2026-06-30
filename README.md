# skillhub

**The package manager for AI agent skills.**

Install, compose, and publish skills for Claude Code, Cursor, Codex, and Gemini CLI — in one command.

```bash
pip install skillhub
skillhub install research-agent
```

---

## The problem

You've been copying skill files manually.

```bash
# What everyone does today
git clone https://github.com/someone/skills
cp skills/research-agent/SKILL.md .claude/commands/
cp skills/research-agent/SKILL.md .cursor/rules/
# now repeat for every skill, every project, every agent
```

There's no versioning. No search. No way to combine skills. And every agent needs a different file in a different place.

**skillhub fixes this.**

---

## Install

```bash
pip install skillhub
```

Requires Python 3.9+. No other dependencies to configure.

---

## Quick Start

```bash
# Search for skills
skillhub search "research"

# Install a skill (Claude Code by default)
skillhub install research-agent

# Install for a specific agent
skillhub install research-agent --agent cursor
skillhub install research-agent --agent codex
skillhub install research-agent --agent gemini

# Install for ALL agents at once
skillhub install research-agent --all-agents

# List everything available
skillhub list

# Show what's installed in this project
skillhub list --installed
```

---

## The Killer Feature: Skill Composer

Combine multiple skills into one unified skill file — conflicts resolved automatically.

```bash
skillhub compose research-agent rag-evaluator code-reviewer
```

Output: a single `.claude/commands/composed-skill.md` (or the equivalent for your agent) that merges all three skills intelligently:

- Combines descriptions
- Merges sections without duplication
- Detects and reports conflicts (first-writer wins)
- Works for Claude, Cursor, Codex, and Gemini

No more manually copy-pasting sections from three different skill files.

---

## Available Skills

| Skill | Description | Agents |
|---|---|---|
| `research-agent` | Multi-source deep research with synthesis and citations | All |
| `rag-evaluator` | Evaluate RAG pipelines: faithfulness, relevance, hallucination | All |
| `code-reviewer` | Five-axis code review with severity labels | All |
| `debug-agent` | Systematic root cause analysis — feedback loop first | All |
| `test-writer` | Write meaningful tests that actually catch bugs | All |
| `pr-summarizer` | Generate PR descriptions: what, why, how, risks | All |
| `cost-tracker` | Track and optimize LLM API costs across providers | All |
| `sql-agent` | Write, optimize, and explain SQL — with query plans | All |
| `doc-generator` | README, API docs, docstrings, changelogs | All |
| `yc-job-tracker` | Daily AI/ML job tracking at YC startups | All |

```bash
skillhub list         # see all skills with descriptions
skillhub info <name>  # see full detail on one skill
```

---

## Agent Support

| Agent | Install path | Config |
|---|---|---|
| Claude Code | `.claude/commands/{name}.md` | default |
| Cursor | `.cursor/rules/{name}.mdc` | `--agent cursor` |
| OpenAI Codex | `AGENTS.md` (appended) | `--agent codex` |
| Gemini CLI | `.gemini/skills/{name}.md` | `--agent gemini` |

---

## Publish Your Skill

Have a skill the community would use? Submit it:

```bash
skillhub publish ./my-skill
```

This opens a guided PR flow to the skillhub registry. The community reviews it for quality — skills that get merged are used by thousands of developers.

[Contribution guide →](CONTRIBUTING.md)

---

## How it Works

skillhub fetches skills from a GitHub-backed registry (`registry/index.json`). Skills are versioned. The registry is cached locally for 1 hour so commands are fast even offline.

```
skillhub install research-agent
    ↓
Fetch registry index from GitHub (cached 1h)
    ↓
Download SKILL.md for your agent
    ↓
Write to the correct path for your agent
    ↓
Done in < 2 seconds
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

The short version:
1. Fork this repo
2. Add your skill under `skills/<your-skill-name>/SKILL.md`
3. Add an entry to `registry/index.json`
4. Open a PR — a human must review the diff before submitting

We review for quality, not quantity. A skill that genuinely helps developers is worth 10 skills that just exist.

---

## Built by

[Chandrashekar DP](https://github.com/chandrudp29) — Senior AI/ML Engineer building open source tools for the AI developer community.

If skillhub saves you time, star it ⭐ — it helps other developers find it.

---

## License

MIT
