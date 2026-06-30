---
name: test-writer
description: Write thorough, meaningful tests for any function, module, or API. Use when user asks to add tests, improve coverage, or ensure a piece of code is tested before shipping.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [testing, tdd, unit-tests, integration, coverage]
---

# Test Writer

Writes tests that actually catch bugs — not tests that just run green.

## When to Use

- "Write tests for this function"
- "Add tests before I refactor this"
- "What should I test here?"
- "My coverage is low — where do I start?"

## What Makes a Test Valuable

A test is valuable if it would fail when the code is wrong and pass when the code is correct. A test that always passes regardless of the implementation has negative value — it creates false confidence.

Before writing any test, ask: "If I deleted the function body and replaced it with `return null`, would this test fail?" If no, the test is measuring nothing.

## Test Categories (write in this order)

### 1. Happy Path

The expected behavior with valid inputs. Should be the first test, simplest to write.

### 2. Edge Cases

The boundaries where behavior changes:
- Empty inputs (empty string, empty array, null, undefined)
- Zero and negative numbers
- Single-element collections
- Maximum/minimum values
- Boundary conditions (n=0, n=1, n=N, n=N+1)

### 3. Error Cases

What happens when things go wrong:
- Invalid input types
- Missing required fields
- Values out of range
- External service failures (mocked)
- Concurrent access

### 4. Integration Points

Where this code meets other systems:
- Database reads/writes produce expected results
- External API calls are made with correct parameters
- Events are emitted in the right order
- State is cleaned up after use

## Test Structure

Every test follows Arrange → Act → Assert:

```python
def test_descriptive_name_of_what_is_being_verified():
    # Arrange — set up the exact state needed
    user = User(id=1, email="test@example.com", role="admin")
    
    # Act — run exactly one thing
    result = can_delete_post(user, post_id=42)
    
    # Assert — verify the specific outcome
    assert result is True
```

One assertion per test is a guideline, not a rule. Multiple assertions are fine when they verify a single behavior. Multiple behaviors in one test = split into multiple tests.

## Naming Tests

Test names are documentation. Name them as complete sentences:

Good: `test_empty_query_returns_empty_list`
Good: `test_expired_token_raises_AuthError`
Bad: `test_function1`
Bad: `test_case_3`

## What NOT to Mock

Mock external dependencies (HTTP, DB, filesystem, time). Don't mock:
- Pure functions you control
- Data structures
- Simple collaborators within the same module

Over-mocking creates tests that pass even when the real system is broken. Mock at the boundary between your code and the outside world.

## Coverage

Coverage tells you what you haven't tested, not whether your tests are good. 100% coverage with trivial tests is worse than 60% coverage with meaningful tests.

Prioritize covering:
1. Branches in business logic (`if/else`, `switch`)
2. Error handling paths
3. Integration boundaries

## Output Format

```python
# [filename]_test.py

import pytest
from [module] import [function]

class Test[FunctionName]:
    """Tests for [function]."""
    
    def test_happy_path(self):
        ...

    def test_empty_input_returns_empty(self):
        ...

    def test_invalid_type_raises_value_error(self):
        with pytest.raises(ValueError, match="expected message"):
            ...

    def test_boundary_condition_at_max(self):
        ...
```

After writing: run the tests, confirm they fail when the implementation is wrong (temporarily break the implementation to verify), then restore.
