#!/usr/bin/env python3
"""Run the captured Evidence 1.1 consumers in an isolated synthetic fixture."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tempfile
from typing import Sequence


GVR3_ID = "REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01"
FROZEN_CONSUMERS = (
    "scripts/evidence_init.sh",
    "scripts/evidence_run.sh",
    "scripts/evidence_task.py",
    "scripts/evidence_validate.py",
    "scripts/task_validate.sh",
    "scripts/atomic_evidence_validate.py",
    "scripts/release_gate.sh",
)


class FrozenAcceptanceError(ValueError):
    """A captured input or frozen acceptance decision is invalid."""


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_relative(value: str, label: str) -> str:
    path = PurePosixPath(value)
    if not value or "\\" in value or path.is_absolute() or ".." in path.parts:
        raise FrozenAcceptanceError(f"invalid {label}: {value!r}")
    if path.as_posix() != value:
        raise FrozenAcceptanceError(f"noncanonical {label}: {value!r}")
    return value


def read_object(path: Path, label: str) -> dict[str, object]:
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise FrozenAcceptanceError(f"{label} must be regular")
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeError) as exc:
        raise FrozenAcceptanceError(f"missing or malformed {label}") from exc
    if not isinstance(value, dict):
        raise FrozenAcceptanceError(f"{label} must contain an object")
    return value


def expected_paths(root: Path, task_id: str) -> tuple[Path, Path, Path, Path]:
    artifact = root / "artifacts" / task_id
    return (
        artifact,
        artifact / "bootstrap/frozen-v1",
        artifact / "bootstrap/frozen-v1-plan.json",
        artifact / "candidate",
    )


def verify_snapshot(
    root: Path,
    task_id: str,
    frozen_root: Path,
    candidate_root: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    artifact, expected_frozen, plan_path, expected_candidate = expected_paths(
        root, task_id
    )
    if frozen_root != expected_frozen or candidate_root != expected_candidate:
        raise FrozenAcceptanceError("runner paths differ from the frozen task contract")
    state = read_object(artifact / "state.json", "v2 state")
    baseline = state.get("baseline")
    if (
        state.get("schema_version") != 2
        or state.get("task_id") != task_id
        or not isinstance(baseline, dict)
    ):
        raise FrozenAcceptanceError("v2 state does not bind the frozen snapshot")
    inventory_path = frozen_root / "inventory.json"
    plan = read_object(plan_path, "frozen-v1 plan")
    inventory = read_object(inventory_path, "frozen-v1 inventory")
    if sha256(plan_path) != baseline.get("frozen_v1_plan_sha256") or sha256(
        inventory_path
    ) != baseline.get("frozen_v1_inventory_sha256"):
        raise FrozenAcceptanceError("frozen-v1 plan or inventory hash changed")
    plan_entries = plan.get("entries")
    inventory_entries = inventory.get("entries")
    if (
        set(plan) != {"schema_version", "entries", "tree_sha256"}
        or plan.get("schema_version") != 1
        or not isinstance(plan_entries, list)
        or plan.get("tree_sha256") != canonical_digest(plan_entries)
        or set(inventory) != {"schema_version", "entries", "tree_sha256"}
        or inventory.get("schema_version") != 1
        or not isinstance(inventory_entries, list)
        or inventory.get("tree_sha256") != canonical_digest(inventory_entries)
        or len(plan_entries) != len(FROZEN_CONSUMERS)
        or len(inventory_entries) != len(FROZEN_CONSUMERS)
    ):
        raise FrozenAcceptanceError("frozen-v1 plan or inventory schema is invalid")
    expected_inventory: list[dict[str, object]] = []
    for expected_path, entry in zip(FROZEN_CONSUMERS, plan_entries, strict=True):
        if not isinstance(entry, dict) or set(entry) != {
            "path",
            "length",
            "sha256",
            "mode",
            "content_b64",
        }:
            raise FrozenAcceptanceError("invalid frozen-v1 plan entry")
        if entry.get("path") != expected_path:
            raise FrozenAcceptanceError("frozen-v1 source order changed")
        safe_relative(expected_path, "frozen consumer path")
        try:
            content = base64.b64decode(str(entry.get("content_b64", "")), validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise FrozenAcceptanceError("invalid frozen-v1 embedded bytes") from exc
        source = frozen_root / expected_path
        try:
            info = source.lstat()
        except FileNotFoundError as exc:
            raise FrozenAcceptanceError(
                f"missing frozen consumer: {expected_path}"
            ) from exc
        if (
            not stat.S_ISREG(info.st_mode)
            or stat.S_IMODE(info.st_mode) != entry.get("mode")
            or source.read_bytes() != content
            or len(content) != entry.get("length")
            or hashlib.sha256(content).hexdigest() != entry.get("sha256")
        ):
            raise FrozenAcceptanceError(f"frozen consumer changed: {expected_path}")
        expected_inventory.append(
            {key: entry[key] for key in ("path", "length", "sha256", "mode")}
        )
    if inventory_entries != expected_inventory:
        raise FrozenAcceptanceError("frozen-v1 inventory differs from the source plan")
    observed_files: set[str] = set()
    for path in frozen_root.rglob("*"):
        info = path.lstat()
        relative = path.relative_to(frozen_root).as_posix()
        if stat.S_ISLNK(info.st_mode):
            raise FrozenAcceptanceError(f"frozen snapshot contains symlink: {relative}")
        if stat.S_ISREG(info.st_mode):
            observed_files.add(relative)
        elif not stat.S_ISDIR(info.st_mode):
            raise FrozenAcceptanceError(
                f"frozen snapshot contains non-regular entry: {relative}"
            )
    if observed_files != {"inventory.json", *FROZEN_CONSUMERS}:
        raise FrozenAcceptanceError("frozen snapshot file set changed")
    return plan, inventory


def protected_hashes(root: Path, task_id: str) -> dict[str, str]:
    artifact = root / "artifacts" / task_id
    metadata = read_object(artifact / "task.json", "task metadata")
    task_file = safe_relative(str(metadata.get("task_file", "")), "task file")
    relatives = [
        "AGENTS.md",
        "docs/agents/manifest.json",
        task_file,
        f"artifacts/{task_id}/summary.md",
        *FROZEN_CONSUMERS,
    ]
    review = artifact / "review"
    if review.is_dir():
        relatives.extend(
            path.relative_to(root).as_posix()
            for path in review.iterdir()
            if path.is_file() and not path.is_symlink()
        )
    hashes: dict[str, str] = {}
    for relative in sorted(set(relatives)):
        path = root / relative
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise FrozenAcceptanceError(f"protected path is unsafe: {relative}")
            hashes[relative] = sha256(path)
    return hashes


def write_fixture(root: Path, frozen_root: Path) -> str:
    task_id = "ENH-FROZEN-V1-SHADOW"
    for relative in FROZEN_CONSUMERS:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(frozen_root / relative, destination)
    task = root / f"tasks/repo/{task_id}.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        f"# {task_id}\n\nStatus: PASS\nRisk-Tier: HIGH\n"
        f"Task-Path: tasks/repo/{task_id}.md\n\n## Allowed Files\n\n"
        f"- `tasks/repo/{task_id}.md`\n- `artifacts/{task_id}/**`\n",
        encoding="utf-8",
    )
    artifact = root / "artifacts" / task_id
    (artifact / "git").mkdir(parents=True)
    (artifact / "outputs").mkdir()
    (artifact / "review").mkdir()
    (artifact / "task.json").write_bytes(
        canonical_json(
            {
                "task_id": task_id,
                "task_file": f"tasks/repo/{task_id}.md",
                "repo_root": str(root),
                "allowlist": [
                    f"tasks/repo/{task_id}.md",
                    f"artifacts/{task_id}/**",
                ],
                "baseline_dirty": False,
            }
        )
    )
    (artifact / "summary.md").write_text(
        f"# Frozen v1 shadow\nStatus: PASS\nTask-ID: {task_id}\n",
        encoding="utf-8",
    )
    (artifact / "git/diff.patch").write_text(
        "diff --git a/shadow b/shadow\n", encoding="utf-8"
    )
    (artifact / "review/independent_review.md").write_text(
        "Reviewer-ID: frozen-v1-reviewer\nVerdict: APPROVED\nP0: 0\nP1: 0\nP2: 0\n",
        encoding="utf-8",
    )
    rows: list[dict[str, object]] = []
    for index, step in enumerate(
        ("lint", "test", "scope", "independent_review", "task_gate"), start=1
    ):
        log = artifact / "outputs" / f"{step}.log"
        log.write_text("PASS\n", encoding="utf-8")
        rows.append(
            {
                "ts": f"20260717T00000{index}000000",
                "step": step,
                "rc": 0,
                "log": log.relative_to(root).as_posix(),
            }
        )
    (artifact / "results.jsonl").write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    (artifact / "commands.jsonl").write_text("{}\n", encoding="utf-8")
    return task_id


def run_shadow(root: Path, frozen_root: Path) -> list[dict[str, object]]:
    task_id = write_fixture(root, frozen_root)
    commands = (
        (
            "semantic_consumer",
            [
                "python3",
                "scripts/evidence_validate.py",
                task_id,
                "--required-step",
                "lint",
                "--required-step",
                "test",
                "--required-step",
                "scope",
            ],
        ),
        ("task_gate", ["./scripts/task_validate.sh", task_id]),
        (
            "atomic_gate",
            [
                "python3",
                "scripts/atomic_evidence_validate.py",
                task_id,
                "--required-step",
                "lint",
                "--required-step",
                "test",
                "--required-step",
                "scope",
            ],
        ),
        ("release_gate", ["./scripts/release_gate.sh"]),
    )
    results: list[dict[str, object]] = []
    for name, argv in commands:
        completed = subprocess.run(
            argv,
            cwd=root,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = completed.stdout[-4000:]
        results.append({"name": name, "rc": completed.returncode, "output": output})
        if completed.returncode != 0:
            raise FrozenAcceptanceError(
                f"frozen {name} rejected the valid shadow fixture: {output}"
            )
    return results


def atomic_report(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(canonical_json(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            Path(temporary).unlink()
        except FileNotFoundError:
            pass


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--frozen-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args(argv)
    root = Path.cwd().resolve()
    try:
        if args.task_id != GVR3_ID:
            raise FrozenAcceptanceError("runner is restricted to the exact GVR-3 task")
        frozen_root = (root / args.frozen_root).resolve()
        candidate_root = (root / args.candidate_root).resolve()
        plan, inventory = verify_snapshot(
            root, args.task_id, frozen_root, candidate_root
        )
        before = protected_hashes(root, args.task_id)
        with tempfile.TemporaryDirectory(prefix="fpms-frozen-v1-") as temporary:
            shadow = Path(temporary).resolve() / "repository"
            shadow.mkdir()
            decisions = run_shadow(shadow, frozen_root)
        after = protected_hashes(root, args.task_id)
        if before != after:
            raise FrozenAcceptanceError(
                "frozen shadow execution changed protected bytes"
            )
        report = {
            "schema_version": 1,
            "task_id": args.task_id,
            "decision": "PASS",
            "plan_sha256": hashlib.sha256(canonical_json(plan)).hexdigest(),
            "inventory_sha256": hashlib.sha256(canonical_json(inventory)).hexdigest(),
            "protected": before,
            "shadow_decisions": decisions,
        }
        atomic_report(candidate_root / "frozen-v1-report.json", report)
    except (FrozenAcceptanceError, OSError, UnicodeError) as exc:
        print(f"Frozen v1 acceptance rejected: {exc}")
        return 1
    print("Frozen v1 acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
