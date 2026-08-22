#!/usr/bin/env python3
"""Shared semantic consumer for immutable legacy ledgers and Evidence v2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Sequence


TASK_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
HEX_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
EVENT_NAME = re.compile(r"(?P<ordinal>[0-9]{8})\.(?P<kind>command|result)\.json\Z")
ALLOWED_HEADING = re.compile(r"^##\s+Allowed Files\s*$")
HEADING = re.compile(r"^#{1,6}\s+")
ALLOWED_ITEM = re.compile(r"^\s*-\s+`([^`]+)`\s*$")
GVR3_ID = "REPO-GOVERNANCE-RESET-ACTIVATION-20260716-01"
GVR3_REQUIRED = {
    "test",
    "shell_check",
    "format_check",
    "lint",
    "compile",
    "frozen_v1",
    "diff_check",
    "scope",
}
GVR3_TEST_ARGV = (
    "env",
    "PYTHONDONTWRITEBYTECODE=1",
    "python3",
    "-m",
    "unittest",
    "-v",
    "scripts.tests.test_governance_reset_adapters",
    "scripts.tests.test_governance_reset_consumers",
    "scripts.tests.test_governance_reset_activation",
)
GVR3_PYTHON_CHECK_FILES = (
    "scripts/evidence_task.py",
    "scripts/evidence_validate.py",
    "scripts/atomic_evidence_validate.py",
    "scripts/frozen_v1_acceptance.py",
    "scripts/tests/test_governance_reset_adapters.py",
    "scripts/tests/test_governance_reset_consumers.py",
    "scripts/tests/test_governance_reset_activation.py",
)
GVR3_REQUIRED_COMMANDS = {
    "test": (GVR3_TEST_ARGV, "NON_SQLITE"),
    "shell_check": (
        (
            "bash",
            "-n",
            "scripts/evidence_init.sh",
            "scripts/evidence_run.sh",
            "scripts/task_validate.sh",
            "scripts/release_gate.sh",
        ),
        "NON_SQLITE",
    ),
    "format_check": (
        ("ruff", "format", "--check", *GVR3_PYTHON_CHECK_FILES),
        "NON_SQLITE",
    ),
    "lint": (("ruff", "check", *GVR3_PYTHON_CHECK_FILES), "NON_SQLITE"),
    "compile": (
        (
            "env",
            "PYTHONPYCACHEPREFIX=/tmp/fpms-gvr3-pycache",
            "python3",
            "-m",
            "py_compile",
            *GVR3_PYTHON_CHECK_FILES,
        ),
        "NON_SQLITE",
    ),
    "frozen_v1": (
        (
            "python3",
            "scripts/frozen_v1_acceptance.py",
            "--task-id",
            GVR3_ID,
            "--frozen-root",
            f"artifacts/{GVR3_ID}/bootstrap/frozen-v1",
            "--candidate-root",
            f"artifacts/{GVR3_ID}/candidate",
        ),
        "FROZEN_V1",
    ),
    "diff_check": (
        (
            "git",
            "diff",
            "--check",
            "--",
            f"tasks/repo/{GVR3_ID}.md",
            "AGENTS.md",
            "docs/agents/manifest.json",
            "docs/agents/legacy-pass-ledger.json",
            "scripts/evidence_init.sh",
            "scripts/evidence_run.sh",
            "scripts/evidence_task.py",
            "scripts/evidence_validate.py",
            "scripts/task_validate.sh",
            "scripts/atomic_evidence_validate.py",
            "scripts/release_gate.sh",
            "scripts/frozen_v1_acceptance.py",
            "scripts/tests/test_governance_reset_adapters.py",
            "scripts/tests/test_governance_reset_consumers.py",
            "scripts/tests/test_governance_reset_activation.py",
        ),
        "NON_SQLITE",
    ),
    "scope": (
        (
            "python3",
            "scripts/evidence_scope.py",
            "finalize",
            GVR3_ID,
        ),
        "SCOPE",
    ),
}
ORDINARY_REQUIRED = {"lint", "test", "scope"}
CLOSE_STEPS = (
    "taskctl_scope_refresh",
    "independent_review",
    "task_gate",
    "atomic_evidence",
    "taskctl_close",
)
REVIEW_FIELDS = (
    "Reviewed-Candidate-Fingerprint",
    "Reviewed-Patch-SHA256",
    "Reviewed-Governance-Digest",
    "Reviewer-ID",
    "Verdict",
    "P0",
    "P1",
    "P2",
)


class EvidenceValidationError(ValueError):
    """Fail-closed semantic evidence error."""


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json_object(path: Path, label: str) -> dict[str, object]:
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise EvidenceValidationError(f"{label} must be a regular file")
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeError) as exc:
        raise EvidenceValidationError(f"missing or malformed {label}") from exc
    if not isinstance(value, dict):
        raise EvidenceValidationError(f"{label} must contain an object")
    return value


def normalized_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise EvidenceValidationError(f"{label} must be a normalized repository path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise EvidenceValidationError(f"{label} must be a normalized repository path")
    return value


def repository_file(root: Path, relative: object, label: str) -> Path:
    value = normalized_relative_path(relative, label)
    current = root
    for part in PurePosixPath(value).parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError as exc:
            raise EvidenceValidationError(f"missing {label}: {value}") from exc
        if stat.S_ISLNK(info.st_mode):
            raise EvidenceValidationError(f"symlink is forbidden for {label}: {value}")
    if not stat.S_ISREG(current.lstat().st_mode):
        raise EvidenceValidationError(f"{label} must be a regular file: {value}")
    return current


def parse_task_allowlist(task: Path, task_id: str, root: Path) -> list[str]:
    try:
        lines = task.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvidenceValidationError("cannot read task contract") from exc
    task_paths = [
        line.removeprefix("Task-Path:").strip()
        for line in lines
        if line.startswith("Task-Path:")
    ]
    try:
        expected_task = task.relative_to(root).as_posix()
    except ValueError as exc:
        raise EvidenceValidationError(
            "task contract is outside repository root"
        ) from exc
    if task_paths != [expected_task]:
        raise EvidenceValidationError("task contract Task-Path is not unique or exact")
    headings = [
        index for index, line in enumerate(lines) if ALLOWED_HEADING.match(line)
    ]
    if len(headings) != 1:
        raise EvidenceValidationError(
            "task contract requires one Allowed Files section"
        )
    entries: list[str] = []
    for line in lines[headings[0] + 1 :]:
        if HEADING.match(line):
            break
        if not line.strip():
            continue
        match = ALLOWED_ITEM.match(line)
        if match is None:
            raise EvidenceValidationError(
                "task contract contains a malformed allowlist"
            )
        entries.append(normalized_relative_path(match.group(1), "allowlist entry"))
    evidence = f"artifacts/{task_id}/**"
    if len(entries) != len(set(entries)) or entries.count(evidence) != 1:
        raise EvidenceValidationError("task contract allowlist is empty or ambiguous")
    return [entry for entry in entries if entry != evidence]


def first_status_is_pass(task: Path) -> bool:
    try:
        values = [
            line.removeprefix("Status:").strip()
            for line in task.read_text(encoding="utf-8").splitlines()
            if line.startswith("Status:")
        ]
    except (OSError, UnicodeError):
        return False
    return bool(values) and (values[0] == "PASS" or values[0].startswith("PASS /"))


def read_jsonl(path: Path, label: str) -> list[dict[str, object]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvidenceValidationError(f"cannot read {label}") from exc
    rows: list[dict[str, object]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvidenceValidationError(f"malformed {label} line {number}") from exc
        if not isinstance(value, dict):
            raise EvidenceValidationError(f"non-object {label} line {number}")
        rows.append(value)
    return rows


def artifact_tree(root: Path, task_id: str) -> tuple[list[dict[str, object]], str]:
    artifact = root / "artifacts" / task_id
    try:
        root_info = artifact.lstat()
    except FileNotFoundError as exc:
        raise EvidenceValidationError(f"missing artifact tree for {task_id}") from exc
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise EvidenceValidationError(f"artifact root is unsafe for {task_id}")
    entries: list[dict[str, object]] = []
    for directory, directories, files in os.walk(artifact, followlinks=False):
        parent = Path(directory)
        for name in sorted(directories, key=lambda item: item.encode("utf-8")):
            info = (parent / name).lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise EvidenceValidationError(
                    f"artifact tree contains an unsafe directory: {parent / name}"
                )
        for name in files:
            path = parent / name
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise EvidenceValidationError(
                    f"artifact tree contains a non-regular file: {path}"
                )
            content = path.read_bytes()
            entries.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "mode": format(stat.S_IFREG | stat.S_IMODE(info.st_mode), "06o"),
                    "length": len(content),
                    "sha256": sha256_bytes(content),
                }
            )
    entries.sort(key=lambda entry: str(entry["path"]).encode("utf-8"))
    return entries, canonical_digest(entries)


def legacy_acceptance_time(artifact: Path) -> str:
    successful = [
        row.get("ts")
        for row in read_jsonl(artifact / "results.jsonl", "legacy results")
        if type(row.get("rc")) is int
        and row.get("rc") == 0
        and isinstance(row.get("ts"), str)
        and row["ts"]
    ]
    if not successful:
        raise EvidenceValidationError("legacy PASS task has no successful result time")
    return max(successful)


def discover_legacy_pass_task_ids(root: Path) -> list[str]:
    root = root.resolve()
    discovered: dict[str, str] = {}
    for task in (root / "tasks").rglob("*.md"):
        if task.is_symlink() or not task.is_file() or not first_status_is_pass(task):
            continue
        task_id = task.stem
        if not TASK_ID_PATTERN.fullmatch(task_id):
            raise EvidenceValidationError(f"invalid PASS task ID: {task_id}")
        artifact = root / "artifacts" / task_id
        if not artifact.is_dir() or (artifact / "state.json").exists():
            continue
        relative = task.relative_to(root).as_posix()
        if (artifact / "task.json").is_file():
            metadata = read_json_object(artifact / "task.json", "legacy task.json")
            if (
                metadata.get("task_id") != task_id
                or metadata.get("task_file") != relative
            ):
                raise EvidenceValidationError(
                    f"legacy PASS identity mismatch: {task_id}"
                )
        elif (
            not (artifact / "summary.md").is_file()
            or not (artifact / "results.jsonl").is_file()
        ):
            raise EvidenceValidationError(
                f"legacy PASS has no bindable identity/evidence: {task_id}"
            )
        previous = discovered.get(task_id)
        if previous is not None and previous != relative:
            raise EvidenceValidationError(f"duplicate legacy PASS task ID: {task_id}")
        discovered[task_id] = relative
    return sorted(discovered, key=lambda value: value.encode("utf-8"))


def locate_legacy_task(root: Path, task_id: str, artifact: Path) -> tuple[str, Path]:
    metadata_path = artifact / "task.json"
    if metadata_path.is_file():
        metadata = read_json_object(metadata_path, "legacy task.json")
        if metadata.get("task_id") != task_id:
            raise EvidenceValidationError(f"legacy task identity mismatch: {task_id}")
        task_relative = normalized_relative_path(
            metadata.get("task_file"), "legacy task file"
        )
        task = repository_file(root, task_relative, "legacy task file")
        return task_relative, task
    candidates = [
        task
        for task in (root / "tasks").rglob(f"{task_id}.md")
        if not task.is_symlink() and task.is_file() and first_status_is_pass(task)
    ]
    if len(candidates) != 1:
        raise EvidenceValidationError(
            f"legacy task without task.json is not uniquely bindable: {task_id}"
        )
    task = candidates[0]
    return task.relative_to(root).as_posix(), task


def build_legacy_ledger(root: Path, task_ids: Sequence[str]) -> dict[str, object]:
    root = root.resolve()
    if len(task_ids) != len(set(task_ids)):
        raise EvidenceValidationError("legacy ledger task IDs must be unique")
    tasks: list[dict[str, object]] = []
    for task_id in sorted(task_ids, key=lambda value: value.encode("utf-8")):
        if not TASK_ID_PATTERN.fullmatch(task_id):
            raise EvidenceValidationError(f"invalid legacy task ID: {task_id}")
        artifact = root / "artifacts" / task_id
        if (artifact / "state.json").exists():
            raise EvidenceValidationError(
                f"v2 task cannot enter legacy ledger: {task_id}"
            )
        task_relative, task = locate_legacy_task(root, task_id, artifact)
        if task.stem != task_id or not first_status_is_pass(task):
            raise EvidenceValidationError(
                f"legacy task is not recorded PASS: {task_id}"
            )
        files, tree_digest = artifact_tree(root, task_id)
        tasks.append(
            {
                "task_id": task_id,
                "accepted_at": legacy_acceptance_time(artifact),
                "task_file": task_relative,
                "task_file_sha256": sha256_file(task),
                "artifact_root_digest": tree_digest,
                "files": files,
            }
        )
    ledger: dict[str, object] = {"schema_version": 1, "tasks": tasks}
    ledger["root_digest"] = canonical_digest(tasks)
    return ledger


def validate_ledger_schema(ledger: dict[str, object]) -> list[dict[str, object]]:
    if (
        set(ledger) != {"schema_version", "tasks", "root_digest"}
        or ledger.get("schema_version") != 1
    ):
        raise EvidenceValidationError("invalid legacy ledger schema")
    tasks = ledger.get("tasks")
    if not isinstance(tasks, list) or ledger.get("root_digest") != canonical_digest(
        tasks
    ):
        raise EvidenceValidationError("legacy ledger root digest mismatch")
    ids: list[str] = []
    for entry in tasks:
        if not isinstance(entry, dict) or set(entry) != {
            "task_id",
            "accepted_at",
            "task_file",
            "task_file_sha256",
            "artifact_root_digest",
            "files",
        }:
            raise EvidenceValidationError("invalid legacy ledger task entry")
        task_id = entry.get("task_id")
        files = entry.get("files")
        if (
            not isinstance(task_id, str)
            or not TASK_ID_PATTERN.fullmatch(task_id)
            or not isinstance(entry.get("accepted_at"), str)
            or not entry["accepted_at"]
            or not isinstance(files, list)
            or entry.get("artifact_root_digest") != canonical_digest(files)
            or not isinstance(entry.get("task_file_sha256"), str)
            or not HEX_PATTERN.fullmatch(str(entry["task_file_sha256"]))
        ):
            raise EvidenceValidationError("invalid legacy ledger task binding")
        normalized_relative_path(entry.get("task_file"), "ledger task file")
        paths: list[str] = []
        for file_entry in files:
            if not isinstance(file_entry, dict) or set(file_entry) != {
                "path",
                "mode",
                "length",
                "sha256",
            }:
                raise EvidenceValidationError("invalid legacy ledger file entry")
            path = normalized_relative_path(file_entry.get("path"), "ledger file")
            if (
                not path.startswith(f"artifacts/{task_id}/")
                or not re.fullmatch(r"1[0-7][0-7]{4}", str(file_entry.get("mode")))
                or type(file_entry.get("length")) is not int
                or file_entry["length"] < 0
                or not isinstance(file_entry.get("sha256"), str)
                or not HEX_PATTERN.fullmatch(str(file_entry["sha256"]))
            ):
                raise EvidenceValidationError("invalid legacy ledger file binding")
            paths.append(path)
        if paths != sorted(paths, key=lambda value: value.encode("utf-8")) or len(
            paths
        ) != len(set(paths)):
            raise EvidenceValidationError("legacy ledger file order or set is invalid")
        ids.append(task_id)
    if ids != sorted(ids, key=lambda value: value.encode("utf-8")) or len(ids) != len(
        set(ids)
    ):
        raise EvidenceValidationError("legacy ledger task order or set is invalid")
    return tasks


def ledger_entry(root: Path, task_id: str) -> dict[str, object] | None:
    path = root / "docs/agents/legacy-pass-ledger.json"
    if not path.exists():
        return None
    tasks = validate_ledger_schema(read_json_object(path, "legacy PASS ledger"))
    matches = [entry for entry in tasks if entry.get("task_id") == task_id]
    if len(matches) > 1:
        raise EvidenceValidationError("duplicate legacy ledger task")
    return matches[0] if matches else None


def validate_legacy(root: Path, task_id: str, entry: dict[str, object]) -> None:
    task = repository_file(root, entry.get("task_file"), "ledger task file")
    if task.stem != task_id or sha256_file(task) != entry.get("task_file_sha256"):
        raise EvidenceValidationError("legacy task file changed after ledger freeze")
    files, digest = artifact_tree(root, task_id)
    if files != entry.get("files") or digest != entry.get("artifact_root_digest"):
        raise EvidenceValidationError(
            "legacy artifact tree changed after ledger freeze"
        )


def valid_identity(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and value.casefold() != "none"
        and all(ord(character) >= 32 and ord(character) != 127 for character in value)
    )


def load_events(
    root: Path, artifact: Path, task_id: str
) -> tuple[dict[int, dict[str, object]], dict[int, dict[str, object]]]:
    events = artifact / "events"
    try:
        info = events.lstat()
    except FileNotFoundError as exc:
        raise EvidenceValidationError("missing v2 events") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise EvidenceValidationError("v2 events root is unsafe")
    commands: dict[int, dict[str, object]] = {}
    results: dict[int, dict[str, object]] = {}
    for path in events.iterdir():
        match = EVENT_NAME.fullmatch(path.name)
        if match is None:
            continue
        if not stat.S_ISREG(path.lstat().st_mode):
            raise EvidenceValidationError(f"event is not regular: {path.name}")
        ordinal = int(match.group("ordinal"))
        if ordinal <= 0 or path.name != f"{ordinal:08d}.{match.group('kind')}.json":
            raise EvidenceValidationError(f"invalid event filename: {path.name}")
        target = commands if match.group("kind") == "command" else results
        if ordinal in target:
            raise EvidenceValidationError(f"duplicate event ordinal: {ordinal}")
        target[ordinal] = read_json_object(path, f"event {path.name}")
    ordinals = sorted(commands)
    if not ordinals or ordinals != list(range(1, ordinals[-1] + 1)):
        raise EvidenceValidationError("command event sequence has an ordinal gap")
    if not set(results) <= set(commands):
        raise EvidenceValidationError("orphan result event")
    for ordinal, command in commands.items():
        if (
            command.get("schema_version") != 2
            or command.get("task_id") != task_id
            or type(command.get("ordinal")) is not int
            or command["ordinal"] != ordinal
            or not isinstance(command.get("step"), str)
            or not command["step"]
            or not isinstance(command.get("argv"), list)
            or not all(isinstance(value, str) for value in command["argv"])
            or not isinstance(command.get("cwd"), str)
            or not isinstance(command.get("classification"), str)
            or not isinstance(command.get("replay_safe"), bool)
            or not isinstance(command.get("request_digest"), str)
            or not HEX_PATTERN.fullmatch(str(command["request_digest"]))
        ):
            raise EvidenceValidationError(f"invalid command event {ordinal}")
        request = {
            "task_id": task_id,
            "step": command["step"],
            "argv": command["argv"],
            "cwd": command["cwd"],
            "classification": command["classification"],
            "replay_safe": command["replay_safe"],
        }
        if canonical_digest(request) != command["request_digest"]:
            raise EvidenceValidationError(f"command digest mismatch at {ordinal}")
    for ordinal, result in results.items():
        command = commands[ordinal]
        if (
            result.get("schema_version") != 2
            or result.get("task_id") != task_id
            or type(result.get("ordinal")) is not int
            or result["ordinal"] != ordinal
            or result.get("step") != command.get("step")
            or type(result.get("rc")) is not int
        ):
            raise EvidenceValidationError(f"invalid result event {ordinal}")
    return commands, results


def validate_result(
    root: Path,
    artifact: Path,
    task_id: str,
    ordinal: int,
    result: dict[str, object],
    *,
    binding: dict[str, object] | None = None,
    require_log_binding: bool = False,
) -> tuple[Path, Path]:
    if result.get("rc") != 0 or result.get("executed") is not True:
        raise EvidenceValidationError(f"required result is not successful: {ordinal}")
    result_path = artifact / "events" / f"{ordinal:08d}.result.json"
    log_relative = normalized_relative_path(result.get("log"), "result log")
    prefix = f"artifacts/{task_id}/outputs/"
    if not log_relative.startswith(prefix) or log_relative == prefix:
        raise EvidenceValidationError("result log is outside task outputs")
    log_path = repository_file(root, log_relative, "result log")
    result_hash = sha256_file(result_path)
    log_hash = sha256_file(log_path)
    if binding is not None and binding != {
        "result_sha256": result_hash,
        "log_sha256": log_hash,
    }:
        raise EvidenceValidationError("candidate result/log binding changed")
    if require_log_binding and result.get("log_sha256") != log_hash:
        raise EvidenceValidationError("close result log hash changed")
    return result_path, log_path


def latest_result(
    commands: dict[int, dict[str, object]],
    results: dict[int, dict[str, object]],
    step: str,
) -> tuple[int, dict[str, object]]:
    matches = [
        ordinal
        for ordinal, command in commands.items()
        if command.get("step") == step and ordinal in results
    ]
    if not matches:
        raise EvidenceValidationError(f"missing required result: {step}")
    ordinal = max(matches)
    return ordinal, results[ordinal]


def parse_review(path: Path, candidate: dict[str, object]) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise EvidenceValidationError("missing review report") from exc
    if "CHANGES_REQUESTED" in text:
        raise EvidenceValidationError("review contains CHANGES_REQUESTED")
    found: dict[str, list[str]] = {field: [] for field in REVIEW_FIELDS}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        for field in REVIEW_FIELDS:
            prefix = f"{field}:"
            if line.startswith(prefix):
                found[field].append(line[len(prefix) :].strip())
    if any(len(values) != 1 for values in found.values()):
        raise EvidenceValidationError("review fields must each appear exactly once")
    fields = {field: values[0] for field, values in found.items()}
    if (
        fields["Reviewed-Candidate-Fingerprint"] != candidate.get("fingerprint")
        or fields["Reviewed-Patch-SHA256"] != candidate.get("patch_sha256")
        or fields["Reviewed-Governance-Digest"] != candidate.get("governance_digest")
        or not valid_identity(fields["Reviewer-ID"])
        or fields["Verdict"] != "APPROVED"
        or any(fields[level] != "0" for level in ("P0", "P1", "P2"))
    ):
        raise EvidenceValidationError("review is not an exact zero-finding approval")
    return fields


def validate_reviews(
    root: Path,
    metadata_root: Path,
    artifact: Path,
    task_id: str,
    state: dict[str, object],
    candidate: dict[str, object],
) -> None:
    axes = ("governance", "tooling") if task_id == GVR3_ID else ("independent",)
    leases = state.get("review_leases")
    reviews = state.get("reviews")
    generation = state.get("review_generation")
    if (
        type(generation) is not int
        or generation <= 0
        or not isinstance(leases, dict)
        or not isinstance(reviews, dict)
        or set(leases) != set(axes)
        or set(reviews) != set(axes)
    ):
        raise EvidenceValidationError("review state is incomplete or ambiguous")
    used: set[str] = set()
    for axis in axes:
        lease = leases.get(axis)
        receipt = reviews.get(axis)
        if (
            not isinstance(lease, dict)
            or set(lease)
            != {
                "axis",
                "reviewer",
                "candidate_fingerprint",
                "review_generation",
                "issued_ns",
            }
            or not isinstance(receipt, dict)
            or set(receipt)
            != {
                "axis",
                "reviewer",
                "report",
                "submission_sha256",
                "report_sha256",
                "candidate_fingerprint",
                "review_generation",
            }
        ):
            raise EvidenceValidationError(f"invalid review receipt: {axis}")
        reviewer = lease.get("reviewer")
        if (
            lease.get("axis") != axis
            or receipt.get("axis") != axis
            or reviewer != receipt.get("reviewer")
            or not valid_identity(reviewer)
            or reviewer == state.get("implementer")
            or reviewer in used
            or lease.get("candidate_fingerprint") != candidate.get("fingerprint")
            or receipt.get("candidate_fingerprint") != candidate.get("fingerprint")
            or lease.get("review_generation") != generation
            or receipt.get("review_generation") != generation
            or type(lease.get("issued_ns")) is not int
        ):
            raise EvidenceValidationError(f"stale or non-independent review: {axis}")
        name = "independent_review.md" if axis == "independent" else f"{axis}_axis.md"
        report = artifact / "review" / name
        expected_report = metadata_root / "artifacts" / task_id / "review" / name
        if receipt.get("report") != str(expected_report):
            raise EvidenceValidationError(f"noncanonical review path: {axis}")
        fields = parse_review(report, candidate)
        content = report.read_bytes()
        prefix = (
            f"Reviewed-Candidate-Fingerprint: {candidate['fingerprint']}\n"
            f"Reviewed-Patch-SHA256: {candidate['patch_sha256']}\n"
            f"Reviewed-Governance-Digest: {candidate['governance_digest']}\n"
        ).encode("utf-8")
        if (
            fields["Reviewer-ID"] != reviewer
            or not content.startswith(prefix)
            or sha256_bytes(content) != receipt.get("report_sha256")
            or sha256_bytes(content[len(prefix) :]) != receipt.get("submission_sha256")
        ):
            raise EvidenceValidationError(f"review byte binding changed: {axis}")
        used.add(str(reviewer))


def expected_gate_argv(
    task_id: str, step: str, candidate: dict[str, object], generation: int
) -> list[str]:
    fingerprint = str(candidate["fingerprint"])
    patch = str(candidate["patch_sha256"])
    governance = str(candidate["governance_digest"])
    if step == "taskctl_scope_refresh":
        return [
            "python3",
            "scripts/evidence_scope.py",
            "finalize",
            task_id,
            "--live-patch-sha256",
            patch,
            "--candidate-fingerprint",
            fingerprint,
            "--review-generation",
            str(generation),
        ]
    if step == "independent_review":
        base = ["taskctl", task_id, "validate-review"]
    elif step == "task_gate":
        base = ["./scripts/task_validate.sh", task_id]
    elif step == "atomic_evidence":
        base = ["python3", "scripts/atomic_evidence_validate.py", task_id]
        for required in ("lint", "test", "scope", "independent_review", "task_gate"):
            base.extend(("--required-step", required))
    elif step == "taskctl_close":
        return [
            "close",
            "--candidate-fingerprint",
            fingerprint,
            "--review-generation",
            str(generation),
        ]
    else:
        raise EvidenceValidationError(f"unknown close step: {step}")
    return [
        *base,
        "--taskctl-candidate-fingerprint",
        fingerprint,
        "--taskctl-patch-sha256",
        patch,
        "--taskctl-governance-digest",
        governance,
        "--taskctl-review-generation",
        str(generation),
    ]


def validate_gate_command(
    command: dict[str, object],
    task_id: str,
    step: str,
    candidate: dict[str, object],
    generation: int,
    metadata_root: Path,
) -> None:
    if (
        command.get("step") != step
        or command.get("argv")
        != expected_gate_argv(task_id, step, candidate, generation)
        or command.get("cwd") != str(metadata_root)
        or command.get("classification") != "INTERNAL"
        or command.get("replay_safe") is not True
    ):
        raise EvidenceValidationError(f"close command binding changed: {step}")


def validate_gvr3_required_command(
    command: dict[str, object], step: str, metadata_root: Path
) -> None:
    expected = GVR3_REQUIRED_COMMANDS.get(step)
    if expected is None:
        raise EvidenceValidationError(f"unknown GVR-3 required command: {step}")
    argv, classification = expected
    if (
        command.get("step") != step
        or command.get("argv") != list(argv)
        or command.get("cwd") != str(metadata_root)
        or command.get("classification") != classification
        or command.get("replay_safe") is not False
    ):
        raise EvidenceValidationError(f"GVR-3 required command binding changed: {step}")


def validate_terminal_receipts(
    root: Path,
    metadata_root: Path,
    artifact: Path,
    task_id: str,
    state: dict[str, object],
    candidate: dict[str, object],
    commands: dict[int, dict[str, object]],
    results: dict[int, dict[str, object]],
) -> None:
    receipts = state.get("terminal_receipts")
    generation = state.get("review_generation")
    if not isinstance(receipts, dict) or set(receipts) != set(CLOSE_STEPS):
        raise EvidenceValidationError("terminal receipt set is incomplete")
    ordinals: list[int] = []
    expected_receipts: dict[str, dict[str, object]] = {}
    for step in CLOSE_STEPS:
        receipt = receipts.get(step)
        if not isinstance(receipt, dict) or type(receipt.get("ordinal")) is not int:
            raise EvidenceValidationError(f"invalid terminal receipt: {step}")
        ordinal = int(receipt["ordinal"])
        if ordinal not in commands or ordinal not in results:
            raise EvidenceValidationError(f"missing terminal event: {step}")
        validate_gate_command(
            commands[ordinal], task_id, step, candidate, int(generation), metadata_root
        )
        if step == "taskctl_close":
            result = results[ordinal]
            if result.get("rc") != 0 or result.get("executed") is not True:
                raise EvidenceValidationError("terminal close result is not successful")
            result_path = artifact / "events" / f"{ordinal:08d}.result.json"
            log_path = None
        else:
            result_path, log_path = validate_result(
                root,
                artifact,
                task_id,
                ordinal,
                results[ordinal],
                require_log_binding=True,
            )
        binding: dict[str, object] = {
            "ordinal": ordinal,
            "result_sha256": sha256_file(result_path),
        }
        if step != "taskctl_close":
            assert log_path is not None
            binding.update(
                {
                    "log": results[ordinal].get("log"),
                    "log_sha256": sha256_file(log_path),
                }
            )
        expected_receipts[step] = binding
        ordinals.append(ordinal)
    if (
        receipts != expected_receipts
        or ordinals != sorted(ordinals)
        or len(ordinals) != len(set(ordinals))
        or state.get("terminal_ordinal") != ordinals[-1]
        or ordinals[-1] != max(commands)
    ):
        raise EvidenceValidationError("terminal receipt order or bytes changed")


def validate_current_inflight(
    state_name: str,
    acceptance_mode: str,
    task_id: str,
    metadata_root: Path,
    candidate: dict[str, object],
    generation: int,
    commands: dict[int, dict[str, object]],
    results: dict[int, dict[str, object]],
) -> int | None:
    missing = sorted(set(commands) - set(results))
    if state_name == "PASS":
        if missing:
            raise EvidenceValidationError("terminal PASS contains an incomplete event")
        return None
    expected = "task_gate" if acceptance_mode == "task" else "atomic_evidence"
    if missing != [max(commands)]:
        raise EvidenceValidationError("close has an unexpected incomplete event")
    validate_gate_command(
        commands[missing[0]],
        task_id,
        expected,
        candidate,
        generation,
        metadata_root,
    )
    return missing[0]


def validate_closing_prefix(
    acceptance_mode: str,
    task_id: str,
    metadata_root: Path,
    artifact: Path,
    root: Path,
    candidate: dict[str, object],
    generation: int,
    current_ordinal: int,
    commands: dict[int, dict[str, object]],
    results: dict[int, dict[str, object]],
) -> None:
    predecessors = ["taskctl_scope_refresh", "independent_review"]
    if acceptance_mode == "atomic":
        predecessors.append("task_gate")
    ordinals: list[int] = []
    for step in predecessors:
        ordinal, result = latest_result(commands, results, step)
        validate_gate_command(
            commands[ordinal],
            task_id,
            step,
            candidate,
            generation,
            metadata_root,
        )
        validate_result(
            root,
            artifact,
            task_id,
            ordinal,
            result,
            require_log_binding=True,
        )
        ordinals.append(ordinal)
    if (
        ordinals != sorted(ordinals)
        or len(ordinals) != len(set(ordinals))
        or any(ordinal >= current_ordinal for ordinal in ordinals)
    ):
        raise EvidenceValidationError("close predecessor order changed")


def validate_v2(
    root: Path,
    metadata_root: Path,
    task_id: str,
    required_steps: Sequence[str],
    acceptance_mode: str,
) -> None:
    artifact = root / "artifacts" / task_id
    metadata = read_json_object(artifact / "task.json", "task.json")
    state = read_json_object(artifact / "state.json", "state.json")
    if metadata.get("task_id") != task_id or state.get("task_id") != task_id:
        raise EvidenceValidationError("v2 task identity mismatch")
    declared_root = metadata.get("repo_root")
    if (
        not isinstance(declared_root, str)
        or Path(declared_root).resolve() != metadata_root
    ):
        raise EvidenceValidationError("task.json repository identity mismatch")
    task_relative = normalized_relative_path(metadata.get("task_file"), "task file")
    task = repository_file(root, task_relative, "task file")
    allowlist = parse_task_allowlist(task, task_id, root)
    if (
        task.stem != task_id
        or metadata.get("allowlist") != allowlist
        or state.get("task_file") != task_relative
        or state.get("allowlist") != allowlist
        or state.get("schema_version") != 2
        or not valid_identity(state.get("controller"))
        or not valid_identity(state.get("implementer"))
        or not isinstance(state.get("baseline"), dict)
    ):
        raise EvidenceValidationError("v2 task contract binding changed")
    baseline_dirty = metadata.get("baseline_dirty")
    if not isinstance(baseline_dirty, bool):
        raise EvidenceValidationError("task.json baseline_dirty must be boolean")
    if baseline_dirty:
        repository_file(
            root,
            f"artifacts/{task_id}/baseline_allowlist.diff",
            "dirty baseline allowlist",
        )
        repository_file(
            root,
            f"artifacts/{task_id}/baseline_external_files.txt",
            "dirty baseline external paths",
        )
    state_name = state.get("state")
    if acceptance_mode == "release":
        if state_name != "PASS":
            raise EvidenceValidationError("release accepts only terminal v2 PASS")
    elif state_name not in {"CLOSING", "PASS"}:
        raise EvidenceValidationError("task/atomic gate requires CLOSING or PASS")

    candidate = state.get("candidate")
    if not isinstance(candidate, dict) or set(candidate) != {
        "task_sha256",
        "summary_sha256",
        "scoped_patch_sha256",
        "patch_sha256",
        "governance_digest",
        "baseline",
        "required_results",
        "source_hashes",
        "fingerprint",
    }:
        raise EvidenceValidationError("candidate authority is incomplete")
    material = dict(candidate)
    fingerprint = material.pop("fingerprint")
    summary = repository_file(root, f"artifacts/{task_id}/summary.md", "summary")
    virtual_patch = artifact / "candidate/virtual.patch"
    patch = (
        repository_file(
            root, virtual_patch.relative_to(root).as_posix(), "virtual patch"
        )
        if virtual_patch.exists()
        else repository_file(
            root, f"artifacts/{task_id}/git/diff.patch", "scoped patch"
        )
    )
    if (
        not isinstance(fingerprint, str)
        or not HEX_PATTERN.fullmatch(fingerprint)
        or canonical_digest(material) != fingerprint
        or sha256_file(task) != candidate.get("task_sha256")
        or sha256_file(summary) != candidate.get("summary_sha256")
        or sha256_file(patch) != candidate.get("patch_sha256")
        or candidate.get("scoped_patch_sha256") != candidate.get("patch_sha256")
        or candidate.get("baseline") != state.get("baseline")
        or candidate.get("governance_digest") != state.get("governance_digest")
        or not isinstance(candidate.get("governance_digest"), str)
        or not HEX_PATTERN.fullmatch(str(candidate["governance_digest"]))
    ):
        raise EvidenceValidationError(
            "candidate fingerprint or immutable bytes changed"
        )

    bindings = candidate.get("required_results")
    expected_required = GVR3_REQUIRED if task_id == GVR3_ID else ORDINARY_REQUIRED
    if not isinstance(bindings, dict) or set(bindings) != expected_required:
        raise EvidenceValidationError("candidate required-result set changed")
    commands, results = load_events(root, artifact, task_id)
    for step, binding in bindings.items():
        if not isinstance(binding, dict):
            raise EvidenceValidationError(f"invalid candidate result binding: {step}")
        ordinal, result = latest_result(commands, results, step)
        if task_id == GVR3_ID:
            validate_gvr3_required_command(commands[ordinal], step, metadata_root)
        validate_result(root, artifact, task_id, ordinal, result, binding=binding)

    source_hashes = candidate.get("source_hashes")
    if task_id == GVR3_ID:
        bootstrap = state.get("bootstrap")
        if (
            not isinstance(source_hashes, dict)
            or set(source_hashes)
            != {
                "kernel_sha256",
                "manifest_sha256",
                "pre_root_sha256",
                "pre_manifest_sha256",
            }
            or not isinstance(bootstrap, dict)
        ):
            raise EvidenceValidationError("activation source binding is incomplete")
        kernel = Path(str(bootstrap.get("kernel_path", "")))
        manifest = Path(str(bootstrap.get("manifest_path", "")))
        if (
            not kernel.is_file()
            or not manifest.is_file()
            or sha256_file(kernel) != source_hashes.get("kernel_sha256")
            or sha256_file(manifest) != source_hashes.get("manifest_sha256")
            or bootstrap.get("kernel_sha256") != source_hashes.get("kernel_sha256")
            or bootstrap.get("manifest_sha256") != source_hashes.get("manifest_sha256")
        ):
            raise EvidenceValidationError("activation candidate source changed")
        if state_name in {"CLOSING", "PASS"}:
            activation = state.get("activation")
            if activation != {
                "kernel_sha256": source_hashes.get("kernel_sha256"),
                "manifest_sha256": source_hashes.get("manifest_sha256"),
                "governance_digest": candidate.get("governance_digest"),
            }:
                raise EvidenceValidationError("installed activation binding changed")
            if sha256_file(
                repository_file(root, "AGENTS.md", "active root")
            ) != source_hashes.get("kernel_sha256") or sha256_file(
                repository_file(
                    root, "docs/agents/manifest.json", "active governance manifest"
                )
            ) != source_hashes.get("manifest_sha256"):
                raise EvidenceValidationError("installed governance bytes changed")
    elif source_hashes != {}:
        raise EvidenceValidationError("ordinary v2 task has activation source hashes")

    validate_reviews(root, metadata_root, artifact, task_id, state, candidate)
    generation = state.get("review_generation")
    current_ordinal = validate_current_inflight(
        str(state_name),
        acceptance_mode,
        task_id,
        metadata_root,
        candidate,
        int(generation),
        commands,
        results,
    )
    if state_name == "CLOSING":
        assert current_ordinal is not None
        validate_closing_prefix(
            acceptance_mode,
            task_id,
            metadata_root,
            artifact,
            root,
            candidate,
            int(generation),
            current_ordinal,
            commands,
            results,
        )
    for step in required_steps:
        if step in bindings:
            continue
        ordinal, result = latest_result(commands, results, step)
        if step in CLOSE_STEPS:
            validate_gate_command(
                commands[ordinal],
                task_id,
                step,
                candidate,
                int(generation),
                metadata_root,
            )
        validate_result(
            root,
            artifact,
            task_id,
            ordinal,
            result,
            require_log_binding=step
            in {"independent_review", "task_gate", "atomic_evidence"},
        )
    if state_name == "PASS":
        validate_terminal_receipts(
            root,
            metadata_root,
            artifact,
            task_id,
            state,
            candidate,
            commands,
            results,
        )


def validate(
    task_id: str,
    required_steps: Sequence[str],
    metadata_root_value: str | None = None,
    *,
    acceptance_mode: str = "task",
) -> None:
    if not TASK_ID_PATTERN.fullmatch(task_id):
        raise EvidenceValidationError("invalid task ID")
    if acceptance_mode not in {"task", "atomic", "release"}:
        raise EvidenceValidationError("invalid acceptance mode")
    if len(required_steps) != len(set(required_steps)) or not all(required_steps):
        raise EvidenceValidationError("invalid required-step set")
    root = Path.cwd().resolve()
    metadata_root = (
        Path(metadata_root_value).resolve() if metadata_root_value is not None else root
    )
    artifact = root / "artifacts" / task_id
    try:
        info = artifact.lstat()
    except FileNotFoundError as exc:
        raise EvidenceValidationError("missing task artifacts") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise EvidenceValidationError("task artifact root is unsafe")
    state_exists = (artifact / "state.json").exists()
    entry = ledger_entry(root, task_id)
    if state_exists and entry is not None:
        raise EvidenceValidationError("task matches both v2 state and legacy ledger")
    if state_exists:
        validate_v2(root, metadata_root, task_id, required_steps, acceptance_mode)
        return
    if entry is not None:
        if acceptance_mode != "release":
            raise EvidenceValidationError("legacy ledger is release-only authority")
        validate_legacy(root, task_id, entry)
        return
    raise EvidenceValidationError("task matches neither v2 state nor legacy ledger")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("--required-step", action="append", default=[])
    parser.add_argument("--metadata-repo-root")
    parser.add_argument(
        "--acceptance-mode", choices=("task", "atomic", "release"), default="task"
    )
    args = parser.parse_args(argv)
    required = args.required_step or ["lint", "test"]
    try:
        validate(
            args.task_id,
            required,
            args.metadata_repo_root,
            acceptance_mode=args.acceptance_mode,
        )
    except (EvidenceValidationError, OSError, UnicodeError) as exc:
        print(f"Evidence validation rejected: {exc}", file=sys.stderr)
        return 1
    print(f"Evidence {args.acceptance_mode} acceptance PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
