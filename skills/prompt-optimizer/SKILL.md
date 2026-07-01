---
name: prompt-optimizer
description: Analyze and improve LLM prompts for clarity, precision, and output quality. Use when a prompt produces inconsistent results, the model ignores instructions, outputs are too long/short, or quality is below expectations.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [prompt, llm, optimization, instructions, output-quality]
triggers: ['improve prompt', 'optimize prompt', 'prompt engineering', 'bad prompt', 'fix prompt']
---

# Prompt Optimizer

Diagnoses why a prompt underperforms and rewrites it to be specific, grounded, and consistent.

## When to Use

- Model ignores part of the instructions
- Outputs vary wildly between runs
- Responses are too verbose, too vague, or formatted wrong
- Model "hallucinates" when it should say "I don't know"
- Chain-of-thought isn't happening when it should

## Diagnosis First

Before rewriting, identify the failure mode:

| Symptom | Likely cause |
|---|---|
| Ignores formatting instructions | Instructions buried in a long prompt |
| Inconsistent output structure | No example provided |
| Too verbose | No length guidance |
| Hallucinates facts | No instruction to acknowledge uncertainty |
| Misunderstands the task | Task description is ambiguous |
| Ignores constraints | Constraints mentioned once, not reinforced |

## The Anatomy of a Strong Prompt

```
[Role / Persona]          ← who the model is in this context
[Task definition]         ← exactly what to do
[Context / Input]         ← the data it operates on
[Constraints]             ← what NOT to do, limits, format
[Output format]           ← exact structure of the response
[Example] (optional)      ← one concrete example of good output
```

Not every prompt needs all sections. A simple prompt doesn't need a persona. A structured extraction task needs an output format and example.

## Common Rewrites

### Vague → Specific

```
# Before (vague)
Summarize this text.

# After (specific)
Summarize the following text in exactly 3 bullet points.
Each bullet must be one sentence under 20 words.
Focus only on actionable findings — ignore background context.
If there are no actionable findings, write "No actionable findings."

Text:
{text}
```

### Missing Output Format

```
# Before
Extract the key information from this job posting.

# After
Extract the following fields from the job posting below.
Return a JSON object with exactly these keys:
{
  "title": "job title",
  "company": "company name",
  "location": "city, country or Remote",
  "salary": "salary range or null if not mentioned",
  "required_skills": ["skill1", "skill2"],
  "years_experience": number or null
}
If a field is not present, use null. Do not add extra fields.

Job posting:
{text}
```

### Hallucination Prevention

```
# Before
Answer the question based on the context.

# After
Answer the question using ONLY the information provided in the context below.
If the answer is not in the context, respond with exactly: "This information is not available in the provided context."
Do not use prior knowledge. Do not guess. Do not infer beyond what is stated.

Context:
{context}

Question: {question}
```

### Inconsistent Reasoning

Add chain-of-thought for complex tasks:
```
Before giving your final answer, think through:
1. What is the question asking?
2. What information in the context is relevant?
3. What does that information tell us?
Then give your final answer.
```

### Role-based Precision

```
# Before
Review this code.

# After
You are a senior software engineer conducting a security-focused code review.
Your job is to find vulnerabilities, not style issues.

Review the code below and list only security findings.
For each finding, provide:
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Location: file:line
- Vulnerability: what it is
- Fix: specific code change needed

If there are no security findings, write "No security vulnerabilities found."

Code:
{code}
```

## Token Efficiency

Long prompts cost more and reduce attention quality on key instructions. Trim:

- Remove filler phrases ("Please", "I'd like you to", "Could you", "As an AI")
- Put the most important instruction first (and sometimes last)
- Use bullet points instead of paragraphs for constraints
- Remove examples that don't add information not already in the instructions

## Testing a Rewritten Prompt

Run both the original and rewritten prompt on the same 5 inputs. Compare:
- Does the new prompt produce the correct format every time?
- Does it handle edge cases (empty input, ambiguous input) correctly?
- Is the output length appropriate?
- Are the failure modes from the original fixed?

If the rewrite improves 4 of 5 cases and regresses 0, ship it.

## System Prompt vs User Prompt

**System prompt**: persona, task definition, constraints, output format — things that don't change per request.

**User prompt**: the actual input the user provides — things that change every request.

Don't mix them. If a constraint is always true, put it in the system prompt. If it's specific to this request, put it in the user message.
