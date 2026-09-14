#!/usr/bin/env python
"""Create deterministic stratified train/val/test splits and a distribution report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vishield.config import RANDOM_SEED
from vishield.ml.dataset import class_distribution, load_records, stratified_split, write_records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/starter_dataset.jsonl", type=Path)
    parser.add_argument("--out", default="data/splits", type=Path)
    parser.add_argument("--val", type=float, default=0.15)
    parser.add_argument("--test", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    records = load_records(args.input)
    train, val, test = stratified_split(records, args.val, args.test, args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    write_records(args.out / "train.jsonl", train)
    write_records(args.out / "val.jsonl", val)
    write_records(args.out / "test.jsonl", test)
    report = {
        "seed": args.seed,
        "total": len(records),
        "train": {"n": len(train), **class_distribution(train)},
        "val": {"n": len(val), **class_distribution(val)},
        "test": {"n": len(test), **class_distribution(test)},
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: (v["n"] if isinstance(v, dict) else v) for k, v in report.items()}))


if __name__ == "__main__":
    main()
