---
name: llm-evaluator
description: Evaluate LLM outputs systematically using LLM-as-judge, human evaluation frameworks, and regression testing. Use when assessing model quality, comparing models, or preventing quality regression.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [llm, evaluation, benchmarking, quality, llm-as-judge, regression]
triggers: ['evaluate llm', 'llm metrics', 'eval framework', 'test prompts', 'benchmark']
---

# LLM Evaluator

A framework for measuring LLM output quality — beyond vibes, before production.

## When to Use

- "Is Model A better than Model B for my use case?"
- "Did my prompt change improve quality?"
- "My LLM outputs look worse after an update — prove it"
- Before deploying any LLM-powered feature

## The Three Evaluation Approaches

Use all three. Each catches different problems.

### 1. LLM-as-Judge

Fast, scalable, good signal. Use a stronger model to evaluate a weaker one's outputs.

```python
JUDGE_PROMPT = """You are evaluating an AI assistant's response quality.

Rate the response on each criterion from 1-5:
- Accuracy: Is the information correct and factual?
- Completeness: Does it address all parts of the question?
- Clarity: Is it easy to understand?
- Conciseness: Does it avoid unnecessary verbosity?

Question: {question}
Response to evaluate: {response}
Reference answer (if available): {reference}

Return JSON only:
{{"accuracy": N, "completeness": N, "clarity": N, "conciseness": N, "reasoning": "brief explanation"}}
"""

async def judge_response(question: str, response: str, reference: str = "") -> dict:
    result = await judge_model.ainvoke(
        JUDGE_PROMPT.format(question=question, response=response, reference=reference)
    )
    return json.loads(result.content)
```

**Known biases**: LLM judges favor longer answers, prefer their own model's style, and are inconsistent on borderline cases. Mitigate by averaging across 3 judge calls and using a different model family as judge.

### 2. Automated Metrics

For structured tasks with clear correct answers:

```python
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu

def compute_metrics(prediction: str, reference: str) -> dict:
    # ROUGE — for summarization
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"])
    rouge = scorer.score(reference, prediction)

    # Exact match — for extraction tasks
    exact = prediction.strip().lower() == reference.strip().lower()

    # F1 over tokens — for QA
    pred_tokens = set(prediction.lower().split())
    ref_tokens = set(reference.lower().split())
    common = pred_tokens & ref_tokens
    precision = len(common) / len(pred_tokens) if pred_tokens else 0
    recall = len(common) / len(ref_tokens) if ref_tokens else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {
        "rouge_l": rouge["rougeL"].fmeasure,
        "exact_match": exact,
        "token_f1": f1,
    }
```

Don't use BLEU for anything except translation — it's a poor metric for generation.

### 3. Human Evaluation (Ground Truth)

The slowest and most reliable. Use for high-stakes decisions (model selection, major prompt changes).

**Comparative evaluation (A/B)**: show evaluators two responses side-by-side (Model A vs Model B, prompt version 1 vs 2). Ask: "Which is better, or are they equal?" Faster and more reliable than absolute scoring.

**Rubric-based scoring**: define criteria before evaluation, not during. Evaluators drift if the rubric isn't written down.

```
Criterion: Factual Accuracy
5 — All claims verifiable and correct
4 — Minor imprecision but no false claims
3 — One factual error that doesn't undermine the response
2 — Multiple factual errors
1 — Fundamentally incorrect
```

Minimum: 3 independent evaluators per example. Report inter-annotator agreement (Cohen's Kappa ≥ 0.6 = acceptable).

## Building an Evaluation Dataset

Quality > quantity. 100 carefully chosen examples > 1000 random ones.

Include:
- **Core capability** examples (what the system must do well)
- **Edge cases** (empty input, ambiguous queries, off-topic requests)
- **Adversarial** examples (jailbreak attempts, confusing phrasing)
- **Regression** examples (things that broke before — ensure they stay fixed)

Version your eval set. As the model improves, add new failure modes.

## Regression Testing

Run evals on every model update, prompt change, or dependency upgrade:

```python
# eval_suite.py
import pytest
import json

EVAL_CASES = json.load(open("eval_dataset.json"))
PASS_THRESHOLD = 0.85  # 85% of cases must score ≥ 4/5

@pytest.mark.parametrize("case", EVAL_CASES)
async def test_response_quality(case):
    response = await generate(case["question"])
    scores = await judge_response(case["question"], response, case.get("reference", ""))
    avg_score = sum(scores[k] for k in ["accuracy", "completeness", "clarity"]) / 3
    assert avg_score >= 4.0, f"Quality below threshold: {scores}"

async def test_regression_suite():
    results = []
    for case in EVAL_CASES:
        response = await generate(case["question"])
        scores = await judge_response(case["question"], response)
        results.append(scores)
    
    pass_rate = sum(1 for r in results if sum(r.values()) / len(r) >= 4) / len(results)
    assert pass_rate >= PASS_THRESHOLD, f"Pass rate {pass_rate:.1%} below threshold {PASS_THRESHOLD:.1%}"
```

## Evaluation Report Format

```
LLM Evaluation Report — [Date]
Model: [name] | Prompt version: [v]
Dataset: [N] examples

SCORES (1-5 scale)
  Accuracy:      4.2 ± 0.6
  Completeness:  3.8 ± 0.8
  Clarity:       4.5 ± 0.4
  Conciseness:   3.6 ± 0.9
  Overall:       4.0

PASS RATE: 87% (target: ≥85%) ✅

FAILURE ANALYSIS (13 failures)
  Accuracy failures: 5 — model invents citations
  Completeness failures: 6 — misses second part of two-part questions
  Conciseness failures: 2 — over-explains simple questions

RECOMMENDATION
  [Ship / Revise] — [specific reasoning]
  Top priority: fix [specific failure mode] before next eval
```
