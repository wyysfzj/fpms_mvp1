from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_SHA = "e6a0440c2823b4ce4a49cfd8e155b5746083775b"
PRE_ADOPTION_TIP_SHA = "3f3177c4d234207ca4b752c3807e4ed933ff1fb6"
PREEXISTING_PATH_COUNT = 84
PREEXISTING_PATHS_SHA256 = "3261ce65b64a2cc44855daa7be907c8434e10c755460d5205f77c5cd180b3c29"
STORY_ID = "V8-FINAL-MATRIX-REMEDIATION-CURRENT-ADOPTION"
REVIEW_REF = "docs/product/v8/reviews/V8-FINAL-MATRIX-REMEDIATION-CURRENT-ADOPTION.md"
TASK_PATH = "tasks/postdemo/v8/FPMS-V8-FINAL-MATRIX-REMEDIATION-CURRENT-ADOPTION-20260813-01.md"
TEST_PATH = "backend/tests/test_v8_final_matrix_remediation_adoption.py"
STORY_PATH = "docs/product/v8/stories/V8-FINAL-MATRIX-REMEDIATION-CURRENT-ADOPTION.md"
ADOPTION_PATHS = [TASK_PATH, TEST_PATH, STORY_PATH]
LEDGER_PATH = ROOT / "docs/product/v8/coverage-ledger.json"


def _git_lines(*args: str) -> list[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()


def _path_manifest_sha256(paths: list[str]) -> str:
    payload = "".join(f"{path}\n" for path in sorted(paths)).encode()
    return hashlib.sha256(payload).hexdigest()


def _load_checker():
    path = ROOT / "scripts/v8_lean_coverage_check.py"
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_exact_preexisting_range_and_adoption_paths_are_frozen() -> None:
    preexisting = _git_lines("diff", "--name-only", f"{BASE_SHA}..{PRE_ADOPTION_TIP_SHA}")
    assert len(preexisting) == len(set(preexisting)) == PREEXISTING_PATH_COUNT
    assert _path_manifest_sha256(preexisting) == PREEXISTING_PATHS_SHA256
    assert set(preexisting).isdisjoint(ADOPTION_PATHS)
    assert all((ROOT / path).is_file() for path in [*preexisting, *ADOPTION_PATHS])

    story = (ROOT / STORY_PATH).read_text()
    task = (ROOT / TASK_PATH).read_text()
    for required in (
        BASE_SHA,
        PRE_ADOPTION_TIP_SHA,
        PREEXISTING_PATHS_SHA256,
        "exactly 87",
        "CONFIG_REQUIRED / PENDING / 409 NO WRITE",
        "Row283 remains the sole PENDING catalog row",
    ):
        assert required in story or required in task


def test_ledger_adoption_is_append_only_when_materialized() -> None:
    ledger = json.loads(LEDGER_PATH.read_text())
    story = next((item for item in ledger["stories"] if item["story_id"] == STORY_ID), None)
    if story is None:
        assert ledger["rows"][282]["disposition"] == "PENDING"
        return

    candidate = story["commits"][-1]
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
    assert len(candidate_paths) == len(set(candidate_paths)) == 87
    assert set(candidate_paths) == set(
        _git_lines("diff", "--name-only", f"{BASE_SHA}..{PRE_ADOPTION_TIP_SHA}")
    ) | set(ADOPTION_PATHS)
    assert ledger["rows"] == baseline["rows"]
    assert ledger["stories"][:-1] == baseline["stories"]
    assert ledger["stories"][-1] == story
    assert story["status"] == "CURRENT_VERIFIED"
    assert story["review_class"] == "PROTECTED"
    assert story["review_ref"] == story["verification_ref"] == REVIEW_REF
    assert story["production_activation_claimed"] is False
    assert story["tree_sha256"] == _load_checker().compute_tree_fingerprint(
        ROOT,
        candidate,
        candidate_paths,
    )
    assert [
        index + 1 for index, row in enumerate(ledger["rows"]) if row["disposition"] == "PENDING"
    ] == [283]
