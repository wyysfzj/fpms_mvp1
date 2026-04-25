# A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01
- Role: worker
- Testcase: TC-A-012
- Handler: `handle_tc_a_012`

## Exact Closure Slice

Implement only TC-A-012 pytest automation:

1. Batch filing with no selected cases is rejected.
2. Batch filing with `submitted_date < recv_date` is rejected.
3. Batch filing with `submitted_date == recv_date` succeeds.
4. Stale skeleton-state assertion for `handle_tc_a_012` is updated.

## Explicit Non-Closure

This task does not:

- implement TC-A-016, TC-A-018, TC-A-020, TC-A-022, or TC-A-024
- modify backend/frontend code
- modify skeleton YAML / JSON / manifest / schema / Playwright assets
- expand API client or DB helpers
- use unrelated validation failures as success

## Remaining Follow-Up Task IDs

- A-AUTO-PY-A-APPLY-FEE-INVALID-P1-01
- A-AUTO-PY-A-GOV-PAYLIST-VALIDATION-P1-01
- A-AUTO-PY-A-BILL-INVALID-COMBOS-P1-01
- A-AUTO-PY-A-PAYMENT-OFFSET-VALIDATION-P1-01
- A-AUTO-PY-A-COMMISSION-WAITPAY-P1-01

## Allowed Files

- tasks/automation/A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01.md
- FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_a.py
- FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_a_batch_submit_handler.py
- artifacts/A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01/**

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
python3 -m ruff check --fix handlers/wave_a.py tests/test_a_batch_submit_handler.py
python3 -m ruff format handlers/wave_a.py tests/test_a_batch_submit_handler.py
python3 -m ruff check handlers/wave_a.py tests/test_a_batch_submit_handler.py
pytest tests/test_a_batch_submit_handler.py -q
pytest tests/test_wave_a.py -k TC-A-012 -q
```

Real smoke must use a fresh run id and `FPMS_DB_DSN=`.

## Evidence Path

- artifacts/A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01/results.jsonl
- artifacts/A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01/summary.md
- artifacts/A-AUTO-PY-A-BATCH-FILING-VALIDATION-P0-01/git/diff.patch
