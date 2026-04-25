# BATCH-B-AUTOMATION-LANDING-02

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Serially land B wave automation handlers for `TC-B-009`, `TC-B-010`, `TC-B-011`, `TC-B-012`, and `TC-B-013` after `BATCH-B-BLOCKER-DRAIN-03` PASS evidence.

## Explicit Non-Closure

Do not implement backend, frontend, skeleton YAML/JSON/schema, or Playwright changes. Do not implement `TC-B-005`. Do not weaken handler assertions to fake PASS. Close audit is executed separately as `BATCH-B-WAVE-CLOSE-AUDIT-01`.

## Wave Order

1. `B-AUTO-PY-B-OA-FEE-DRAFT-P1-01` for `TC-B-009`
2. `B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01` for `TC-B-010` and `TC-B-011`
3. `B-AUTO-PY-B-OA-COMMISSION-P1-01` for `TC-B-012`
4. `B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01` for `TC-B-013`
5. `BATCH-B-WAVE-CLOSE-AUDIT-01`

## Shared File Serialization

- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py` is edited serially.
- Stale skeleton assertions in B-wave pytest tests are edited serially.
- No backend shared files are edited by this batch.
- SQLite write tests and real smoke commands are run serially.

## Allowed Files

- `tasks/batches/BATCH-B-AUTOMATION-LANDING-02.md`
- `tasks/automation/B-AUTO-PY-B-OA-FEE-DRAFT-P1-01.md`
- `tasks/automation/B-AUTO-PY-B-OA-BILL-PAYMENT-P0-01.md`
- `tasks/automation/B-AUTO-PY-B-OA-COMMISSION-P1-01.md`
- `tasks/automation/B-AUTO-PY-B-NEED-REPLY-DEADLINE-EDIT-P1-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_b.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_partial_landing_handlers.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_b_remaining_landing_handlers.py`
- `artifacts/BATCH-B-AUTOMATION-LANDING-02/**`

## Verification Commands

From `FPMS_Automation_Skeleton_Pack/pytest_python`:

- `python3 -m ruff check --fix handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `python3 -m ruff format handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `python3 -m ruff check handlers/wave_b.py tests/test_b_partial_landing_handlers.py tests/test_b_remaining_landing_handlers.py`
- `pytest tests/test_b_remaining_landing_handlers.py tests/test_b_partial_landing_handlers.py -q`
- `FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_USERNAME=admin FPMS_PASSWORD="$FPMS_LOCAL_PASSWORD" FPMS_RUN_ID=<fresh> FPMS_DB_DSN= pytest tests/test_wave_b.py -k <case> -q`

Task gate:

- `./scripts/task_validate.sh BATCH-B-AUTOMATION-LANDING-02`

## Evidence Path

- `artifacts/BATCH-B-AUTOMATION-LANDING-02/results.jsonl`
- `artifacts/BATCH-B-AUTOMATION-LANDING-02/summary.md`
- `artifacts/BATCH-B-AUTOMATION-LANDING-02/git/diff.patch`

## Remaining Follow-Up Task IDs

- `BATCH-B-WAVE-CLOSE-AUDIT-01`
