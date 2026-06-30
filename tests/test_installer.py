"""
Tests for skillhub.installer module.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from skillhub import installer


class TestInstall:
    """Tests for install function."""

    def test_install_creates_file(self, mock_httpx_success, temp_project):
        """Should create skill file in correct location."""
        installed = installer.install("test-skill", agent="claude", project_root=temp_project)

        assert "claude" in installed
        assert installed["claude"].exists()
        assert ".claude/commands/test-skill.md" in str(installed["claude"])

    def test_install_all_agents(self, mock_httpx_success, temp_project):
        """Should install for all agents when all_agents=True."""
        installed = installer.install("test-skill", all_agents=True, project_root=temp_project)

        assert len(installed) == 4
        assert "claude" in installed
        assert "cursor" in installed
        assert "codex" in installed
        assert "gemini" in installed

    def test_install_raises_for_nonexistent_skill(self, mock_httpx_success, temp_project):
        """Should raise ValueError for nonexistent skill."""
        with pytest.raises(ValueError, match="not found"):
            installer.install("nonexistent-xyz", project_root=temp_project)

    def test_install_raises_file_exists(self, mock_httpx_success, temp_project):
        """Should raise FileExistsError if skill already installed."""
        installer.install("test-skill", project_root=temp_project)

        with pytest.raises(FileExistsError):
            installer.install("test-skill", project_root=temp_project)

    def test_install_overwrite(self, mock_httpx_success, temp_project):
        """Should overwrite existing file when overwrite=True."""
        installer.install("test-skill", project_root=temp_project)
        # Should not raise
        installed = installer.install("test-skill", project_root=temp_project, overwrite=True)
        assert installed["claude"].exists()

    def test_install_cursor_creates_mdc(self, mock_httpx_success, temp_project):
        """Should create .mdc file for cursor agent."""
        installed = installer.install("test-skill", agent="cursor", project_root=temp_project)

        assert installed["cursor"].suffix == ".mdc"

    def test_install_codex_appends_to_agents_md(self, mock_httpx_success, temp_project):
        """Should append to AGENTS.md for codex agent."""
        installed = installer.install("test-skill", agent="codex", project_root=temp_project)

        agents_md = temp_project / "AGENTS.md"
        assert agents_md.exists()
        content = agents_md.read_text()
        assert "<!-- skillhub:test-skill -->" in content


class TestUninstall:
    """Tests for uninstall function."""

    def test_uninstall_removes_file(self, mock_httpx_success, temp_project):
        """Should remove installed skill file."""
        installer.install("test-skill", project_root=temp_project)
        removed = installer.uninstall("test-skill", project_root=temp_project)

        assert len(removed) == 1
        assert not removed[0].exists()

    def test_uninstall_nonexistent_returns_empty(self, temp_project):
        """Should return empty list for nonexistent skill."""
        removed = installer.uninstall("nonexistent-xyz", project_root=temp_project)
        assert removed == []

    def test_uninstall_codex_removes_from_agents_md(self, mock_httpx_success, temp_project):
        """Should remove skill block from AGENTS.md."""
        installer.install("test-skill", agent="codex", project_root=temp_project)

        agents_md = temp_project / "AGENTS.md"
        assert "<!-- skillhub:test-skill -->" in agents_md.read_text()

        installer.uninstall("test-skill", agent="codex", project_root=temp_project)
        content = agents_md.read_text()
        assert "<!-- skillhub:test-skill -->" not in content


class TestListInstalled:
    """Tests for list_installed function."""

    def test_list_installed_empty(self, temp_project):
        """Should return empty list when no skills installed."""
        installed = installer.list_installed("claude", project_root=temp_project)
        assert installed == []

    def test_list_installed_finds_skills(self, mock_httpx_success, temp_project):
        """Should list installed skills."""
        installer.install("test-skill", project_root=temp_project)
        installed = installer.list_installed("claude", project_root=temp_project)

        assert "test-skill" in installed

    def test_list_installed_codex(self, mock_httpx_success, temp_project):
        """Should list skills from AGENTS.md for codex."""
        installer.install("test-skill", agent="codex", project_root=temp_project)
        installed = installer.list_installed("codex", project_root=temp_project)

        assert "test-skill" in installed
