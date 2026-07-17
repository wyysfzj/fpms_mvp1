#!/usr/bin/env python3
"""Repository entry point for atomic evidence validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Sequence


EVIDENCE_CONSUMER = Path(__file__).resolve().with_name("evidence_validate.py")
MANIFEST_HEADING = re.compile(r"^##\s+\d{3}\.\s+(\S+)\s*$")
MANIFEST_TASK_FILE = re.compile(r"^\s*-\s*Task file:\s*`([^`]+)`\s*$")
TABLE_SEPARATOR = re.compile(r"^:?-{3,}:?$")
ALLOWED_FILES_HEADING = re.compile(r"^##\s+Allowed Files\s*$")
ANY_HEADING = re.compile(r"^#{1,6}\s+")
ALLOWED_FILE_ITEM = re.compile(r"^\s*-\s+`([^`]+)`\s*$")


class ContractError(ValueError):
    pass


def repository_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise ContractError("cannot locate Git repository root")
    return Path(result.stdout.strip()).resolve()


def relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ContractError(f"task.json {label} must be a repository-relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ContractError(
            f"task.json {label} must be a normalized repository-relative path"
        )
    return value


def parse_allowed_files(task_path: Path) -> list[str]:
    lines = task_path.read_text(encoding="utf-8").splitlines()
    headings = [
        index for index, line in enumerate(lines) if ALLOWED_FILES_HEADING.match(line)
    ]
    if len(headings) != 1:
        raise ContractError(
            f"allowlist requires exactly one ## Allowed Files in {task_path}"
        )
    entries: list[str] = []
    started = False
    for line in lines[headings[0] + 1 :]:
        if ANY_HEADING.match(line):
            break
        if not line.strip():
            continue
        match = ALLOWED_FILE_ITEM.match(line)
        if match:
            started = True
            entries.append(match.group(1))
            continue
        if started:
            break
        raise ContractError(f"malformed allowlist entry in {task_path}: {line!r}")
    if not entries or len(entries) != len(set(entries)):
        raise ContractError(f"allowlist is empty or contains duplicates in {task_path}")
    return entries


def normalize_allowlist(task_id: str, entries: list[str]) -> list[str]:
    evidence = f"artifacts/{task_id}/**"
    normalized: list[str] = []
    for entry in entries:
        if not entry or "\\" in entry:
            raise ContractError(
                f"allowlist entry is not repository-relative: {entry!r}"
            )
        path = PurePosixPath(entry)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != entry:
            raise ContractError(f"allowlist entry is not normalized: {entry!r}")
        if any(character in entry for character in "*?[") and entry != evidence:
            raise ContractError(
                f"allowlist permits only own evidence glob {evidence!r}: {entry!r}"
            )
        normalized.append(entry)
    if len(normalized) != len(set(normalized)):
        raise ContractError(
            f"allowlist contains duplicate normalized paths for {task_id}"
        )
    if normalized.count(evidence) != 1:
        raise ContractError(
            f"allowlist must contain exactly one own evidence glob {evidence!r}"
        )
    return normalized


def load_task(root: Path, task_id: str) -> tuple[str, list[str]]:
    metadata_path = root / "artifacts" / task_id / "task.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"missing or malformed task.json for {task_id}") from exc
    if not isinstance(metadata, dict):
        raise ContractError(f"task.json for {task_id} must be an object")
    required = ("task_id", "task_file", "repo_root", "allowlist")
    if any(field not in metadata for field in required):
        raise ContractError(f"task.json for {task_id} is missing required fields")
    if metadata["task_id"] != task_id:
        raise ContractError(f"task.json task_id mismatch for {task_id}")
    if metadata["repo_root"] != root.as_posix():
        raise ContractError(f"task.json repo_root mismatch for {task_id}")
    task_file = relative_path(metadata["task_file"], "task_file")
    task_path = root / task_file
    if Path(task_file).stem != task_id or not task_path.is_file():
        raise ContractError(f"task.json task_file identity mismatch for {task_id}")
    allowlist = metadata["allowlist"]
    if not isinstance(allowlist, list) or not all(
        isinstance(item, str) for item in allowlist
    ):
        raise ContractError(f"task.json allowlist must be a string list for {task_id}")
    try:
        metadata_allowlist = normalize_allowlist(task_id, allowlist)
    except ContractError as exc:
        raise ContractError(f"task.json {exc}") from exc
    task_allowlist = normalize_allowlist(task_id, parse_allowed_files(task_path))
    if set(metadata_allowlist) != set(task_allowlist):
        raise ContractError(
            f"task file allowlist differs from task.json allowlist for {task_id}"
        )
    return task_file, metadata_allowlist


def non_evidence(task_id: str, allowlist: list[str]) -> list[str]:
    evidence = f"artifacts/{task_id}/**"
    return [entry for entry in allowlist if entry != evidence]


def validate_overlap(tasks: dict[str, tuple[str, list[str]]]) -> None:
    task_ids = list(tasks)
    for left_index, left_id in enumerate(task_ids):
        for right_id in task_ids[left_index + 1 :]:
            for left in non_evidence(left_id, tasks[left_id][1]):
                for right in non_evidence(right_id, tasks[right_id][1]):
                    if (
                        left == right
                        or left.startswith(right + "/")
                        or right.startswith(left + "/")
                    ):
                        raise ContractError(
                            f"allowlist overlap: {left_id}:{left} and {right_id}:{right}"
                        )


def has_symlink_component(root: Path, relative: str) -> bool:
    candidate = root
    for part in PurePosixPath(relative).parts:
        candidate = candidate / part
        if candidate.is_symlink():
            return True
    return False


def validate_allowlist_files(
    root: Path, tasks: dict[str, tuple[str, list[str]]]
) -> None:
    for task_id, (_, allowlist) in tasks.items():
        for entry in non_evidence(task_id, allowlist):
            if has_symlink_component(root, entry):
                raise ContractError(f"allowlist symlink path is forbidden: {entry}")
            path = root / entry
            if path.exists():
                if not path.is_file():
                    raise ContractError(f"allowlist directory is forbidden: {entry}")
                continue
            tracked = subprocess.run(
                ["git", "ls-tree", "--full-tree", "-z", "HEAD", "--", entry],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            records = [record for record in tracked.stdout.split(b"\0") if record]
            if tracked.returncode != 0 or len(records) != 1:
                raise ContractError(
                    f"allowlist entry is neither an exact file nor tracked deletion: {entry}"
                )
            metadata, separator, tracked_path = records[0].partition(b"\t")
            fields = metadata.split()
            decoded_path = tracked_path.decode("utf-8", "surrogateescape")
            if separator != b"\t" or len(fields) != 3 or decoded_path != entry:
                raise ContractError(
                    f"invalid tracked deletion object for allowlist path: {entry}"
                )
            mode = fields[0].decode("ascii")
            object_type = fields[1].decode("ascii")
            if object_type != "blob" or mode not in {"100644", "100755"}:
                raise ContractError(
                    f"deleted tracked path has forbidden object type/mode: "
                    f"{entry} ({object_type} {mode})"
                )


def parse_status(status: bytes) -> list[str]:
    records = status.split(b"\0")
    paths: list[str] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4:
            raise ContractError("malformed NUL-delimited Git status record")
        state = record[:2].decode("ascii", "strict")
        destination = record[3:].decode("utf-8", "surrogateescape")
        if "R" in state or "C" in state:
            if index >= len(records) or not records[index]:
                raise ContractError(f"malformed rename/copy status for {destination}")
            source = records[index].decode("utf-8", "surrogateescape")
            index += 1
            kind = "rename" if "R" in state else "copy"
            raise ContractError(f"Git {kind} is forbidden: {source} -> {destination}")
        paths.append(destination)
    return paths


def owns_path(task_id: str, allowlist: list[str], path: str) -> bool:
    artifact = f"artifacts/{task_id}"
    if path == artifact or path.startswith(artifact + "/"):
        return True
    return path in non_evidence(task_id, allowlist)


def validate_worktree(
    root: Path, tasks: dict[str, tuple[str, list[str]]], current_id: str
) -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise ContractError("cannot read NUL-safe Git worktree status")
    dirty_paths = parse_status(result.stdout)
    baseline_path = root / "artifacts" / current_id / "baseline_external_files.txt"
    baseline: set[str] = set()
    if baseline_path.exists():
        baseline = {
            line
            for line in baseline_path.read_text(encoding="utf-8").splitlines()
            if line
        }
    current_allowlist = tasks[current_id][1]
    for path in dirty_paths:
        if owns_path(current_id, current_allowlist, path) or path in baseline:
            continue
        owners = [
            task_id
            for task_id, (_, allowlist) in tasks.items()
            if task_id != current_id and owns_path(task_id, allowlist, path)
        ]
        if len(owners) == 1:
            continue
        if not owners:
            raise ContractError(f"unknown dirty path outside active ownership: {path}")
        raise ContractError(
            f"dirty path has multiple peer owners ({', '.join(owners)}): {path}"
        )


def copy_current_task(
    root: Path,
    clone: Path,
    task_id: str,
    allowlist: list[str],
) -> None:
    for entry in non_evidence(task_id, allowlist):
        source = root / entry
        destination = clone / entry
        if source.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        elif destination.exists():
            destination.unlink()
    artifact_relative = Path("artifacts") / task_id
    source_artifact = root / artifact_relative
    destination_artifact = clone / artifact_relative
    if destination_artifact.exists():
        shutil.rmtree(destination_artifact)
    if source_artifact.exists():
        destination_artifact.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_artifact, destination_artifact)


def copy_active_runtime(root: Path, clone: Path) -> None:
    relative_paths = [
        "AGENTS.md",
        "docs/agents/manifest.json",
        "docs/agents/legacy-pass-ledger.json",
        "scripts/taskctl",
        "scripts/evidence_scope.py",
        "scripts/evidence_validate.py",
    ]
    agents = root / "docs/agents"
    if agents.is_dir():
        relative_paths.extend(
            path.relative_to(root).as_posix()
            for path in agents.iterdir()
            if path.name.endswith(".md")
        )
    for relative in sorted(set(relative_paths)):
        source = root / relative
        if not source.exists():
            continue
        if source.is_symlink() or not source.is_file():
            raise ContractError(f"active runtime authority is not regular: {relative}")
        destination = clone / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def delegate_isolated(
    root: Path,
    task_id: str,
    allowlist: list[str],
    required_steps: list[str],
) -> int:
    temporary = tempfile.TemporaryDirectory(prefix="fpms-atomic-evidence-")
    try:
        clone = Path(temporary.name) / "repository"
        cloned = subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks", str(root), str(clone)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if cloned.returncode != 0:
            raise ContractError(
                f"temporary local clone failed: {cloned.stderr.strip()}"
            )
        copy_current_task(root, clone, task_id, allowlist)
        copy_active_runtime(root, clone)
        return subprocess.run(
            helper_command(
                task_id,
                required_steps,
                root,
                consumer=clone / "scripts/evidence_validate.py",
            ),
            cwd=clone,
            check=False,
        ).returncode
    finally:
        temporary.cleanup()


def parse_manifest(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[tuple[str, str]] = []
    index = 0
    while index < len(lines):
        heading = MANIFEST_HEADING.match(lines[index])
        if not heading:
            index += 1
            continue
        task_id = heading.group(1).strip("`")
        task_files: list[str] = []
        index += 1
        while index < len(lines) and not lines[index].startswith("## "):
            match = MANIFEST_TASK_FILE.match(lines[index])
            if match:
                task_files.append(match.group(1))
            index += 1
        if len(task_files) == 1:
            rows.append((task_id, task_files[0]))
    index = 0
    while index + 1 < len(lines):
        if not lines[index].strip().startswith("|"):
            index += 1
            continue
        headers = table_cells(lines[index])
        separators = table_cells(lines[index + 1])
        if len(headers) != len(separators) or not all(
            TABLE_SEPARATOR.fullmatch(cell) for cell in separators
        ):
            index += 1
            continue
        id_columns = [
            position for position, cell in enumerate(headers) if cell == "Task ID"
        ]
        path_columns = [
            position
            for position, cell in enumerate(headers)
            if cell in {"Task file", "Exact task-file path"}
        ]
        explicit = (
            len(id_columns) == 1
            and len(path_columns) == 1
            and headers[path_columns[0]] == "Task file"
        )
        path_only = not id_columns and len(path_columns) == 1
        index += 2
        while index < len(lines) and lines[index].strip().startswith("|"):
            cells = table_cells(lines[index])
            if (explicit or path_only) and len(cells) == len(headers):
                task_file = cells[path_columns[0]]
                if is_normalized_task_file(task_file):
                    task_id = cells[id_columns[0]] if explicit else Path(task_file).stem
                    rows.append((task_id, task_file))
            index += 1
    return rows


def table_cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def is_normalized_task_file(value: str) -> bool:
    path = PurePosixPath(value)
    return (
        bool(value)
        and not path.is_absolute()
        and ".." not in path.parts
        and path.as_posix() == value
        and value.endswith(".md")
        and "/" in value
    )


def validate_manifest(
    root: Path,
    manifest_value: str,
    tasks: dict[str, str],
) -> None:
    manifest_relative = relative_path(manifest_value, "manifest")
    manifest_path = root / manifest_relative
    if has_symlink_component(root, manifest_relative):
        raise ContractError(
            "manifest must be repository-local and contain no symlink component"
        )
    try:
        resolved_manifest = manifest_path.resolve(strict=True)
        resolved_manifest.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ContractError(
            "manifest must resolve to a repository-local regular file"
        ) from exc
    if not resolved_manifest.is_file():
        raise ContractError("manifest must be a repository-local regular file")
    rows = parse_manifest(resolved_manifest)
    ids = [task_id for task_id, _ in rows]
    paths = [task_file for _, task_file in rows]
    for task_id, task_file in tasks.items():
        matches = [row for row in rows if row[0] == task_id]
        if len(matches) != 1 or ids.count(task_id) != 1:
            raise ContractError(f"manifest must contain exactly one row for {task_id}")
        if matches[0][1] != task_file or paths.count(task_file) != 1:
            raise ContractError(f"manifest path mismatch or duplication for {task_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_id")
    parser.add_argument("--required-step", action="append", default=[])
    parser.add_argument("--manifest", action="append", default=[])
    parser.add_argument("--concurrent-task", action="append", default=[])
    return parser


def helper_command(
    task_id: str,
    required_steps: list[str],
    metadata_root: Path | None = None,
    *,
    consumer: Path = EVIDENCE_CONSUMER,
) -> list[str]:
    command = [
        "python3",
        str(consumer),
        task_id,
        "--acceptance-mode",
        "atomic",
    ]
    for step in required_steps:
        command.extend(("--required-step", step))
    if metadata_root is not None:
        command.extend(("--metadata-repo-root", metadata_root.resolve().as_posix()))
    return command


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    peers: list[str] = args.concurrent_task
    manifests: list[str] = args.manifest

    if len(peers) != len(set(peers)):
        print("duplicate peer task IDs are forbidden", file=sys.stderr)
        return 2
    if args.task_id in peers:
        print("current task cannot also be a peer", file=sys.stderr)
        return 2
    if not peers:
        if manifests:
            print("--manifest is forbidden when no peer is declared", file=sys.stderr)
            return 2
        return subprocess.run(
            helper_command(args.task_id, args.required_step),
            check=False,
        ).returncode

    if len(manifests) != 1:
        print("peer mode requires --manifest exactly once", file=sys.stderr)
        return 2
    try:
        root = repository_root()
        tasks = {
            task_id: load_task(root, task_id) for task_id in (args.task_id, *peers)
        }
        validate_manifest(
            root,
            manifests[0],
            {task_id: task[0] for task_id, task in tasks.items()},
        )
        validate_overlap(tasks)
        validate_allowlist_files(root, tasks)
        validate_worktree(root, tasks, args.task_id)
        return delegate_isolated(
            root,
            args.task_id,
            tasks[args.task_id][1],
            args.required_step,
        )
    except (ContractError, OSError, UnicodeError) as exc:
        print(f"atomic evidence validation rejected: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
