"""
Composer: the killer feature.
Merges multiple skills into one unified skill file, resolving conflicts.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from .registry import fetch_skill_content, get_skill


@dataclass
class ParsedSkill:
    name: str
    description: str
    frontmatter: dict
    body: str
    sections: dict[str, str] = field(default_factory=dict)


def _parse_skill(content: str, name: str) -> ParsedSkill:
    frontmatter: dict = {}
    body = content

    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if fm_match:
        try:
            frontmatter = yaml.safe_load(fm_match.group(1)) or {}
        except yaml.YAMLError as e:
            import sys
            print(f"[skillhub] Warning: Invalid YAML in skill '{name}': {e}", file=sys.stderr)
            frontmatter = {}
        body = fm_match.group(2).strip()

    # Extract H2 sections
    sections: dict[str, str] = {}
    current_title = "__preamble__"
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections[current_title] = "\n".join(current_lines).strip()

    return ParsedSkill(
        name=name,
        description=frontmatter.get("description", ""),
        frontmatter=frontmatter,
        body=body,
        sections=sections,
    )


def _detect_conflicts(skills: list[ParsedSkill]) -> list[str]:
    conflicts = []
    seen_sections: dict[str, str] = {}
    for skill in skills:
        for section in skill.sections:
            if section == "__preamble__":
                continue
            if section in seen_sections:
                conflicts.append(
                    f"Section conflict: '{section}' exists in both '{seen_sections[section]}' and '{skill.name}'"
                )
            else:
                seen_sections[section] = skill.name
    return conflicts


def compose(
    skill_names: list[str],
    output_name: str,
    agent: str = "claude",
    project_root: Optional[Path] = None,
    install: bool = True,
) -> tuple[str, list[str]]:
    """
    Merge multiple skills into one.
    Returns (composed_content, list_of_conflicts_resolved).
    """
    root = project_root or Path.cwd()
    parsed: list[ParsedSkill] = []

    for name in skill_names:
        meta = get_skill(name)
        if not meta:
            raise ValueError(f"Skill '{name}' not found in registry.")
        content = fetch_skill_content(name, agent)
        if not content:
            raise RuntimeError(f"Could not fetch content for '{name}'")
        parsed.append(_parse_skill(content, name))

    conflicts = _detect_conflicts(parsed)

    # Merge descriptions
    combined_desc = "; ".join(
        f"{s.name}: {s.description}" for s in parsed if s.description
    )[:1024]

    # Merge sections — first-writer wins on conflicts, but note them
    merged_sections: dict[str, str] = {}
    for skill in parsed:
        for section, body in skill.sections.items():
            if section == "__preamble__":
                continue
            if section not in merged_sections:
                merged_sections[section] = f"<!-- from: {skill.name} -->\n{body}"

    # Merge preambles
    preambles = [
        s.sections.get("__preamble__", "").strip()
        for s in parsed
        if s.sections.get("__preamble__")
    ]
    preamble_block = "\n\n".join(preambles) if preambles else ""

    # Compose tags
    all_tags: set[str] = set()
    for s in parsed:
        all_tags.update(s.frontmatter.get("tags", []))

    # Build the output
    source_names = ", ".join(skill_names)
    frontmatter_block = (
        f"---\n"
        f"name: {output_name}\n"
        f"description: Composed skill from [{source_names}]. {combined_desc}\n"
        f"composed_from: [{source_names}]\n"
        f"tags: [{', '.join(sorted(all_tags))}]\n"
        f"---"
    )

    section_blocks = ""
    for section_title, section_body in merged_sections.items():
        section_blocks += f"\n\n## {section_title}\n\n{section_body}"

    composed = f"{frontmatter_block}\n\n# {output_name.replace('-', ' ').title()}\n\n{preamble_block}{section_blocks}"

    if install:
        from .adapters import install_skill_to_agent
        install_skill_to_agent(composed, agent, output_name, root, overwrite=True)

    return composed, conflicts
