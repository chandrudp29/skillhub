"""
Bridge: convert between AGENTS.md (OpenAI Codex / Codex CLI) and SKILL.md (Claude Code).

60,000+ repos use AGENTS.md. Claude Code doesn't load it natively.
`skillhub bridge` fills the gap in both directions:
  --from AGENTS.md   Extract skills from AGENTS.md → install to Claude/Cursor/Gemini
  --to   AGENTS.md   Pack installed Claude skills  → write into AGENTS.md for Codex
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

_MARKER_START = "<!-- skillhub:{name}:start -->"
_MARKER_END = "<!-- skillhub:{name}:end -->"
_BLOCK_START = "<!-- skillhub:managed:start -->"
_BLOCK_END = "<!-- skillhub:managed:end -->"


def _get_install_dir(agent: str, root: Path) -> Path:
    return {
        "claude": root / ".claude" / "commands",
        "cursor": root / ".cursor" / "rules",
        "gemini": root / ".gemini" / "skills",
    }.get(agent, root / ".claude" / "commands")


def _slugify(text: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug[:60] or "bridge"


def from_agents_md(
    agents_path: Path,
    project_root: Optional[Path] = None,
    agent: str = "claude",
) -> list[str]:
    """
    Import AGENTS.md into Claude/Cursor/Gemini skill files.

    Looks for skillhub block markers first. If none found, treats the whole
    AGENTS.md as one skill named from its H1 title (or 'agents-bridge').

    Returns list of installed skill names.
    """
    if not agents_path.exists():
        raise FileNotFoundError(f"{agents_path} not found")

    root = project_root or Path.cwd()
    content = agents_path.read_text()

    # Detect skillhub-managed blocks (written by `bridge --to`)
    managed = re.findall(
        r'<!-- skillhub:(\S+?):start -->(.*?)<!-- skillhub:\1:end -->',
        content,
        re.DOTALL,
    )

    install_dir = _get_install_dir(agent, root)
    install_dir.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []

    if managed:
        for skill_name, body in managed:
            skill_file = install_dir / f"{skill_name}.md"
            skill_file.write_text(body.strip() + "\n")
            installed.append(skill_name)
        return installed

    # No markers — treat whole file as one skill
    title_match = re.match(r'^#\s+(.+)', content.strip())
    skill_name = _slugify(title_match.group(1)) if title_match else "agents-bridge"

    wrapped = (
        f"---\n"
        f"name: {skill_name}\n"
        f"description: Imported from AGENTS.md via skillhub bridge\n"
        f"version: 1.0.0\n"
        f"agents: [{agent}]\n"
        f"source: AGENTS.md\n"
        f"---\n\n"
        f"{content.strip()}\n"
    )

    out = install_dir / f"{skill_name}.md"
    out.write_text(wrapped)
    return [skill_name]


def to_agents_md(
    agents_path: Path,
    project_root: Optional[Path] = None,
    agent: str = "claude",
) -> int:
    """
    Pack all installed skills into AGENTS.md with skillhub block markers.

    Safe to run multiple times — replaces the previous managed block.
    Returns number of skills packed.
    """
    root = project_root or Path.cwd()
    install_dir = _get_install_dir(agent, root)

    if not install_dir.exists():
        raise FileNotFoundError(f"No skills installed for {agent} in {root}")

    skill_files = sorted(install_dir.glob("*.md"))
    if not skill_files:
        raise ValueError(f"No skills installed for {agent}")

    # Read existing AGENTS.md (create if missing)
    existing = agents_path.read_text() if agents_path.exists() else ""

    # Remove previous managed block
    existing = re.sub(
        r'\n?' + re.escape(_BLOCK_START) + r'.*?' + re.escape(_BLOCK_END) + r'\n?',
        '',
        existing,
        flags=re.DOTALL,
    ).rstrip()

    # Build new managed block
    block_lines = [_BLOCK_START, "<!-- managed by skillhub — edit via `skillhub install/uninstall` -->"]

    for f in skill_files:
        name = f.stem
        body = f.read_text().strip()
        start = _MARKER_START.format(name=name)
        end = _MARKER_END.format(name=name)
        block_lines += ["", start, body, end]

    block_lines.append(_BLOCK_END)

    new_content = existing + "\n\n" + "\n".join(block_lines) + "\n"
    agents_path.write_text(new_content)

    return len(skill_files)
