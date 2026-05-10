# BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

When a GRANT_NOTICE document is registered through the UI, create or reuse exactly one `T_GrantFeeTask` for the case, expose it through the existing grant-fee task API, and allow grant-fee task completion to advance the case to the intended granted state when required grant fields are present.

## Explicit Non-Closure

- Do not add migrations or schema changes.
- Do not change annuity task generation in this task.
- Do not change frontend grant-fee filtering in this task.
- Do not mutate Skeleton Pack assets.

## Allowed Files

- `backend/app/modules/documents/api.py`
- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_grant_fee_notice_task_creation.py`
- `backend/tests/test_grant_fee_state_machine_api.py`
- `tasks/backend/business_logic/BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01.md`
- `artifacts/BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01 test /bin/zsh -lc 'cd backend && pytest -q tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_state_machine_api.py'
```

```bash
./scripts/evidence_run.sh BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01 lint /bin/zsh -lc 'cd backend && ruff check --fix app/modules/documents/api.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_state_machine_api.py && ruff format app/modules/documents/api.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_state_machine_api.py && ruff check app/modules/documents/api.py app/modules/grant_fees/service.py tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_state_machine_api.py'
```

```bash
./scripts/evidence_run.sh BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01 task_gate ./scripts/task_validate.sh BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01
```

## Evidence Path

- `artifacts/BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01/results.jsonl`
- `artifacts/BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01/summary.md`
- `artifacts/BL-E2E-GRANT-FEE-TASK-LIFECYCLE-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `FE-E2E-GRANT-FEE-CASE-FILTER-01`
- `BL-E2E-ANNUITY-TARGETED-GENERATION-01`

