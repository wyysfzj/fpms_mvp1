from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "docs/product/v8/coverage-ledger.json"
STORY_PATH = (
    ROOT
    / "docs/product/v8/stories/"
    "V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION.md"
)
STORY_ID = "V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION"
REVIEW_REF = (
    "docs/product/v8/reviews/"
    "V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION.md"
)
EXTERNAL_PATHS = {
    "FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01": [
        "backend/app/modules/fees/official_rate_book.py",
        "backend/tests/test_v8_official_fee_estimate_rate_provider.py",
    ],
    "FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01": [
        "backend/tests/test_official_fee_preview_api.py",
    ],
    "FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01": [
        "backend/app/modules/official_workflows/filing_evidence_resolver.py",
        "backend/tests/test_v8_filing_submission_evidence_resolver.py",
    ],
}
CANDIDATE_PATHS = [
    *[path for paths in EXTERNAL_PATHS.values() for path in paths],
    "tasks/postdemo/v8/FPMS-V8-ROW282-EXTERNAL-PATH-OWNERSHIP-ADOPTION-20260813-01.md",
    "backend/tests/test_v8_row282_external_path_ownership_adoption.py",
    "docs/product/v8/stories/V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION.md",
]
ROW282_OWNERSHIP_ADOPTION_SHA = "d3f51ae"


def _load_checker():
    path = ROOT / "scripts/v8_lean_coverage_check.py"
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_show_json(commit: str, path: str) -> dict:
    content = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(content)


def test_required_story_binds_the_three_exact_external_path_sets() -> None:
    text = STORY_PATH.read_text()
    assert "Status: `CURRENT_VERIFIED`" in text
    for task_id, paths in EXTERNAL_PATHS.items():
        assert task_id in text
        for path in paths:
            assert path in text
            assert (ROOT / path).is_file()
    assert len(CANDIDATE_PATHS) == len(set(CANDIDATE_PATHS)) == 8
    assert "CONFIG_REQUIRED / PENDING / 409 NO WRITE" in text
    assert "No Row282" in text


def test_ledger_adds_only_the_reviewed_external_ownership_story() -> None:
    ledger = _git_show_json(
        ROW282_OWNERSHIP_ADOPTION_SHA,
        "docs/product/v8/coverage-ledger.json",
    )
    story = next(item for item in ledger["stories"] if item["story_id"] == STORY_ID)
    assert story["status"] == "CURRENT_VERIFIED"
    assert story["paths"] == CANDIDATE_PATHS
    assert story["external_task_paths"] == EXTERNAL_PATHS
    assert story["review_class"] == "PROTECTED"
    assert story["review_ref"] == REVIEW_REF
    assert story["verification_ref"] == REVIEW_REF
    assert story["production_activation_claimed"] is False

    candidate = story["commits"][-1]
    baseline = _git_show_json(candidate, "docs/product/v8/coverage-ledger.json")
    assert ledger["rows"] == baseline["rows"]
    assert ledger["stories"][:-1] == baseline["stories"]
    assert ledger["stories"][-1] == story
    assert [
        index + 1
        for index, row in enumerate(ledger["rows"])
        if row["disposition"] == "PENDING"
    ] == [282, 283]

    checker = _load_checker()
    assert story["tree_sha256"] == checker.compute_tree_fingerprint(
        ROOT,
        candidate,
        CANDIDATE_PATHS,
    )
