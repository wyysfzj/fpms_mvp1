# FPMS V8 Inherited Case-Create Input Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`
Runbook: `P0-single-lane-story`

## Observable outcome

Align the exact 23 inherited regression test files whose case-creation fixtures predate the
mandatory explicit `fee_reduction` customer input. Each positive case-create fixture must state
the canonical no-reduction choice `"0"`; the product API must remain fail closed when the field
is absent.

## Exact closure

- Preserve the existing product requirement that `fee_reduction` is an explicit canonical
  customer selection.
- Add only `"fee_reduction": "0"` to the positive case-create payloads that currently fail with
  `422 VALIDATION_ERROR` / missing `body.fee_reduction`.
- Re-run the exact 103 failing inherited nodes, then all 23 affected test files.
- Preserve every deadline, notice, grant, OA, document, task, fee, lifecycle and permission
  assertion unchanged.

## Non-closure

- No product, schema, migration, seed, API validation, permission, fee or lifecycle change.
- No default injection through `conftest.py`, transport middleware or a shared fixture.
- No assertion deletion, weakening, skip or xfail.
- No changes for the separate 17 Row281 failures in filing, seed overlay or OA reply projection.
- No Row281 story, matrix result, ledger adoption, Row282, Row283 or release close.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-CASE-CREATE-INPUT-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_addgap_document_create_atomicity.py`
- `backend/tests/test_addgap_document_deadline_create_api.py`
- `backend/tests/test_addgap_document_deadline_impact_preview.py`
- `backend/tests/test_addgap_document_deadline_read_projection.py`
- `backend/tests/test_addgap_document_deadline_update_api.py`
- `backend/tests/test_addgap_document_wizard_deadline_backend.py`
- `backend/tests/test_addgap_grant_auto_draft_gate.py`
- `backend/tests/test_addgap_grant_preview_no_auto_draft.py`
- `backend/tests/test_addgap_legacy_deadline_task_sync.py`
- `backend/tests/test_addgap_notice_catalog_reference_gate.py`
- `backend/tests/test_addgap_notice_grant_activation.py`
- `backend/tests/test_addgap_oa_alias_reply_validation.py`
- `backend/tests/test_addgap_oa_deadline_fail_closed.py`
- `backend/tests/test_b3_fee_linking.py`
- `backend/tests/test_b_official_due_date_task_generation.py`
- `backend/tests/test_document_specific_search_api.py`
- `backend/tests/test_document_wizard_task_preview.py`
- `backend/tests/test_grant_fee_draft_linkage_api.py`
- `backend/tests/test_grant_fee_notice_document_api.py`
- `backend/tests/test_grant_fee_notice_task_creation.py`
- `backend/tests/test_grant_fee_state_machine_api.py`
- `backend/tests/test_grant_fee_worklist_api.py`
- `backend/tests/test_task_template.py`

## Verification and acceptance

The recorded Row281 RED is exactly 103 nodes failing because positive case creation omitted the
required field. Final verification is the exact 23-file pytest tranche, scoped Ruff, exact diff
and independent High review with P0/P1/P2 `0/0/0`.

Rollback reverts only this task card and the explicit test input fields; it never changes product
behavior or business data.
