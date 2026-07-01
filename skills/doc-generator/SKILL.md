---
name: doc-generator
description: Generate accurate, useful documentation for code — README files, API docs, inline docstrings, and changelogs. Use when user needs to document code, write a README, or generate API reference docs.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [documentation, readme, api-docs, docstrings, changelog]
triggers: ['documentation', 'readme', 'docstring', 'api docs', 'write docs', 'generate docs']
---

# Doc Generator

Generates documentation that developers actually read and use — not boilerplate that everyone ignores.

## When to Use

- "Write a README for this project"
- "Add docstrings to these functions"
- "Generate API documentation"
- "Write a changelog entry for this release"
- Before open-sourcing or sharing any code

## README Generation

A README answers these questions in this order:

**1. What is this? (one sentence)**
Not "a powerful, flexible, enterprise-grade solution" — what does it actually do?

**2. Why would I use this? (one paragraph)**
What problem does it solve? What's the alternative? When should I NOT use it?

**3. How do I install it? (one command)**
```bash
pip install yourpackage
```

**4. How do I use it? (minimal working example)**
The simplest thing that works, copy-pasteable, tested:
```python
from yourpackage import Thing
result = Thing().do_something("input")
print(result)  # "expected output"
```

**5. Full API / configuration reference**
Only after the quick example. Developers who need it will scroll; those who don't won't be overwhelmed.

**6. Contributing / Development setup**
How to run tests, how to open a PR.

### README Template

```markdown
# project-name

One sentence: what it does.

## Install

\`\`\`bash
pip install project-name
\`\`\`

## Quick Start

\`\`\`python
[minimal working example]
\`\`\`

## Why project-name?

[problem it solves, who it's for, what makes it different]

## Usage

[fuller examples and configuration]

## API Reference

[function signatures and descriptions]

## Contributing

[how to set up dev environment, run tests, open PRs]

## License

MIT
```

## Docstring Generation

Write docstrings that explain WHY and WHAT, not HOW (the code shows how):

**Good**:
```python
def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks for RAG ingestion.

    Overlap prevents context loss at chunk boundaries — a sentence split
    across two chunks is still fully recoverable during retrieval.

    Args:
        text: The document text to split. Handles Unicode correctly.
        max_tokens: Target chunk size. Actual chunks may be slightly larger
                    to avoid splitting mid-sentence.
        overlap: Tokens of overlap between consecutive chunks.

    Returns:
        List of text chunks, ordered by position in the original text.

    Raises:
        ValueError: If max_tokens < overlap.
    """
```

**Bad** (just describes the signature):
```python
def chunk_text(text: str, max_tokens: int = 512) -> list[str]:
    """Chunks text with max_tokens tokens and returns a list of strings."""
```

### Docstring Rules

- Explain the non-obvious: why overlap exists, what the side effects are, what errors to expect
- Include types in Args even if type-hinted (they appear in generated API docs)
- For complex return values, describe the structure
- For functions with important behavior (mutation, I/O, randomness) — say so explicitly

## Changelog Generation

Changelogs are for users, not developers. Format:

```markdown
## [1.2.0] — 2026-06-30

### Added
- Skill Composer: merge multiple skills into one with conflict detection
- `--all-agents` flag on `skillhub install` to install for all agents at once

### Changed  
- Registry now caches locally for 1 hour (was fetched on every command)

### Fixed
- `skillhub list --installed` now works correctly for Codex (AGENTS.md)

### Removed
- Deprecated `--format` flag removed (use `--agent` instead)
```

Keep entries user-facing: "Added streaming support" not "Refactored response handler to use async generator." The commit history is for the latter.

## Quality Check Before Delivering Docs

- [ ] The quick start example is copy-pasteable and actually works
- [ ] Install command is correct
- [ ] No placeholder text ("Coming soon", "TODO", "Description here")
- [ ] No documentation of private/internal APIs in public docs
- [ ] Code examples use realistic inputs, not `foo`, `bar`, `test`
