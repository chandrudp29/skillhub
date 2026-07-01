---
name: yc-job-tracker
description: Track and filter YC startup job listings for AI/ML engineering roles. Builds a daily-refreshed local database of relevant jobs with scoring and alerts for new postings.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [jobs, yc, ai-ml, scraping, career, startup]
triggers: ['yc jobs', 'job search', 'startup jobs', 'y combinator', 'job tracker', 'hiring']
---

# YC Job Tracker

Automates daily job discovery on workatastartup.com — finds AI/ML engineering roles at YC startups, scores them for fit, and alerts you to new postings.

## When to Use

- "Show me AI/ML jobs at YC startups"
- "What new jobs posted today match my profile?"
- "Track jobs at YC startups daily"
- Job searching at YC/startup companies

## Setup

```bash
git clone https://github.com/chandrudp29/yc-jobs-tracker
cd yc-jobs-tracker
pip install -r requirements.txt
cp .env.example .env
# Add your HYPERBROWSER_API_KEY to .env
```

## Daily Use

```bash
# Fetch today's jobs and show top AI/ML matches
python fetch_today.py

# Filter for India/Bengaluru roles only
python fetch_today.py --india

# Load from yesterday's cache (no network request)
python fetch_today.py --load
```

## Start the API

```bash
uvicorn api:app --port 8765
```

Endpoints:
- `GET /jobs/ai` — top AI/ML matches with scores
- `GET /jobs/new` — jobs posted since yesterday
- `POST /jobs/fetch` — trigger a fresh scrape in background

## Scoring System

Jobs are scored on relevance:

| Signal | Points |
|---|---|
| "AI Engineer" / "ML Engineer" in title | 10 |
| "Founding AI Engineer" in title | 12 |
| India / Bengaluru location | 6 |
| LangChain / LangGraph / PyTorch in description | 3 |
| OpenAI / Claude / Bedrock mentioned | 2 |
| Remote | 2 |

**Score ≥ 15** = PERFECT match (🟢)
**Score ≥ 10** = Strong match (🔵)

## Daily Automation (9 AM IST)

```bash
# Runs daily at 3:30 AM UTC = 9 AM IST
python -c "from scheduler import start; start()"
```

## Cookie Authentication (for full 438-company listing)

Without authentication, workatastartup.com shows ~30 preview listings. For all 438:

1. Log in to workatastartup.com in Chrome
2. Install "Cookie-Editor" extension
3. Export all cookies as JSON
4. Save as `cookies.json` in the project root

The scraper auto-detects `cookies.json` and injects the session.

## Configuration

Edit `config.py` to customize:
- `TITLE_BOOST` — which job titles to prioritize
- `LOCATION_BOOST` — which locations to weight
- `TECH_BOOST` — which tech keywords to score

## Source

Full implementation: [github.com/chandrudp29/yc-jobs-tracker](https://github.com/chandrudp29/yc-jobs-tracker)
