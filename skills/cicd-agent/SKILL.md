---
name: cicd-agent
description: CI/CD pipeline design and review — GitHub Actions, pipeline best practices, secrets management, deployment strategies, and release automation
version: 1.0.0
tags: [cicd, github-actions, devops, deployment, automation]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when writing, reviewing, or debugging CI/CD pipelines. Covers GitHub Actions primarily but principles apply to any CI system.

## Core Rules

- Every pipeline must have: lint → test → build → deploy (in that order, each blocking the next)
- Secrets never in code, YAML, or logs — use environment secrets or a secrets manager
- Pin action versions to a commit SHA, not a tag (`uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683`)
- Jobs that can run in parallel, should — don't serialize unnecessarily
- Always define a timeout for jobs — runaway jobs eat minutes/money

## GitHub Actions Structure

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # cancel stale PR runs

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install ruff && ruff check .

  test:
    needs: lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '${{ matrix.python-version }}' }
      - run: pip install -e ".[dev]" && pytest --tb=short

  deploy:
    needs: [lint, test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

## Secrets Management

```yaml
# Never do this:
env:
  API_KEY: "sk-abc123"  # ❌ visible in git history forever

# Do this — repository/org secrets:
env:
  API_KEY: ${{ secrets.API_KEY }}  # ✓

# For complex secrets, use a secrets manager:
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GithubActionsRole
    aws-region: us-east-1

- name: Get secrets from SSM
  run: |
    DB_PASSWORD=$(aws ssm get-parameter --name /prod/db/password --with-decryption --query Parameter.Value --output text)
    echo "::add-mask::$DB_PASSWORD"  # mask in logs
    echo "DB_PASSWORD=$DB_PASSWORD" >> $GITHUB_ENV
```

## Caching

```yaml
# Python dependencies
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: ${{ runner.os }}-pip-

# Node modules
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

## Deployment Strategies

```
Blue-Green:
  Two identical environments (blue=live, green=staging)
  Deploy to green → run smoke tests → switch traffic → blue becomes new staging
  Instant rollback: switch traffic back

Canary:
  Route 5% of traffic to new version → monitor → gradually increase → 100%
  Good for: high-traffic services where you want real-traffic validation

Rolling:
  Replace instances one by one (or in batches)
  No duplicate infrastructure cost, but brief period of mixed versions

Feature flags (preferred for risk reduction):
  Deploy code to 100% → enable flag for 1% → monitor → expand
  Decouple deployment from release
```

## Release Automation

```yaml
# Auto-version on merge to main using conventional commits
- name: Semantic Release
  uses: cycjimmy/semantic-release-action@v4
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}

# Python: bump version + publish to PyPI on tag
- name: Publish to PyPI
  if: startsWith(github.ref, 'refs/tags/v')
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

## Pipeline Health

- Track mean pipeline duration — if it grows past 10 min, investigate
- Use `GITHUB_STEP_SUMMARY` to write markdown summaries visible in the Actions UI
- Fail fast: lint and type-check before running tests (10s vs 5 min)
- Flaky tests are a pipeline emergency — fix or quarantine within 24h
