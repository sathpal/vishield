#!/usr/bin/env python
"""Replay the fictional dataset through the API to populate metrics (demo/load helper).

Only fictional text is sent. Mixes in a few invalid requests so error metrics are visible.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import requests

from vishield.config import RANDOM_SEED


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--dataset", default="data/starter_dataset.jsonl", type=Path)
    parser.add_argument("--minutes", type=float, default=5.0)
    parser.add_argument("--rps", type=float, default=0.5, help="average requests per second")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    rng = random.Random(args.seed)  # noqa: S311 - demo pacing only
    records = [json.loads(line) for line in args.dataset.read_text(encoding="utf-8").splitlines()]
    deadline = time.time() + args.minutes * 60
    sent = errors = 0
    batch_every = 40
    while time.time() < deadline:
        roll = rng.random()
        try:
            if roll < 0.05:
                requests.post(
                    f"{args.api}/analyze/transcript", json={"transcript": "  "}, timeout=10
                )
                errors += 1
            elif roll < 0.08:
                requests.post(
                    f"{args.api}/analyze/audio",
                    files={"file": ("x.txt", b"nope", "text/plain")},
                    data={"consent_confirmed": "true"},
                    timeout=10,
                )
                errors += 1
            else:
                rec = rng.choice(records)
                text = rec["text"]
                if rng.random() < 0.3:  # sprinkle redactable values so redaction metrics move
                    text += " Call back on 98765 43210 or mail help@example.com, code 483920."
                requests.post(
                    f"{args.api}/analyze/transcript", json={"transcript": text}, timeout=10
                )
            sent += 1
            if sent % batch_every == 0:
                items = [
                    {"id": r["id"], "transcript": r["text"], "label": r["label"]}
                    for r in rng.sample(records, 20)
                ]
                requests.post(f"{args.api}/evaluate/batch", json={"items": items}, timeout=60)
        except requests.RequestException as exc:
            print("request failed:", exc.__class__.__name__)
        time.sleep(max(0.05, rng.expovariate(args.rps)))
    print(f"sent={sent} deliberate_errors={errors}")


if __name__ == "__main__":
    main()
