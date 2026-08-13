from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "docs/product/v8/catalog.frozen.json"
LEDGER_PATH = ROOT / "docs/product/v8/coverage-ledger.json"
OUTPUT_PATH = ROOT / "docs/product/v8/final-item-slice-ledger.json"
STORY_PATH = ROOT / "docs/product/v8/stories/V8-FINAL-ITEM-SLICE-LEDGER-CLOSE.md"
CHECKER_PATH = ROOT / "scripts/v8_lean_coverage_check.py"

ROW282_ID = "FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01"
ROW283_ID = "FPMS-V8-FINAL-CLOSE-20260712-01"
STORY_ID = "V8-FINAL-ITEM-SLICE-LEDGER-CURRENT-ADOPTION"
REVIEW_REF = "docs/product/v8/reviews/V8-FINAL-ITEM-SLICE-LEDGER-CURRENT-ADOPTION.md"
CANDIDATE_PATHS = [
    "tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md",
    "backend/tests/test_v8_final_item_slice_ledger.py",
    "docs/product/v8/final-item-slice-ledger.json",
    "docs/product/v8/stories/V8-FINAL-ITEM-SLICE-LEDGER-CLOSE.md",
]

EXTERNAL_ITEMS = {
    "FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01": {
        "story_ids": ["V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-CURRENT-ADOPTION"],
        "current_paths": [
            "backend/app/modules/documents/grant_fee_lines.py",
            "backend/tests/test_v8_grant_notice_fee_line_snapshot.py",
        ],
    },
    "FPMS-V8-OFFICIAL-FEE-ESTIMATE-RATE-PROVIDER-20260713-01": {
        "story_ids": ["V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION"],
        "current_paths": [
            "backend/app/modules/fees/official_rate_book.py",
            "backend/tests/test_v8_official_fee_estimate_rate_provider.py",
        ],
    },
    "FPMS-V8-OFFICIAL-FEE-PREVIEW-LEGACY-TEST-MIGRATION-20260713-01": {
        "story_ids": ["V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION"],
        "current_paths": ["backend/tests/test_official_fee_preview_api.py"],
    },
    "FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01": {
        "story_ids": ["V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION"],
        "current_paths": ["backend/tests/test_v8_lifecycle_case_opened.py"],
    },
    "FPMS-V8-DE-RAW-ATTACHMENT-EVIDENCE-ROLE-20260714-01": {
        "story_ids": ["V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION"],
        "current_paths": [
            "backend/app/modules/documents/evidence_contracts.py",
            "backend/tests/test_v8_document_evidence_contracts.py",
        ],
    },
    "FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01": {
        "story_ids": ["V8-D4-07-REGISTRATION-MATRIX-CURRENT-VERIFICATION"],
        "current_paths": [
            "backend/app/modules/documents/evidence_service.py",
            "backend/tests/test_v8_document_evidence_register_version.py",
            "backend/tests/test_v8_raw_attachment_registration_guard.py",
        ],
    },
    "FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01": {
        "story_ids": [
            "V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION",
            "V8-DOCUMENT-EVIDENCE-CORE-CURRENT-VERIFICATION",
        ],
        "current_paths": [
            "backend/app/modules/documents/evidence_workflow_service.py",
            "backend/tests/test_v8_external_submission_role_allowlist.py",
            "backend/tests/test_v8_finalize_external_submission_seam.py",
        ],
    },
    "FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01": {
        "story_ids": ["V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION"],
        "current_paths": [
            "backend/app/modules/cases/lifecycle_rules.py",
            "backend/tests/test_v8_lifecycle_case_opened.py",
        ],
    },
    "FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01": {
        "story_ids": [
            "V8-CANARY-CASE-STATUS-UI-VERTICAL-CURRENT-VERIFICATION",
            "V8-FULL-INHERITED-REGRESSION-MATRIX-CURRENT-ADOPTION",
        ],
        "current_paths": [
            "backend/app/modules/cases/service.py",
            "backend/tests/test_case_missing_fields_crud.py",
            "backend/tests/test_v8_case_create_status_gate.py",
        ],
    },
    "FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01": {
        "story_ids": ["V8-FILING-LIFECYCLE-VERTICAL-CURRENT-VERIFICATION"],
        "current_paths": [
            "backend/app/modules/cases/lifecycle_rules.py",
            "backend/tests/test_v8_lifecycle_filing_preparation_started.py",
        ],
    },
    "FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01": {
        "story_ids": ["V8-FILING-LIFECYCLE-VERTICAL-CURRENT-VERIFICATION"],
        "current_paths": [
            "backend/app/modules/cases/lifecycle_rules.py",
            "backend/tests/test_v8_lifecycle_filing_external_submission.py",
        ],
    },
    "FPMS-V8-FILING-SUBMISSION-EVIDENCE-RESOLVER-20260715-01": {
        "story_ids": ["V8-ROW282-EXTERNAL-PATH-OWNERSHIP-CURRENT-ADOPTION"],
        "current_paths": [
            "backend/app/modules/official_workflows/filing_evidence_resolver.py",
            "backend/tests/test_v8_filing_submission_evidence_resolver.py",
        ],
    },
    "FPMS-V8-DE-DELTA4-EVIDENCE-ROLE-EXTENSION-20260715-01": {
        "story_ids": ["V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION"],
        "current_paths": [
            "backend/app/modules/documents/evidence_contracts.py",
            "backend/tests/test_v8_delta4_evidence_role_extension.py",
            "backend/tests/test_v8_document_evidence_contracts.py",
        ],
    },
    "FPMS-V8-DE-DELTA4-REGISTRATION-MATRIX-CORRECTION-20260715-01": {
        "story_ids": ["V8-D4-07-REGISTRATION-MATRIX-CURRENT-VERIFICATION"],
        "current_paths": [
            "backend/app/modules/documents/evidence_service.py",
            "backend/tests/test_v8_delta4_registration_matrix.py",
        ],
    },
    "FPMS-V8-DE-OA-STRUCTURED-ATTACHMENT-PROMOTION-20260715-01": {
        "story_ids": ["V8-D4-08-OA-STRUCTURED-ATTACHMENT-PROMOTION"],
        "current_paths": [
            "backend/app/modules/documents/oa_attachment_promotion_service.py",
            "backend/tests/test_v8_oa_structured_attachment_promotion.py",
        ],
    },
    "FPMS-V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-20260715-01": {
        "story_ids": ["V8-CNIPA-246-LAYOUT-RATE-CANDIDATE-CURRENT-ADOPTION"],
        "current_paths": [
            "backend/app/modules/fees/cnipa_layout_rate_candidate.py",
            "backend/app/modules/fees/data/cnipa_246_layout_rate.json",
            "backend/tests/test_v8_cnipa_246_layout_rate_candidate.py",
        ],
    },
    "FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01": {
        "story_ids": ["V8-CNIPA-ANNUITY-RATE-CANDIDATE-CURRENT-ADOPTION"],
        "current_paths": [
            "backend/app/modules/fees/cnipa_annuity_rate_candidate.py",
            "backend/app/modules/fees/data/cnipa_payment_guide_20260330_annuity_rates.json",
            "backend/tests/test_v8_cnipa_annuity_rate_candidate.py",
        ],
    },
    "FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01": {
        "story_ids": ["V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-CURRENT-ADOPTION"],
        "current_paths": [
            "backend/alembic/versions/v8_delta4_annuity_obligation_lineage.py",
            "backend/app/modules/annuity/models.py",
            "backend/tests/test_v8_annuity_task_obligation_lineage_carrier.py",
        ],
    },
    "FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01": {
        "story_ids": ["V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-CURRENT-VERIFICATION"],
        "current_paths": [
            "backend/alembic/versions/v8_delta4_legacy_fee_reduction_provenance.py",
            "backend/app/modules/fees/models.py",
            "backend/tests/test_v8_legacy_fee_reduction_provenance_carrier.py",
        ],
    },
}

