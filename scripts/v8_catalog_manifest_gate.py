#!/usr/bin/env python3
"""Validate phase-specific V8 task manifest coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MATERIALIZATION = (
    ROOT
    / "artifacts"
    / "PD-POSTDEMO-V8-MITIGATION-TASK-MANIFEST-20260712-01"
    / "materialization"
)
CATALOG_PATH = MATERIALIZATION / "catalog.json"
BASE_GATE_REGISTER_PATH = MATERIALIZATION / "gate_register.json"
FOUNDATION_INDEX_PATH = MATERIALIZATION / "foundation_manifest_index.json"
ALLOWED_STATUSES = (
    "unresolved",
    "confirmed-pending",
    "activated",
    "prior-PASS",
)
FOUNDATION_SELF_PENDING = "FPMS-V8-FOUNDATION-CLOSE-20260712-01"
FULL_ACTIVATION_SELF_PENDING = "FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01"
FINAL_CLOSE_SELF_PENDING = "FPMS-V8-FINAL-CLOSE-20260712-01"
TASK_DECLARATION = re.compile(r"^- Task file: `(tasks/postdemo/v8/[^`]+\.md)`$")
DECLARED_COUNT = re.compile(r"^Task count: (\d+)$")


class InputError(Exception):
    """The command or one of its inputs is malformed."""


class CoverageError(Exception):
    """A well-formed input violates the frozen coverage contract."""


class StoreOnce(argparse.Action):
    """Reject repeated uses of an option whose contract is singular."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} may be supplied only once")
        setattr(namespace, self.dest, values)


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read {label}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"{label} must be a JSON object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise InputError(f"{label} must be a JSON array")
    return value


