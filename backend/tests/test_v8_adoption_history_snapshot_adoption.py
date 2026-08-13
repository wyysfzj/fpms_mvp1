from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "74caa4c7a5f64c3426769a9d47f5d9e4d56b5310"
STORY_ID = "V8-ADOPTION-HISTORY-SNAPSHOT-CURRENT-ADOPTION"
REVIEW_REF = "docs/product/v8/reviews/V8-ADOPTION-HISTORY-SNAPSHOT-CURRENT-ADOPTION.md"
SOURCE_PATHS = [
    "backend/tests/test_v8_final_governance_snapshot_adoption.py",
    "backend/tests/test_v8_sqlite_pragma_isolation_adoption.py",
    "tasks/postdemo/v8/FPMS-V8-ADOPTION-HISTORY-SNAPSHOT-ALIGNMENT-20260813-01.md",
]
ADOPTION_PATHS = [
    "backend/tests/test_v8_adoption_history_snapshot_adoption.py",
    "docs/product/v8/stories/V8-ADOPTION-HISTORY-SNAPSHOT-CURRENT-ADOPTION.md",
    "tasks/postdemo/v8/FPMS-V8-ADOPTION-HISTORY-SNAPSHOT-CURRENT-ADOPTION-20260813-01.md",
]
PATHS = sorted([*SOURCE_PATHS, *ADOPTION_PATHS])
LEDGER = ROOT / "docs/product/v8/coverage-ledger.json"


def _checker():
    spec = importlib.util.spec_from_file_location(
        "checker", ROOT / "scripts/v8_lean_coverage_check.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_json(revision: str) -> dict:
    return json.loads(
        subprocess.run(
            ["git", "show", f"{revision}:docs/product/v8/coverage-ledger.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )


def test_exact_candidate_paths_and_story() -> None:
    changed = subprocess.run(
        ["git", "show", "--name-only", "--format=", SOURCE_SHA],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert changed == SOURCE_PATHS
    assert len(PATHS) == len(set(PATHS)) == 6
    assert all((ROOT / path).is_file() for path in PATHS)
    text = (ROOT / ADOPTION_PATHS[1]).read_text()
    for value in (SOURCE_SHA, "2 passed", "P0/P1/P2=0/0/0", "Row283 sole PENDING"):
        assert value in text


def test_adoption_is_exact_prefix_even_after_future_appends() -> None:
    ledger = json.loads(LEDGER.read_text())
    story = next((item for item in ledger["stories"] if item["story_id"] == STORY_ID), None)
    if story is None:
        assert ledger["rows"][282]["disposition"] == "PENDING"
        return
    candidate = story["commits"][-1]
    baseline = _git_json(candidate)
    index = len(baseline["stories"])
    assert ledger["rows"] == baseline["rows"]
    assert ledger["stories"][:index] == baseline["stories"]
    assert ledger["stories"][index] == story
    assert story["paths"] == PATHS
    assert story["review_ref"] == story["verification_ref"] == REVIEW_REF
    assert story["tree_sha256"] == _checker().compute_tree_fingerprint(ROOT, candidate, PATHS)
    assert [i + 1 for i, row in enumerate(ledger["rows"]) if row["disposition"] == "PENDING"] == [
        283
    ]
