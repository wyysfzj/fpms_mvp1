#!/usr/bin/env python3
"""Compatibility CLI that delegates every durable action to taskctl."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Sequence


TASKCTL = Path(__file__).resolve().with_name("taskctl")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)

    run = commands.add_parser("run")
    run.add_argument("task_id")
    run.add_argument("step")
    run.add_argument("--cwd", required=True)

    backend = commands.add_parser("backend-pytest")
    backend.add_argument("task_id")
    backend.add_argument("--step", required=True, choices=("red", "test"))
    backend.add_argument("--expect-nonzero", action="store_true")

    close = commands.add_parser("close")
    close.add_argument("task_id")
    return parser


def split_payload(values: list[str]) -> tuple[list[str], list[str]]:
    if not values or values[0] not in {"run", "backend-pytest"}:
        return values, []
    try:
        separator = values.index("--")
    except ValueError:
        build_parser().error(f"{values[0]} requires -- before command arguments")
    payload = values[separator + 1 :]
    if not payload:
        build_parser().error(f"{values[0]} requires command arguments after --")
    return values[:separator], payload


def delegate(command: Sequence[str], *, cwd: Path) -> int:
    try:
        return subprocess.run([str(TASKCTL), *command], cwd=cwd, check=False).returncode
    except OSError as exc:
        print(f"Evidence adapter rejected: {exc}", file=sys.stderr)
        return 75


def main(argv: Sequence[str] | None = None) -> int:
    values, payload = split_payload(list(argv) if argv is not None else sys.argv[1:])
    args = build_parser().parse_args(values)
    caller = Path.cwd()
    if args.mode == "run":
        return delegate(
            [args.task_id, "record", args.step, "--", *payload],
            cwd=Path(args.cwd),
        )
    if args.mode == "backend-pytest":
        if args.step == "red" and not args.expect_nonzero:
            build_parser().error("red requires --expect-nonzero")
        if args.step == "test" and args.expect_nonzero:
            build_parser().error("--expect-nonzero is allowed only for red")
        return delegate(
            [args.task_id, "backend-test", args.step, "--", *payload], cwd=caller
        )
    return delegate([args.task_id, "close"], cwd=caller)


if __name__ == "__main__":
    raise SystemExit(main())
