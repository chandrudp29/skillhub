"""
Adapters: convert a canonical SKILL.md into the correct format/path for each agent.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentTarget:
    name: str
    install_path: str        # relative to project root, may use {name}
    mode: str                # "file" = standalone file, "append" = append to existing


AGENTS: dict[str, AgentTarget] = {
    "claude": AgentTarget(
        name="claude",
        install_path=".claude/commands/{name}.md",
        mode="file",
    ),
    "cursor": AgentTarget(
        name="cursor",
        install_path=".cursor/rules/{name}.mdc",
        mode="file",
    ),
    "codex": AgentTarget(
        name="codex",
        install_path="AGENTS.md",
        mode="append",
    ),
    "gemini": AgentTarget(
        name="gemini",
        install_path=".gemini/skills/{name}.md",
        mode="file",
    ),
}


def get_install_path(agent: str, skill_name: str, project_root: Path) -> Path:
    target = AGENTS.get(agent)
    if not target:
        raise ValueError(f"Unknown agent '{agent}'. Choose: {list(AGENTS)}")
    rel = target.install_path.format(name=skill_name)
    return project_root / rel


def adapt_content(content: str, agent: str, skill_name: str) -> str:
    """Wrap skill content in agent-specific header if needed."""
    if agent == "codex":
        return f"\n\n<!-- skillhub:{skill_name} -->\n{content}\n<!-- /skillhub:{skill_name} -->\n"
    return content


def install_skill_to_agent(
    content: str,
    agent: str,
    skill_name: str,
    project_root: Path,
    overwrite: bool = False,
) -> Path:
    target = AGENTS[agent]
    dest = get_install_path(agent, skill_name, project_root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    adapted = adapt_content(content, agent, skill_name)

    if target.mode == "append":
        if dest.exists():
            existing = dest.read_text()
            marker = f"<!-- skillhub:{skill_name} -->"
            if marker in existing:
                # already installed — replace block
                import re
                pattern = rf"<!-- skillhub:{re.escape(skill_name)} -->.*?<!-- /skillhub:{re.escape(skill_name)} -->"
                existing = re.sub(pattern, adapted.strip(), existing, flags=re.DOTALL)
                dest.write_text(existing)
            else:
                dest.write_text(existing + adapted)
        else:
            dest.write_text(adapted)
    else:
        if dest.exists() and not overwrite:
            raise FileExistsError(f"{dest} already exists. Use --overwrite to replace.")
        dest.write_text(adapted)

    return dest
