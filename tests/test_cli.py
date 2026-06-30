"""
Tests for skillhub CLI (main.py).
"""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from skillhub.main import app


runner = CliRunner()


class TestSearchCommand:
    """Tests for 'skillhub search' command."""

    def test_search_displays_results(self, mock_httpx_success):
        """Should display matching skills."""
        result = runner.invoke(app, ["search", "test"])
        assert result.exit_code == 0
        assert "test-skill" in result.output

    def test_search_no_results(self, mock_httpx_success):
        """Should show message when no results."""
        result = runner.invoke(app, ["search", "nonexistent-xyz-123"])
        assert result.exit_code == 1
        assert "No skills found" in result.output


class TestListCommand:
    """Tests for 'skillhub list' command."""

    def test_list_all_skills(self, mock_httpx_success):
        """Should list all available skills."""
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "test-skill" in result.output
        assert "another-skill" in result.output

    def test_list_installed_empty(self, temp_project):
        """Should show message when no skills installed."""
        with patch("skillhub.main.Path.cwd", return_value=temp_project):
            result = runner.invoke(app, ["list", "--installed"])
            assert "No skills installed" in result.output


class TestInfoCommand:
    """Tests for 'skillhub info' command."""

    def test_info_shows_details(self, mock_httpx_success):
        """Should display skill details."""
        result = runner.invoke(app, ["info", "test-skill"])
        assert result.exit_code == 0
        assert "test-skill" in result.output
        assert "1.0.0" in result.output
        assert "test-author" in result.output

    def test_info_not_found(self, mock_httpx_success):
        """Should show error for nonexistent skill."""
        result = runner.invoke(app, ["info", "nonexistent-xyz"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestInstallCommand:
    """Tests for 'skillhub install' command."""

    def test_install_success(self, mock_httpx_success, temp_project):
        """Should install skill successfully."""
        with patch("skillhub.main.Path.cwd", return_value=temp_project):
            with patch("skillhub.installer.Path.cwd", return_value=temp_project):
                result = runner.invoke(app, ["install", "test-skill"])
                assert result.exit_code == 0
                assert "Done!" in result.output

    def test_install_not_found(self, mock_httpx_success, temp_project):
        """Should show error for nonexistent skill."""
        with patch("skillhub.main.Path.cwd", return_value=temp_project):
            result = runner.invoke(app, ["install", "nonexistent-xyz"])
            assert result.exit_code == 1
            assert "not found" in result.output.lower() or "error" in result.output.lower()


class TestUninstallCommand:
    """Tests for 'skillhub uninstall' command."""

    def test_uninstall_not_found(self, temp_project):
        """Should show message when skill not installed."""
        with patch("skillhub.main.Path.cwd", return_value=temp_project):
            with patch("skillhub.installer.Path.cwd", return_value=temp_project):
                result = runner.invoke(app, ["uninstall", "nonexistent"])
                assert "not found" in result.output


class TestComposeCommand:
    """Tests for 'skillhub compose' command."""

    def test_compose_requires_two_skills(self):
        """Should require at least 2 skills."""
        result = runner.invoke(app, ["compose", "single-skill"])
        assert result.exit_code == 1
        assert "at least 2" in result.output

    def test_compose_with_no_install(self, mock_httpx_success, temp_project):
        """Should print composed skill with --no-install."""
        with patch("skillhub.main.Path.cwd", return_value=temp_project):
            with patch("skillhub.composer.Path.cwd", return_value=temp_project):
                result = runner.invoke(app, [
                    "compose", "test-skill", "another-skill",
                    "--no-install", "-o", "merged"
                ])
                assert result.exit_code == 0


class TestMainCallback:
    """Tests for main app callback."""

    def test_no_command_shows_help(self):
        """Should show help when no command given."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "skillhub" in result.output
        assert "install" in result.output
