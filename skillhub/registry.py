"""
Registry: fetches and caches the skillhub index from GitHub.
Falls back to bundled index when offline.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import httpx

REGISTRY_URL = "https://raw.githubusercontent.com/chandrudp29/skillhub/main/registry/index.json"
SKILL_BASE_URL = "https://raw.githubusercontent.com/chandrudp29/skillhub/main/skills"
CACHE_DIR = Path.home() / ".skillhub" / "cache"
CACHE_FILE = CACHE_DIR / "index.json"
CACHE_TTL = int(os.environ.get("SKILLHUB_CACHE_TTL", 3600))  # 1 hour default, configurable


def _log_warning(message: str) -> None:
    """Print warning to stderr (visible but non-blocking)."""
    if os.environ.get("SKILLHUB_QUIET") != "1":
        print(f"[skillhub] {message}", file=sys.stderr)


def _bundled_index() -> dict:
    bundled = Path(__file__).parent.parent / "registry" / "index.json"
    if bundled.exists():
        return json.loads(bundled.read_text())
    return {"version": "0.0.0", "skills": []}


def fetch_index(force: bool = False) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    bundled = _bundled_index()

    if not force and CACHE_FILE.exists():
        age = time.time() - CACHE_FILE.stat().st_mtime
        if age < CACHE_TTL:
            cached = json.loads(CACHE_FILE.read_text())
            # prefer whichever has more skills (bundled wins when developing locally)
            if len(bundled.get("skills", [])) > len(cached.get("skills", [])):
                return bundled
            return cached

    try:
        resp = httpx.get(REGISTRY_URL, timeout=10)
        resp.raise_for_status()
        remote = resp.json()
        # prefer the index with more skills so local dev always wins
        data = remote if len(remote.get("skills", [])) >= len(bundled.get("skills", [])) else bundled
        CACHE_FILE.write_text(json.dumps(data, indent=2))
        return data
    except httpx.TimeoutException:
        _log_warning("Registry fetch timed out. Using cached/bundled index.")
    except httpx.ConnectError as e:
        _log_warning(f"Network unreachable: {e}. Using offline mode.")
    except httpx.HTTPStatusError as e:
        _log_warning(f"Registry returned HTTP {e.response.status_code}. Using cached/bundled index.")
    except json.JSONDecodeError as e:
        _log_warning(f"Invalid JSON from registry: {e}. Using cached/bundled index.")
    except Exception as e:
        _log_warning(f"Unexpected error fetching registry: {type(e).__name__}: {e}")

    # Fallback logic for all error cases
    if CACHE_FILE.exists():
        try:
            cached = json.loads(CACHE_FILE.read_text())
            if len(bundled.get("skills", [])) > len(cached.get("skills", [])):
                return bundled
            return cached
        except (json.JSONDecodeError, OSError):
            pass
    return bundled


def search_skills(query: str, tags: Optional[list[str]] = None) -> list[dict]:
    index = fetch_index()
    q = query.lower()
    results = []
    for skill in index.get("skills", []):
        name_match = q in skill["name"].lower()
        desc_match = q in skill.get("description", "").lower()
        tag_match = any(q in t.lower() for t in skill.get("tags", []))
        tag_filter = not tags or any(t in skill.get("tags", []) for t in tags)
        if (name_match or desc_match or tag_match) and tag_filter:
            results.append(skill)
    return results


def get_skill(name: str) -> Optional[dict]:
    index = fetch_index()
    for skill in index.get("skills", []):
        if skill["name"] == name:
            return skill
    return None


def list_all_skills() -> list[dict]:
    return fetch_index().get("skills", [])


def fetch_from_source(
    source: str,
    agent: str = "claude",
    project_root: Optional[Path] = None,
) -> tuple[Optional[str], str]:
    """Fetch skill content from any source. Returns (content, display_name).

    Source formats:
      name                    → skillhub registry
      skills.sh:name          → vercel-labs/skills repo
      agency-agents:name      → msitarzewski/agency-agents repo
      github:owner/repo/path  → any public GitHub raw file
      claude:name             → skill already installed in Claude Code (.claude/commands/)
      cursor:name             → skill already installed in Cursor (.cursor/rules/)
      codex:name              → skill already installed in Codex (AGENTS.md block)
      gemini:name             → skill already installed in Gemini CLI (.gemini/skills/)
      ./local/path.md         → local file on disk
    """
    root = project_root or Path.cwd()

    # ── Local file paths ────────────────────────────────────────────────────
    if source.startswith(("./", "/", "../")):
        p = Path(source) if source.startswith("/") else root / source.lstrip("./")
        if not p.exists():
            p = Path(source)  # try as-is
        if p.exists():
            return p.read_text(), p.stem
        return None, source

    # ── Already-installed agent skills ──────────────────────────────────────
    _INSTALLED_PATHS = {
        "claude":  (".claude", "commands", "{name}.md"),
        "cursor":  (".cursor", "rules", "{name}.mdc"),
        "gemini":  (".gemini", "skills", "{name}.md"),
    }

    for prefix, parts in _INSTALLED_PATHS.items():
        tag = f"{prefix}:"
        if source.startswith(tag):
            skill_name = source[len(tag):]
            p = root / parts[0] / parts[1] / parts[2].format(name=skill_name)
            if p.exists():
                return p.read_text(), f"{prefix}:{skill_name}"
            _log_warning(f"Skill '{skill_name}' not found in {prefix} at {p}")
            return None, source

    if source.startswith("codex:"):
        skill_name = source[6:]
        agents_md = root / "AGENTS.md"
        if agents_md.exists():
            import re as _re
            text = agents_md.read_text()
            pattern = rf"<!-- skillhub:{_re.escape(skill_name)} -->(.*?)<!-- /skillhub:{_re.escape(skill_name)} -->"
            m = _re.search(pattern, text, _re.DOTALL)
            if m:
                return m.group(1).strip(), f"codex:{skill_name}"
        _log_warning(f"Skill '{skill_name}' not found in AGENTS.md")
        return None, source

    # ── Remote registries ───────────────────────────────────────────────────

    def _gh_raw(owner: str, repo: str, path: str) -> Optional[str]:
        """Fetch a raw file from GitHub, trying main then master branch."""
        for branch in ("main", "master"):
            try:
                resp = httpx.get(
                    f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}",
                    timeout=10,
                )
                if resp.status_code == 200:
                    return resp.text
            except Exception:
                pass
        return None

    def _try_paths(owner: str, repo: str, candidates: list[str]) -> Optional[str]:
        for p in candidates:
            content = _gh_raw(owner, repo, p)
            if content:
                return content
        return None

    # github:owner/repo/path/to/SKILL.md  — raw GitHub file
    if source.startswith("github:"):
        path = source[7:]
        parts = path.split("/", 2)
        if len(parts) >= 3:
            owner, repo, file_path = parts[0], parts[1], parts[2]
            content = _gh_raw(owner, repo, file_path)
            if content:
                display = file_path.split("/")[-1].replace(".md", "").replace(".mdc", "")
                return content, f"github/{display}"
        return None, source

    # skills.sh:name  — Vercel's open skills registry
    if source.startswith("skills.sh:"):
        name = source[10:]
        content = _gh_raw("vercel-labs", "skills", f"skills/{name}/SKILL.md")
        if content:
            return content, f"skills.sh/{name}"
        return None, name

    # anthropic:name  — Anthropic's official skills  (anthropics/skills)
    if source.startswith("anthropic:"):
        name = source[10:]
        content = _try_paths("anthropics", "skills", [
            f"skills/{name}/SKILL.md",
            f"skills/{name}.md",
        ])
        if content:
            return content, f"anthropic/{name}"
        _log_warning(f"anthropic skill '{name}' not found in anthropics/skills/skills/")
        return None, name

    # openai:name  — OpenAI / Codex official skills  (openai/skills)
    if source.startswith("openai:"):
        name = source[7:]
        content = _try_paths("openai", "skills", [
            f"skills/.curated/{name}/SKILL.md",
            f"skills/{name}/SKILL.md",
            f"skills/.system/{name}/SKILL.md",
        ])
        if content:
            return content, f"openai/{name}"
        _log_warning(f"openai skill '{name}' not found in openai/skills")
        return None, name

    # copilot:name  — GitHub's awesome-copilot skills  (github/awesome-copilot)
    if source.startswith("copilot:"):
        name = source[8:]
        content = _try_paths("github", "awesome-copilot", [
            f"skills/{name}/SKILL.md",
            f"skills/{name}.md",
        ])
        if content:
            return content, f"copilot/{name}"
        _log_warning(f"copilot skill '{name}' not found in github/awesome-copilot/skills/")
        return None, name

    # microsoft:name  — Microsoft official skills  (microsoft/skills)
    if source.startswith("microsoft:"):
        name = source[10:]
        content = _try_paths("microsoft", "skills", [
            f".github/skills/{name}/SKILL.md",
            f"skills/{name}/SKILL.md",
        ])
        if content:
            return content, f"microsoft/{name}"
        _log_warning(f"microsoft skill '{name}' not found in microsoft/skills")
        return None, name

    # google:name  — Google official skills  (google/skills)
    # skills are organized as skills/{category}/{name}/SKILL.md
    if source.startswith("google:"):
        name = source[7:]
        _GOOGLE_CATEGORIES = ["cloud", "ads", "analytics"]
        candidates_g = [f"skills/{cat}/{name}/SKILL.md" for cat in _GOOGLE_CATEGORIES]
        candidates_g.append(f"skills/{name}/SKILL.md")
        content = _try_paths("google", "skills", candidates_g)
        if content:
            return content, f"google/{name}"
        _log_warning(f"google skill '{name}' not found. Categories: {_GOOGLE_CATEGORIES}")
        return None, name

    # addyosmani:name  — Addy Osmani's production-grade skills  (addyosmani/agent-skills)
    if source.startswith("addyosmani:"):
        name = source[11:]
        content = _try_paths("addyosmani", "agent-skills", [
            f"skills/{name}/SKILL.md",
            f"skills/{name}.md",
        ])
        if content:
            return content, f"addyosmani/{name}"
        _log_warning(f"addyosmani skill '{name}' not found in addyosmani/agent-skills/skills/")
        return None, name

    # scientific:name  — K-Dense AI scientific skills  (K-Dense-AI/scientific-agent-skills)
    if source.startswith("scientific:"):
        name = source[11:]
        content = _try_paths("K-Dense-AI", "scientific-agent-skills", [
            f"skills/{name}/SKILL.md",
            f"skills/{name}.md",
        ])
        if content:
            return content, f"scientific/{name}"
        _log_warning(f"scientific skill '{name}' not found in K-Dense-AI/scientific-agent-skills/skills/")
        return None, name

    # antigravity:name  — Antigravity/OpenClaw community skills  (sickn33/antigravity-awesome-skills)
    if source.startswith("antigravity:"):
        name = source[12:]
        content = _try_paths("sickn33", "antigravity-awesome-skills", [
            f"skills/{name}/SKILL.md",
            f"skills/{name}.md",
        ])
        if content:
            return content, f"antigravity/{name}"
        _log_warning(f"antigravity skill '{name}' not found in sickn33/antigravity-awesome-skills/skills/")
        return None, name

    # gamedev:name  — Game dev skills  (gamedev-skills/awesome-gamedev-agent-skills)
    # skills/{engine-or-discipline}/{name}/SKILL.md
    if source.startswith("gamedev:"):
        name = source[8:]
        _GAMEDEV_CATS = ["disciplines", "genres", "godot", "unity", "other-engines"]
        candidates_gd = [f"skills/{cat}/{name}/SKILL.md" for cat in _GAMEDEV_CATS]
        candidates_gd.append(f"skills/{name}/SKILL.md")
        content = _try_paths("gamedev-skills", "awesome-gamedev-agent-skills", candidates_gd)
        if content:
            return content, f"gamedev/{name}"
        _log_warning(f"gamedev skill '{name}' not found. Categories: {_GAMEDEV_CATS}")
        return None, name

    # tech-leads:name  — Tech Leads Club validated skills  (tech-leads-club/agent-skills)
    # packages/skills-catalog/skills/(category)/{name}/SKILL.md
    if source.startswith("tech-leads:"):
        name = source[11:]
        _TL_CATS = [
            "(architecture)", "(cloud)", "(creation)", "(decision-making)",
            "(design)", "(development)", "(gtm)", "(learning)",
            "(monitoring)", "(performance)", "(quality)", "(security)",
            "(tooling)", "(web-automation)",
        ]
        candidates_tl = [
            f"packages/skills-catalog/skills/{cat}/{name}/SKILL.md"
            for cat in _TL_CATS
        ]
        candidates_tl.append(f"packages/skills-catalog/skills/{name}/SKILL.md")
        content = _try_paths("tech-leads-club", "agent-skills", candidates_tl)
        if content:
            return content, f"tech-leads/{name}"
        _log_warning(f"tech-leads skill '{name}' not found in tech-leads-club/agent-skills")
        return None, name

    # agency-agents:name  — msitarzewski/agency-agents (role-based personalities)
    # {category}/{category}-{name}.md
    if source.startswith("agency-agents:"):
        name = source[14:]
        _AGENCY_CATEGORIES = [
            "engineering", "security", "design", "product", "testing",
            "strategy", "marketing", "sales", "finance", "support",
            "specialized", "academic", "game-development", "spatial-computing",
            "gis", "integrations", "paid-media", "project-management",
        ]
        candidates_aa = [f"{cat}/{cat}-{name}.md" for cat in _AGENCY_CATEGORIES]
        candidates_aa.append(f"engineering/{name}.md")
        content = _try_paths("msitarzewski", "agency-agents", candidates_aa)
        if content:
            return content, f"agency-agents/{name}"
        _log_warning(
            f"agency-agents skill '{name}' not found. "
            f"Try: github:msitarzewski/agency-agents/engineering/engineering-{name}.md"
        )
        return None, name

    # ── Default: skillhub registry ──────────────────────────────────────────
    content = fetch_skill_content(source, agent)
    return content, source


def fetch_skill_content(name: str, agent: str = "claude") -> Optional[str]:
    skill = get_skill(name)
    if not skill:
        return None

    agents = skill.get("agents", ["claude"])
    target_agent = agent if agent in agents else "claude"
    file_map = {
        "claude": "claude.md",
        "cursor": "cursor.md",
        "codex": "codex.md",
        "gemini": "gemini.md",
    }
    filename = file_map.get(target_agent, "claude.md")

    try:
        url = f"{SKILL_BASE_URL}/{name}/{filename}"
        resp = httpx.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.text
        # fallback to SKILL.md
        url = f"{SKILL_BASE_URL}/{name}/SKILL.md"
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except httpx.TimeoutException:
        _log_warning(f"Timeout fetching skill '{name}'. Trying bundled version.")
    except httpx.ConnectError:
        _log_warning(f"Network unreachable. Trying bundled version of '{name}'.")
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            _log_warning(f"HTTP {e.response.status_code} fetching '{name}'. Trying bundled version.")
    except Exception as e:
        _log_warning(f"Error fetching skill '{name}': {type(e).__name__}: {e}")

    # try local bundled skills
    local = Path(__file__).parent.parent / "skills" / name / "SKILL.md"
    if local.exists():
        return local.read_text()
    return None
