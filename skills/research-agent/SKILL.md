---
name: research-agent
description: Multi-source deep research with synthesis and inline citations. Use when user asks to research a topic, compare technologies, do competitive analysis, or investigate a subject in depth.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [research, web, synthesis, citations, analysis]
triggers: ['research', 'investigate', 'compare', 'analyze', 'find information', 'deep dive']
---

# Research Agent

Produces thorough, cited research reports from multiple sources. Not a search wrapper — a research analyst.

## When to Use

- "Research X for me"
- "Compare A vs B"
- "What's the current state of X?"
- "Competitive analysis of X"
- "Should we use X or Y?"

## Workflow

### Step 1 — Clarify scope (30 seconds max)

Ask exactly one question if the goal is ambiguous:
- Decision context ("choosing a tool") → focus on tradeoffs
- Learning context ("understand X") → focus on concepts and examples
- Writing context ("write a report") → focus on structure and evidence

If obvious, skip clarification and proceed.

### Step 2 — Decompose into sub-questions

Break the topic into 3–5 research sub-questions. Think like a research analyst:

Example: "Should we use Pinecone or Weaviate?"
- What are the performance benchmarks at 10M+ vectors?
- What are the pricing models at scale?
- What are the operational differences (managed vs self-hosted)?
- What does the developer community say (GitHub issues, Reddit, HN)?
- What are the migration paths if we need to switch?

State the sub-questions before researching. This prevents rabbit holes.

### Step 3 — Search each sub-question

For each sub-question, run 2–3 searches with different keyword angles:
- Exact name searches
- Comparison searches ("X vs Y")
- Recent news searches ("X 2025" or "X latest")
- Community searches ("X reddit" or "X hacker news")

Prioritize sources: official docs > peer-reviewed > reputable tech press > community discussion > personal blogs.

### Step 4 — Read primary sources

Don't rely on summaries. For each key claim, read the actual source:
- Official documentation for feature claims
- Benchmark methodology for performance claims
- GitHub issues for real-world problems
- Pricing pages for cost claims (pricing pages change — note the date)

### Step 5 — Synthesize with citations

Structure the output:

```
## Summary (3–5 sentences, the answer upfront)

## Key Findings
- Finding 1 [Source: URL, Date]
- Finding 2 [Source: URL, Date]

## Deep Dive: [Sub-question 1]
...content with inline citations [1]...

## Deep Dive: [Sub-question 2]
...

## Comparison Table (if applicable)
| Criterion | Option A | Option B |
|-----------|----------|----------|

## Recommendation
Clear recommendation with reasoning. State confidence level.

## Sources
[1] URL — description — accessed YYYY-MM-DD
```

## Quality Standards

Every factual claim must have a source. "Generally known" is not a source.

Date every piece of data — the AI space moves fast and a 6-month-old benchmark is often outdated.

State what you couldn't find. "I could not find independent benchmarks for X — treat vendor claims with skepticism" is more valuable than silence.

Distinguish between facts ("Pinecone charges $0.096/hr for p1.x1"), estimates ("~10ms p99 latency based on their docs"), and opinions ("the developer community prefers Weaviate for...").

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I already know this topic" | Do the search anyway. The space changes daily. |
| "The summary is enough" | Read the primary source for any claim you'll act on. |
| "I'll cite it as general knowledge" | Find the source. Every claim has one. |
| "One search is enough" | Different phrasings surface different sources. |
