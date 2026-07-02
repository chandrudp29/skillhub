"""
Composer: the killer feature.
Merges multiple skills into one unified skill file, resolving conflicts.
Supports two strategies: first-wins (default) and ai (Claude-powered merge).
Supports any source: skillhub registry, skills.sh:name, github:owner/repo/path, ./local.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from .registry import fetch_from_source, fetch_skill_content, get_skill


_EXTERNAL_PREFIXES = (
    # Installed-agent prefixes (read from local project dir)
    "claude:", "cursor:", "codex:", "gemini:",
    # Remote ecosystem registries
    "skills.sh:",       # Vercel (vercel-labs/skills)
    "agency-agents:",   # msitarzewski/agency-agents
    "anthropic:",       # anthropics/skills  (official)
    "openai:",          # openai/skills  (official)
    "copilot:",         # github/awesome-copilot  (official)
    "microsoft:",       # microsoft/skills  (official)
    "google:",          # google/skills  (official)
    "addyosmani:",      # addyosmani/agent-skills
    "scientific:",      # K-Dense-AI/scientific-agent-skills
    "antigravity:",     # sickn33/antigravity-awesome-skills
    "gamedev:",         # gamedev-skills/awesome-gamedev-agent-skills
    "tech-leads:",      # tech-leads-club/agent-skills
    # Raw GitHub / local / URL
    "github:",
    "./", "/", "../",
    "http://", "https://",
)


def _is_external(source: str) -> bool:
    return source.startswith(_EXTERNAL_PREFIXES)


@dataclass
class ParsedSkill:
    name: str
    display_name: str
    description: str
    frontmatter: dict
    body: str
    sections: dict[str, str] = field(default_factory=dict)


def parse_skill(content: str, name: str, display_name: str = "") -> ParsedSkill:
    frontmatter: dict = {}
    body = content

    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if fm_match:
        try:
            frontmatter = yaml.safe_load(fm_match.group(1)) or {}
        except yaml.YAMLError as e:
            print(f"[skillhub] Warning: Invalid YAML in skill '{name}': {e}", file=sys.stderr)
            frontmatter = {}
        body = fm_match.group(2).strip()

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
        display_name=display_name or name,
        description=frontmatter.get("description", ""),
        frontmatter=frontmatter,
        body=body,
        sections=sections,
    )


def detect_conflicts(skills: list[ParsedSkill]) -> list[tuple[str, str, str]]:
    """Returns list of (section_title, owner_a, owner_b) conflict tuples."""
    conflicts = []
    seen: dict[str, str] = {}
    for skill in skills:
        for section in skill.sections:
            if section == "__preamble__":
                continue
            if section in seen:
                conflicts.append((section, seen[section], skill.display_name))
            else:
                seen[section] = skill.display_name
    return conflicts


def _ai_merge_section(
    section_title: str,
    content_a: str,
    name_a: str,
    content_b: str,
    name_b: str,
) -> tuple[str, bool]:
    """Call Claude to intelligently merge two conflicting sections.

    Returns (merged_content, was_ai_merged). Falls back to first-wins on any failure.
    """
    import os

    try:
        import anthropic  # type: ignore[import-untyped]
    except ImportError:
        print(
            "[skillhub] anthropic package not installed. "
            "Run: pip install anthropic  (or: pip install skillhub-ai[ai])  then retry.",
            file=sys.stderr,
        )
        return content_a, False

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "[skillhub] ANTHROPIC_API_KEY not set. "
            "Export it or use --strategy first-wins.",
            file=sys.stderr,
        )
        return content_a, False

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": (
                    f"You are merging two AI agent skill files. "
                    f"Intelligently merge the '## {section_title}' sections below into one unified best-of-both version.\n\n"
                    f"SKILL A ({name_a}):\n{content_a}\n\n"
                    f"SKILL B ({name_b}):\n{content_b}\n\n"
                    f"Rules:\n"
                    f"- Return ONLY the merged markdown content (no section header, no explanation)\n"
                    f"- If both say the same thing differently, keep the clearer version\n"
                    f"- If they are complementary, combine both\n"
                    f"- If they contradict, prefer the more specific/actionable guidance\n"
                    f"- Preserve all bullet points, numbered lists, and code blocks"
                ),
            }],
        )
        return response.content[0].text.strip(), True
    except Exception as e:
        print(f"[skillhub] AI merge failed ({e}). Falling back to first-wins.", file=sys.stderr)
        return content_a, False


def compose(
    skill_sources: list[str],
    output_name: str,
    agent: str = "claude",
    project_root: Optional[Path] = None,
    install: bool = True,
    strategy: str = "first-wins",
) -> tuple[str, list[str]]:
    """
    Merge multiple skills into one unified file.

    skill_sources: list of skill names or source URIs (skills.sh:, github:, ./local)
    strategy: "first-wins" (default) or "ai" (Claude-powered merge)
    Returns (composed_content, list_of_conflict_descriptions).
    """
    root = project_root or Path.cwd()
    parsed: list[ParsedSkill] = []

    for source in skill_sources:
        if _is_external(source):
            content, display_name = fetch_from_source(source, agent, project_root=root)
            if not content:
                raise RuntimeError(f"Could not fetch content from '{source}'")
            parsed.append(parse_skill(content, source, display_name))
        else:
            meta = get_skill(source)
            if not meta:
                raise ValueError(f"Skill '{source}' not found in registry.")
            content = fetch_skill_content(source, agent)
            if not content:
                raise RuntimeError(f"Could not fetch content for '{source}'")
            parsed.append(parse_skill(content, source))

    merged_sections: dict[str, str] = {}
    conflict_log: list[str] = []

    for skill in parsed:
        for section, body in skill.sections.items():
            if section == "__preamble__":
                continue
            if section not in merged_sections:
                merged_sections[section] = f"<!-- from: {skill.display_name} -->\n{body}"
            else:
                # Conflict: section already exists
                existing_owner = next(
                    (s.display_name for s in parsed if section in s.sections and s.display_name != skill.display_name),
                    "unknown",
                )
                if strategy == "ai":
                    existing_body = merged_sections[section]
                    clean_existing = re.sub(r"^<!-- from: .* -->\n", "", existing_body)
                    merged_body, was_ai = _ai_merge_section(section, clean_existing, existing_owner, body, skill.display_name)
                    label = "ai-merged" if was_ai else "fallback-first-wins"
                    merged_sections[section] = f"<!-- {label}: {existing_owner} + {skill.display_name} -->\n{merged_body}"
                    verb = "AI-merged" if was_ai else "Conflict (AI unavailable, kept first-wins)"
                    conflict_log.append(f"{verb}: '## {section}' ({existing_owner} + {skill.display_name})")
                else:
                    conflict_log.append(
                        f"Section conflict '## {section}': kept {existing_owner}, skipped {skill.display_name}"
                    )

    preambles = [
        s.sections.get("__preamble__", "").strip()
        for s in parsed
        if s.sections.get("__preamble__")
    ]
    preamble_block = "\n\n".join(preambles) if preambles else ""

    all_tags: set[str] = set()
    for s in parsed:
        all_tags.update(s.frontmatter.get("tags", []))

    combined_desc = "; ".join(
        f"{s.display_name}: {s.description}" for s in parsed if s.description
    )[:1024]

    source_names = ", ".join(s.display_name for s in parsed)

    frontmatter_block = (
        f"---\n"
        f"name: {output_name}\n"
        f"description: Composed from [{source_names}]. {combined_desc}\n"
        f"composed_from: [{source_names}]\n"
        + (f"compose_strategy: {strategy}\n" if strategy != "first-wins" else "")
        + f"tags: [{', '.join(sorted(all_tags))}]\n"
        f"---"
    )

    section_blocks = ""
    for title, body in merged_sections.items():
        section_blocks += f"\n\n## {title}\n\n{body}"

    composed = (
        f"{frontmatter_block}\n\n"
        f"# {output_name.replace('-', ' ').title()}\n\n"
        f"{preamble_block}"
        f"{section_blocks}"
    )

    if install:
        from .adapters import install_skill_to_agent
        install_skill_to_agent(composed, agent, output_name, root, overwrite=True)

    return composed, conflict_log


def diff(
    skill_a: str,
    skill_b: str,
    agent: str = "claude",
    project_root: Optional[Path] = None,
) -> dict:
    """
    Compare two skills section by section.
    Returns a dict with keys: only_a, only_b, conflicts, skill_a_name, skill_b_name.
    """
    root = project_root or Path.cwd()

    if _is_external(skill_a):
        content_a, name_a = fetch_from_source(skill_a, agent, project_root=root)
    else:
        content_a = fetch_skill_content(skill_a, agent)
        name_a = skill_a
    if not content_a:
        raise ValueError(f"Could not fetch '{skill_a}'")

    if _is_external(skill_b):
        content_b, name_b = fetch_from_source(skill_b, agent, project_root=root)
    else:
        content_b = fetch_skill_content(skill_b, agent)
        name_b = skill_b
    if not content_b:
        raise ValueError(f"Could not fetch '{skill_b}'")

    parsed_a = parse_skill(content_a, skill_a, name_a)
    parsed_b = parse_skill(content_b, skill_b, name_b)

    secs_a = {k for k in parsed_a.sections if k != "__preamble__"}
    secs_b = {k for k in parsed_b.sections if k != "__preamble__"}

    return {
        "skill_a_name": name_a,
        "skill_b_name": name_b,
        "only_a": sorted(secs_a - secs_b),
        "only_b": sorted(secs_b - secs_a),
        "conflicts": sorted(secs_a & secs_b),
        "total_a": len(secs_a),
        "total_b": len(secs_b),
    }
