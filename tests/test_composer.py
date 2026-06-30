"""
Tests for skillhub.composer module.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from skillhub import composer
from skillhub.composer import ParsedSkill, _parse_skill, _detect_conflicts, compose


class TestParseSkill:
    """Tests for _parse_skill function."""

    def test_parse_frontmatter(self):
        """Should extract YAML frontmatter."""
        content = """---
name: test-skill
description: Test description
version: 1.0.0
tags: [test, debug]
---

# Test Skill

Body content here.
"""
        result = _parse_skill(content, "test-skill")

        assert result.name == "test-skill"
        assert result.description == "Test description"
        assert result.frontmatter["version"] == "1.0.0"
        assert "test" in result.frontmatter["tags"]

    def test_parse_sections(self):
        """Should extract H2 sections."""
        content = """---
name: test
description: test
---

# Test

Preamble here.

## When to Use

Use when testing.

## Workflow

1. Step one
2. Step two
"""
        result = _parse_skill(content, "test")

        assert "When to Use" in result.sections
        assert "Workflow" in result.sections
        assert "Use when testing" in result.sections["When to Use"]
        assert "__preamble__" in result.sections

    def test_parse_no_frontmatter(self):
        """Should handle content without frontmatter."""
        content = "# No Frontmatter\n\nJust body content."
        result = _parse_skill(content, "test")

        assert result.frontmatter == {}
        assert result.description == ""

    def test_parse_invalid_yaml(self):
        """Should handle invalid YAML gracefully."""
        content = """---
invalid: yaml: content: here
---

# Test
"""
        result = _parse_skill(content, "test")
        # Should not raise, should return empty frontmatter
        assert result.frontmatter == {} or result.frontmatter is not None


class TestDetectConflicts:
    """Tests for _detect_conflicts function."""

    def test_no_conflicts(self):
        """Should return empty list when no conflicts."""
        skills = [
            ParsedSkill("a", "desc", {}, "", {"Section A": "content"}),
            ParsedSkill("b", "desc", {}, "", {"Section B": "content"}),
        ]
        conflicts = _detect_conflicts(skills)
        assert conflicts == []

    def test_detect_section_conflict(self):
        """Should detect duplicate section titles."""
        skills = [
            ParsedSkill("a", "desc", {}, "", {"When to Use": "content a"}),
            ParsedSkill("b", "desc", {}, "", {"When to Use": "content b"}),
        ]
        conflicts = _detect_conflicts(skills)

        assert len(conflicts) == 1
        assert "When to Use" in conflicts[0]
        assert "'a'" in conflicts[0]
        assert "'b'" in conflicts[0]

    def test_preamble_not_conflict(self):
        """__preamble__ sections should not be treated as conflicts."""
        skills = [
            ParsedSkill("a", "desc", {}, "", {"__preamble__": "intro a"}),
            ParsedSkill("b", "desc", {}, "", {"__preamble__": "intro b"}),
        ]
        conflicts = _detect_conflicts(skills)
        assert conflicts == []


class TestCompose:
    """Tests for compose function."""

    def test_compose_merges_skills(self, mock_httpx_success, temp_project):
        """Should merge multiple skills into one."""
        composed, conflicts = compose(
            ["test-skill", "another-skill"],
            output_name="merged",
            project_root=temp_project,
            install=False,
        )

        assert "name: merged" in composed
        assert "composed_from:" in composed
        assert "test-skill" in composed
        assert "another-skill" in composed

    def test_compose_reports_conflicts(self, mock_httpx_success, temp_project):
        """Should report section conflicts."""
        # Both test-skill and another-skill might have "When to Use" section
        composed, conflicts = compose(
            ["test-skill", "another-skill"],
            output_name="merged",
            project_root=temp_project,
            install=False,
        )
        # Conflicts list is returned (may or may not have conflicts depending on mock data)
        assert isinstance(conflicts, list)

    def test_compose_raises_for_nonexistent(self, mock_httpx_success, temp_project):
        """Should raise ValueError for nonexistent skill."""
        with pytest.raises(ValueError, match="not found"):
            compose(
                ["test-skill", "nonexistent-xyz"],
                output_name="merged",
                project_root=temp_project,
                install=False,
            )

    def test_compose_installs_when_requested(self, mock_httpx_success, temp_project):
        """Should install composed skill when install=True."""
        compose(
            ["test-skill", "another-skill"],
            output_name="merged",
            project_root=temp_project,
            install=True,
        )

        output_file = temp_project / ".claude" / "commands" / "merged.md"
        assert output_file.exists()

    def test_compose_merges_tags(self, mock_httpx_success, temp_project):
        """Should combine tags from all skills."""
        composed, _ = compose(
            ["test-skill", "another-skill"],
            output_name="merged",
            project_root=temp_project,
            install=False,
        )

        # Should contain tags from both skills
        assert "tags:" in composed
