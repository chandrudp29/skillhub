---
name: rag-evaluator
description: Evaluate RAG pipeline quality across faithfulness, relevance, and hallucination metrics. Use when user asks to test, benchmark, or improve a RAG system, or when RAG outputs look wrong.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [rag, evaluation, llm, retrieval, quality, benchmarking]
triggers: ['rag', 'retrieval augmented', 'faithfulness', 'hallucination', 'evaluate rag', 'context']
---

# RAG Evaluator

A systematic evaluation framework for Retrieval-Augmented Generation pipelines. Finds where your RAG breaks before your users do.

## When to Use

- "Is my RAG system giving correct answers?"
- "My RAG is hallucinating — help me find where"
- "Evaluate my retrieval quality"
- "My RAG answers are vague / not using the documents"
- Before deploying a RAG system to production

## The Three Failure Modes

**Retrieval failure**: Right question, wrong chunks retrieved. The answer exists in the corpus but wasn't found.

**Generation failure**: Right chunks retrieved, but the LLM ignored them, hallucinated, or answered a different question.

**Context failure**: Chunks retrieved but they're too long, poorly formatted, or overlap confusingly — LLM gets lost.

Most RAG problems are retrieval failures. Check retrieval first.

## Evaluation Workflow

### Step 1 — Build a test set

Minimum 20 question-answer pairs. Include:
- Questions whose answers are clearly in the corpus (should always pass)
- Questions whose answers are NOT in the corpus (should return "I don't know")
- Multi-hop questions requiring synthesis across chunks
- Edge cases: short answers, numerical facts, recent events

Without a test set, you're evaluating by vibes. Build it first.

### Step 2 — Evaluate retrieval independently

For each test question:
1. Run retrieval only (no generation)
2. Check: is the answer in the top-k chunks?
3. Check: is the most relevant chunk ranked #1?

Compute:
- **Recall@k**: % of questions where answer chunk is in top-k
- **MRR** (Mean Reciprocal Rank): average of 1/rank of first relevant chunk

Target: Recall@5 > 0.85 before touching generation.

### Step 3 — Evaluate generation independently

Feed the oracle chunks (the correct ones) directly to the LLM. Ask it to answer using only those chunks. If it still fails, the problem is generation, not retrieval.

### Step 4 — Run the full pipeline evaluation

For each question in test set:

**Faithfulness** — Does the answer only use information from the retrieved chunks?
- LLM-as-judge: "Given these chunks and this answer, does the answer contain any claims not supported by the chunks? Yes/No and cite specific claims."
- Target: > 0.90

**Answer Relevance** — Does the answer actually address the question?
- LLM-as-judge: "On a scale of 1–5, how well does this answer address the question? Question: X, Answer: Y"
- Target: average > 4.0

**Context Precision** — Are the retrieved chunks actually useful?
- Check: what % of retrieved chunks contain information used in the answer?
- Low precision = noise in context = confused LLM

### Step 5 — Diagnose and fix

| Symptom | Root cause | Fix |
|---|---|---|
| Recall@5 < 0.7 | Chunking too coarse or fine | Adjust chunk size (try 256, 512, 1024 tokens) |
| MRR < 0.5 | Embedding model mismatch | Try domain-specific embeddings |
| High retrieval, low faithfulness | LLM not grounding on context | Add explicit "Answer ONLY using the provided context" to prompt |
| Answers vague, not specific | Chunks too long, key info buried | Smaller chunks + reranker |
| "I don't know" for answerable questions | Similarity threshold too strict | Lower the retrieval threshold |
| Hallucination on numbers/dates | Model filling gaps with priors | Add "If the exact value isn't in the context, say so" |

### Step 6 — Report

```
RAG Evaluation Report — [Date]

Dataset: [N] questions, [corpus description]
Model: [embedding model], [generation model]
Retrieval: top-[k], similarity threshold [t]

RETRIEVAL
  Recall@5:    0.XX  (target: >0.85)
  Recall@10:   0.XX
  MRR:         0.XX  (target: >0.70)

GENERATION
  Faithfulness:      0.XX  (target: >0.90)
  Answer Relevance:  0.XX  (target: >4.0)
  Context Precision: 0.XX

FAILURE ANALYSIS
  [N] retrieval failures — top categories:
  [N] generation failures — top categories:

RECOMMENDATIONS (priority order)
  1. ...
  2. ...
```

## Verification Checklist

- [ ] Test set has ≥20 questions
- [ ] Test set includes "not in corpus" questions
- [ ] Retrieval evaluated independently before full pipeline
- [ ] Each metric has a numeric value (not "looks good")
- [ ] At least 3 failure examples analyzed for root cause
- [ ] Recommendations are specific and actionable
