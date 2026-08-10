from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "docs/product/v8/coverage-ledger.json"

SUCCESSOR_STORIES = {
    "document": ("V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-SUCCESSOR-CURRENT-ADOPTION",),
    "package": (
        "V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-CURRENT-ADOPTION",
        "V8-FILING-EXTERNAL-SUBMISSION-ADAPTER-CURRENT-ADOPTION",
        "V8-OA-OUT-PACKAGE-ATOMIC-LINK-CURRENT-ADOPTION",
    ),
    "oa_receipt": (
        "V8-OA-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION",
        "V8-OA-REPLY-DATE-RECEIPT-PROJECTION-CURRENT-ADOPTION",
    ),
    "notice": (
        "V8-PROSECUTION-LIFECYCLE-NOTICE-VERTICAL-CURRENT-ADOPTION",
        "V8-APPLICATION-FEE-NOTICE-ACTIVATION-CURRENT-ADOPTION",
        "V8-FEE-REDUCTION-APPROVAL-NOTICE-ACTIVATION-CURRENT-ADOPTION",
    ),
    "deadline": (
        "V8-OA-REPLY-DATE-RECEIPT-PROJECTION-CURRENT-ADOPTION",
        "V8-PROSECUTION-LIFECYCLE-NOTICE-VERTICAL-CURRENT-ADOPTION",
    ),
    "grant": (
        "V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-CURRENT-ADOPTION",
        "V8-GRANT-ATTACHMENT-NO-LEGAL-EFFECT-CURRENT-ADOPTION",
        "V8-GRANT-FEE-DONE-NO-LEGAL-EFFECT-CURRENT-ADOPTION",
        "V8-GRANT-DRAFT-OBLIGATION-ADAPTER-CURRENT-ADOPTION",
    ),
    "governance": ("C3-LEAN-GOVERNANCE-ADOPTION",),
    "real_e2e": (
        "V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-CURRENT-ADOPTION",
        "V8-DOCUMENT-CREATE-LIFECYCLE-NEUTRAL-SUCCESSOR-CURRENT-ADOPTION",
        "V8-WORK-PACKAGE-MANIFEST-EVIDENCE-VERSION-CURRENT-ADOPTION",
        "V8-OA-RECEIPT-LIFECYCLE-ADAPTER-CURRENT-ADOPTION",
        "V8-PROSECUTION-LIFECYCLE-NOTICE-VERTICAL-CURRENT-ADOPTION",
        "V8-OA-REPLY-DATE-RECEIPT-PROJECTION-CURRENT-ADOPTION",
        "V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-CURRENT-ADOPTION",
        "C3-LEAN-GOVERNANCE-ADOPTION",
    ),
}

SUCCESSOR_VERIFICATION_PATHS = {
    "document": (
        "backend/tests/test_v8_document_semantics_event_adapter.py",
        "backend/tests/test_v8_case_create_opened_evidence_adapter.py",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-wizard-template-limit.spec.ts",
    ),
    "package": (
        "backend/tests/test_v8_w1_d3_work_package_evidence_link.py",
        "backend/tests/test_v8_work_package_manifest_evidence_version.py",
        "backend/tests/test_v8_filing_external_submission_adapter.py",
        "backend/tests/test_v8_oa_out_package_atomic_link.py",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-oa-page-resolve.spec.ts",
    ),
    "oa_receipt": (
        "backend/tests/test_v8_oa_receipt_lifecycle_adapter.py",
        "backend/tests/test_v8_oa_reply_date_receipt_projection.py",
    ),
    "notice": (
        "backend/tests/test_v8_acceptance_notice_evidence_adapter.py",
        "backend/tests/test_v8_oa_notice_evidence_api.py",
        "backend/tests/test_v8_application_fee_notice_activation.py",
        "backend/tests/test_v8_fee_reduction_approval_notice_activation.py",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-notice-catalog-ui-clarity.spec.ts",
    ),
    "deadline": (
        "backend/tests/test_v8_oa_reply_date_receipt_projection.py",
        "backend/tests/test_v8_oa_notice_evidence_api.py",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-create-ui.spec.ts",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-wizard-ui.spec.ts",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-edit-ui.spec.ts",
    ),
    "grant": (
        "backend/tests/test_v8_grant_notice_lifecycle_adapter.py",
        "backend/tests/test_v8_grant_notice_lifecycle_api.py",
        "backend/tests/test_v8_grant_attachment_no_legal_effect.py",
        "backend/tests/test_v8_grant_fee_done_no_legal_effect.py",
        "backend/tests/test_v8_grant_draft_obligation_adapter.py",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-lineage-ui.spec.ts",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-replacement-ui.spec.ts",
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts",
    ),
    "governance": ("scripts/tests/test_v8_lean_coverage_check.py",),
    "real_e2e": (
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts",
        "backend/tests/test_v8_document_semantics_event_adapter.py",
        "backend/tests/test_v8_filing_external_submission_adapter.py",
        "backend/tests/test_v8_oa_receipt_lifecycle_adapter.py",
        "backend/tests/test_v8_oa_reply_date_receipt_projection.py",
        "backend/tests/test_v8_grant_notice_lifecycle_adapter.py",
    ),
}

