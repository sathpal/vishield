#!/usr/bin/env python
"""Evaluate Baseline A (rules), Baseline B (ML) and the hybrid on the held-out test split.

Writes reports/metrics.json. All numbers come from the included data; nothing is fabricated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vishield.config import get_settings
from vishield.domain.risk_engine import RiskThresholds, RiskWeights, fuse
from vishield.domain.rules import detect_hits, rule_score
from vishield.ml.classifier import load_or_none
from vishield.ml.dataset import load_records
from vishield.ml.evaluate import compute_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="data/splits/test.jsonl", type=Path)
    parser.add_argument("--out", default="reports/metrics.json", type=Path)
    args = parser.parse_args()
    settings = get_settings()

    records = load_records(args.split)
    texts = [r.text for r in records]
    labels = [r.label for r in records]

    rule_scores = [rule_score(detect_hits(t), settings.rule_saturation_weight) for t in texts]
    thresholds = RiskThresholds(settings.risk_medium_threshold, settings.risk_high_threshold)
    weights = RiskWeights(settings.weight_rules, settings.weight_ml, settings.weight_acoustic)
    cut = thresholds.medium / 100.0

    report: dict[str, object] = {"split": str(args.split), "n": len(records)}
    report["rules_only"] = compute_metrics(
        labels, ["phishing" if s >= cut else "legitimate" for s in rule_scores], rule_scores
    ).model_dump()

    clf = load_or_none(settings.model_path)
    if clf is None:
        report["ml_only"] = {"error": f"model not found at {settings.model_path}; run train first"}
        report["hybrid"] = report["ml_only"]
    else:
        ml_scores = clf.predict_proba_batch(texts)
        report["ml_only"] = compute_metrics(
            labels, ["phishing" if s >= 0.5 else "legitimate" for s in ml_scores], ml_scores
        ).model_dump()
        hybrid = [
            fuse(r, m, None, weights, thresholds).score / 100.0
            for r, m in zip(rule_scores, ml_scores, strict=True)
        ]
        report["hybrid"] = compute_metrics(
            labels, ["phishing" if s >= cut else "legitimate" for s in hybrid], hybrid
        ).model_dump()
        report["model_metadata"] = clf.metadata.__dict__

    per_category: dict[str, dict[str, int]] = {}
    for rec, s in zip(records, rule_scores, strict=True):
        bucket = per_category.setdefault(rec.category, {"n": 0, "rules_correct": 0})
        bucket["n"] += 1
        pred = "phishing" if s >= cut else "legitimate"
        bucket["rules_correct"] += int(pred == rec.label)
    report["per_category_rules"] = per_category

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
