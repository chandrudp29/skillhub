# Contributing to skillhub

Skills are reviewed for quality before merging. One excellent skill is worth ten mediocre ones.

## Before You Submit

Ask yourself:
- **Is this skill genuinely useful to other developers?** Not just to me, not just for my project.
- **Does it describe a workflow, not just facts?** Skills are processes, not reference docs.
- **Is it specific and actionable?** "Run `npm test`" beats "verify the tests work."

If yes to all three — welcome.

## What We Will Not Accept

- Skills that only work for one specific company's stack
- Skills that add third-party service dependencies without a fallback
- Rewrites of existing skills without clear improvement evidence
- Duplicate skills (search first: `skillhub search <topic>`)
- Bulk submissions (one skill per PR, understood deeply)

## Skill Format

Every skill is a folder under `skills/` containing:

```
skills/
  your-skill-name/
    SKILL.md       ← required
    skill.json     ← required
```

### SKILL.md frontmatter (required)

```yaml
---
name: your-skill-name
description: What this skill does and when to use it. Max 1024 chars.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [tag1, tag2, tag3]
---
```

### skill.json (required)

```json
{
  "name": "your-skill-name",
  "display_name": "Your Skill Name",
  "description": "One-line description for the registry listing.",
  "version": "1.0.0",
  "agents": ["claude", "cursor", "codex", "gemini"],
  "tags": ["tag1", "tag2"],
  "author": "your-github-username",
  "license": "MIT"
}
```

### registry/index.json entry (required)

Add your skill to `registry/index.json` in alphabetical order:

```json
{
  "name": "your-skill-name",
  "display_name": "Your Skill Name",
  "description": "One-line description.",
  "version": "1.0.0",
  "agents": ["claude", "cursor", "codex", "gemini"],
  "tags": ["tag1", "tag2"],
  "author": "your-github-username",
  "license": "MIT"
}
```

## PR Requirements

1. **One skill per PR.** Split multiple skills into separate PRs.
2. **Fill in the PR template completely.** Empty sections = closed PR.
3. **A human must review the diff before submitting.** If an AI wrote it, you reviewed it.
4. **Disclose your authoring environment** in the PR: wrote by hand, or which AI tool helped.
5. **Real problem only.** Describe the specific scenario where you needed this skill and it didn't exist.

## Skill Quality Bar

Read `skills/research-agent/SKILL.md` and `skills/code-reviewer/SKILL.md` as examples of the quality bar.

Key properties of a good skill:
- **Process over knowledge**: steps to follow, not facts to memorize
- **Specific over general**: exact commands and outputs, not "run the tests"
- **Anti-rationalization**: every step that could be skipped has a rebuttal
- **Verification**: checklist of exit criteria with evidence requirements
- **Under 500 lines**: if longer, split into a main skill + supporting files

## Development Setup

```bash
git clone https://github.com/chandrudp29/skillhub
cd skillhub
pip install -e ".[dev]"

# Verify the CLI works
skillhub list
skillhub install research-agent
```

## Questions

Open an issue before starting work on a large skill — saves you time if it's already in progress.
