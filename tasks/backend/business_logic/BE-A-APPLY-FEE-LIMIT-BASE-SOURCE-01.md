# BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01

Task ID: `BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01`

Role: worker

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Ensure batch filing generated `APPLY_FEE_LIMIT` tasks honor the configured task template base source needed by `TC-A-014`.

This task closes only:

1. `deadline_base=CASE_EVENT` continues to use batch `submitted_date`.
2. `deadline_base=FILING_DATE` uses the case `filing_date`.
3. Reminder, internal deadline, daily reminder, assignment, idempotency, status, and task log behavior remain stable.
4. Existing Batch 2 apply-fee task field behavior remains intact.

## Explicit Non-Closure

Do not implement `handle_tc_a_014`, do not modify pytest skeleton assets, do not modify frontend, do not modify skeleton YAML/JSON/manifest/schema, and do not add schema or migration changes.

## Remaining Follow-Up Task IDs

- `A-AUTO-PY-A-TASK_REASSIGN-P1-01`

## Allowed Files

- `tasks/backend/business_logic/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_apply_fee_limit_base_source.py`
- `artifacts/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/cases/service.py tests/test_apply_fee_limit_base_source.py
python3 -m ruff format app/modules/cases/service.py tests/test_apply_fee_limit_base_source.py
python3 -m ruff check app/modules/cases/service.py tests/test_apply_fee_limit_base_source.py
pytest tests/test_apply_fee_limit_base_source.py -q
pytest tests/test_apply_fee_limit_task_fields.py -q
```

Task gate:

```bash
./scripts/evidence_run.sh BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01 task_gate ./scripts/task_validate.sh BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01
```

## Evidence Path

- `artifacts/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01/results.jsonl`
- `artifacts/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01/summary.md`
- `artifacts/BE-A-APPLY-FEE-LIMIT-BASE-SOURCE-01/git/diff.patch`
