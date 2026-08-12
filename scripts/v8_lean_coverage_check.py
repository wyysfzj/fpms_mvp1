#!/usr/bin/env python3
"""Stateless V8 catalog/coverage validation for the C3 lean delivery flow."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPECTED_CATALOG_SHA256 = (
    "72c849825c9cbd39cb25f743d448b67a2a31bfccf7cfb68a3d2557c7bda178bf"
)
EXPECTED_DIRTY_PATH_MANIFEST_SHA256 = (
    "f4baccb49ea2cd331c76aa9c3b41dc4a4952be7be22a1e03ebac2524b0d22ab0"
)
EXPECTED_DIRTY_PATH_COUNT = 474
DISPOSITIONS = {
    "HISTORICAL_PASS_CANDIDATE",
    "INHERITED_EVIDENCE",
    "CURRENT_VERIFIED",
    "WIP",
    "PENDING",
    "CUSTOMER_BLOCKED",
    "AUTHORITY_BLOCKED",
    "SUPERSEDED_BY_STORY",
    "DEFERRED_FULL_ONLY",
}
STORY_STATUSES = {"PENDING", "CURRENT_VERIFIED", "BLOCKED"}
REVIEW_CLASSES = {"PROTECTED", "NORMAL", "MECHANICAL"}
MILESTONES = {"inventory", "foundation", "full", "final", "release"}
ROW278 = "FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01"
ROW281 = "FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01"
ROW282 = "FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01"
ROW283 = "FPMS-V8-FINAL-CLOSE-20260712-01"
FULL_TERMINAL_BASE_DEPENDENCY_SHA256 = {
    ROW281: "5800da16f9408789bd14370c40fe03264890f0bd46f76ad2070ed3404351ee5d",
    ROW282: "5800da16f9408789bd14370c40fe03264890f0bd46f76ad2070ed3404351ee5d",
}
FULL_TERMINAL_EFFECTIVE_DEPENDENCY_SHA256 = {
    ROW281: "6b17123b63d5a862a5f702454e38d2bab1e5a41512a4ed177b79957946c362b7",
    ROW282: "4369ee52400b52b368f66f2c447bf78b4d4c786834c1c74108c11ac13d70387b",
}
ROW283_DEPENDENCY_SHA256 = (
    "bbba116012490f9117f9fb68c539b45d0d8666733a77febbd0197076fb328e82"
)
FULL_TERMINAL_DEPENDENCY_OVERLAYS = [
    {"target_task_id": ROW281, "add": [ROW278]},
    {"target_task_id": ROW282, "add": [ROW278, ROW281]},
]
FULL_TERMINAL_EFFECTIVE_ORDER = [ROW278, ROW281, ROW282, ROW283]
FULL_TERMINAL_DEFERRED_COVERAGE = {
    "deferred_kinds": ["gated_product", "legacy_form"],
    "expected_catalog_rows": 53,
    "target_task_ids": [ROW281, ROW282],
}


class ValidationError(RuntimeError):
    """Raised when the lean coverage contract fails closed."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"top-level JSON must be an object: {path}")
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _require_exact_keys(
    value: Any,
    expected_keys: set[str],
    field: str,
) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise ValidationError(f"{field} does not match the exact schema")
    return value


def _require_acyclic(dependencies: dict[str, list[str]]) -> None:
    state: dict[str, int] = {}

    def visit(task_id: str) -> None:
        if state.get(task_id) == 1:
            raise ValidationError("effective dependency graph must remain acyclic")
        if state.get(task_id) == 2:
            return
        state[task_id] = 1
        for dependency in dependencies[task_id]:
            if dependency not in dependencies:
                raise ValidationError(
                    f"catalog dependency is not an exact catalog task: {dependency}"
                )
            visit(dependency)
        state[task_id] = 2

    for task_id in dependencies:
        visit(task_id)


