# FPMS V8 Current-Head Migration Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`
Runbook: `P0-single-lane-story`

## Observable outcome

Align the ten exact historical schema tests exposed by the Row281 Full backend matrix with the
current unique Alembic head `v8_w6_service_price_book_01`. Each test must continue proving that its
own migration revision is reachable, its frozen schema/constraints are unchanged, and a clean
upgrade reaches the unique current head.

## Exact closure

- Replace only stale assertions that equate an older reachable revision with the repository head.
- Preserve exact revision lookup, clean upgrade, reflection, zero-seed and constraint assertions.
- Prove Alembic has exactly one current head and each historical revision is its ancestor.

## Non-closure

No migration/model/product/schema change, no assertion removal, no downgrade, no adjacent cleanup,
and no Row281 adoption.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-CURRENT-HEAD-MIGRATION-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_v8_future_annuity_exception_carrier_schema.py`
- `backend/tests/test_v8_future_annuity_reduction_lineage_carrier.py`
- `backend/tests/test_v8_grant_evidence_source_carrier_schema.py`
- `backend/tests/test_v8_grant_manual_review_role_carrier_schema.py`
- `backend/tests/test_v8_grant_official_copy_verification_carrier_schema.py`
- `backend/tests/test_v8_lifecycle_evidence_kind_capacity.py`
- `backend/tests/test_v8_official_rate_book_schema.py`
- `backend/tests/test_v8_overlay_warning_conflict_migration.py`
- `backend/tests/test_v8_pay_list_export_artifact_schema.py`
- `backend/tests/test_v8_payment_workbook_input_version.py`

`backend/uv.lock` remains unrelated and untouched.

## Verification

Run the exact ten failing tests from the Row281 result, scoped Ruff, exact diff check, then obtain
independent High review. This task changes tests only and cannot claim Row281 or production PASS.
