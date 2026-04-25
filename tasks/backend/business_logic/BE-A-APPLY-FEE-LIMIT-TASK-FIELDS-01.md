# BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01
- Role: worker
- Runbook: P0-prereq-heavy-story

## Exact Closure Slice

Ensure batch filing generated `APPLY_FEE_LIMIT` tasks have stable field semantics required by `TC-A-013`.

This task closes only:

1. Base date is the batch filing submitted date.
2. Deadline and internal deadline are calculated from the task template.
3. Reminder fields are calculated from template reminder offsets.
4. Worker and supervisor assignment follow existing template conventions when configured.
5. Task status is `OPEN`.
6. TaskLog creation semantics are stable.
7. Existing batch filing side effects remain intact.

## Explicit Non-Closure

This task does not:

- implement pytest handler `handle_tc_a_013`
- implement fee draft generation
- implement pay list, bill, payment, or commission behavior
- modify frontend or skeleton data
- modify task models or migrations

## Remaining Follow-Up Task IDs

- PRODUCT-A-APPLY-FEE-DRAFT-CONTRACT-01
- BE-A-APPLY-FEE-DRAFT-RULE-01

## Allowed Files

- tasks/backend/business_logic/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01.md
- backend/app/modules/cases/service.py
- backend/tests/test_apply_fee_limit_task_fields.py
- artifacts/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/cases/service.py tests/test_apply_fee_limit_task_fields.py
python3 -m ruff format app/modules/cases/service.py tests/test_apply_fee_limit_task_fields.py
python3 -m ruff check app/modules/cases/service.py tests/test_apply_fee_limit_task_fields.py
pytest tests/test_apply_fee_limit_task_fields.py -q
pytest tests/test_case_batch_filing_side_effects.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01
```

## Evidence Path

- artifacts/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01/results.jsonl
- artifacts/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01/summary.md
- artifacts/BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01/git/diff.patch
