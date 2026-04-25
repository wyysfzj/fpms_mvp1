# B-AUTO-PY-B-OA-DUE-DATE-P1-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only `TC-B-002` / `handle_tc_b_002`: assert `OfficialDueDate` overrides OA task due date while task `base_date` remains document date and generated task is `OPEN`.

## Explicit Non-Closure

Do not implement reply write-off, fee draft, bill, payment, commission, or other B handlers.

## Allowed Files

- `tasks/automation/B-AUTO-PY-B-OA-DUE-DATE-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `artifacts/B-AUTO-PY-B-OA-DUE-DATE-P1-01/**`

## Verification Commands

See batch manifest scoped B partial commands. Real smoke target: `pytest tests/test_wave_b.py -k TC-B-002 -q` with `FPMS_DB_DSN=`.

## Evidence Path

- `artifacts/B-AUTO-PY-B-OA-DUE-DATE-P1-01/results.jsonl`
- `artifacts/B-AUTO-PY-B-OA-DUE-DATE-P1-01/summary.md`
- `artifacts/B-AUTO-PY-B-OA-DUE-DATE-P1-01/git/diff.patch`

## Remaining Follow-Up Task IDs

None
