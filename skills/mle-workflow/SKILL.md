---
name: mle-workflow
description: Production ML engineering workflow — data contracts, reproducible training, evaluation gates, deployment, and monitoring. Use when building, reviewing, or hardening ML systems beyond notebooks.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [ml, machine-learning, mlops, training, evaluation, deployment, monitoring]
triggers: ['ml workflow', 'train model', 'machine learning', 'deploy model', 'mlops', 'pipeline']
---

# ML Engineering Workflow

Turns model work into production ML systems. Use only the stages that match your system — don't force heavyweight MLOps onto a simple classifier.

## When to Use

- Building a production ML feature (classifier, ranker, embeddings, LLM pipeline)
- Converting notebook code into a reproducible training pipeline
- Designing evaluation criteria before training starts
- Debugging data drift, stale features, or training/serving skew
- Planning model deployment and rollback

## Stage 1 — Data Contract

Define before writing code. Everything downstream depends on this.

```python
# data_contract.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class TrainingExample:
    text: str                    # input feature
    label: str                   # target: "positive" | "negative" | "neutral"
    source: str                  # where this came from
    created_at: str              # ISO 8601 timestamp
    metadata: Optional[dict] = None

# Constraints (validate in data loader, not model)
LABEL_SET = {"positive", "negative", "neutral"}
MAX_TEXT_TOKENS = 512
MIN_EXAMPLES_PER_LABEL = 100
```

Document: feature schema, label definitions (with examples of edge cases), known data quality issues, train/val/test split strategy, and class balance.

**Gate**: do not proceed until you have ≥ MIN_EXAMPLES_PER_LABEL for every label.

## Stage 2 — Baseline First

Before trying a complex model, establish a baseline you can beat:

- **Rule-based**: keyword matching, regex, heuristics
- **Classical ML**: TF-IDF + logistic regression, or fastText
- **Pretrained zero-shot**: test the LLM without fine-tuning first

Baselines are not just warm-ups. They define the performance floor and often expose that a simpler model is good enough.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

baseline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10_000)),
    ("clf", LogisticRegression(max_iter=1000))
])
baseline.fit(X_train, y_train)
print(classification_report(y_test, baseline.predict(X_test)))
```

Record baseline scores. Every iteration must beat this or explain why it doesn't.

## Stage 3 — Reproducible Training

```python
# train.py
import mlflow  # or wandb, neptune
import yaml

def train(config_path: str):
    config = yaml.safe_load(open(config_path))
    
    mlflow.set_experiment(config["experiment_name"])
    with mlflow.start_run():
        mlflow.log_params(config)
        
        # Seed everything for reproducibility
        set_seed(config["seed"])
        
        model = build_model(config)
        train_loader, val_loader = build_dataloaders(config)
        
        for epoch in range(config["epochs"]):
            train_loss = train_epoch(model, train_loader)
            val_metrics = evaluate(model, val_loader)
            
            mlflow.log_metrics(val_metrics, step=epoch)
            
            if val_metrics["f1"] > best_f1:
                mlflow.pytorch.log_model(model, "model")
                best_f1 = val_metrics["f1"]
```

Every training run must be: seeded, config-driven (no hardcoded hyperparams), tracked (metrics logged), and reproducible (same config = same result).

## Stage 4 — Evaluation Gates

Define promotion criteria before training, not after. "Good enough" decided by looking at results is a form of p-hacking.

```yaml
# evaluation_gates.yaml
gates:
  - metric: f1_weighted
    threshold: 0.85
    description: "Must beat baseline (0.78) by 7pp"
  - metric: precision_negative_class
    threshold: 0.90
    description: "False positives are expensive — precision on negative is critical"
  - metric: latency_p99_ms
    threshold: 200
    description: "SLA requirement for online inference"
  - metric: calibration_ece
    threshold: 0.05
    description: "Model probabilities must be reliable for downstream ranking"
```

If any gate fails: do not promote. Investigate, fix, retrain.

**Slice evaluation** — always evaluate on problem subgroups:
- By label class (catch per-class degradation)
- By data source (catch distribution shift)
- By time (catch temporal drift)
- By demographic slice (catch fairness issues)

## Stage 5 — Deployment

```python
# inference.py
class ModelServer:
    def __init__(self, model_uri: str):
        self.model = mlflow.pytorch.load_model(model_uri)
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_uri)
    
    def predict(self, texts: list[str]) -> list[dict]:
        inputs = self.tokenizer(texts, return_tensors="pt", 
                                truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)
        return [
            {"label": LABEL_SET[p.argmax()], "confidence": p.max().item()}
            for p in probs
        ]
```

**Deployment checklist:**
- [ ] Model artifact versioned and stored (S3/GCS/MLflow Registry)
- [ ] Input validation at the serving boundary (not in model code)
- [ ] Prediction logging enabled (inputs, outputs, latency)
- [ ] Health check endpoint returns model version
- [ ] Rollback procedure documented and tested

## Stage 6 — Monitoring

Production models degrade silently. Monitor:

**Data drift** — are inputs changing from what the model was trained on?
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=train_df, current_data=production_df)
```

**Prediction drift** — are output distributions shifting?
Track: label distribution, average confidence, % of low-confidence predictions.

**Business metrics** — does the model still improve the thing it was built for?
(CTR, conversion rate, user engagement — whichever it affects)

Set alerts for: data drift score > threshold, p99 latency spike, error rate increase, confidence distribution shift.

## Training/Serving Skew (The Sneaky Killer)

The most common production ML bug: the model sees different features in training vs production.

Common causes:
- Training used future data (label leakage)
- Feature computation differs between offline pipeline and online service
- Preprocessing applied inconsistently (normalize training but not production)

Fix: use the exact same feature extraction code in training and serving. Not "equivalent" code — the same function.

```python
# features.py — imported by BOTH train.py and server.py
def extract_features(text: str, user_context: dict) -> dict:
    return {
        "text_length": len(text.split()),
        "has_question": "?" in text,
        "user_tenure_days": (datetime.now() - user_context["created_at"]).days,
    }
```
