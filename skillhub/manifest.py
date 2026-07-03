"""
Project-level skill manifest (skillhub.json) — the package.json for skills.

Enables reproducible skill setups: commit skillhub.json so teammates run
`skillhub install` and get the exact same skills.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

MANIFEST_FILE = "skillhub.json"
MANIFEST_VERSION = "0.4.0"


def manifest_path(root: Optional[Path] = None) -> Path:
    return (root or Path.cwd()) / MANIFEST_FILE


def read_manifest(root: Optional[Path] = None) -> Optional[dict]:
    p = manifest_path(root)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def write_manifest(data: dict, root: Optional[Path] = None) -> Path:
    p = manifest_path(root)
    p.write_text(json.dumps(data, indent=2) + "\n")
    return p


def init_manifest(project_name: str = "", root: Optional[Path] = None) -> Path:
    """Create a new skillhub.json manifest at project root."""
    p = manifest_path(root)
    if p.exists():
        raise FileExistsError(f"{p} already exists")

    data: dict = {
        "_skillhub": MANIFEST_VERSION,
        "name": project_name or (root or Path.cwd()).name,
        "description": "",
        "skills": {},
        "composed": {},
    }
    return write_manifest(data, root)


def add_to_manifest(
    skill_name: str,
    version: str = "latest",
    root: Optional[Path] = None,
) -> dict:
    """Add a skill to the manifest. Creates manifest if it doesn't exist."""
    data = read_manifest(root) or {
        "_skillhub": MANIFEST_VERSION,
        "name": (root or Path.cwd()).name,
        "description": "",
        "skills": {},
        "composed": {},
    }
    data["skills"][skill_name] = version
    write_manifest(data, root)
    return data


def remove_from_manifest(skill_name: str, root: Optional[Path] = None) -> bool:
    """Remove a skill from the manifest. Returns True if it was present."""
    data = read_manifest(root)
    if not data or skill_name not in data.get("skills", {}):
        return False
    del data["skills"][skill_name]
    write_manifest(data, root)
    return True


def get_manifest_skills(root: Optional[Path] = None) -> dict[str, str]:
    """Return {skill_name: version} dict from manifest."""
    data = read_manifest(root)
    if not data:
        return {}
    return dict(data.get("skills", {}))


def lock_manifest(agent: str = "claude", root: Optional[Path] = None) -> dict:
    """Pin all currently installed skills into the manifest with their source info."""
    from .installer import list_installed
    from .registry import get_skill

    installed = list_installed(agent, root)
    data = read_manifest(root) or {
        "_skillhub": MANIFEST_VERSION,
        "name": (root or Path.cwd()).name,
        "description": "",
        "skills": {},
        "composed": {},
    }

    for name in installed:
        meta = get_skill(name)
        version = meta.get("version", "latest") if meta else "latest"
        if name not in data["skills"]:
            data["skills"][name] = version

    write_manifest(data, root)
    return data
