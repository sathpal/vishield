#!/usr/bin/env python
"""Train the TF-IDF + logistic-regression baseline on data/splits/train.jsonl.

Writes models/tfidf_logreg.joblib (git-ignored) and prints validation metrics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from vishield.ml.classifier import PhishingClassifier
from vishield.ml.dataset import load_records
from vishield.ml.evaluate import compute_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", default="data/splits", type=Path)
    parser.add_argument("--out", default="models/tfidf_logreg.joblib", type=Path)
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    train = load_records(args.splits / "train.jsonl")
    val = load_records(args.splits / "val.jsonl")
    sha = hashlib.sha256((args.splits / "train.jsonl").read_bytes()).hexdigest()

    clf = PhishingClassifier()
    clf.fit([r.text for r in train], [r.label for r in train], dataset_sha256=sha)
    clf.save(args.out)

    scores = clf.predict_proba_batch([r.text for r in val])
    preds = ["phishing" if s >= args.threshold else "legitimate" for s in scores]
    metrics = compute_metrics([r.label for r in val], preds, scores)
    print(json.dumps({"saved": str(args.out), "metadata": clf.metadata.__dict__}, indent=2))
    print("validation:", metrics.model_dump_json())
    top = clf.global_top_features(10)
    print("top phishing features:", [f for f, _ in top["phishing"]])
    print("top legitimate features:", [f for f, _ in top["legitimate"]])


if __name__ == "__main__":
    main()
