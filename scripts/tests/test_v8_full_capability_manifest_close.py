from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "docs/product/v8/catalog.frozen.json"
LEDGER_PATH = ROOT / "docs/product/v8/coverage-ledger.json"
SUCCESSOR_PATH = ROOT / "docs/product/v8/stories/V8-FULL-CAPABILITY-MANIFEST-CLOSE.md"
CHECKER_PATH = ROOT / "scripts/v8_lean_coverage_check.py"

PRE_ADOPTION_SHA = "c24acdd8dcba3329acc9cfac626954cfa49c20ac"
CONFIG_SUCCESSOR_SHA = "99316d6c83fe9c1c0e93b9703a5ea28509ea1ac6"
CONFIG_REVIEW_SHA = "dcb78fe978d3c655ef5fae7280ffba9e34b9bbeb"
STORY_ID = "V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION"
REVIEW_REF = "docs/product/v8/reviews/V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION.md"
PRODUCTION_INPUTS = {
    "DG-PAYMENT-WORKBOOK:GLOBAL": "CONFIG_REQUIRED",
    "DG-SERVICE-RATE-VERSION:GLOBAL": "CONFIG_REQUIRED",
}
SOURCE_DECISION_STATUS = {
    "DG-PAYMENT-WORKBOOK:GLOBAL": "PENDING",
    "DG-SERVICE-RATE-VERSION:GLOBAL": "PENDING",
}
TERMINAL_IDS = [
    "FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01",
    "FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01",
    "FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01",
    "FPMS-V8-FINAL-CLOSE-20260712-01",
]
GLOBAL_IDENTITIES = [
    "DG-GRANT-EVIDENCE-SOURCE:GLOBAL",
    "DG-GRANT-MANUAL-REVIEW:GLOBAL",
    "DG-FEE-APPLICATION-DRAFT:GLOBAL",
    "DG-FEE-GRANT-YEAR-DRAFT:GLOBAL",
    "DG-FEE-FUTURE-ANNUITY:GLOBAL",
    "DG-PAYMENT-WORKBOOK:GLOBAL",
    "DG-SERVICE-RATE-VERSION:GLOBAL",
]
FORM_IDENTITIES = [f"DG-LEGACY-FORM-CLASS:form-{number:03d}" for number in range(1, 23)]
CANDIDATE_PATHS = [
    "tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-FULL-CONFIG-REQUIRED-SUCCESSOR-20260813-01.md",
    "docs/product/v8/stories/V8-FULL-CONFIG-REQUIRED-SUCCESSOR.md",
    "scripts/tests/test_v8_full_config_required_successor.py",
    "tasks/postdemo/v8/FPMS-V8-FULL-CAPABILITY-MANIFEST-CLOSE-20260813-01.md",
    "docs/product/v8/stories/V8-FULL-CAPABILITY-MANIFEST-CLOSE.md",
    "scripts/tests/test_v8_full_capability_manifest_close.py",
]


def _load_checker():
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_json(commit: str, relative_path: str) -> dict[str, object]:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _unresolved_ordinals(ledger: dict[str, object]) -> list[int]:
    rows = ledger["rows"]
    return [
        ordinal
        for ordinal, row in enumerate(rows, start=1)
        if row["disposition"] not in {"CURRENT_VERIFIED", "SUPERSEDED_BY_STORY"}
    ]


def test_candidate_preserves_row199_and_binds_exact_pre_adoption_authority() -> None:
    catalog = json.loads(CATALOG_PATH.read_text())
    assert len(catalog["tasks"]) == 283
    assert [task["ordinal"] for task in catalog["tasks"]] == list(range(1, 284))
    assert len({task["task_id"] for task in catalog["tasks"]}) == 283
    row199 = catalog["tasks"][198]
    assert row199["task_id"] == TERMINAL_IDS[0]
    assert row199["profile"] == "TC-QA"
    assert row199["serialization_groups"] == [
        {"ownership": "FULL_MANIFEST_OWNERSHIP", "order_key": 1}
    ]

    pre_adoption = _git_json(PRE_ADOPTION_SHA, "docs/product/v8/coverage-ledger.json")
    assert _unresolved_ordinals(pre_adoption) == [199, 281, 282, 283]
    for ordinal in range(170, 199):
        row = pre_adoption["rows"][ordinal - 1]
        assert row["disposition"] == "CURRENT_VERIFIED", ordinal
        assert row["story_id"], ordinal

    story = SUCCESSOR_PATH.read_text(encoding="utf-8")
    for row in pre_adoption["rows"][169:198]:
        assert f"`{row['catalog_id']}` → `{row['story_id']}`" in story
    for identity in GLOBAL_IDENTITIES + FORM_IDENTITIES:
        assert f"`{identity}`" in story
    assert CONFIG_SUCCESSOR_SHA in story
    assert CONFIG_REVIEW_SHA in story
    assert "29 requested identities" in story


def test_ledger_adopts_only_row199_with_exact_capability_metadata() -> None:
    ledger = json.loads(LEDGER_PATH.read_text())
    row199 = ledger["rows"][198]
    assert row199 == {
        "catalog_id": TERMINAL_IDS[0],
        "phase": "deferred",
        "disposition": "CURRENT_VERIFIED",
        "story_id": STORY_ID,
        "successor_story_id": None,
        "blocker": None,
    }
    assert _unresolved_ordinals(ledger) == [281, 282, 283]
    for ordinal, task_id in zip((281, 282, 283), TERMINAL_IDS[1:], strict=True):
        row = ledger["rows"][ordinal - 1]
        assert row["catalog_id"] == task_id
        assert row["disposition"] == "PENDING"
        assert row["story_id"] is None

    story = next(story for story in ledger["stories"] if story["story_id"] == STORY_ID)
    assert story["status"] == "CURRENT_VERIFIED"
    assert story["paths"] == CANDIDATE_PATHS
    assert story["review_class"] == "PROTECTED"
    assert story["review_ref"] == REVIEW_REF
    assert story["verification_ref"] == REVIEW_REF
    assert story["capability_status"] == "CAPABILITY_VERIFIED"
    assert story["production_inputs"] == PRODUCTION_INPUTS
    assert story["source_decision_status"] == SOURCE_DECISION_STATUS
    assert story["production_failure"] == "409 / NO WRITE"
    assert story["production_activation_claimed"] is False
    assert story["full_config_successor_commit"] == CONFIG_SUCCESSOR_SHA
    assert story["full_config_successor_review_commit"] == CONFIG_REVIEW_SHA

    candidate_sha = story["commits"][-1]
    checker = _load_checker()
    assert story["tree_sha256"] == checker.compute_tree_fingerprint(
        ROOT,
        candidate_sha,
        CANDIDATE_PATHS,
    )
