# B-AUTO-PY-B-OA-REPLY-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Implement only `TC-B-006` / `handle_tc_b_006`: create OA reply document with `reply_to_id`, assert reply document persistence and original OA `reply_date`.

## Explicit Non-Closure

Do not assert file binary storage unless backend exposes it through current stable API. Do not implement auto write-off assertions in this task.

## Allowed Files

- `tasks/automation/B-AUTO-PY-B-OA-REPLY-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `artifacts/B-AUTO-PY-B-OA-REPLY-P0-01/**`

## Verification Commands

See batch manifest scoped B partial commands. Real smoke target: `pytest tests/test_wave_b.py -k TC-B-006 -q` with `FPMS_DB_DSN=`.

## Evidence Path

- `artifacts/B-AUTO-PY-B-OA-REPLY-P0-01/results.jsonl`
- `artifacts/B-AUTO-PY-B-OA-REPLY-P0-01/summary.md`
- `artifacts/B-AUTO-PY-B-OA-REPLY-P0-01/git/diff.patch`

## Remaining Follow-Up Task IDs

None
