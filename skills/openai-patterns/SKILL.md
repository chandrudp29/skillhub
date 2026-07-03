---
name: openai-patterns
description: Production OpenAI API patterns — model selection, prompt engineering, function calling, streaming, error handling, cost control, and structured outputs
version: 1.0.0
tags: [openai, gpt, llm, ai, api, function-calling]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when building or reviewing code that calls the OpenAI API. Covers GPT-4, GPT-4o, o1, and Responses API.

## Core Rules

- Always handle rate limits with exponential backoff — they happen in production
- Set `max_tokens` on every call — unbounded completions cause cost surprises
- Log token usage per call — you need this for cost attribution and anomaly detection
- Use structured outputs (`response_format`) when you need parseable data — regex on free text is fragile
- Never hardcode API keys — use env vars, rotate quarterly

## Model Selection

| Model | Best for | Approx cost |
|-------|----------|-------------|
| `gpt-4o-mini` | Classification, extraction, simple Q&A | ~$0.15/1M input |
| `gpt-4o` | Complex reasoning, code generation, long context | ~$2.50/1M input |
| `o1-mini` | Math, coding problems requiring multi-step reasoning | ~$1.10/1M input |
| `o1` | Hardest reasoning tasks, research-grade | ~$15/1M input |

Rule: start with `gpt-4o-mini` and only upgrade if quality is insufficient. The gap is smaller than you think.

## Basic Call Pattern

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain transformer attention in one paragraph."},
    ],
    max_tokens=500,
    temperature=0.7,
)

text = response.choices[0].message.content
usage = response.usage  # prompt_tokens, completion_tokens, total_tokens
```

## Structured Outputs

```python
from pydantic import BaseModel

class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
    reason: str

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Analyze: {text}"}],
    response_format=SentimentResult,
)

result: SentimentResult = response.choices[0].message.parsed
# result.sentiment, result.confidence, result.reason — all typed
```

## Function Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "units": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["city"],
        },
    },
}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto",
)

if response.choices[0].message.tool_calls:
    call = response.choices[0].message.tool_calls[0]
    args = json.loads(call.function.arguments)
    result = get_weather(**args)  # your actual function
    # send result back for final response
```

## Streaming

```python
with client.chat.completions.stream(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a story about..."}],
    max_tokens=1000,
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## Error Handling & Retries

```python
import time
from openai import RateLimitError, APIError

def call_with_retry(messages, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
            )
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)
        except APIError as e:
            if e.status_code in (500, 502, 503) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
```

## Cost Control

```python
# Track usage and alert on anomalies
def tracked_call(messages, model="gpt-4o-mini", **kwargs):
    response = client.chat.completions.create(
        model=model, messages=messages, **kwargs
    )
    usage = response.usage
    cost = estimate_cost(model, usage.prompt_tokens, usage.completion_tokens)

    logger.info("openai_call", extra={
        "model": model,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "estimated_cost_usd": cost,
    })
    return response

# Prompt caching: identical system prompts reuse cached tokens
# → Put stable content at the start of system prompt
# → Cost drops 50% for repeated calls with same prefix
```