INHERITED_TASK_GROUPS = {
    "document": (
        "FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01",
        "FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01",
    ),
    "package": (
        "FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01",
        "FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01",
        "FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01",
        "FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01",
        "FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01",
        "FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01",
        "FPMS-ADDGAP-OA-RESOLVE-API-20260710-01",
        "FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01",
    ),
    "oa_receipt": (
        "FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01",
        "FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01",
        "FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01",
        "FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01",
        "FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01",
        "FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01",
    ),
    "notice": (
        "FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01",
        "FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01",
        "FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01",
        "FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01",
        "FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01",
        "FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01",
    ),
    "deadline": (
        "FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01",
        "FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01",
        "FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01",
        "FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01",
        "FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02",
        "FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02",
        "FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02",
        "FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02",
        "FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02",
    ),
    "grant": (
        "FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01",
        "FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01",
        "FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01",
        "FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01",
        "FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01",
        "FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01",
        "FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01",
        "FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01",
        "FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01",
        "FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01",
        "FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01",
        "FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01",
        "FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01",
        "FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01",
        "FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02",
    ),
    "governance": (
        "FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01",
        "FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01",
        "FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01",
    ),
    "real_e2e": ("FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01",),
}

RETIRED_TASKCTL_TASKS = {
    "FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01",
    "FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01",
}

SUPERSEDED_TASKS = {
    "FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01": {
        "successor_stories": ("C3-LEAN-GOVERNANCE-ADOPTION",),
        "verification_paths": ("scripts/tests/test_v8_lean_coverage_check.py",),
    },
    "FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01": {
        "successor_stories": SUCCESSOR_STORIES["real_e2e"],
        "verification_paths": SUCCESSOR_VERIFICATION_PATHS["real_e2e"],
    },
    "FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01": {
        "successor_stories": ("C3-LEAN-GOVERNANCE-ADOPTION",),
        "verification_paths": ("scripts/tests/test_v8_lean_coverage_check.py",),
    },
    "FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01": {
        "successor_stories": ("C3-LEAN-GOVERNANCE-ADOPTION",),
        "verification_paths": ("scripts/tests/test_v8_lean_coverage_check.py",),
    },
}

EXACT_INHERITED_PATHS = {
    "FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01": (
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-wizard-template-limit.spec.ts",
    ),
    "FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01": (
        "backend/tests/test_addgap_workpkg_resolve_key_schema.py",
    ),
    "FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01": (
        "backend/tests/test_addgap_filing_ensure_service.py",
    ),
    "FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01": (
        "backend/tests/test_addgap_filing_resolve_api.py",
    ),
    "FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01": (
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts",
    ),
    "FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01": (
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts",
    ),
    "FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01": (
        "backend/tests/test_addgap_oa_ensure_service.py",
    ),
    "FPMS-ADDGAP-OA-RESOLVE-API-20260710-01": ("backend/tests/test_addgap_oa_resolve_api.py",),
    "FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01": (
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-oa-page-resolve.spec.ts",
    ),
}


def _task_contract_path(task_id: str) -> Path:
    return REPO_ROOT / "tasks/additional_gaps" / f"{task_id}.md"


