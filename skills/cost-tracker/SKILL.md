---
name: cost-tracker
description: Track, estimate, and optimize LLM API costs across providers. Use when user wants to understand their LLM spending, reduce costs, or compare provider pricing for a given workload.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [llm, cost, optimization, openai, anthropic, bedrock, pricing]
triggers: ['cost', 'spending', 'token usage', 'llm cost', 'api cost', 'budget', 'expensive']
---

# Cost Tracker

Helps you understand, estimate, and reduce LLM API costs before they become a surprise bill.

## When to Use

- "How much is this going to cost at scale?"
- "Our LLM bill is too high — help me reduce it"
- "Compare cost of GPT-4o vs Claude vs Gemini for my workload"
- "Estimate cost for N users / N requests per day"
- Before building any LLM feature that will run in production

## Current Pricing Reference (verify at provider — prices change)

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|---|---|---|
| GPT-4o | $2.50 | $10.00 |
| GPT-4o mini | $0.15 | $0.60 |
| Claude Sonnet 4 | $3.00 | $15.00 |
| Claude Haiku 4 | $0.80 | $4.00 |
| Gemini 1.5 Pro | $1.25 | $5.00 |
| Gemini 1.5 Flash | $0.075 | $0.30 |
| Llama 3.1 70B (Bedrock) | $0.72 | $0.72 |

**Always verify on the provider pricing page before using for decisions.**

## Cost Estimation Workflow

### Step 1 — Measure actual token usage

For a representative sample of real requests, count:
- Average input tokens (system prompt + context + user message)
- Average output tokens
- Request volume per day/month

Tools:
- OpenAI: response.usage.total_tokens
- Anthropic: response.usage.input_tokens / output_tokens
- Most providers return usage in the response object

### Step 2 — Calculate baseline cost

```
daily_cost = (avg_input_tokens * input_price + avg_output_tokens * output_price) 
             * requests_per_day / 1_000_000

monthly_cost = daily_cost * 30
```

Example: 1000 req/day, avg 2000 input + 500 output tokens, GPT-4o:
```
= (2000 * $2.50 + 500 * $10.00) * 1000 / 1,000,000
= ($5.00 + $5.00) * 1000 / 1,000,000
= $10,000 / 1,000,000 = $0.01/req
= $10/day = $300/month
```

### Step 3 — Identify the biggest cost drivers

In most LLM applications, costs come from:
1. **System prompt length** — injected on every request, often 2000+ tokens
2. **Context window stuffing** — passing entire docs or chat history
3. **Over-powered model** — using GPT-4 for tasks GPT-4o mini handles fine
4. **Long outputs** — asking for verbose responses when brief would do

Profile which of these dominates before optimizing.

### Step 4 — Optimization strategies (in order of impact)

**Prompt compression (20–60% reduction)**
- Remove redundant instructions from system prompt
- Use references instead of pasting full content ("See section 3 of the attached doc")
- Use tools like LLMLingua or headroomlabs/headroom for automatic compression

**Model downsizing (50–90% cost reduction)**
- Run cheaper models on simpler tasks (classification, extraction, short answers)
- Use the expensive model only for generation, reasoning, and complex synthesis
- Test: does the smaller model produce acceptable quality for this specific task?

**Caching (up to 90% reduction on repeated content)**
- Semantic caching: cache responses for similar questions
- Prompt caching: Anthropic and OpenAI offer cached input token pricing (50–75% off)
- Cache static system prompts that don't change per request

**Context management**
- Summarize long conversation history instead of passing all turns
- Retrieve only relevant chunks (RAG) instead of entire documents
- Truncate or compress retrieved context before sending

**Batching**
- Batch API: 50% cheaper on OpenAI for non-real-time requests
- Process async workloads (summaries, embeddings) in batch mode

### Step 5 — Report

```
LLM Cost Analysis — [Date]

Current usage:
  Requests/day: [N]
  Avg input tokens: [N]
  Avg output tokens: [N]
  Current model: [name]
  Monthly cost: $[X]

Top cost driver: [system prompt / context / model choice / output length]

Optimization opportunities:
  1. [Action]: estimated [X%] reduction → saves $[Y]/month
  2. [Action]: estimated [X%] reduction → saves $[Y]/month

Recommended first step: [specific, actionable recommendation]
```
