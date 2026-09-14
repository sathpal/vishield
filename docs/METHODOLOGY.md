# Methodology

## Research questions

RQ1 Can a small, explainable pipeline flag common vishing tactics in transcripts with useful
precision on held-out fictional data?
RQ2 Does fusing rule scores with a linear text model improve over either alone?
RQ3 Which explanations (rule spans vs feature attributions) do reviewers find clearer?
RQ4 Do simple acoustic aggregates add signal, or noise?

## Design

Design-science / prototype methodology in three iterations (phases). Each iteration produces a
runnable increment, tests and a measured result.

## Data

* Fictional starter set (80 samples, 10 categories) written by the team; see DATASET_CARD.
* Deterministic stratified split by category: 50 / 10 / 20 (seed 42).
* Validation: schema, label–category consistency, exact and near-duplicate detection (token
  Jaccard ≥ 0.85), PII pattern scan, real-organisation name scan.

## Models

| Stage | Model | Explanation mechanism |
|---|---|---|
| Baseline A | 8 regex rule families, weighted, saturating score `1 − e^(−Σw/3)` | matched spans |
| Baseline B | TF-IDF (1–2 gram, sublinear tf) + logistic regression (balanced, C = 2) | tf-idf × coefficient per token |
| Hybrid | weighted mean of A, B (and acoustic heuristic when audio) | both, plus weights used |
| Optional | transformer classifier (disabled), synthetic-voice heuristic (disabled) | – |

## Evaluation protocol

* Metrics: accuracy, precision, recall, F1 (positive = phishing), ROC-AUC, confusion matrix,
  per-category accuracy.
* Thresholds: rules and hybrid use the "medium" risk threshold (35/100); ML uses 0.5.
* Only the test split is reported; validation split is used for weight/threshold tuning.
* Every number is produced by `scripts/evaluate_model.py` → `reports/metrics.json`.
* Small-sample caveat: with n = 20 one error moves accuracy by 5 points; report counts, not
  just percentages.

## Explainability evaluation (RQ3)

Small-scale, within-team review: 10 transcripts, each student rates the clarity of rule-span
explanation vs feature-attribution explanation on a 1–5 scale; report medians and comments.
No external participants (avoids ethics approval overhead for a course project).

## Threats to validity

Construct: fictional text may not reflect real scam language. Internal: tiny data, possible
leakage of phrasing between categories written by the same authors. External: English-only,
Indian-English bias, no real audio. Conclusion: small n; confidence intervals are wide.