def parse_catalog(
    catalog: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    tasks = require_list(catalog.get("tasks"), "catalog.tasks")
    if len(tasks) != 283 or not all(isinstance(row, dict) for row in tasks):
        raise InputError("catalog.tasks must contain 283 task objects")

    path_to_id: dict[str, str] = {}
    for row in tasks:
        task_id = row.get("task_id")
        task_path = row.get("task_path")
        if not isinstance(task_id, str) or not isinstance(task_path, str):
            raise InputError("catalog task identity is malformed")
        if task_path in path_to_id or task_id in path_to_id.values():
            raise InputError("catalog contains duplicate task identity")
        path_to_id[task_path] = task_id
    return tasks, path_to_id


def validate_gate_snapshot(
    snapshot: dict[str, Any], base: dict[str, Any]
) -> list[dict[str, Any]]:
    if set(snapshot) != set(base):
        raise InputError("gate register snapshot has the wrong top-level schema")
    if base.get("allowed_statuses") != list(ALLOWED_STATUSES):
        raise InputError("immutable base gate register has unexpected allowed_statuses")
    if snapshot.get("allowed_statuses") != base.get("allowed_statuses"):
        raise CoverageError("gate register allowed_statuses changed")
    if snapshot.get("counts") != base.get("counts"):
        raise CoverageError("gate register counts changed")

    rows = require_list(snapshot.get("rows"), "gate register rows")
    base_rows = require_list(base.get("rows"), "base gate register rows")
    if len(rows) != len(base_rows) or not all(
        isinstance(row, dict) for row in rows + base_rows
    ):
        raise InputError("gate register rows have the wrong schema")

    for row, base_row in zip(rows, base_rows, strict=True):
        if set(row) != set(base_row):
            raise InputError("gate register row has the wrong schema")
        if row.get("status") not in ALLOWED_STATUSES:
            raise CoverageError("gate register contains a disallowed status")
        if {key: value for key, value in row.items() if key != "status"} != {
            key: value for key, value in base_row.items() if key != "status"
        }:
            raise CoverageError("gate register changed an immutable row field")
    return rows


def parse_manifest(path: Path, path_to_id: dict[str, str]) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise InputError(f"cannot read manifest: {path}: {exc}") from exc

    count_matches = [DECLARED_COUNT.fullmatch(line) for line in lines]
    counts = [int(match.group(1)) for match in count_matches if match]
    if len(counts) != 1:
        raise InputError("manifest must declare exactly one Task count")

    task_ids: list[str] = []
    for line in lines:
        if "Task file" not in line:
            continue
        match = TASK_DECLARATION.fullmatch(line)
        if match is None:
            raise InputError(f"malformed task declaration: {line}")
        task_path = match.group(1)
        try:
            task_ids.append(path_to_id[task_path])
        except KeyError as exc:
            raise InputError(f"task path is outside the catalog: {task_path}") from exc

    if counts[0] != len(task_ids):
        raise InputError(
            f"declared Task count {counts[0]} does not equal parsed count {len(task_ids)}"
        )
    if len(task_ids) != len(set(task_ids)):
        raise InputError("manifest contains duplicate task IDs")
    return task_ids


def validate_foundation(
    task_ids: list[str],
    catalog_tasks: list[dict[str, Any]],
    foundation_index: dict[str, Any],
    gate_rows: list[dict[str, Any]],
    self_pending: str | None,
) -> None:
    expected = require_list(foundation_index.get("task_ids"), "foundation task_ids")
    excluded = require_list(
        foundation_index.get("excluded_task_ids"), "foundation excluded_task_ids"
    )
    if not all(isinstance(task_id, str) for task_id in expected + excluded):
        raise InputError("foundation index task IDs are malformed")
    if foundation_index.get("task_count") != 197 or len(expected) != 197:
        raise InputError("foundation index must contain 197 tasks")
    if len(excluded) != 86:
        raise InputError("foundation index must exclude 86 tasks")

    catalog_ids = [row["task_id"] for row in catalog_tasks]
    omitted = [task_id for task_id in catalog_ids if task_id not in set(expected)]
    if omitted != excluded:
        raise InputError("foundation index does not match catalog order and exclusions")
    if [row.get("task_id") for row in gate_rows] != excluded:
        raise CoverageError("foundation gate register rows do not match excluded tasks")
    if task_ids != expected:
        raise CoverageError("foundation manifest membership or order is incorrect")
    if self_pending is not None:
        if self_pending != FOUNDATION_SELF_PENDING or self_pending not in task_ids:
            raise CoverageError("foundation SELF_PENDING is not permitted")


def validate_lane(
    task_ids: list[str],
    catalog_tasks: list[dict[str, Any]],
    gate_rows: list[dict[str, Any]],
    self_pending: str | None,
) -> None:
    if self_pending is None:
        raise CoverageError("lane SELF_PENDING is required")

    catalog_by_id = {row["task_id"]: row for row in catalog_tasks}
    activation = catalog_by_id.get(self_pending)
    if activation is None or activation.get("deferred_kind") != "gate_activation":
        raise CoverageError("lane SELF_PENDING must identify a gate activation task")
    children = [
        row["task_id"]
        for row in catalog_tasks
        if row.get("lane_activation_task_id") == self_pending
    ]
    if task_ids != [self_pending, *children]:
        raise CoverageError("lane manifest membership or order is incorrect")

    gate_by_id = {row["task_id"]: row for row in gate_rows}
    active_statuses = {"confirmed-pending", "activated", "prior-PASS"}
    for task_id in task_ids:
        gate_row = gate_by_id.get(task_id)
        catalog_row = catalog_by_id[task_id]
        if gate_row is None:
            raise CoverageError(f"lane member is missing from gate register: {task_id}")
        if gate_row.get("status") not in active_statuses:
            raise CoverageError(f"lane member is not active: {task_id}")
        if gate_row.get("gate_requirements") != catalog_row.get("gate_requirements"):
            raise CoverageError(f"lane gate requirements changed: {task_id}")

    dependencies = activation.get("depends_on")
    if not isinstance(dependencies, list) or not all(
        isinstance(task_id, str) for task_id in dependencies
    ):
        raise InputError("lane activation depends_on is malformed")
    task_validate = ROOT / "scripts" / "task_validate.sh"
    failed_dependencies: list[str] = []
    for dependency in dependencies:
        try:
            result = subprocess.run(
                [str(task_validate), dependency],
                cwd=ROOT,
                check=False,
            )
        except OSError as exc:
            raise InputError(f"cannot run task gate: {task_validate}: {exc}") from exc
        if result.returncode != 0:
            failed_dependencies.append(dependency)
    if failed_dependencies:
        raise CoverageError(
            "prerequisite task gate failed: " + ", ".join(failed_dependencies)
        )


def validate_full(
    task_ids: list[str],
    catalog_tasks: list[dict[str, Any]],
    gate_rows: list[dict[str, Any]],
    self_pending: str | None,
) -> None:
    expected = [row["task_id"] for row in catalog_tasks]
    if task_ids != expected:
        raise CoverageError("full manifest membership or order is incorrect")
    if self_pending is not None:
        allowed_self = {FULL_ACTIVATION_SELF_PENDING, FINAL_CLOSE_SELF_PENDING}
        if self_pending not in allowed_self or self_pending not in task_ids:
            raise CoverageError("full SELF_PENDING is not permitted")

    complete_statuses = {"activated", "prior-PASS"}
    for row in gate_rows:
        task_id = row["task_id"]
        status = row["status"]
        if self_pending == FULL_ACTIVATION_SELF_PENDING and task_id == self_pending:
            if status not in complete_statuses | {"confirmed-pending"}:
                raise CoverageError("full activation has an invalid pending status")
        elif status not in complete_statuses:
            raise CoverageError(f"full deferred task is not complete: {task_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", required=True, choices=("foundation", "lane", "full")
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--gate-register", type=Path)
    parser.add_argument("--self-pending", action=StoreOnce)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        catalog = load_json(CATALOG_PATH, "catalog")
        base_register = load_json(BASE_GATE_REGISTER_PATH, "base gate register")
        foundation_index = load_json(FOUNDATION_INDEX_PATH, "foundation index")
        catalog_tasks, path_to_id = parse_catalog(catalog)
        gate_path = args.gate_register or BASE_GATE_REGISTER_PATH
        snapshot = load_json(gate_path, "gate register snapshot")
        gate_rows = validate_gate_snapshot(snapshot, base_register)
        task_ids = parse_manifest(args.manifest, path_to_id)

        if args.phase == "foundation":
            validate_foundation(
                task_ids,
                catalog_tasks,
                foundation_index,
                gate_rows,
                args.self_pending,
            )
        elif args.phase == "lane":
            validate_lane(task_ids, catalog_tasks, gate_rows, args.self_pending)
        else:
            validate_full(task_ids, catalog_tasks, gate_rows, args.self_pending)
    except InputError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    except CoverageError as exc:
        print(f"coverage violation: {exc}", file=sys.stderr)
        return 1

    print(f"{args.phase} manifest coverage accepted: {len(task_ids)} tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