AUDIT_LINEAGE = [
    {
        "identity": "FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01",
        "kind": "DELTA_CONTROLLER",
        "artifact": "artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-20260713-01/materialization/delta_overlay.json",
    },
    {
        "identity": "FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01",
        "kind": "DELTA_CONTROLLER",
        "artifact": "artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-2-20260714-01/materialization/delta_overlay.json",
    },
    {
        "identity": "FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01",
        "kind": "DELTA_CONTROLLER",
        "artifact": "artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01/materialization/delta3_overlay.json",
    },
    {
        "identity": "FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01",
        "kind": "DELTA_CONTROLLER",
        "artifact": "artifacts/FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-4-20260715-01/analysis/cumulative_delta4_overlay.json",
    },
    {
        "identity": "REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01",
        "kind": "HISTORICAL_GATE",
        "artifact": None,
    },
    {
        "identity": "REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01",
        "kind": "HISTORICAL_GATE",
        "artifact": None,
    },
]


def _load_checker():
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _is_ancestor(commit: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def _story_map(ledger: dict) -> dict[str, dict]:
    return {story["story_id"]: story for story in ledger["stories"]}


def _row_story_id(row: dict) -> str | None:
    if row["disposition"] == "CURRENT_VERIFIED":
        return row["story_id"]
    if row["disposition"] == "SUPERSEDED_BY_STORY":
        return row["successor_story_id"]
    return None


def _expected_catalog_entry(task: dict, row: dict) -> dict:
    ordinal = task["ordinal"]
    story_id = STORY_ID if ordinal == 282 else _row_story_id(row)
    if ordinal == 282:
        disposition = "CURRENT_VERIFIED"
        residual = None
    elif ordinal == 283:
        disposition = "FINAL_CLOSE_PENDING"
        residual = "FINAL_CLOSE_PENDING"
    else:
        disposition = row["disposition"]
        residual = None
    return {
        "ordinal": ordinal,
        "task_id": task["task_id"],
        "task_path": task["task_path"],
        "phase": task["phase"],
        "deferred_kind": task["deferred_kind"],
        "closure": task["closure"],
        "non_closure": task["non_closure"],
        "primary_tests": task["primary_tests"],
        "regression_inputs": task["regression_inputs"],
        "gate_requirements": task["gate_requirements"],
        "disposition": disposition,
        "story_id": story_id,
        "residual": residual,
    }


def test_output_is_the_exact_302_node_current_ledger() -> None:
    catalog = json.loads(CATALOG_PATH.read_text())
    ledger = json.loads(LEDGER_PATH.read_text())
    output = json.loads(OUTPUT_PATH.read_text())
    story_text = STORY_PATH.read_text()

    assert output["schema_version"] == "v8-final-item-slice-ledger-v1"
    assert output["catalog_sha256"] == ledger["catalog_sha256"]
    assert output["counts"] == {
        "catalog_rows": 283,
        "foundation_rows": 197,
        "external_product_nodes": 19,
        "effective_product_nodes": 302,
        "effective_foundation_requirements": 216,
        "deferred_rows": 86,
    }
    assert output["catalog_entries"] == [
        _expected_catalog_entry(task, row)
        for task, row in zip(catalog["tasks"], ledger["rows"], strict=True)
    ]
    assert output["external_entries"] == [
        {
            "task_id": task_id,
            "classification": "FOUNDATION_EXTERNAL_PRODUCT",
            **item,
            "residual": None,
        }
        for task_id, item in EXTERNAL_ITEMS.items()
    ]
    assert output["audit_lineage"] == AUDIT_LINEAGE
    assert "302" in story_text and "216" in story_text and "86" in story_text
    assert "Row283" in story_text and "FINAL_CLOSE_PENDING" in story_text


def test_all_resolved_items_bind_current_reviewed_reachable_path_owners() -> None:
    ledger = json.loads(LEDGER_PATH.read_text())
    stories = _story_map(ledger)

    resolved_story_ids = {_row_story_id(row) for row in ledger["rows"][:281]} - {None}
    for story_id in resolved_story_ids:
        story = stories[story_id]
        assert story["status"] == "CURRENT_VERIFIED"
        assert story["commits"] and _is_ancestor(story["commits"][-1])
        assert re.fullmatch(r"[0-9a-f]{64}", story["tree_sha256"])
        assert story["paths"] and story["tests"]
        assert story["review_ref"] and story["verification_ref"]
        assert (ROOT / story["review_ref"]).is_file()
        assert (ROOT / story["verification_ref"]).is_file()

    for item in EXTERNAL_ITEMS.values():
        owned_paths: set[str] = set()
        for story_id in item["story_ids"]:
            story = stories[story_id]
            assert story["status"] == "CURRENT_VERIFIED"
            assert story["commits"] and _is_ancestor(story["commits"][-1])
            assert story["tests"] and (ROOT / story["review_ref"]).is_file()
            owned_paths.update(story["paths"])
        assert set(item["current_paths"]) <= owned_paths
        assert all((ROOT / path).is_file() for path in item["current_paths"])


def test_configuration_and_final_close_remain_fail_closed() -> None:
    output = json.loads(OUTPUT_PATH.read_text())
    assert output["production_configuration"] == {
        "inputs": {
            "DG-PAYMENT-WORKBOOK:GLOBAL": "CONFIG_REQUIRED",
            "DG-SERVICE-RATE-VERSION:GLOBAL": "CONFIG_REQUIRED",
        },
        "source_decisions": {
            "DG-PAYMENT-WORKBOOK:GLOBAL": "PENDING",
            "DG-SERVICE-RATE-VERSION:GLOBAL": "PENDING",
        },
        "production_failure": "409 / NO WRITE",
        "test_only_isolated": True,
        "production_activation_claimed": False,
    }
    assert output["final_close"] == {
        "task_id": ROW283_ID,
        "status": "FINAL_CLOSE_PENDING",
        "release_gate_executed": False,
    }


def test_row282_adoption_is_exact_when_present() -> None:
    ledger = json.loads(LEDGER_PATH.read_text())
    row282 = ledger["rows"][281]
    story = _story_map(ledger).get(STORY_ID)
    if row282["disposition"] == "PENDING":
        assert story is None
        return

    assert row282 == {
        "catalog_id": ROW282_ID,
        "phase": "deferred",
        "disposition": "CURRENT_VERIFIED",
        "story_id": STORY_ID,
        "successor_story_id": None,
        "blocker": None,
    }
    assert story is not None
    assert story["status"] == "CURRENT_VERIFIED"
    assert story["paths"] == CANDIDATE_PATHS
    assert story["review_class"] == "PROTECTED"
    assert story["review_ref"] == story["verification_ref"] == REVIEW_REF
    assert story["counts"] == {
        "catalog_rows": 283,
        "foundation_rows": 197,
        "external_product_nodes": 19,
        "effective_product_nodes": 302,
        "effective_foundation_requirements": 216,
        "deferred_rows": 86,
    }
    assert story["production_activation_claimed"] is False
    assert (
        _load_checker().compute_tree_fingerprint(ROOT, story["commits"][-1], CANDIDATE_PATHS)
        == story["tree_sha256"]
    )
    assert ledger["rows"][282]["disposition"] == "PENDING"
