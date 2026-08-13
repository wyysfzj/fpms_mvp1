from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_SHA = "e19d615c84c4c2d2afd10dcc440c4f2683fc2b77"
REMEDIATION_SHA = "9557d1c58ae51d4e9c68b7d435e2873ebb154205"
ADOPTION_SHA = "327e88f87364d0e6f63103972a920be7bc6d87ef"
STORY_ID = "V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION"
REVIEW_REF = "docs/product/v8/reviews/V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION.md"
TASK_PATH = "tasks/postdemo/v8/FPMS-V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION-20260813-01.md"
TEST_PATH = "backend/tests/test_v8_sqlite_pragma_isolation_adoption.py"
STORY_PATH = "docs/product/v8/stories/V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION.md"
ADOPTION_PATHS = [TASK_PATH, TEST_PATH, STORY_PATH]
LEDGER_PATH = ROOT / "docs/product/v8/coverage-ledger.json"


def _git_lines(*args: str) -> list[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()


def _load_checker():
    path = ROOT / "scripts/v8_lean_coverage_check.py"
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _path_manifest_sha256(paths: list[str]) -> str:
    return hashlib.sha256("".join(f"{path}\n" for path in sorted(paths)).encode()).hexdigest()


def test_exact_remediation_and_adoption_paths_are_frozen() -> None:
    remediation = _git_lines("diff", "--name-only", f"{BASE_SHA}..{REMEDIATION_SHA}")
    assert remediation == [
        "backend/tests/conftest.py",
        "backend/tests/test_v8_sqlite_pragma_isolation.py",
        "tasks/postdemo/v8/FPMS-V8-FINAL-SUITE-SQLITE-PRAGMA-ISOLATION-20260813-01.md",
    ]
    assert _path_manifest_sha256(remediation) == (
        "c6832c84850d466db65a6dc9294eb10f82e7fe906b7c7b59022bae94ee4f8235"
    )
    assert set(remediation).isdisjoint(ADOPTION_PATHS)
    assert all((ROOT / path).is_file() for path in [*remediation, *ADOPTION_PATHS])

    story = (ROOT / STORY_PATH).read_text()
    for required in (
        BASE_SHA,
        REMEDIATION_SHA,
        "exactly six",
        "3 passed",
        "P0/P1/P2 = 0/0/0",
        "CONFIG_REQUIRED / PENDING / 409 NO WRITE",
        "Row283 remains the sole PENDING catalog row",
    ):
        assert required in story


def test_ledger_adoption_is_append_only_when_materialized() -> None:
    ledger = json.loads(LEDGER_PATH.read_text())
    story = next((item for item in ledger["stories"] if item["story_id"] == STORY_ID), None)
    if story is None:
        assert ledger["rows"][282]["disposition"] == "PENDING"
        return

    adopted = json.loads(
        subprocess.run(
            ["git", "show", f"{ADOPTION_SHA}:docs/product/v8/coverage-ledger.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    adopted_story = adopted["stories"][-1]
    assert adopted_story["story_id"] == STORY_ID
    assert story == adopted_story
    candidate = adopted_story["commits"][-1]
    baseline = json.loads(
        subprocess.run(
            ["git", "show", f"{candidate}:docs/product/v8/coverage-ledger.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    candidate_paths = _git_lines("diff", "--name-only", f"{BASE_SHA}..{candidate}")
    assert candidate_paths == story["paths"]
    assert len(candidate_paths) == len(set(candidate_paths)) == 6
    assert adopted["rows"] == baseline["rows"]
    assert adopted["stories"][:-1] == baseline["stories"]
    assert adopted["stories"][-1] == story
    assert ledger["rows"] == adopted["rows"]
    assert ledger["stories"][: len(adopted["stories"])] == adopted["stories"]
    assert story["status"] == "CURRENT_VERIFIED"
    assert story["review_class"] == "PROTECTED"
    assert story["review_ref"] == story["verification_ref"] == REVIEW_REF
    assert story["production_activation_claimed"] is False
    assert story["tree_sha256"] == _load_checker().compute_tree_fingerprint(
        ROOT, candidate, candidate_paths
    )
    assert [
        index + 1 for index, row in enumerate(ledger["rows"]) if row["disposition"] == "PENDING"
    ] == [283]