def validate_full_terminal_dependency_successor(
    *,
    contract_path: Path,
    catalog_path: Path,
    repo_root: Path,
) -> None:
    """Validate the immutable additive Row278/281/282 terminal overlay."""

    contract = _require_exact_keys(
        _load_json(contract_path),
        {
            "schema_version",
            "catalog_sha256",
            "base_dependency_sha256",
            "dependency_overlays",
            "effective_dependency_sha256",
            "row283_dependency_sha256",
            "effective_order",
            "deferred_coverage",
        },
        "full-terminal dependency contract",
    )
    if contract["schema_version"] != 1:
        raise ValidationError("unsupported full-terminal dependency schema_version")

    overlays = contract["dependency_overlays"]
    if not isinstance(overlays, list):
        raise ValidationError("dependency_overlays does not match the exact schema")
    for index, overlay in enumerate(overlays):
        _require_exact_keys(
            overlay,
            {"target_task_id", "add"},
            f"dependency_overlays[{index}]",
        )
    if overlays != FULL_TERMINAL_DEPENDENCY_OVERLAYS:
        raise ValidationError("full-terminal contract requires exact additive dependency edges")

    actual_catalog_sha256 = _sha256(catalog_path)
    if (
        contract["catalog_sha256"] != EXPECTED_CATALOG_SHA256
        or actual_catalog_sha256 != EXPECTED_CATALOG_SHA256
    ):
        raise ValidationError("full-terminal catalog SHA-256 mismatch")
    if (
        contract["base_dependency_sha256"]
        != FULL_TERMINAL_BASE_DEPENDENCY_SHA256
    ):
        raise ValidationError("full-terminal base dependency SHA-256 mismatch")
    if (
        contract["effective_dependency_sha256"]
        != FULL_TERMINAL_EFFECTIVE_DEPENDENCY_SHA256
    ):
        raise ValidationError("full-terminal effective dependency SHA-256 mismatch")
    if contract["row283_dependency_sha256"] != ROW283_DEPENDENCY_SHA256:
        raise ValidationError("Row283 dependency SHA-256 mismatch")
    if contract["effective_order"] != FULL_TERMINAL_EFFECTIVE_ORDER:
        raise ValidationError("full-terminal effective order mismatch")
    if contract["deferred_coverage"] != FULL_TERMINAL_DEFERRED_COVERAGE:
        raise ValidationError("full-terminal deferred coverage contract mismatch")

    catalog = _load_json(catalog_path)
    tasks = catalog.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 283:
        raise ValidationError("full-terminal catalog must contain exactly 283 tasks")

    catalog_by_id: dict[str, dict[str, Any]] = {}
    for ordinal, task in enumerate(tasks, start=1):
        if not isinstance(task, dict) or task.get("ordinal") != ordinal:
            raise ValidationError("catalog ordinals must be exact and contiguous")
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or task_id in catalog_by_id:
            raise ValidationError("catalog task IDs must be exact and unique")
        for field, expected_type in {
            "gate_requirements": list,
            "owner_role": str,
            "serialization_groups": list,
            "phase": str,
            "task_path": str,
        }.items():
            if not isinstance(task.get(field), expected_type):
                raise ValidationError(
                    f"catalog remains authoritative for {field}: {task_id}"
                )
        catalog_by_id[task_id] = task

    for ordinal, task_id in zip((278, 281, 282, 283), FULL_TERMINAL_EFFECTIVE_ORDER):
        if tasks[ordinal - 1].get("task_id") != task_id:
            raise ValidationError(f"catalog Row{ordinal} identity mismatch")

    row283_dependencies = catalog_by_id[ROW283].get("depends_on")
    exact_predecessors = [task["task_id"] for task in tasks[:282]]
    if row283_dependencies != exact_predecessors:
        raise ValidationError("Row283 must remain all exact 282 predecessors")
    if _canonical_sha256(row283_dependencies) != ROW283_DEPENDENCY_SHA256:
        raise ValidationError("Row283 dependency SHA-256 mismatch")

    effective_dependencies: dict[str, list[str]] = {}
    additions = {
        overlay["target_task_id"]: overlay["add"] for overlay in overlays
    }
    for task_id, task in catalog_by_id.items():
        dependencies = task.get("depends_on")
        if not isinstance(dependencies, list) or any(
            not isinstance(dependency, str) for dependency in dependencies
        ):
            raise ValidationError(f"catalog depends_on must be a string list: {task_id}")
        if len(dependencies) != len(set(dependencies)):
            raise ValidationError(f"catalog depends_on contains duplicates: {task_id}")
        effective_dependencies[task_id] = dependencies + additions.get(task_id, [])

    for task_id, expected_sha256 in FULL_TERMINAL_BASE_DEPENDENCY_SHA256.items():
        if _canonical_sha256(catalog_by_id[task_id]["depends_on"]) != expected_sha256:
            raise ValidationError(f"base dependency SHA-256 mismatch: {task_id}")
    for task_id, expected_sha256 in FULL_TERMINAL_EFFECTIVE_DEPENDENCY_SHA256.items():
        if _canonical_sha256(effective_dependencies[task_id]) != expected_sha256:
            raise ValidationError(f"effective dependency SHA-256 mismatch: {task_id}")

    deferred_ids = {
        task["task_id"]
        for task in tasks
        if task.get("deferred_kind") in {"gated_product", "legacy_form"}
    }
    if len(deferred_ids) != 53:
        raise ValidationError(
            "full-terminal catalog must contain exactly 53 gated_product/legacy_form rows"
        )
    for task_id in (ROW281, ROW282):
        if not deferred_ids.issubset(effective_dependencies[task_id]):
            raise ValidationError(f"{task_id} does not cover all 53 deferred rows")
    if ROW281 not in effective_dependencies[ROW282] or not set(
        effective_dependencies[ROW281]
    ).issubset(effective_dependencies[ROW282]):
        raise ValidationError("Row282 effective dependencies must include Row281")

    _require_acyclic(effective_dependencies)


