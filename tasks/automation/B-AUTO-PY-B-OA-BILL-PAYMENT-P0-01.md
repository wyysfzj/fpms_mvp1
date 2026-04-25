# B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only `TC-B-010` / `handle_tc_b_010` and `TC-B-011` / `handle_tc_b_011` because `TC-B-011` is the P0 billing/payment continuation of the same OA fee draft readiness evidence from `BE-B-OA-BILL-PAYMENT-READINESS-01`.

This task closes only:

1. OA official fee pay-list creation from GOV fee items.
2. Official payment registration and pay-list paid state.
3. OA bill generation from OA fee draft.
4. Payment creation, offset, bill balance/status, and case receipt assertions.

## Explicit Non-Closure

Do not implement commission, reply/deadline edit, `TC-B-005`, backend, frontend, or skeleton data changes.

## Allowed Files

- `tasks/automation/B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_remaining_landing_handlers.py`
- `artifacts/B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01/**`

## Verification Commands

From `FPMS_Automation_Skeleton_Pack/pytest_python`:

- `python3 -m ruff check --fix handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `python3 -m ruff format handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `python3 -m ruff check handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `pytest tests/test_b_remaining_landing_handlers.py tests/test_b_partial_landing_handlers.py -q`
- `FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=LOCAL-RUN-BLAND2-010011-001 FPMS_DB_DSN= pytest tests/test_wave_b.py -k "TC-B-010 or TC-B-011" -q`
- `./scripts/task_validate.sh B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01`

## Evidence Path

- `artifacts/B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01/results.jsonl`
- `artifacts/B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01/summary.md`
- `artifacts/B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01/git/diff.patch`

## Remaining Follow-Up Task IDs

None
