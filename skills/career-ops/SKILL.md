---
name: career-ops
description: Global AI/ML job hunt — USA, Europe, Singapore, Dubai, remote-first startups. Daily fetch, score, and track Senior AI/ML Engineer roles with LangChain/LangGraph/agent stack.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [jobs, career, ai-ml, remote, startup, usa, europe, singapore, dubai, langgraph, langchain]
triggers: ['career ops', 'job search', 'find jobs', 'remote jobs', 'ai ml jobs', 'startup jobs', 'usa jobs', 'europe jobs', 'singapore jobs', 'dubai jobs', 'founding engineer']
author: chandrudp29
---

# Career Ops — Global AI/ML Job Hunter

Finds and scores Senior AI/ML Engineer roles across USA, Europe, Singapore, Dubai, and remote-first startups. Focused on founding engineer / early-stage / high-equity positions with modern LLM/agent stack.

## Profile

- **Role target**: Senior AI/ML Engineer · Founding AI Engineer · AI Platform Engineer
- **Stack**: LangChain, LangGraph, LlamaIndex, CrewAI, RAG, vector DBs, Python, FastAPI
- **Locations**: Remote (USA-timezone) · Remote (Europe-timezone) · Singapore · Dubai · On-site USA
- **Stage preference**: Seed → Series B startups, YC-backed, a16z/Sequoia portfolio

---

## Daily Job Search — Where to Look

### USA Remote

