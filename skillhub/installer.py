"""
Installer: orchestrates fetching a skill from registry and writing to project.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .adapters import AGENTS, install_skill_to_agent
from .registry import fetch_skill_content, get_skill


def _update_skills_json(skill_meta: dict, root: Path) -> None:
    """Write/update .claude/skills.json with a lightweight index for agent routing."""
    skills_json = root / ".claude" / "skills.json"
    skills_json.parent.mkdir(parents=True, exist_ok=True)

    index: dict = {"_skillhub": "1.0", "skills": {}}
    if skills_json.exists():
        try:
            index = json.loads(skills_json.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    name = skill_meta["name"]
    index["skills"][name] = {
        "path": f"commands/{name}.md",
        "description": skill_meta.get("description", ""),
        "triggers": skill_meta.get("triggers", []),
    }
    skills_json.write_text(json.dumps(index, indent=2))


def install(
    skill_name: str,
    agent: str = "claude",
    all_agents: bool = False,
    project_root: Optional[Path] = None,
    overwrite: bool = False,
) -> dict[str, Path]:
    root = project_root or Path.cwd()

    skill_meta = get_skill(skill_name)
    if not skill_meta:
        raise ValueError(f"Skill '{skill_name}' not found in registry. Run: skillhub search {skill_name}")

    targets = list(AGENTS.keys()) if all_agents else [agent]
    supported = skill_meta.get("agents", ["claude"])

    installed: dict[str, Path] = {}
    for tgt in targets:
        if tgt not in supported:
            continue
        content = fetch_skill_content(skill_name, tgt)
        if not content:
            # fallback: use bundled SKILL.md
            content = fetch_skill_content(skill_name, "claude")
        if not content:
            raise RuntimeError(f"Could not fetch content for '{skill_name}'")

        path = install_skill_to_agent(content, tgt, skill_name, root, overwrite)
        installed[tgt] = path

    if "claude" in installed:
        _update_skills_json(skill_meta, root)

    return installed


def uninstall(skill_name: str, agent: str = "claude", project_root: Optional[Path] = None) -> list[Path]:
    from .adapters import get_install_path, AGENTS
    import re

    root = project_root or Path.cwd()
    removed = []

    targets = [agent] if agent != "all" else list(AGENTS.keys())
    for tgt in targets:
        dest = get_install_path(tgt, skill_name, root)
        target_cfg = AGENTS[tgt]
        if target_cfg.mode == "append" and dest.exists():
            text = dest.read_text()
            pattern = rf"\n\n<!-- skillhub:{re.escape(skill_name)} -->.*?<!-- /skillhub:{re.escape(skill_name)} -->\n"
            new_text = re.sub(pattern, "", text, flags=re.DOTALL)
            dest.write_text(new_text)
            removed.append(dest)
        elif dest.exists():
            dest.unlink()
            removed.append(dest)

    return removed


def list_installed(agent: str = "claude", project_root: Optional[Path] = None) -> list[str]:
    from .adapters import AGENTS

    root = project_root or Path.cwd()
    target = AGENTS.get(agent)
    if not target:
        return []

    if target.mode == "file":
        base = root / target.install_path.format(name="").rstrip("/").rstrip("\\")
        parent = Path(str(base).replace("{name}", "").rsplit("/", 1)[0])
        if agent == "claude":
            parent = root / ".claude" / "commands"
        elif agent == "cursor":
            parent = root / ".cursor" / "rules"
        elif agent == "gemini":
            parent = root / ".gemini" / "skills"

        if not parent.exists():
            return []
        return [p.stem for p in parent.iterdir() if p.suffix in (".md", ".mdc")]

    elif target.mode == "append":
        import re
        agents_file = root / "AGENTS.md"
        if not agents_file.exists():
            return []
        text = agents_file.read_text()
        return re.findall(r"<!-- skillhub:(\S+?) -->", text)

    return []
