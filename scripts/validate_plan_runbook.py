#!/usr/bin/env python3
"""Validate required runbook-selection headings in a plan document."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REQUIRED_HEADINGS = (
    "Story Shape",
    "Chosen Runbook",
    "Preflight Dependency Audit",
    "Baseline Promotion Protocol",
    "Replan Triggers",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required runbook-selection headings in a plan document."
    )
    parser.add_argument("plan", type=Path, help="Path to the plan markdown file")
    return parser.parse_args()


def find_missing_headings(plan_text: str) -> list[str]:
    missing: list[str] = []
    for heading in REQUIRED_HEADINGS:
        needle = f"## {heading}"
        if not any(line.strip() == needle for line in plan_text.splitlines()):
            missing.append(heading)
    return missing


def main() -> int:
    args = parse_args()
    try:
        plan_text = args.plan.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Plan file not found: {args.plan}", file=sys.stderr)
        return 2

    missing = find_missing_headings(plan_text)
    if missing:
        print(
            "Missing required sections: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    print(f"OK: required runbook-selection headings present in {args.plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
