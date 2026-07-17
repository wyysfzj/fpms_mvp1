#!/usr/bin/env python3
"""Produce one baseline-subtracted, allowlist-scoped evidence patch."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import glob
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import subprocess
import sys
import tempfile
import threading
from typing import Generator, Iterable, Mapping, Sequence
import uuid


TASK_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_TEMP_INDEX_OWNERS: dict[str, dict[str, object]] = {}


class EvidenceError(RuntimeError):
    """Fail-closed evidence producer error."""


def git(
    root: Path,
    args: Sequence[str],
    *,
    env: dict[str, str] | None = None,
    input_data: bytes | None = None,
) -> bytes:
    effective_env = os.environ.copy()
    if env is not None:
        effective_env.update(env)
    effective_env["GIT_OPTIONAL_LOCKS"] = "0"
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        env=effective_env,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    _record_temporary_index_ownership(effective_env)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise EvidenceError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _record_temporary_index_ownership(env: dict[str, str] | None) -> None:
    """Bind cleanup to children produced by each trusted Git invocation."""
    if env is None:
        return
    token = env.get("FPMS_EVIDENCE_INDEX_OWNER")
    if token is None:
        return
    owner = _TEMP_INDEX_OWNERS.get(token)
    if owner is None:
        raise EvidenceError("temporary index ownership token is unknown")
    workspace = owner.get("workspace")
    workspace_identity = owner.get("workspace_identity")
    object_directory = owner.get("object_directory")
    object_identity = owner.get("object_identity")
    identities = owner.get("identities")
    if (
        not isinstance(workspace, Path)
        or not isinstance(object_directory, Path)
        or not isinstance(identities, dict)
    ):
        raise EvidenceError("temporary index ownership record is invalid")

    current = workspace.lstat()
    if (
        stat.S_ISLNK(current.st_mode)
        or not stat.S_ISDIR(current.st_mode)
        or (current.st_dev, current.st_ino) != workspace_identity
    ):
        raise EvidenceError("temporary index workspace ownership changed")
    objects_current = object_directory.lstat()
    if (
        stat.S_ISLNK(objects_current.st_mode)
        or not stat.S_ISDIR(objects_current.st_mode)
        or (objects_current.st_dev, objects_current.st_ino) != object_identity
    ):
        raise EvidenceError("temporary object directory ownership changed")

    allowed_top = {"index", "index.lock", "objects"}
    for child in workspace.iterdir():
        if child.name not in allowed_top:
            raise EvidenceError(
                f"temporary index workspace contains foreign path: {child.name}"
            )
    for name in ("index", "index.lock"):
        path = workspace / name
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_nlink != 1
        ):
            raise EvidenceError(f"temporary index child is unsafe: {name}")
        identities[name] = (info.st_dev, info.st_ino)

    for fanout in object_directory.iterdir():
        info = fanout.lstat()
        key = f"objects/{fanout.name}"
        if (
            stat.S_ISLNK(info.st_mode)
            or not stat.S_ISDIR(info.st_mode)
            or re.fullmatch(r"[0-9a-f]{2}", fanout.name) is None
            or info.st_uid != os.getuid()
        ):
            raise EvidenceError(f"temporary object directory is unsafe: {fanout.name}")
        identity = (info.st_dev, info.st_ino)
        previous = identities.get(key)
        if previous is not None and previous != identity:
            raise EvidenceError(
                f"temporary object directory inode changed: {fanout.name}"
            )
        identities[key] = identity
        for object_path in fanout.iterdir():
            object_info = object_path.lstat()
            object_key = f"{key}/{object_path.name}"
            if (
                not stat.S_ISREG(object_info.st_mode)
                or re.fullmatch(r"[0-9a-f]{38}", object_path.name) is None
                or object_info.st_uid != os.getuid()
                or object_info.st_nlink != 1
            ):
                raise EvidenceError(
                    "temporary object fanout contains unsafe path: "
                    f"{fanout.name}/{object_path.name}"
                )
            identity = (object_info.st_dev, object_info.st_ino)
            previous = identities.get(object_key)
            if previous is not None and previous != identity:
                raise EvidenceError(
                    f"temporary object inode changed: {fanout.name}/{object_path.name}"
                )
            identities[object_key] = identity


def apply_baseline_patch(
    root: Path,
    patch: Path,
    env: dict[str, str],
) -> None:
    content = patch.read_bytes()
    if not content:
        return
    arguments = ("apply", "--cached", "--binary", "--whitespace=nowarn", "-")
    try:
        git(root, arguments, env=env, input_data=content)
        return
    except EvidenceError:
        # The legacy initializer concatenates unstaged then staged diffs. If the
        # same path has both, replay file sections in reverse to reconstruct the
        # actual pre-task worktree state from HEAD.
        git(root, ("read-tree", "HEAD"), env=env)
    sections = [
        b"diff --git " + section
        for section in content.split(b"diff --git ")
        if section.strip()
    ]
    if not sections:
        raise EvidenceError("baseline_allowlist.diff is not a Git patch")
    try:
        for section in reversed(sections):
            git(root, arguments, env=env, input_data=section)
    except EvidenceError as exc:
        raise EvidenceError(f"unusable baseline_allowlist.diff: {exc}") from exc


def repository_root() -> Path:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise EvidenceError("current directory is not inside a Git repository")
    return Path(result.stdout.decode().strip()).resolve()


def normalize_allowlist(raw: object) -> tuple[str, ...]:
    if not isinstance(raw, list) or not raw:
        raise EvidenceError("task.json allowlist must be a non-empty list")
    normalized: list[str] = []
    for value in raw:
        if not isinstance(value, str) or not value or "\x00" in value:
            raise EvidenceError("task.json allowlist contains an invalid path")
        value = value.removeprefix("./")
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise EvidenceError(f"unsafe allowlist path: {value}")
        if path.parts[0] == ".git":
            raise EvidenceError(f"unsafe allowlist path: {value}")
        normalized.append(path.as_posix())
    return tuple(dict.fromkeys(normalized))


def load_metadata(
    root: Path, task_id: str
) -> tuple[Path, dict[str, object], tuple[str, ...]]:
    if not TASK_ID_PATTERN.fullmatch(task_id):
        raise EvidenceError("invalid task id")
    artifact = root / "artifacts" / task_id
    metadata_path = artifact / "task.json"
    if not metadata_path.is_file():
        raise EvidenceError(f"missing {metadata_path.relative_to(root)}")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise EvidenceError(f"invalid task.json: {exc}") from exc
    if not isinstance(metadata, dict):
        raise EvidenceError("task.json must contain an object")
    if metadata.get("task_id") != task_id:
        raise EvidenceError("task.json task_id does not match requested task")
    declared_root = metadata.get("repo_root")
    if not isinstance(declared_root, str) or Path(declared_root).resolve() != root:
        raise EvidenceError("task.json repo_root does not match current repository")
    return artifact, metadata, normalize_allowlist(metadata.get("allowlist"))


def is_allowed(path: str, allowlist: Iterable[str]) -> bool:
    def anchored_match(candidate: str, pattern: str) -> bool:
        return PurePosixPath("/" + candidate).match("/" + pattern)

    for pattern in allowlist:
        normalized = pattern.rstrip("/")
        if normalized.endswith("/**"):
            base_pattern = normalized[:-3].rstrip("/")
            if glob.has_magic(base_pattern):
                parts = PurePosixPath(path).parts
                if any(
                    anchored_match("/".join(parts[:count]), base_pattern)
                    for count in range(1, len(parts) + 1)
                ):
                    return True
            elif path == base_pattern or path.startswith(base_pattern + "/"):
                return True
            continue
        if not glob.has_magic(pattern):
            if path == normalized:
                return True
            continue
        if anchored_match(path, pattern):
            return True
    return False


def is_own_artifact(path: str, task_id: str) -> bool:
    prefix = f"artifacts/{task_id}"
    return path == prefix or path.startswith(prefix + "/")


def filesystem_matches(root: Path, pattern: str) -> set[str]:
    matches: set[str] = set()
    absolute_pattern = str(root / pattern)
    for raw in glob.iglob(absolute_pattern, recursive=True):
        path = Path(raw)
        if path.is_file() or path.is_symlink():
            matches.add(path.relative_to(root).as_posix())
        elif path.is_dir():
            for directory, names, files in os.walk(path, followlinks=False):
                names[:] = [name for name in names if name != ".git"]
                for filename in files:
                    child = Path(directory, filename)
                    matches.add(child.relative_to(root).as_posix())
    return matches


def concrete_paths(
    root: Path,
    allowlist: tuple[str, ...],
    task_id: str,
) -> tuple[str, ...]:
    tracked = {
        value.decode("utf-8", errors="surrogateescape")
        for value in git(root, ("ls-files", "-z", "--cached")).split(b"\x00")
        if value
    }
    candidates = {path for path in tracked if is_allowed(path, allowlist)}
    for pattern in allowlist:
        if is_own_artifact(pattern.rstrip("/**"), task_id):
            continue
        candidates.update(filesystem_matches(root, pattern))
    return tuple(
        sorted(
            path
            for path in candidates
            if is_allowed(path, allowlist) and not is_own_artifact(path, task_id)
        )
    )


class EvidenceSignal(EvidenceError):
    """Turn a handleable signal into normal scope cleanup."""


def _cleanup_temporary_index(
    workspace: Path,
    workspace_identity: tuple[int, int],
    index_path: Path,
    object_directory: Path,
    object_identity: tuple[int, int],
    identities: dict[str, tuple[int, int]],
) -> None:
    try:
        current = workspace.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError("temporary index workspace disappeared") from exc
    if (
        stat.S_ISLNK(current.st_mode)
        or not stat.S_ISDIR(current.st_mode)
        or (current.st_dev, current.st_ino) != workspace_identity
    ):
        raise EvidenceError("temporary index workspace ownership changed")

    try:
        objects_current = object_directory.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError("temporary object directory disappeared") from exc
    if (
        stat.S_ISLNK(objects_current.st_mode)
        or not stat.S_ISDIR(objects_current.st_mode)
        or (objects_current.st_dev, objects_current.st_ino) != object_identity
    ):
        raise EvidenceError("temporary object directory ownership changed")
    owned_names = {index_path.name, f"{index_path.name}.lock"}
    unexpected = sorted(
        path.name
        for path in workspace.iterdir()
        if path.name not in {*owned_names, object_directory.name}
    )
    if unexpected:
        raise EvidenceError(
            "temporary index workspace contains foreign paths: " + ", ".join(unexpected)
        )
    for name in owned_names:
        path = workspace / name
        try:
            child = path.lstat()
        except FileNotFoundError:
            continue
        if (
            not stat.S_ISREG(child.st_mode)
            or child.st_uid != os.getuid()
            or child.st_nlink != 1
            or identities.get(name) != (child.st_dev, child.st_ino)
        ):
            raise EvidenceError(f"temporary index child ownership changed: {name}")

    for fanout in object_directory.iterdir():
        fanout_info = fanout.lstat()
        fanout_key = f"objects/{fanout.name}"
        if (
            stat.S_ISLNK(fanout_info.st_mode)
            or not stat.S_ISDIR(fanout_info.st_mode)
            or re.fullmatch(r"[0-9a-f]{2}", fanout.name) is None
            or identities.get(fanout_key) != (fanout_info.st_dev, fanout_info.st_ino)
        ):
            raise EvidenceError(
                f"temporary object directory contains foreign path: {fanout.name}"
            )
        for object_path in fanout.iterdir():
            object_info = object_path.lstat()
            object_key = f"{fanout_key}/{object_path.name}"
            if (
                not stat.S_ISREG(object_info.st_mode)
                or re.fullmatch(r"[0-9a-f]{38}", object_path.name) is None
                or object_info.st_uid != os.getuid()
                or object_info.st_nlink != 1
                or identities.get(object_key)
                != (object_info.st_dev, object_info.st_ino)
            ):
                raise EvidenceError(
                    "temporary object fanout contains foreign path: "
                    f"{fanout.name}/{object_path.name}"
                )
            object_path.unlink()
        fanout.rmdir()
    object_directory.rmdir()
    for name in owned_names:
        path = workspace / name
        try:
            child = path.lstat()
        except FileNotFoundError:
            continue
        path.unlink()
    workspace.rmdir()


@contextmanager
def temporary_index(root: Path) -> Generator[tuple[Path, dict[str, str]], None, None]:
    """Yield a task-private Git index outside `.git`, then remove only owned paths."""
    root_digest = hashlib.sha256(str(root.resolve()).encode("utf-8")).hexdigest()[:16]
    handled_signals = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
    main_thread = threading.current_thread() is threading.main_thread()
    previous_mask: set[signal.Signals] | None = None
    if main_thread and hasattr(signal, "pthread_sigmask"):
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, handled_signals)
    try:
        workspace = Path(tempfile.mkdtemp(prefix=f"fpms-evidence-index-{root_digest}-"))
    except BaseException:
        if previous_mask is not None:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        raise
    index_path = workspace / "index"
    object_directory = workspace / "objects"
    identity: tuple[int, int] | None = None
    object_identity: tuple[int, int] | None = None
    ownership: dict[str, object] | None = None
    token: str | None = None
    previous_handlers: dict[int, object] = {}

    def handle_signal(number: int, _frame: object) -> None:
        raise EvidenceSignal(f"scope interrupted by signal {number}")

    try:
        created = workspace.lstat()
        if stat.S_ISLNK(created.st_mode) or not stat.S_ISDIR(created.st_mode):
            raise EvidenceError("temporary index workspace is unsafe")
        identity = (created.st_dev, created.st_ino)
        if main_thread:
            for number in handled_signals:
                previous_handlers[number] = signal.getsignal(number)
                signal.signal(number, handle_signal)
        if previous_mask is not None:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        workspace.chmod(0o700)
        created = workspace.lstat()
        if (created.st_dev, created.st_ino) != identity or stat.S_IMODE(
            created.st_mode
        ) != 0o700:
            raise EvidenceError("temporary index workspace mode must be 0700")
        object_directory.mkdir(mode=0o700)
        object_created = object_directory.lstat()
        object_identity = (object_created.st_dev, object_created.st_ino)
        git_directory = Path(
            git(root, ("rev-parse", "--absolute-git-dir")).decode().strip()
        )
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(index_path)
        env["GIT_OBJECT_DIRECTORY"] = str(object_directory)
        alternates = str(git_directory / "objects")
        if inherited := env.get("GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            alternates = alternates + os.pathsep + inherited
        env["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = alternates
        token = uuid.uuid4().hex
        env["FPMS_EVIDENCE_INDEX_OWNER"] = token
        ownership = {
            "workspace": workspace,
            "workspace_identity": identity,
            "object_directory": object_directory,
            "object_identity": object_identity,
            "identities": {},
        }
        _TEMP_INDEX_OWNERS[token] = ownership
        yield index_path, env
    finally:
        if previous_mask is not None:
            signal.pthread_sigmask(signal.SIG_BLOCK, handled_signals)
        try:
            if identity is not None and object_identity is not None:
                identities = ownership.get("identities", {}) if ownership else {}
                if not isinstance(identities, dict):
                    raise EvidenceError("temporary index identity record is invalid")
                _cleanup_temporary_index(
                    workspace,
                    identity,
                    index_path,
                    object_directory,
                    object_identity,
                    identities,
                )
            elif identity is not None:
                current = workspace.lstat()
                if (
                    stat.S_ISLNK(current.st_mode)
                    or not stat.S_ISDIR(current.st_mode)
                    or (current.st_dev, current.st_ino) != identity
                    or any(workspace.iterdir())
                ):
                    raise EvidenceError(
                        "temporary index workspace changed during failed setup"
                    )
                workspace.rmdir()
        finally:
            if token is not None:
                _TEMP_INDEX_OWNERS.pop(token, None)
            for number, handler in previous_handlers.items():
                signal.signal(number, handler)
            if previous_mask is not None:
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)


def changed_paths(
    root: Path,
    before: str,
    after: str,
    *,
    env: dict[str, str],
) -> tuple[str, ...]:
    return tuple(
        value.decode("utf-8", errors="surrogateescape")
        for value in git(
            root,
            ("diff", "--name-only", "-z", before, after),
            env=env,
        ).split(b"\x00")
        if value
    )


def assert_scoped(
    paths: Iterable[str],
    allowlist: tuple[str, ...],
    task_id: str,
    label: str,
) -> None:
    invalid = sorted(
        path
        for path in paths
        if not is_allowed(path, allowlist) or is_own_artifact(path, task_id)
    )
    if invalid:
        raise EvidenceError(
            f"{label} contains paths outside semantic allowlist: {', '.join(invalid)}"
        )


def baseline_tree(
    root: Path,
    artifact: Path,
    metadata: dict[str, object],
    allowlist: tuple[str, ...],
    task_id: str,
    *,
    env: dict[str, str],
) -> str:
    head = git(root, ("rev-parse", "HEAD^{tree}")).decode().strip()
    baseline_dirty = metadata.get("baseline_dirty")
    if not isinstance(baseline_dirty, bool):
        raise EvidenceError("task.json baseline_dirty must be boolean")
    patch = artifact / "baseline_allowlist.diff"
    external = artifact / "baseline_external_files.txt"
    if not baseline_dirty:
        if patch.exists() and patch.stat().st_size:
            raise EvidenceError(
                "clean baseline has a non-empty baseline_allowlist.diff"
            )
        return head
    if not patch.is_file():
        raise EvidenceError("missing baseline_allowlist.diff for dirty baseline")
    if not external.is_file():
        raise EvidenceError("missing baseline_external_files.txt for dirty baseline")

    git(root, ("read-tree", "HEAD"), env=env)
    apply_baseline_patch(root, patch, env)
    tree = git(root, ("write-tree",), env=env).decode().strip()
    assert_scoped(
        changed_paths(root, head, tree, env=env),
        allowlist,
        task_id,
        "dirty baseline",
    )
    return tree


def current_tree(
    root: Path,
    allowlist: tuple[str, ...],
    task_id: str,
    *,
    env: dict[str, str],
) -> str:
    head = git(root, ("rev-parse", "HEAD^{tree}")).decode().strip()
    paths = concrete_paths(root, allowlist, task_id)
    git(root, ("read-tree", "HEAD"), env=env)
    for offset in range(0, len(paths), 200):
        git(root, ("add", "-A", "-f", "--", *paths[offset : offset + 200]), env=env)
    tree = git(root, ("write-tree",), env=env).decode().strip()
    assert_scoped(
        changed_paths(root, head, tree, env=env),
        allowlist,
        task_id,
        "current state",
    )
    return tree


def parse_status_paths(status: bytes) -> tuple[str, ...]:
    records = status.split(b"\x00")
    paths: list[str] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            raise EvidenceError("malformed NUL-delimited Git status")
        state = record[:2].decode("ascii", errors="strict")
        paths.append(record[3:].decode("utf-8", errors="surrogateescape"))
        if "R" in state or "C" in state:
            if index >= len(records) or not records[index]:
                raise EvidenceError("malformed rename/copy Git status")
            paths.append(records[index].decode("utf-8", errors="surrogateescape"))
            index += 1
    return tuple(paths)


def current_external_paths(
    root: Path, allowlist: tuple[str, ...], task_id: str
) -> tuple[str, ...]:
    status = git(
        root,
        ("status", "--porcelain=v1", "-z", "--untracked-files=all"),
    )
    return tuple(
        sorted(
            {
                path
                for path in parse_status_paths(status)
                if not is_allowed(path, allowlist)
                and not is_own_artifact(path, task_id)
            }
        )
    )


def assert_external_unchanged(
    root: Path,
    artifact: Path,
    allowlist: tuple[str, ...],
    task_id: str,
) -> None:
    baseline_path = artifact / "baseline_external_files.txt"
    if not baseline_path.is_file():
        raise EvidenceError("missing baseline_external_files.txt")
    try:
        baseline = tuple(
            sorted(
                line
                for line in baseline_path.read_bytes()
                .decode("utf-8", errors="surrogateescape")
                .splitlines()
                if line
            )
        )
    except OSError as exc:
        raise EvidenceError(f"cannot read baseline external paths: {exc}") from exc
    if len(baseline) != len(set(baseline)):
        raise EvidenceError("baseline external paths must be unique")
    current = current_external_paths(root, allowlist, task_id)
    if current != baseline:
        added = sorted(set(current) - set(baseline))
        removed = sorted(set(baseline) - set(current))
        raise EvidenceError(
            f"outside-allowlist dirty paths changed: added={added}, removed={removed}"
        )


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def capture_material(
    root: Path,
    allowlist: tuple[str, ...],
    task_id: str,
) -> tuple[bytes, bytes]:
    with temporary_index(root) as (_index_path, env):
        head = git(root, ("rev-parse", "HEAD^{tree}"), env=env).decode().strip()
        before = current_tree(root, allowlist, task_id, env=env)
        baseline = git(
            root,
            ("diff", "--binary", "--full-index", "--no-renames", head, before),
            env=env,
        )
    external = current_external_paths(root, allowlist, task_id)
    external_content = "".join(f"{path}\n" for path in external).encode(
        "utf-8", errors="surrogateescape"
    )
    return baseline, external_content


def capture(task_id: str) -> None:
    root = repository_root()
    artifact, _, allowlist = load_metadata(root, task_id)
    baseline, external = capture_material(root, allowlist, task_id)
    atomic_write(artifact / "baseline_allowlist.diff", baseline)
    atomic_write(artifact / "baseline_external_files.txt", external)


def build_patch(
    task_id: str, *, root: Path | None = None, check_external: bool = True
) -> bytes:
    """Build the current exact scoped patch without writing evidence artifacts."""
    root = root.resolve() if root is not None else repository_root()
    artifact, metadata, allowlist = load_metadata(root, task_id)
    if check_external:
        assert_external_unchanged(root, artifact, allowlist, task_id)
    with temporary_index(root) as (_index_path, env):
        before = baseline_tree(
            root,
            artifact,
            metadata,
            allowlist,
            task_id,
            env=env,
        )
        after = current_tree(root, allowlist, task_id, env=env)
        paths = changed_paths(root, before, after, env=env)
        assert_scoped(paths, allowlist, task_id, "final patch")

        patch = git(
            root,
            (
                "diff",
                "--binary",
                "--full-index",
                "--no-renames",
                before,
                after,
            ),
            env=env,
        )
    if check_external:
        assert_external_unchanged(root, artifact, allowlist, task_id)
    return patch


def finalize(task_id: str) -> None:
    root = repository_root()
    artifact, _metadata, _allowlist = load_metadata(root, task_id)
    patch = build_patch(task_id, root=root)
    git_dir = artifact / "git"
    atomic_write(git_dir / "diff.patch", patch)
    atomic_write(git_dir / "status.txt", git(root, ("status", "-sb")))
    atomic_write(git_dir / "rev.txt", git(root, ("rev-parse", "HEAD")))


def preview_with_replacements(
    task_id: str,
    replacements: Mapping[str, bytes],
    *,
    root: Path | None = None,
) -> bytes:
    """Return the exact scoped patch after virtual in-allowlist replacements."""
    root = root.resolve() if root is not None else repository_root()
    artifact, metadata, allowlist = load_metadata(root, task_id)
    assert_external_unchanged(root, artifact, allowlist, task_id)
    normalized: dict[str, bytes] = {}
    for raw_path, content in replacements.items():
        path = PurePosixPath(raw_path).as_posix()
        if (
            not isinstance(content, bytes)
            or not is_allowed(path, allowlist)
            or is_own_artifact(path, task_id)
        ):
            raise EvidenceError(f"unsafe virtual replacement: {raw_path}")
        normalized[path] = content
    if not normalized:
        raise EvidenceError("virtual replacement set must not be empty")

    with temporary_index(root) as (_index_path, env):
        before = baseline_tree(
            root,
            artifact,
            metadata,
            allowlist,
            task_id,
            env=env,
        )
        current = current_tree(root, allowlist, task_id, env=env)
        git(root, ("read-tree", current), env=env)
        for path, content in sorted(normalized.items()):
            blob = (
                git(
                    root,
                    ("hash-object", "-w", "--stdin"),
                    env=env,
                    input_data=content,
                )
                .decode()
                .strip()
            )
            tree_row = git(root, ("ls-tree", "-z", current, "--", path), env=env)
            mode = "100644"
            if tree_row:
                header = tree_row.split(b"\t", 1)[0].decode("ascii")
                mode = header.split(" ", 1)[0]
            git(
                root,
                ("update-index", "--add", "--cacheinfo", f"{mode},{blob},{path}"),
                env=env,
            )
        after = git(root, ("write-tree",), env=env).decode().strip()
        paths = changed_paths(root, before, after, env=env)
        assert_scoped(paths, allowlist, task_id, "virtual final patch")
        patch = git(
            root,
            (
                "diff",
                "--binary",
                "--full-index",
                "--no-renames",
                before,
                after,
            ),
            env=env,
        )
    assert_external_unchanged(root, artifact, allowlist, task_id)
    return patch


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("capture", "finalize"))
    parser.add_argument("task_id")
    args = parser.parse_args(argv)
    try:
        if args.command == "capture":
            capture(args.task_id)
        else:
            finalize(args.task_id)
    except EvidenceError as exc:
        print(f"Evidence producer failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
