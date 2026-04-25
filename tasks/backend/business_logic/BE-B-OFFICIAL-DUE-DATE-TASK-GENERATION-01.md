# BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01

Task ID: `BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01`

Story Shape Classification:
- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Implement the B-wave `OfficialDueDate` task-generation rule for `TC-B-002`.

This task closes only:
- parse `OfficialDueDate` from document `extra_data`
- use valid `OfficialDueDate` as task `due_date`
- keep task `base_date` as the document `doc_date`
- calculate internal deadline/reminders from the effective due date
- return `DOCUMENT_OFFICIAL_DUE_DATE_INVALID` when `OfficialDueDate` is present but invalid

## Explicit Non-Closure

Do not:
- implement pytest automation handlers
- implement ReplyTo rules
- implement OA fee/bill/payment/commission behavior
- modify frontend or skeleton data
- add schema or migration

## Remaining Follow-Up Task IDs

- `B-AUTO-PY-B-OFFICIAL-DUE-DATE-P1-01`
- `BE-B-OA-FEE-DRAFT-READINESS-01`

## Allowed Files

- `tasks/backend/business_logic/BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01.md`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_b_official_due_date_task_generation.py`
- `artifacts/BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01/**`

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix app/modules/tasks/task_generation_service.py app/modules/documents/service.py tests/test_b_official_due_date_task_generation.py
python3 -m ruff format app/modules/tasks/task_generation_service.py app/modules/documents/service.py tests/test_b_official_due_date_task_generation.py
python3 -m ruff check app/modules/tasks/task_generation_service.py app/modules/documents/service.py tests/test_b_official_due_date_task_generation.py
pytest tests/test_b_official_due_date_task_generation.py -q
pytest tests/test_document_wizard_task_preview.py tests/test_document_wizard_batch_create.py tests/test_b2_reply_chain.py -q
./scripts/task_validate.sh BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01
```

## Evidence Path

- `artifacts/BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01/results.jsonl`
- `artifacts/BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01/summary.md`
- `artifacts/BE-B-OFFICIAL-DUE-DATE-TASK-GENERATION-01/git/diff.patch`
