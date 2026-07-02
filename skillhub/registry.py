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
    if source.startswith("github:"):
        path = source[7:]
        parts = path.split("/", 2)
        if len(parts) >= 3:
            owner, repo, file_path = parts[0], parts[1], parts[2]
            for branch in ("main", "master"):
                url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
                try:
                    resp = httpx.get(url, timeout=10)
                    if resp.status_code == 200:
                        display = file_path.split("/")[-1].replace(".md", "").replace(".mdc", "")
                        return resp.text, f"github/{display}"
                except Exception:
                    pass
        return None, source

    if source.startswith("skills.sh:"):
        skill_name = source[10:]
        for branch in ("main", "master"):
            url = f"https://raw.githubusercontent.com/vercel-labs/skills/{branch}/skills/{skill_name}/SKILL.md"
            try:
                resp = httpx.get(url, timeout=10)
                if resp.status_code == 200:
                    return resp.text, f"skills.sh/{skill_name}"
            except Exception:
                pass
        return None, skill_name

    if source.startswith("agency-agents:"):
        skill_name = source[14:]
        # Files live in category folders named {category}/{category}-{skill}.md
        # e.g. engineering/engineering-frontend-developer.md
        _AGENCY_CATEGORIES = [
            "engineering", "security", "design", "product", "testing",
            "strategy", "marketing", "sales", "finance", "support",
            "specialized", "academic", "game-development", "spatial-computing",
            "gis", "integrations", "paid-media", "project-management",
        ]
        candidates: list[str] = []
        for cat in _AGENCY_CATEGORIES:
            candidates.append(f"{cat}/{cat}-{skill_name}.md")
        # Also try direct name in root of each category
        candidates.append(f"engineering/{skill_name}.md")
        for file_path in candidates:
            url = f"https://raw.githubusercontent.com/msitarzewski/agency-agents/main/{file_path}"
            try:
                resp = httpx.get(url, timeout=10)
                if resp.status_code == 200:
                    return resp.text, f"agency-agents/{skill_name}"
            except Exception:
                pass
        _log_warning(f"agency-agents skill '{skill_name}' not found. "
                     f"Try: github:msitarzewski/agency-agents/engineering/engineering-{skill_name}.md")
        return None, skill_name

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
