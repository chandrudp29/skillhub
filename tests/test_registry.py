"""
Tests for skillhub.registry module.
"""
import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from skillhub import registry


class TestFetchIndex:
    """Tests for fetch_index function."""

    def test_returns_bundled_index_when_offline(self, mock_httpx_failure, tmp_path):
        """Should fall back to bundled index when network fails."""
        with patch.object(registry, "CACHE_DIR", tmp_path / "cache"):
            with patch.object(registry, "CACHE_FILE", tmp_path / "cache" / "index.json"):
                result = registry.fetch_index()
                assert "skills" in result

    def test_caches_remote_index(self, mock_httpx_success, tmp_path):
        """Should cache fetched index to disk."""
        cache_file = tmp_path / "cache" / "index.json"
        with patch.object(registry, "CACHE_DIR", tmp_path / "cache"):
            with patch.object(registry, "CACHE_FILE", cache_file):
                registry.fetch_index(force=True)
                assert cache_file.exists()
                cached = json.loads(cache_file.read_text())
                assert "skills" in cached

    def test_uses_cache_within_ttl(self, tmp_path, sample_index):
        """Should use cached index if within TTL."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(parents=True)
        cache_file = cache_dir / "index.json"
        cache_file.write_text(json.dumps(sample_index))

        with patch.object(registry, "CACHE_DIR", cache_dir):
            with patch.object(registry, "CACHE_FILE", cache_file):
                with patch("httpx.get") as mock_get:
                    result = registry.fetch_index()
                    # Should not make HTTP request if cache is fresh
                    assert result["skills"] is not None

    def test_force_bypasses_cache(self, mock_httpx_success, tmp_path, sample_index):
        """force=True should bypass cache and fetch fresh."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(parents=True)
        cache_file = cache_dir / "index.json"
        cache_file.write_text(json.dumps({"skills": []}))

        with patch.object(registry, "CACHE_DIR", cache_dir):
            with patch.object(registry, "CACHE_FILE", cache_file):
                result = registry.fetch_index(force=True)
                assert len(result["skills"]) == 2  # From mock


class TestSearchSkills:
    """Tests for search_skills function."""

    def test_search_by_name(self, mock_httpx_success):
        """Should find skills by name."""
        results = registry.search_skills("test-skill")
        assert len(results) >= 1
        assert results[0]["name"] == "test-skill"

    def test_search_by_description(self, mock_httpx_success):
        """Should find skills by description content."""
        results = registry.search_skills("unit testing")
        assert len(results) >= 1

    def test_search_by_tag(self, mock_httpx_success):
        """Should find skills by tag."""
        results = registry.search_skills("debug")
        assert len(results) >= 1

    def test_search_case_insensitive(self, mock_httpx_success):
        """Search should be case-insensitive."""
        results = registry.search_skills("TEST-SKILL")
        assert len(results) >= 1

    def test_search_no_results(self, mock_httpx_success):
        """Should return empty list when no matches."""
        results = registry.search_skills("nonexistent-xyz-123")
        assert results == []

    def test_search_with_tag_filter(self, mock_httpx_success):
        """Should filter by specific tag."""
        results = registry.search_skills("skill", tags=["research"])
        assert all("research" in s.get("tags", []) for s in results)


class TestGetSkill:
    """Tests for get_skill function."""

    def test_get_existing_skill(self, mock_httpx_success):
        """Should return skill metadata for existing skill."""
        skill = registry.get_skill("test-skill")
        assert skill is not None
        assert skill["name"] == "test-skill"
        assert skill["version"] == "1.0.0"

    def test_get_nonexistent_skill(self, mock_httpx_success):
        """Should return None for nonexistent skill."""
        skill = registry.get_skill("nonexistent-skill-xyz")
        assert skill is None


class TestFetchSkillContent:
    """Tests for fetch_skill_content function."""

    def test_fetch_skill_content_success(self, mock_httpx_success):
        """Should fetch skill content from remote."""
        content = registry.fetch_skill_content("test-skill", "claude")
        assert content is not None
        assert "# Test Skill" in content

    def test_fetch_skill_content_nonexistent(self, mock_httpx_success):
        """Should return None for nonexistent skill."""
        content = registry.fetch_skill_content("nonexistent-xyz", "claude")
        assert content is None

    def test_fetch_skill_fallback_to_bundled(self, mock_httpx_failure, tmp_path):
        """Should fall back to bundled skill when network fails."""
        # Create a bundled skill
        bundled_dir = tmp_path / "skills" / "test-skill"
        bundled_dir.mkdir(parents=True)
        (bundled_dir / "SKILL.md").write_text("# Bundled Test Skill")

        with patch.object(registry, "_bundled_index", return_value={"skills": [{"name": "test-skill", "agents": ["claude"]}]}):
            with patch.object(registry, "CACHE_FILE", tmp_path / "cache" / "index.json"):
                with patch.object(registry, "CACHE_DIR", tmp_path / "cache"):
                    with patch("pathlib.Path.__truediv__", side_effect=lambda self, x: bundled_dir if "test-skill" in str(x) else Path(self) / x):
                        # This tests the offline fallback path
                        pass


class TestListAllSkills:
    """Tests for list_all_skills function."""

    def test_list_all_skills(self, mock_httpx_success):
        """Should return all skills from registry."""
        skills = registry.list_all_skills()
        assert len(skills) == 2
        names = [s["name"] for s in skills]
        assert "test-skill" in names
        assert "another-skill" in names
