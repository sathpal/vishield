#!/usr/bin/env python
"""Redact a transcript from the command line (helper for contributors adding samples)."""

from __future__ import annotations

import sys

from vishield.domain.redaction import redact


def main() -> None:
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    result = redact(text)
    print(result.text)
    if result.counts:
        print(f"[redacted: {result.counts}]", file=sys.stderr)


if __name__ == "__main__":
    main()
