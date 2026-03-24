# PE-BE-TEST-01 Rework Summary

## Executed Task
- `tasks/postenhancement/backend/PE-BE-TEST-01.md`
- Rework focus: enforce stable business error-code assertions for key negative branches.

## Modified Files
- `backend/tests/test_annuity_e2e.py`
- `backend/tests/test_collections_e2e.py`
- `backend/tests/test_commission_e2e.py`
- `backend/tests/test_consulting_e2e.py`

## What Changed
- Upgraded shared test helper in each file from:
  - status + envelope-key existence checks
- To:
  - status + exact `error.code` + `error.message` checks.
- Added concrete expected codes on key `400/404/409` branches in each module chain (and kept `422` checks with `VALIDATION_ERROR`).

### Key code assertions added
- Annuity: `ANNUITY_DATE_RANGE_INVALID`, `ANNUITY_INSTRUCTION_INVALID`, `ANNUITY_TASK_NOT_FOUND`, `ANNUITY_STATE_CONFLICT`, `GOV_PAYMENT_DUPLICATE`, `PAY_LIST_SCOPE_INVALID`, `PAY_LIST_NOT_FOUND`.
- Collections: `DUNNING_BATCH_STATE_INVALID`, `DUNNING_BATCH_NOT_FOUND`, `BAD_DEBT_ALREADY_MARKED`, `BAD_DEBT_RESTORE_INVALID`, `BILL_NOT_FOUND`, `BAD_DEBT_NOT_ALLOWED`.
- Commission: `COMMISSION_RULE_CONFLICT`, `COMMISSION_RULE_INVALID`, `COMMISSION_RULE_NOT_FOUND`, `COMMISSION_SETTLEMENT_CONFLICT`, `COMMISSION_SETTLEMENT_INVALID`, `COMMISSION_FILTER_INVALID`, `COMMISSION_REPORT_INVALID`, `COMMISSION_SETTLEMENT_NOT_FOUND`.
- Consulting: `CASE_NO_DUPLICATE`, `CONSULTING_CASE_INVALID`, `FEE_DRAFT_CONFLICT`, `CONSULTING_FEE_INVALID`, `CASE_NOT_FOUND`.

## Gate Commands and Outcomes
- `cd backend && pytest -q tests/test_annuity_e2e.py tests/test_collections_e2e.py tests/test_commission_e2e.py tests/test_consulting_e2e.py`
  - Passed: `8 passed, 3 warnings`.
- `cd backend && ruff format tests/test_annuity_e2e.py tests/test_collections_e2e.py tests/test_commission_e2e.py tests/test_consulting_e2e.py`
  - Passed: `4 files left unchanged`.
- `cd backend && ruff check tests/test_annuity_e2e.py tests/test_collections_e2e.py tests/test_commission_e2e.py tests/test_consulting_e2e.py`
  - Passed: `All checks passed`.

## Evidence
- `artifacts/PE-BE-TEST-01/results.jsonl`
- `artifacts/PE-BE-TEST-01/git/diff.patch`
- `artifacts/PE-BE-TEST-01/outputs/*_test_rework.log`
- `artifacts/PE-BE-TEST-01/outputs/*_format_rework.log`
- `artifacts/PE-BE-TEST-01/outputs/*_lint_rework.log`
