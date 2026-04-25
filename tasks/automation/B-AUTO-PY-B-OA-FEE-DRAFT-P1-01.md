# B-AUTO-PY-B-OA-FEE-DRAFT-P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Attempt only `TC-B-009` / `handle_tc_b_009`: create OA fee-enabled document template, preview fee rows, submit wizard fee rows, then assert `OA_FEE` draft, SERVICE/GOV items, and totals.

Current status: READY after `BE-B-OA-FEE-ITEM-LIST-SCHEMA-01` PASS evidence. This task removes only the `TC-B-009` skeleton marker and validates the already-scoped OA fee draft handler against real backend behavior.

## Explicit Non-Closure

Do not implement pay list, bill, payment, or commission behavior.

## Allowed Files

- `tasks/automation/B-AUTO-PY-B-OA-FEE-DRAFT-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_remaining_landing_handlers.py`
- `artifacts/B-AUTO-PY-B-OA-FEE-DRAFT-P1-01/**`

## Verification Commands

See batch manifest scoped B partial commands. Real smoke target: `pytest tests/test_wave_b.py -k TC-B-009 -q` with `FPMS_DB_DSN=`.

## Evidence Path

- `artifacts/B-AUTO-PY-B-OA-FEE-DRAFT-P1-01/results.jsonl`
- `artifacts/B-AUTO-PY-B-OA-FEE-DRAFT-P1-01/summary.md`
- `artifacts/B-AUTO-PY-B-OA-FEE-DRAFT-P1-01/git/diff.patch`

## Remaining Follow-Up Task IDs

None
