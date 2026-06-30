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