def _contract_verification_paths(task_id: str) -> tuple[str, ...]:
    paths = re.findall(
        r"`((?:backend/tests|scripts/tests|FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests)/[^`]+(?:\.py|\.spec\.ts))`",
        _task_contract_path(task_id).read_text(encoding="utf-8"),
    )
    return tuple(dict.fromkeys(paths))


def _resolved_task_authority(task_id: str) -> dict[str, object]:
    if task_id in SUPERSEDED_TASKS:
        return {
            "authority_kind": "SUPERSEDED_BY_CURRENT_STORY",
            "authority_ref": SUPERSEDED_TASKS[task_id]["successor_stories"],
            **SUPERSEDED_TASKS[task_id],
        }
    return {
        "authority_kind": "INHERITED_TASK_CONTRACT",
        "authority_ref": f"tasks/additional_gaps/{task_id}.md",
        "successor_stories": (),
        "verification_paths": _contract_verification_paths(task_id),
    }


def _ledger() -> dict[str, object]:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_exactly_70_inherited_tasks_have_one_exact_authority_record() -> None:
    task_ids = [task_id for group in INHERITED_TASK_GROUPS.values() for task_id in group]

    assert len(task_ids) == len(set(task_ids)) == 70
    for task_id in task_ids:
        assert (REPO_ROOT / "tasks/additional_gaps" / f"{task_id}.md").is_file()


def test_every_inherited_task_resolves_to_exact_current_authority_and_verification() -> None:
    stories = {story["story_id"]: story for story in _ledger()["stories"]}
    task_ids = [task_id for group in INHERITED_TASK_GROUPS.values() for task_id in group]
    resolved = {task_id: _resolved_task_authority(task_id) for task_id in task_ids}

    assert set(INHERITED_TASK_GROUPS) == set(SUCCESSOR_STORIES) == set(SUCCESSOR_VERIFICATION_PATHS)
    assert len(resolved) == 70
    for task_id, mapping in resolved.items():
        assert mapping["authority_kind"] in {
            "INHERITED_TASK_CONTRACT",
            "SUPERSEDED_BY_CURRENT_STORY",
        }, task_id
        assert mapping["verification_paths"], task_id
        assert all((REPO_ROOT / path).is_file() for path in mapping["verification_paths"]), task_id
        for story_id in mapping["successor_stories"]:
            story = stories[story_id]
            assert story["status"] == "CURRENT_VERIFIED", task_id
            assert story["tests"], task_id
            assert story["review_ref"], task_id
            assert (REPO_ROOT / story["review_ref"]).is_file(), task_id


def test_tasks_01_and_05_through_12_keep_their_exact_contract_paths() -> None:
    for task_id, expected_paths in EXACT_INHERITED_PATHS.items():
        mapping = _resolved_task_authority(task_id)

        assert mapping["authority_kind"] == "INHERITED_TASK_CONTRACT"
        assert mapping["authority_ref"] == f"tasks/additional_gaps/{task_id}.md"
        assert set(mapping["verification_paths"]) >= set(expected_paths)


def test_task_46_uses_the_current_real_ui_successor() -> None:
    mapping = _resolved_task_authority("FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01")

    assert mapping["authority_kind"] == "SUPERSEDED_BY_CURRENT_STORY"
    assert "V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-CURRENT-ADOPTION" in mapping["successor_stories"]
    assert (
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-lifecycle-overlay-live.spec.ts"
        in mapping["verification_paths"]
    )


def test_retired_taskctl_gates_map_only_to_c3_governance() -> None:
    governance_tasks = set(INHERITED_TASK_GROUPS["governance"])

    assert governance_tasks >= RETIRED_TASKCTL_TASKS
    assert SUCCESSOR_STORIES["governance"] == ("C3-LEAN-GOVERNANCE-ADOPTION",)
    assert all(
        SUPERSEDED_TASKS[task_id]["successor_stories"] == ("C3-LEAN-GOVERNANCE-ADOPTION",)
        for task_id in RETIRED_TASKCTL_TASKS
    )
    assert RETIRED_TASKCTL_TASKS.isdisjoint(
        task_id
        for group, task_ids in INHERITED_TASK_GROUPS.items()
        if group != "governance"
        for task_id in task_ids
    )
