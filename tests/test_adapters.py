"""
Tests for skillhub.adapters module.
"""
import pytest
from pathlib import Path

from skillhub.adapters import (
    AGENTS,
    AgentTarget,
    get_install_path,
    adapt_content,
    install_skill_to_agent,
)


class TestAgentTargets:
    """Tests for agent configuration."""

    def test_all_agents_defined(self):
        """All expected agents should be defined."""
        assert "claude" in AGENTS
        assert "cursor" in AGENTS
        assert "codex" in AGENTS
        assert "gemini" in AGENTS

    def test_claude_config(self):
        """Claude agent should have correct config."""
        claude = AGENTS["claude"]
        assert claude.mode == "file"
        assert "{name}" in claude.install_path
        assert ".claude/commands" in claude.install_path

    def test_codex_uses_append_mode(self):
        """Codex should use append mode."""
        codex = AGENTS["codex"]
        assert codex.mode == "append"
        assert codex.install_path == "AGENTS.md"


class TestGetInstallPath:
    """Tests for get_install_path function."""

    def test_claude_path(self, tmp_path):
        """Should return correct path for Claude."""
        path = get_install_path("claude", "my-skill", tmp_path)
        assert path == tmp_path / ".claude" / "commands" / "my-skill.md"

    def test_cursor_path(self, tmp_path):
        """Should return correct path for Cursor."""
        path = get_install_path("cursor", "my-skill", tmp_path)
        assert path == tmp_path / ".cursor" / "rules" / "my-skill.mdc"

    def test_gemini_path(self, tmp_path):
        """Should return correct path for Gemini."""
        path = get_install_path("gemini", "my-skill", tmp_path)
        assert path == tmp_path / ".gemini" / "skills" / "my-skill.md"

    def test_codex_path(self, tmp_path):
        """Should return AGENTS.md for Codex."""
        path = get_install_path("codex", "my-skill", tmp_path)
        assert path == tmp_path / "AGENTS.md"

    def test_unknown_agent_raises(self, tmp_path):
        """Should raise ValueError for unknown agent."""
        with pytest.raises(ValueError, match="Unknown agent"):
            get_install_path("unknown-agent", "my-skill", tmp_path)


class TestAdaptContent:
    """Tests for adapt_content function."""

    def test_codex_wraps_in_markers(self):
        """Codex content should be wrapped in HTML comments."""
        content = "# My Skill\n\nContent here."
        adapted = adapt_content(content, "codex", "my-skill")

        assert "<!-- skillhub:my-skill -->" in adapted
        assert "<!-- /skillhub:my-skill -->" in adapted
        assert content in adapted

    def test_claude_unchanged(self):
        """Claude content should be returned unchanged."""
        content = "# My Skill\n\nContent here."
        adapted = adapt_content(content, "claude", "my-skill")

        assert adapted == content

    def test_cursor_unchanged(self):
        """Cursor content should be returned unchanged."""
        content = "# My Skill"
        adapted = adapt_content(content, "cursor", "my-skill")
        assert adapted == content


class TestInstallSkillToAgent:
    """Tests for install_skill_to_agent function."""

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories if they don't exist."""
        content = "# Test Skill"
        path = install_skill_to_agent(content, "claude", "test-skill", tmp_path)

        assert path.parent.exists()
        assert path.exists()

    def test_file_mode_writes_standalone(self, tmp_path):
        """File mode should write standalone file."""
        content = "# Test Skill"
        path = install_skill_to_agent(content, "claude", "test-skill", tmp_path)

        assert path.read_text() == content

    def test_append_mode_appends(self, tmp_path):
        """Append mode should append to existing file."""
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("# Existing Content\n")

        install_skill_to_agent("New content", "codex", "new-skill", tmp_path)

        result = agents_md.read_text()
        assert "# Existing Content" in result
        assert "New content" in result

    def test_append_mode_replaces_existing_skill(self, tmp_path):
        """Append mode should replace existing skill block."""
        content_v1 = "Version 1"
        content_v2 = "Version 2"

        install_skill_to_agent(content_v1, "codex", "my-skill", tmp_path)
        install_skill_to_agent(content_v2, "codex", "my-skill", tmp_path)

        agents_md = tmp_path / "AGENTS.md"
        result = agents_md.read_text()

        assert "Version 2" in result
        assert result.count("<!-- skillhub:my-skill -->") == 1

    def test_file_exists_raises_without_overwrite(self, tmp_path):
        """Should raise FileExistsError if file exists and overwrite=False."""
        content = "# Test"
        install_skill_to_agent(content, "claude", "test-skill", tmp_path)

        with pytest.raises(FileExistsError):
            install_skill_to_agent(content, "claude", "test-skill", tmp_path, overwrite=False)

    def test_overwrite_replaces_file(self, tmp_path):
        """Should replace file when overwrite=True."""
        install_skill_to_agent("Version 1", "claude", "test-skill", tmp_path)
        install_skill_to_agent("Version 2", "claude", "test-skill", tmp_path, overwrite=True)

        path = tmp_path / ".claude" / "commands" / "test-skill.md"
        assert "Version 2" in path.read_text()
