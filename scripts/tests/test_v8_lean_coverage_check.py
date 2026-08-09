from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "v8_lean_coverage_check.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
    path.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()


def _catalog(task_ids: list[str]) -> dict:
    return {
        "counts": {
            "catalog": len(task_ids),
            "foundation": len(task_ids),
            "deferred": 0,
        },
        "tasks": [
            {
                "task_id": task_id,
                "phase": "foundation",
            }
            for task_id in task_ids
        ],
    }


def _row(task_id: str, disposition: str = "PENDING") -> dict:
    return {
        "catalog_id": task_id,
        "phase": "foundation",
        "disposition": disposition,
        "story_id": None,
        "successor_story_id": None,
        "blocker": None,
    }


def _ledger(catalog_sha256: str, rows: list[dict]) -> dict:
    return {
        "schema_version": 1,
        "catalog_sha256": catalog_sha256,
        "integration_sha": None,
        "rows": rows,
        "stories": [],
    }


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "C3 Test")
    _git(repo, "config", "user.email", "c3-test@example.com")
    (repo / "owned.txt").write_text("v1\n")
    _git(repo, "add", "owned.txt")
    _git(repo, "commit", "-q", "-m", "initial")
    return repo, _git(repo, "rev-parse", "HEAD")


def test_inventory_accepts_exactly_one_pending_row_per_catalog_id(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A", "B"]))
    _write_json(ledger_path, _ledger(digest, [_row("A"), _row("B")]))

    checker.validate(
        catalog_path=catalog_path,
        ledger_path=ledger_path,
        expected_catalog_sha256=digest,
        milestone="inventory",
        repo_root=tmp_path,
        integration_sha=None,
    )


def test_inventory_rejects_catalog_digest_drift(tmp_path: Path) -> None:
    checker = _load_checker()
    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A"]))
    _write_json(ledger_path, _ledger(digest, [_row("A")]))

    with pytest.raises(checker.ValidationError, match="catalog SHA-256"):
        checker.validate(
            catalog_path=catalog_path,
            ledger_path=ledger_path,
            expected_catalog_sha256="0" * 64,
            milestone="inventory",
            repo_root=tmp_path,
            integration_sha=None,
        )


def test_inventory_rejects_missing_or_duplicate_catalog_rows(tmp_path: Path) -> None:
    checker = _load_checker()
    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A", "B"]))
    _write_json(ledger_path, _ledger(digest, [_row("A"), _row("A")]))

    with pytest.raises(checker.ValidationError, match="exactly once"):
        checker.validate(
            catalog_path=catalog_path,
            ledger_path=ledger_path,
            expected_catalog_sha256=digest,
            milestone="inventory",
            repo_root=tmp_path,
            integration_sha=None,
        )


def test_dirty_path_disposition_requires_exact_unique_manifest(tmp_path: Path) -> None:
    checker = _load_checker()
    digest = hashlib.sha256("a.txt\nnested/b.txt\n".encode()).hexdigest()
    payload = {
        "schema_version": 1,
        "source_path_manifest_sha256": digest,
        "total_paths": 2,
        "entries": [
            {
                "path": "a.txt",
                "disposition": "ARCHIVE_ONLY_HISTORY",
                "story_id": None,
            },
            {
                "path": "nested/b.txt",
                "disposition": "ADOPTION_STORY",
                "story_id": "STORY-B",
            },
        ],
    }
    disposition_path = tmp_path / "disposition.json"
    _write_json(disposition_path, payload)

    checker.validate_dirty_path_disposition(
        disposition_path,
        expected_path_manifest_sha256=digest,
        expected_count=2,
    )

    payload["entries"][1]["path"] = "a.txt"
    _write_json(disposition_path, payload)
    with pytest.raises(checker.ValidationError, match="exactly once"):
        checker.validate_dirty_path_disposition(
            disposition_path,
            expected_path_manifest_sha256=digest,
            expected_count=2,
        )


def test_current_verified_rejects_unreachable_commit(tmp_path: Path) -> None:
    checker = _load_checker()
    repo, integration_sha = _git_repo(tmp_path)
    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A"]))
    row = _row("A", "CURRENT_VERIFIED")
    row["story_id"] = "STORY-A"
    ledger = _ledger(digest, [row])
    ledger["integration_sha"] = integration_sha
    ledger["stories"] = [
        {
            "story_id": "STORY-A",
            "status": "CURRENT_VERIFIED",
            "commits": ["f" * 40],
            "paths": ["owned.txt"],
            "tree_sha256": "0" * 64,
            "tests": ["pytest focused"],
            "review_class": "NORMAL",
            "review_ref": "reviews/wave.md",
            "verification_ref": "verification/wave.md",
        }
    ]
    _write_json(ledger_path, ledger)

    with pytest.raises(checker.ValidationError, match="not reachable"):
        checker.validate(
            catalog_path=catalog_path,
            ledger_path=ledger_path,
            expected_catalog_sha256=digest,
            milestone="foundation",
            repo_root=repo,
            integration_sha=integration_sha,
        )


def test_current_verified_rejects_integrated_tree_drift(tmp_path: Path) -> None:
    checker = _load_checker()
    repo, reviewed_sha = _git_repo(tmp_path)
    reviewed_tree_sha = checker.compute_tree_fingerprint(
        repo, reviewed_sha, ["owned.txt"]
    )
    (repo / "owned.txt").write_text("changed after review\n")
    _git(repo, "add", "owned.txt")
    _git(repo, "commit", "-q", "-m", "drift")
    integration_sha = _git(repo, "rev-parse", "HEAD")

    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A"]))
    row = _row("A", "CURRENT_VERIFIED")
    row["story_id"] = "STORY-A"
    ledger = _ledger(digest, [row])
    ledger["integration_sha"] = integration_sha
    ledger["stories"] = [
        {
            "story_id": "STORY-A",
            "status": "CURRENT_VERIFIED",
            "commits": [reviewed_sha],
            "paths": ["owned.txt"],
            "tree_sha256": reviewed_tree_sha,
            "tests": ["pytest focused"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/protected.md",
            "verification_ref": "verification/protected.md",
        }
    ]
    _write_json(ledger_path, ledger)

    with pytest.raises(checker.ValidationError, match="integrated bytes changed"):
        checker.validate(
            catalog_path=catalog_path,
            ledger_path=ledger_path,
            expected_catalog_sha256=digest,
            milestone="foundation",
            repo_root=repo,
            integration_sha=integration_sha,
        )


def test_current_verified_accepts_linear_reviewed_successor_on_shared_path(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    repo, first_sha = _git_repo(tmp_path)
    first_tree_sha = checker.compute_tree_fingerprint(repo, first_sha, ["owned.txt"])
    (repo / "owned.txt").write_text("reviewed successor\n")
    _git(repo, "add", "owned.txt")
    _git(repo, "commit", "-q", "-m", "reviewed successor")
    successor_sha = _git(repo, "rev-parse", "HEAD")
    successor_tree_sha = checker.compute_tree_fingerprint(
        repo, successor_sha, ["owned.txt"]
    )

    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A", "B"]))
    first_row = _row("A", "CURRENT_VERIFIED")
    first_row["story_id"] = "STORY-A"
    successor_row = _row("B", "CURRENT_VERIFIED")
    successor_row["story_id"] = "STORY-B"
    ledger = _ledger(digest, [first_row, successor_row])
    ledger["integration_sha"] = successor_sha
    ledger["stories"] = [
        {
            "story_id": "STORY-A",
            "status": "CURRENT_VERIFIED",
            "commits": [first_sha],
            "paths": ["owned.txt"],
            "tree_sha256": first_tree_sha,
            "tests": ["pytest first"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/first.md",
            "verification_ref": "verification/first.md",
        },
        {
            "story_id": "STORY-B",
            "status": "CURRENT_VERIFIED",
            "commits": [successor_sha],
            "paths": ["owned.txt"],
            "tree_sha256": successor_tree_sha,
            "tests": ["pytest successor"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/successor.md",
            "verification_ref": "verification/successor.md",
        },
    ]
    _write_json(ledger_path, ledger)

    checker.validate(
        catalog_path=catalog_path,
        ledger_path=ledger_path,
        expected_catalog_sha256=digest,
        milestone="foundation",
        repo_root=repo,
        integration_sha=successor_sha,
    )


def test_current_verified_coalesces_aliases_of_the_same_owner_commit(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    repo, integration_sha = _git_repo(tmp_path)
    tree_sha = checker.compute_tree_fingerprint(repo, integration_sha, ["owned.txt"])
    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A", "B"]))
    first_row = _row("A", "CURRENT_VERIFIED")
    first_row["story_id"] = "STORY-A"
    second_row = _row("B", "CURRENT_VERIFIED")
    second_row["story_id"] = "STORY-B"
    ledger = _ledger(digest, [first_row, second_row])
    ledger["integration_sha"] = integration_sha
    ledger["stories"] = [
        {
            "story_id": "STORY-A",
            "status": "CURRENT_VERIFIED",
            "commits": [integration_sha],
            "paths": ["owned.txt"],
            "tree_sha256": tree_sha,
            "tests": ["pytest first"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/first.md",
            "verification_ref": "verification/first.md",
        },
        {
            "story_id": "STORY-B",
            "status": "CURRENT_VERIFIED",
            "commits": [integration_sha[:12]],
            "paths": ["owned.txt"],
            "tree_sha256": tree_sha,
            "tests": ["pytest second"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/second.md",
            "verification_ref": "verification/second.md",
        },
    ]
    _write_json(ledger_path, ledger)

    checker.validate(
        catalog_path=catalog_path,
        ledger_path=ledger_path,
        expected_catalog_sha256=digest,
        milestone="foundation",
        repo_root=repo,
        integration_sha=integration_sha,
    )


def test_current_verified_rejects_unreviewed_drift_after_reviewed_successor(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    repo, first_sha = _git_repo(tmp_path)
    first_tree_sha = checker.compute_tree_fingerprint(repo, first_sha, ["owned.txt"])
    (repo / "owned.txt").write_text("reviewed successor\n")
    _git(repo, "add", "owned.txt")
    _git(repo, "commit", "-q", "-m", "reviewed successor")
    successor_sha = _git(repo, "rev-parse", "HEAD")
    successor_tree_sha = checker.compute_tree_fingerprint(
        repo, successor_sha, ["owned.txt"]
    )
    (repo / "owned.txt").write_text("unreviewed drift\n")
    _git(repo, "add", "owned.txt")
    _git(repo, "commit", "-q", "-m", "unreviewed drift")
    integration_sha = _git(repo, "rev-parse", "HEAD")

    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A", "B"]))
    first_row = _row("A", "CURRENT_VERIFIED")
    first_row["story_id"] = "STORY-A"
    successor_row = _row("B", "CURRENT_VERIFIED")
    successor_row["story_id"] = "STORY-B"
    ledger = _ledger(digest, [first_row, successor_row])
    ledger["integration_sha"] = integration_sha
    ledger["stories"] = [
        {
            "story_id": "STORY-A",
            "status": "CURRENT_VERIFIED",
            "commits": [first_sha],
            "paths": ["owned.txt"],
            "tree_sha256": first_tree_sha,
            "tests": ["pytest first"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/first.md",
            "verification_ref": "verification/first.md",
        },
        {
            "story_id": "STORY-B",
            "status": "CURRENT_VERIFIED",
            "commits": [successor_sha],
            "paths": ["owned.txt"],
            "tree_sha256": successor_tree_sha,
            "tests": ["pytest successor"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/successor.md",
            "verification_ref": "verification/successor.md",
        },
    ]
    _write_json(ledger_path, ledger)

    with pytest.raises(checker.ValidationError, match="latest accepted review"):
        checker.validate(
            catalog_path=catalog_path,
            ledger_path=ledger_path,
            expected_catalog_sha256=digest,
            milestone="foundation",
            repo_root=repo,
            integration_sha=integration_sha,
        )


def test_current_verified_accepts_reachable_unchanged_story(tmp_path: Path) -> None:
    checker = _load_checker()
    repo, integration_sha = _git_repo(tmp_path)
    tree_sha = checker.compute_tree_fingerprint(repo, integration_sha, ["owned.txt"])
    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A"]))
    row = _row("A", "CURRENT_VERIFIED")
    row["story_id"] = "STORY-A"
    ledger = _ledger(digest, [row])
    ledger["integration_sha"] = integration_sha
    ledger["stories"] = [
        {
            "story_id": "STORY-A",
            "status": "CURRENT_VERIFIED",
            "commits": [integration_sha],
            "paths": ["owned.txt"],
            "tree_sha256": tree_sha,
            "tests": ["pytest focused"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/protected.md",
            "verification_ref": "verification/protected.md",
        }
    ]
    _write_json(ledger_path, ledger)

    checker.validate(
        catalog_path=catalog_path,
        ledger_path=ledger_path,
        expected_catalog_sha256=digest,
        milestone="foundation",
        repo_root=repo,
        integration_sha=integration_sha,
    )


def test_explicit_integration_head_does_not_require_self_referential_ledger_sha(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    repo, integration_sha = _git_repo(tmp_path)
    tree_sha = checker.compute_tree_fingerprint(repo, integration_sha, ["owned.txt"])
    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A"]))
    row = _row("A", "CURRENT_VERIFIED")
    row["story_id"] = "STORY-A"
    ledger = _ledger(digest, [row])
    ledger["stories"] = [
        {
            "story_id": "STORY-A",
            "status": "CURRENT_VERIFIED",
            "commits": [integration_sha],
            "paths": ["owned.txt"],
            "tree_sha256": tree_sha,
            "tests": ["pytest focused"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/protected.md",
            "verification_ref": "verification/protected.md",
        }
    ]
    _write_json(ledger_path, ledger)

    checker.validate(
        catalog_path=catalog_path,
        ledger_path=ledger_path,
        expected_catalog_sha256=digest,
        milestone="foundation",
        repo_root=repo,
        integration_sha=integration_sha,
    )


def test_non_inventory_direct_validation_requires_integration_sha(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    repo, _integration_sha = _git_repo(tmp_path)
    catalog_path = tmp_path / "catalog.json"
    ledger_path = tmp_path / "ledger.json"
    digest = _write_json(catalog_path, _catalog(["A"]))
    row = _row("A", "CURRENT_VERIFIED")
    row["story_id"] = "STORY-A"
    ledger = _ledger(digest, [row])
    ledger["stories"] = [
        {
            "story_id": "STORY-A",
            "status": "CURRENT_VERIFIED",
            "commits": ["f" * 40],
            "paths": ["owned.txt"],
            "tree_sha256": "0" * 64,
            "tests": ["pytest focused"],
            "review_class": "PROTECTED",
            "review_ref": "reviews/protected.md",
            "verification_ref": "verification/protected.md",
        }
    ]
    _write_json(ledger_path, ledger)

    with pytest.raises(
        checker.ValidationError,
        match="non-inventory validation requires integration_sha",
    ):
        checker.validate(
            catalog_path=catalog_path,
            ledger_path=ledger_path,
            expected_catalog_sha256=digest,
            milestone="foundation",
            repo_root=repo,
            integration_sha=None,
        )