def _git(
    repo_root: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=check,
        capture_output=True,
        text=True,
    )


def _require_string_list(value: Any, field: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise ValidationError(f"{field} must be a non-empty string list")
    return value


def validate_dirty_path_disposition(
    disposition_path: Path,
    *,
    expected_path_manifest_sha256: str,
    expected_count: int,
) -> None:
    """Prove that every quarantined visible dirty path has one disposition."""

    payload = _load_json(disposition_path)
    entries = payload.get("entries")
    if payload.get("schema_version") != 1 or not isinstance(entries, list):
        raise ValidationError("invalid dirty-path disposition schema")
    if payload.get("total_paths") != expected_count or len(entries) != expected_count:
        raise ValidationError("dirty-path disposition count mismatch")

    paths: list[str] = []
    story_counts: dict[str, int] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValidationError(
                "every dirty-path disposition entry must be an object"
            )
        owned_path = entry.get("path")
        if not isinstance(owned_path, str) or not owned_path:
            raise ValidationError("every dirty-path disposition requires a path")
        paths.append(owned_path)
        disposition = entry.get("disposition")
        story_id = entry.get("story_id")
        if disposition == "ARCHIVE_ONLY_HISTORY":
            if story_id is not None:
                raise ValidationError("archive-only path cannot name an adoption story")
            count_key = "ARCHIVE_ONLY_HISTORY"
        elif disposition == "ADOPTION_STORY":
            if not isinstance(story_id, str) or not story_id:
                raise ValidationError("adoption path requires a story_id")
            count_key = story_id
        else:
            raise ValidationError(f"invalid dirty-path disposition: {owned_path}")
        story_counts[count_key] = story_counts.get(count_key, 0) + 1

    if len(set(paths)) != expected_count:
        raise ValidationError("every visible dirty path must appear exactly once")
    path_manifest = "".join(f"{owned_path}\n" for owned_path in sorted(paths)).encode()
    actual_manifest_sha = hashlib.sha256(path_manifest).hexdigest()
    if (
        payload.get("source_path_manifest_sha256") != expected_path_manifest_sha256
        or actual_manifest_sha != expected_path_manifest_sha256
    ):
        raise ValidationError("dirty-path source manifest SHA-256 mismatch")
    if payload.get("story_counts") not in (None, story_counts):
        raise ValidationError("dirty-path story_counts do not match entries")


def compute_tree_fingerprint(
    repo_root: Path,
    commit_sha: str,
    paths: list[str],
) -> str:
    """Hash exact Git blobs/modes for the story-owned paths at one commit."""

    records: list[bytes] = []
    for owned_path in sorted(set(paths)):
        result = _git(repo_root, "ls-tree", commit_sha, "--", owned_path, check=False)
        if result.returncode != 0 or not result.stdout.strip():
            raise ValidationError(f"story path is absent at {commit_sha}: {owned_path}")
        lines = result.stdout.rstrip("\n").splitlines()
        exact = [line for line in lines if line.split("\t", 1)[-1] == owned_path]
        if len(exact) != 1:
            raise ValidationError(
                f"story path is not one exact Git entry at {commit_sha}: {owned_path}"
            )
        metadata, resolved_path = exact[0].split("\t", 1)
        mode, object_type, object_sha = metadata.split()
        records.append(
            (f"{resolved_path}\0{mode}\0{object_type}\0{object_sha}\n").encode()
        )
    return hashlib.sha256(b"".join(records)).hexdigest()


def _validate_current_story(
    story: dict[str, Any],
    *,
    repo_root: Path,
    integration_sha: str,
) -> None:
    story_id = story.get("story_id")
    commits = _require_string_list(story.get("commits"), f"{story_id}.commits")
    paths = _require_string_list(story.get("paths"), f"{story_id}.paths")
    _require_string_list(story.get("tests"), f"{story_id}.tests")

    review_class = story.get("review_class")
    if review_class not in REVIEW_CLASSES:
        raise ValidationError(f"{story_id}.review_class is invalid")
    if review_class != "MECHANICAL" and not story.get("review_ref"):
        raise ValidationError(f"{story_id} requires independent review_ref")
    if review_class == "PROTECTED" and not story.get("verification_ref"):
        raise ValidationError(f"{story_id} requires independent verification_ref")

    for commit_sha in commits:
        reachable = _git(
            repo_root,
            "merge-base",
            "--is-ancestor",
            commit_sha,
            integration_sha,
            check=False,
        )
        if reachable.returncode != 0:
            raise ValidationError(
                f"{story_id} commit is not reachable from integration: {commit_sha}"
            )

    recorded_tree_sha = story.get("tree_sha256")
    if not isinstance(recorded_tree_sha, str) or len(recorded_tree_sha) != 64:
        raise ValidationError(f"{story_id}.tree_sha256 is invalid")
    reviewed_tree_sha = compute_tree_fingerprint(repo_root, commits[-1], paths)
    if reviewed_tree_sha != recorded_tree_sha:
        raise ValidationError(f"{story_id} review fingerprint does not match commit")


def _validate_integrated_path_owners(
    stories: list[dict[str, Any]],
    *,
    repo_root: Path,
    integration_sha: str,
) -> None:
    """Require current bytes to match each path's latest accepted owner."""

    owners: dict[str, dict[str, set[str]]] = {}
    canonical_commits: dict[str, str] = {}
    for story in stories:
        story_id = story["story_id"]
        final_ref = story["commits"][-1]
        if final_ref not in canonical_commits:
            canonical_commits[final_ref] = _git(
                repo_root,
                "rev-parse",
                f"{final_ref}^{{commit}}",
            ).stdout.strip()
        final_commit = canonical_commits[final_ref]
        for owned_path in story["paths"]:
            if owned_path == "docs/product/v8/coverage-ledger.json":
                continue
            owners.setdefault(owned_path, {}).setdefault(final_commit, set()).add(
                story_id
            )

    ancestry: dict[tuple[str, str], bool] = {}

    def is_ancestor(ancestor: str, descendant: str) -> bool:
        if ancestor == descendant:
            return True
        key = (ancestor, descendant)
        if key not in ancestry:
            ancestry[key] = (
                _git(
                    repo_root,
                    "merge-base",
                    "--is-ancestor",
                    ancestor,
                    descendant,
                    check=False,
                ).returncode
                == 0
            )
        return ancestry[key]

    for owned_path, owners_by_commit in owners.items():
        commits = tuple(owners_by_commit)
        latest = tuple(
            commit
            for commit in commits
            if not any(
                commit != other and is_ancestor(commit, other) for other in commits
            )
        )
        if len(latest) != 1:
            story_ids = sorted(
                story_id for commit in latest for story_id in owners_by_commit[commit]
            )
            raise ValidationError(
                f"{owned_path} has incomparable latest accepted owners: "
                + ", ".join(story_ids)
            )
        reviewed_tree_sha = compute_tree_fingerprint(
            repo_root,
            latest[0],
            [owned_path],
        )
        integrated_tree_sha = compute_tree_fingerprint(
            repo_root,
            integration_sha,
            [owned_path],
        )
        if integrated_tree_sha != reviewed_tree_sha:
            raise ValidationError(
                f"{owned_path} integrated bytes changed after latest accepted review"
            )


def validate(
    *,
    catalog_path: Path,
    ledger_path: Path,
    expected_catalog_sha256: str,
    milestone: str,
    repo_root: Path,
    integration_sha: str | None,
) -> None:
    if milestone not in MILESTONES:
        raise ValidationError(f"unknown milestone: {milestone}")
    if milestone != "inventory" and integration_sha is None:
        raise ValidationError("non-inventory validation requires integration_sha")

    actual_catalog_sha = _sha256(catalog_path)
    if actual_catalog_sha != expected_catalog_sha256:
        raise ValidationError(
            "catalog SHA-256 mismatch: "
            f"expected {expected_catalog_sha256}, got {actual_catalog_sha}"
        )

    catalog = _load_json(catalog_path)
    ledger = _load_json(ledger_path)
    tasks = catalog.get("tasks")
    rows = ledger.get("rows")
    stories = ledger.get("stories")
    if not isinstance(tasks, list) or not isinstance(rows, list):
        raise ValidationError("catalog tasks and ledger rows must be arrays")
    if not isinstance(stories, list):
        raise ValidationError("ledger stories must be an array")

    catalog_ids = [task.get("task_id") for task in tasks if isinstance(task, dict)]
    ledger_ids = [row.get("catalog_id") for row in rows if isinstance(row, dict)]
    if (
        len(catalog_ids) != len(tasks)
        or len(set(catalog_ids)) != len(catalog_ids)
        or len(ledger_ids) != len(rows)
        or sorted(ledger_ids) != sorted(catalog_ids)
        or len(set(ledger_ids)) != len(ledger_ids)
    ):
        raise ValidationError("every catalog ID must appear exactly once in the ledger")

    expected_count = catalog.get("counts", {}).get("catalog")
    if expected_count != len(tasks):
        raise ValidationError("catalog counts.catalog does not match tasks")
    if ledger.get("schema_version") != 1:
        raise ValidationError("unsupported coverage ledger schema_version")
    if ledger.get("catalog_sha256") != actual_catalog_sha:
        raise ValidationError("ledger catalog_sha256 does not match catalog bytes")

    catalog_by_id = {task["task_id"]: task for task in tasks}
    rows_by_id = {row["catalog_id"]: row for row in rows}
    stories_by_id: dict[str, dict[str, Any]] = {}
    for story in stories:
        if not isinstance(story, dict) or not isinstance(story.get("story_id"), str):
            raise ValidationError("every story requires a string story_id")
        story_id = story["story_id"]
        if story_id in stories_by_id:
            raise ValidationError(f"duplicate story_id: {story_id}")
        if story.get("status") not in STORY_STATUSES:
            raise ValidationError(f"invalid story status: {story_id}")
        stories_by_id[story_id] = story

    resolved_integration_sha = integration_sha
    if integration_sha is not None:
        try:
            resolved_integration_sha = _git(
                repo_root, "rev-parse", integration_sha
            ).stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise ValidationError("integration SHA cannot be resolved") from exc
        recorded_integration_sha = ledger.get("integration_sha")
        if recorded_integration_sha not in (None, resolved_integration_sha):
            raise ValidationError("ledger integration_sha does not match current input")

    for catalog_id, row in rows_by_id.items():
        if row.get("phase") != catalog_by_id[catalog_id].get("phase"):
            raise ValidationError(f"phase mismatch: {catalog_id}")
        disposition = row.get("disposition")
        if disposition not in DISPOSITIONS:
            raise ValidationError(f"invalid disposition: {catalog_id}")

        if disposition == "CURRENT_VERIFIED":
            story_id = row.get("story_id")
            story = stories_by_id.get(story_id)
            if story is None or story.get("status") != "CURRENT_VERIFIED":
                raise ValidationError(
                    f"{catalog_id} does not resolve to CURRENT_VERIFIED story"
                )
        elif disposition == "SUPERSEDED_BY_STORY":
            story_id = row.get("successor_story_id")
            story = stories_by_id.get(story_id)
            if story is None or story.get("status") != "CURRENT_VERIFIED":
                raise ValidationError(
                    f"{catalog_id} supersession lacks CURRENT_VERIFIED successor"
                )

    if resolved_integration_sha is not None:
        current_stories = [
            story for story in stories if story.get("status") == "CURRENT_VERIFIED"
        ]
        for story in current_stories:
            _validate_current_story(
                story,
                repo_root=repo_root,
                integration_sha=resolved_integration_sha,
            )
        _validate_integrated_path_owners(
            current_stories,
            repo_root=repo_root,
            integration_sha=resolved_integration_sha,
        )

    if milestone != "inventory":
        required_rows = (
            [
                row
                for row in rows
                if catalog_by_id[row["catalog_id"]].get("phase") == "foundation"
            ]
            if milestone == "foundation"
            else rows
        )
        unresolved = [
            row["catalog_id"]
            for row in required_rows
            if row.get("disposition") not in {"CURRENT_VERIFIED", "SUPERSEDED_BY_STORY"}
        ]
        if unresolved:
            raise ValidationError(
                f"{milestone} has unresolved required catalog rows: "
                + ", ".join(unresolved[:10])
            )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path("docs/product/v8/catalog.frozen.json"),
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("docs/product/v8/coverage-ledger.json"),
    )
    parser.add_argument(
        "--dirty-path-disposition",
        type=Path,
        default=Path("docs/product/v8/cutover-dirty-path-disposition.json"),
    )
    parser.add_argument(
        "--full-terminal-dependency-successor",
        type=Path,
        default=Path("docs/product/v8/full-terminal-dependency-successor.json"),
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--integration-sha")
    parser.add_argument("--milestone", choices=sorted(MILESTONES), required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    integration_sha = args.integration_sha
    if args.milestone != "inventory" and integration_sha is None:
        integration_sha = "HEAD"
    try:
        validate_dirty_path_disposition(
            args.dirty_path_disposition,
            expected_path_manifest_sha256=EXPECTED_DIRTY_PATH_MANIFEST_SHA256,
            expected_count=EXPECTED_DIRTY_PATH_COUNT,
        )
        validate_full_terminal_dependency_successor(
            contract_path=args.full_terminal_dependency_successor,
            catalog_path=args.catalog,
            repo_root=args.repo_root.resolve(),
        )
        validate(
            catalog_path=args.catalog,
            ledger_path=args.ledger,
            expected_catalog_sha256=EXPECTED_CATALOG_SHA256,
            milestone=args.milestone,
            repo_root=args.repo_root.resolve(),
            integration_sha=integration_sha,
        )
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: V8 coverage ledger ({args.milestone})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
