from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_SHA = "b77c743e2f83883ecf97ff5111e5179aabd3af0f"
STORY_ID = "V8-FINAL-GOVERNANCE-SNAPSHOT-CURRENT-ADOPTION"
REVIEW_REF = "docs/product/v8/reviews/V8-FINAL-GOVERNANCE-SNAPSHOT-CURRENT-ADOPTION.md"
SOURCE_PATHS = [
    "backend/tests/test_v8_final_matrix_remediation_adoption.py",
    "backend/tests/test_v8_input_activation_decoupling_contract.py",
    "tasks/postdemo/v8/FPMS-V8-FINAL-SUITE-GOVERNANCE-SNAPSHOT-ALIGNMENT-20260813-01.md",
]
ADOPTION_PATHS = [
    "backend/tests/test_v8_final_governance_snapshot_adoption.py",
    "docs/product/v8/stories/V8-FINAL-GOVERNANCE-SNAPSHOT-CURRENT-ADOPTION.md",
    "tasks/postdemo/v8/FPMS-V8-FINAL-GOVERNANCE-SNAPSHOT-CURRENT-ADOPTION-20260813-01.md",
]
PATHS = sorted([*SOURCE_PATHS, *ADOPTION_PATHS])
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


def test_exact_source_and_adoption_paths_are_frozen() -> None:
    assert _git_lines("show", "--name-only", "--format=", CANDIDATE_SHA) == SOURCE_PATHS
    assert len(PATHS) == len(set(PATHS)) == 6
    assert all((ROOT / path).is_file() for path in PATHS)
    story = (ROOT / ADOPTION_PATHS[1]).read_text()
    for required in (
        CANDIDATE_SHA,
        "580476b07d992dbf23175f308b9e75322733ecbbae2e2c9b009e4e62ed667ce6",
        "2 passed",
        "P0/P1/P2 = 0/0/0",
        "Row283 remains the sole PENDING catalog row",
        "CONFIG_REQUIRED / PENDING / 409 NO WRITE",
    ):
        assert required in story


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
    assert story["paths"] == PATHS
    assert ledger["rows"] == baseline["rows"]
    assert ledger["stories"][:-1] == baseline["stories"]
    assert ledger["stories"][-1] == story
    assert story["review_ref"] == story["verification_ref"] == REVIEW_REF
    assert story["tree_sha256"] == _load_checker().compute_tree_fingerprint(ROOT, candidate, PATHS)
    assert [
        index + 1 for index, row in enumerate(ledger["rows"]) if row["disposition"] == "PENDING"
    ] == [283]
