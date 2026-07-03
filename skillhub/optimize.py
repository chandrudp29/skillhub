"""
Context optimizer: reduce token usage by deduplicating redundant sections
across the installed skill set. Solves "context rot" — the token bloat problem
named by Microsoft where loading all skills dilutes attention and wastes tokens.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def estimate_tokens(text: str) -> int:
    """Rough estimate: ~1 token per 4 characters."""
    return max(1, len(text) // 4)


def _strip_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Strip YAML frontmatter; return (frontmatter_fields, body)."""
    fields: dict[str, str] = {}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            fm_block = content[3:end].strip()
            for line in fm_block.split("\n"):
                if ":" in line:
                    k, _, v = line.partition(":")
                    fields[k.strip()] = v.strip()
            return fields, content[end + 3:].lstrip()
    return fields, content


def _parse_sections(body: str) -> list[tuple[str, str]]:
    """Return ordered list of (heading, content) pairs, preserving order."""
    sections: list[tuple[str, str]] = []
    current_heading = ""
    current_lines: list[str] = []

    for line in body.split("\n"):
        m = re.match(r'^(#{1,3})\s+(.+)', line)
        if m:
            if current_heading or current_lines:
                sections.append((current_heading, "\n".join(current_lines).rstrip()))
            current_heading = m.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_heading or current_lines:
        sections.append((current_heading, "\n".join(current_lines).rstrip()))

    return sections


def _get_skills_dir(agent: str, root: Path) -> Path:
    return {
        "claude": root / ".claude" / "commands",
        "cursor": root / ".cursor" / "rules",
        "gemini": root / ".gemini" / "skills",
    }.get(agent, root / ".claude" / "commands")


def optimize(
    agent: str = "claude",
    project_root: Optional[Path] = None,
    output_name: str = "optimized",
    install: bool = True,
) -> tuple[str, int, int, dict[str, int]]:
    """
    Scan installed skills, deduplicate repeated sections, produce a lean bundle.

    Returns (bundle_text, original_tokens, optimized_tokens, duplicates_map)
    where duplicates_map is {section_heading: count_of_skills_that_had_it}.
    """
    root = project_root or Path.cwd()
    skills_dir = _get_skills_dir(agent, root)

    if not skills_dir.exists():
        raise FileNotFoundError(f"No installed skills for {agent} at {skills_dir}")

    skill_files = [
        f for f in sorted(skills_dir.glob("*.md"))
        if f.stem != output_name
    ]
    if not skill_files:
        raise FileNotFoundError(f"No skill files in {skills_dir}")

    # Parse each skill
    parsed: list[tuple[str, dict[str, str], list[tuple[str, str]]]] = []
    for f in skill_files:
        raw = f.read_text()
        fm, body = _strip_frontmatter(raw)
        sections = _parse_sections(body)
        parsed.append((f.stem, fm, sections))

    # Count section heading occurrences
    heading_count: dict[str, int] = {}
    for _, _, sections in parsed:
        for heading, _ in sections:
            if heading:
                heading_count[heading] = heading_count.get(heading, 0) + 1

    duplicates = {h: c for h, c in heading_count.items() if c > 1}

    # Build optimized bundle
    seen_headings: set[str] = set()
    out_lines: list[str] = [
        "---",
        f"name: {output_name}",
        f"description: Token-optimized bundle — {len(skill_files)} skills, duplicates removed",
        "version: 1.0.0",
        f"source_skills: {', '.join(f.stem for f in skill_files)}",
        "generated_by: skillhub optimize",
        "---",
        "",
    ]

    for skill_name, _fm, sections in parsed:
        skill_added = False
        for heading, content in sections:
            if not heading and not content.strip():
                continue

            # If heading appears in multiple skills, only include once (first-wins)
            if heading and heading in duplicates and heading in seen_headings:
                continue

            if not skill_added:
                out_lines.append(f"\n<!-- ── {skill_name} ── -->")
                skill_added = True

            out_lines.append(content)
            out_lines.append("")
            if heading:
                seen_headings.add(heading)

    bundle = "\n".join(out_lines)

    # Calculate savings
    original_text = "".join(f.read_text() for f in skill_files)
    original_tokens = estimate_tokens(original_text)
    optimized_tokens = estimate_tokens(bundle)

    if install:
        out_path = skills_dir / f"{output_name}.md"
        out_path.write_text(bundle)

    return bundle, original_tokens, optimized_tokens, duplicates
