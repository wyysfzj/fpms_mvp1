# A-AUTO-PY-A-TASK_REASSIGN-P1-01

Task ID: `A-AUTO-PY-A-TASK_REASSIGN-P1-01`

Role: worker

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement only `TC-A-014` / `handle_tc_a_014` for A3 deadline base and reminder behavior.

This task closes only:

1. Configure `APPLY_FEE_LIMIT` template for `CASE_EVENT`.
2. Generate an apply-fee task through real batch filing.
3. Assert base date, due date, internal deadline, reminders, daily reminder, status, and create log.
4. Configure `APPLY_FEE_LIMIT` template for `FILING_DATE`.
5. Generate a second apply-fee task from a case with filing date and assert the same date/reminder surface.
6. Cover DB disabled/enabled behavior.
7. Update stale `handle_tc_a_014` skeleton assertion only in the allowlisted test.

## Explicit Non-Closure

Do not implement `TC-A-002`, `TC-A-007`, `TC-A-009`, backend logic, frontend UI, skeleton YAML/JSON/manifest/schema, or Playwright assets.

## Remaining Follow-Up Task IDs

- `PRODUCT-A-CASE-A2-FULL-FIELDS-CONTRACT-01`
- `PRODUCT-A-CASE-A7-INVENTOR-ADDRESS-CONTRACT-01`
- `PRODUCT-A-CASE-SPEC-FEE-DISCOUNT-CONTRACT-01`

## Allowed Files

- `tasks/automation/A-AUTO-PY-A-TASK_REASSIGN-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_task_reassign_handler.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_apply_fee_limit_handler.py`
- `artifacts/A-AUTO-PY-A-TASK_REASSIGN-P1-01/**`

## Verification Commands

Run from `FPMS_Automation_Skeleton_Pack/pytest_python`:

```bash
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_task_reassign_handler.py tests/test_a_apply_fee_limit_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_task_reassign_handler.py tests/test_a_apply_fee_limit_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_task_reassign_handler.py tests/test_a_apply_fee_limit_handler.py
pytest tests/test_a_task_reassign_handler.py -q
pytest tests/test_wave_a.py -k TC-A-014 -q
pytest tests/test_a_apply_fee_limit_handler.py -q
```

Real smoke uses `FPMS_DB_DSN=` and a fresh run id.

## Evidence Path

- `artifacts/A-AUTO-PY-A-TASK_REASSIGN-P1-01/results.jsonl`
- `artifacts/A-AUTO-PY-A-TASK_REASSIGN-P1-01/summary.md`
- `artifacts/A-AUTO-PY-A-TASK_REASSIGN-P1-01/git/diff.patch`
