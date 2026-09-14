#!/usr/bin/env python
"""Validate the starter dataset: schema, label/category consistency, duplicates, PII scan.

Exit code 1 on any blocking issue so it can run in CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from vishield.ml.dataset import (
    class_distribution,
    find_duplicates,
    load_records,
    scan_pii,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="data/starter_dataset.jsonl", type=Path)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    args = parser.parse_args()

    try:
        records = load_records(args.path)
    except (ValueError, OSError) as exc:
        print(f"SCHEMA ERROR: {exc}", file=sys.stderr)
        return 1

    issues = find_duplicates(records) + scan_pii(records)
    report = {
        "path": str(args.path),
        "records": len(records),
        "distribution": class_distribution(records),
        "issues": [i.model_dump() for i in issues],
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Loaded {len(records)} records from {args.path}")
        for group, counts in report["distribution"].items():
            print(f"  {group}: {counts}")
        if issues:
            print(f"\n{len(issues)} issue(s):")
            for issue in issues:
                print(f"  [{issue.kind}] {issue.record_id}: {issue.message}")
        else:
            print("\nNo duplicate, PII or organisation-name issues found.")
    blocking = [i for i in issues if i.kind in {"duplicate_id", "exact_duplicate", "pii_pattern"}]
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
