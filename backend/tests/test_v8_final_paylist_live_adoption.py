from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "5065900d6355e39bd5817af4ef895a5c7add6581"
STORY_ID = "V8-FINAL-PAYLIST-LIVE-CURRENT-ADOPTION"
REVIEW = "docs/product/v8/reviews/V8-FINAL-PAYLIST-LIVE-CURRENT-ADOPTION.md"
PATHS = [
    "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-pay-list-boundary-live.spec.ts",
    "backend/tests/test_v8_final_paylist_live_adoption.py",
    "docs/product/v8/stories/V8-FINAL-PAYLIST-LIVE-CURRENT-ADOPTION.md",
    "tasks/postdemo/v8/FPMS-V8-FINAL-PAYLIST-LIVE-CURRENT-ADOPTION-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-FINAL-PAYLIST-LIVE-LOCATOR-ALIGNMENT-20260813-01.md",
]
LEDGER = ROOT / "docs/product/v8/coverage-ledger.json"


def _checker():
    spec = importlib.util.spec_from_file_location(
        "checker", ROOT / "scripts/v8_lean_coverage_check.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_candidate_and_story_are_exact() -> None:
    source_paths = subprocess.run(
        ["git", "show", "--name-only", "--format=", SOURCE],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert source_paths == [PATHS[0], PATHS[4]]
    assert len(PATHS) == len(set(PATHS)) == 5
    assert all((ROOT / path).is_file() for path in PATHS)
    story = (ROOT / PATHS[2]).read_text()
    for value in (SOURCE, "1 passed", "P0/P1/P2=0/0/0", "Row283 sole PENDING"):
        assert value in story


def test_ledger_append_is_exact_prefix() -> None:
    ledger = json.loads(LEDGER.read_text())
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
    index = len(baseline["stories"])
    assert ledger["rows"] == baseline["rows"]
    assert ledger["stories"][:index] == baseline["stories"]
    assert ledger["stories"][index] == story
    assert story["paths"] == PATHS
    assert story["review_ref"] == story["verification_ref"] == REVIEW
    assert story["tree_sha256"] == _checker().compute_tree_fingerprint(ROOT, candidate, PATHS)
    assert [i + 1 for i, row in enumerate(ledger["rows"]) if row["disposition"] == "PENDING"] == [
        283
    ]
