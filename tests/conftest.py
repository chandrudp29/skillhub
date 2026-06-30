"""
Shared pytest fixtures for skillhub tests.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def sample_index():
    """Sample registry index for testing."""
    return {
        "version": "1.0.0",
        "updated_at": "2024-01-01",
        "skills": [
            {
                "name": "test-skill",
                "display_name": "Test Skill",
                "description": "A test skill for unit testing",
                "version": "1.0.0",
                "agents": ["claude", "cursor", "codex", "gemini"],
                "tags": ["test", "debug"],
                "author": "test-author",
                "license": "MIT",
            },
            {
                "name": "another-skill",
                "display_name": "Another Skill",
                "description": "Another skill for testing search",
                "version": "2.0.0",
                "agents": ["claude"],
                "tags": ["research", "analysis"],
                "author": "test-author",
                "license": "MIT",
            },
        ],
    }


@pytest.fixture
def sample_skill_content():
    """Sample SKILL.md content."""
    return """---
name: test-skill
description: A test skill for unit testing
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [test, debug]
---

# Test Skill

A skill for testing purposes.

## When to Use

- When writing tests
- When debugging

## Workflow

1. Step one
2. Step two

## Output Format

Return structured test results.
"""


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    project = tmp_path / "test-project"
    project.mkdir()
    return project


@pytest.fixture
def mock_cache_dir(tmp_path):
    """Provide a temporary cache directory."""
    cache = tmp_path / ".skillhub" / "cache"
    cache.mkdir(parents=True)
    return cache


@pytest.fixture
def mock_httpx_success(sample_index, sample_skill_content):
    """Mock httpx to return successful responses."""
    class MockResponse:
        def __init__(self, content, status_code=200):
            self._content = content
            self.status_code = status_code
            self.text = content if isinstance(content, str) else json.dumps(content)

        def json(self):
            if isinstance(self._content, dict):
                return self._content
            return json.loads(self._content)

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")

    def mock_get(url, timeout=10):
        if "index.json" in url:
            return MockResponse(sample_index)
        elif "SKILL.md" in url or ".md" in url:
            return MockResponse(sample_skill_content)
        return MockResponse({}, 404)

    with patch("httpx.get", side_effect=mock_get):
        yield


@pytest.fixture
def mock_httpx_failure():
    """Mock httpx to simulate network failure."""
    import httpx

    def mock_get(url, timeout=10):
        raise httpx.ConnectError("Network unreachable")

    with patch("httpx.get", side_effect=mock_get):
        yield