| Platform | URL | Filter tip |
|----------|-----|------------|
| HN Who is Hiring (June 2026) | [hnhiring.com/locations/remote](https://hnhiring.com/locations/remote) | Ctrl+F "AI" + "LangGraph" |
| Wellfound (AngelList) | [wellfound.com/role/r/ai-engineer](https://wellfound.com/role/r/ai-engineer) | Filter: Remote · Seed/Series A |
| YC Work at a Startup | [workatastartup.com](https://www.workatastartup.com/) | AI role · Remote |
| LinkedIn | [linkedin.com/jobs/remote-machine-learning-engineer-jobs](https://www.linkedin.com/jobs/remote-machine-learning-engineer-jobs) | Past 24h · Remote |
| Arc.dev | [arc.dev/remote-jobs/llm](https://arc.dev/remote-jobs/llm) | Senior · LLM |
| Built In | [builtin.com/jobs/remote/dev-engineering/search/artificial-intelligence-engineer](https://builtin.com/jobs/remote/dev-engineering/search/artificial-intelligence-engineer) | Remote only |
| Turing | [turing.com/jobs/remote-ai-ml-jobs](https://www.turing.com/jobs/remote-ai-ml-jobs) | US-timezone remote |

### Europe Remote

| Platform | URL | Filter tip |
|----------|-----|------------|
| LinkedIn | Search: "AI Engineer" + "Remote" + "Europe" | Sort: Most Recent |
| Arc.dev | [arc.dev/remote-jobs/langchain](https://arc.dev/remote-jobs/langchain) | Europe timezone |
| Lemon.io | [lemon.io/for-developers/ai-engineer-jobs](https://lemon.io/for-developers/ai-engineer-jobs) | $60-95/hr contract |
| Agentic Jobs | [agentic-engineering-jobs.com/jobs/mid/langgraph/remote](https://agentic-engineering-jobs.com/jobs/mid/langgraph/remote) | LangGraph-specific |

### Singapore & Dubai

| Platform | URL | Filter tip |
|----------|-----|------------|
| LinkedIn | "Senior AI Engineer" + "Singapore" / "Dubai" | Sort: Most Recent |
| Glassdoor | "ML Engineer" + Singapore/Dubai | Past week |
| Indeed | AI Engineer Dubai remote | Salary filter |
| Naukri Gulf | Gulf AI jobs | Dubai/UAE filter |

### Startup-Specific (All Regions)

| Platform | URL | Why |
|----------|-----|-----|
| YC Companies | [ycombinator.com/jobs/role/all/remote](https://www.ycombinator.com/jobs/role/all/remote) | 1000+ vetted funded startups |
| Wellfound | wellfound.com/role/r/artificial-intelligence-engineer | Equity visible |
| HN Who is Hiring | [news.ycombinator.com/item?id=47601859](https://news.ycombinator.com/item?id=47601859) | Founding roles |
| RemoteRocketship | [remoterocketship.com/jobs/llm-engineer](https://www.remoterocketship.com/jobs/llm-engineer) | 55+ LLM roles |
| ZipRecruiter | ziprecruiter.com/Jobs/Llm-Engineer-Remote | $43-69/hr LLM roles |

---

## Scoring System

Score each job before applying. **Apply only to score ≥ 12.**

| Signal | Points |
|--------|--------|
| "Founding AI Engineer" or "Staff AI Engineer" in title | 12 |
| LangGraph / LangChain / agentic AI in description | 8 |
| Series A or earlier (seed, pre-seed, YC batch) | 6 |
| Remote — full async (not "remote in USA only") | 5 |
| Equity explicitly mentioned (0.1%+) | 5 |
| Located USA / Europe / Singapore / Dubai | 4 |
| $150k+ base or $60+/hr | 4 |
| RAG / vector DB / embedding pipeline | 3 |
| Python FastAPI LlamaIndex mentioned | 2 |
| Team < 20 people | 2 |

**Score ≥ 20**: Apply same day — perfect match  
**Score 14-19**: Apply within 48 hours  
**Score 10-13**: Bookmark, apply if pipeline is slow  
**Score < 10**: Skip

---

## Application Template

### Cold DM / LinkedIn Note (140 chars)

```
Hi [Name] — Senior AI/ML Engineer (LangGraph, RAG, FastAPI). Built [X] at [company]. 
Open to [role]. Can I send my work?
```

### Email subject

```
Senior AI Engineer — [LangGraph / RAG / Agent stack] — [Your result in one number]
```

### What to lead with in cover note

1. One sentence: what you shipped, how it's measured
2. One sentence: why this company specifically (not generic)
3. One ask: "Can I show you what I built?"

---

## Weekly Tracking Table

Paste this into a Notion / spreadsheet and update daily:

| Company | Role | Score | Source | Applied | Response | Status |
|---------|------|-------|--------|---------|----------|--------|
| | | | | | | |

---

## Resume Keywords to Include

For ATS pass-through on USA/Singapore/Dubai roles:

```
LangChain · LangGraph · LlamaIndex · CrewAI · RAG · vector database · Pinecone · 
Weaviate · FastAPI · Python · PyTorch · OpenAI API · Claude API · Bedrock · 
agentic AI · multi-agent · tool use · function calling · prompt engineering · 
MLflow · evaluation · evals · production LLM · inference optimization
```

---

## Today's Live Boards (Run Each Morning)

```bash
# Open all boards in browser tabs
open https://hnhiring.com/locations/remote
open https://wellfound.com/role/r/ai-engineer
open https://www.workatastartup.com/
open https://arc.dev/remote-jobs/llm
open https://www.ycombinator.com/jobs/role/all/remote
```

Or ask Claude:
```
/career-ops

Search today's openings for Senior AI/ML Engineer roles. 
I want: remote USA or Europe or Singapore or Dubai.
Stack: LangGraph, RAG, FastAPI.
Score each role and give me the top 5 to apply today.
```

---

## O-1A / Visa Framing

When targeting USA roles for O-1A visa evidence:

- **Prioritize**: companies that can write a peer review letter (staff 20+, VC-backed)
- **Avoid**: pure contractor roles with no employment relationship
- **Ask in final round**: "Would your team be willing to sponsor O-1A in 6-12 months if the fit is strong?"
- **Track citations**: every time a company uses your open-source work (skillhub installs), document it — it counts as evidence of extraordinary ability

---

## Source

Built with skillhub. Search daily. Apply fast. Track everything.
