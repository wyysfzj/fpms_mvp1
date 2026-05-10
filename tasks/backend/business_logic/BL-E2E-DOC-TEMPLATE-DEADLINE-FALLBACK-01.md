# BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Ensure documents created through the UI with a generic `doc_type` such as `OFFICIAL_IN` still use the selected DocTemplate's deadline task code, so OA_IN creates an OA_REPLY task and OA_OUT reply writes off that task.

## Explicit Non-Closure

- Do not change document schemas or database schema.
- Do not modify frontend document forms in this task.
- Do not implement grant-fee task creation here.
- Do not change Skeleton Pack assets.

## Allowed Files

- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_task_generation.py`
- `backend/tests/test_document_ui_deadline_generation.py`
- `tasks/backend/business_logic/BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01.md`
- `artifacts/BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01 test /bin/zsh -lc 'cd backend && pytest -q tests/test_task_generation.py tests/test_document_ui_deadline_generation.py'
```

```bash
./scripts/evidence_run.sh BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01 lint /bin/zsh -lc 'cd backend && ruff check --fix app/modules/tasks/task_generation_service.py tests/test_task_generation.py tests/test_document_ui_deadline_generation.py && ruff format app/modules/tasks/task_generation_service.py tests/test_task_generation.py tests/test_document_ui_deadline_generation.py && ruff check app/modules/tasks/task_generation_service.py tests/test_task_generation.py tests/test_document_ui_deadline_generation.py'
```

```bash
./scripts/evidence_run.sh BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01 task_gate ./scripts/task_validate.sh BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01
```

## Evidence Path

- `artifacts/BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01/results.jsonl`
- `artifacts/BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01/summary.md`
- `artifacts/BL-E2E-DOC-TEMPLATE-DEADLINE-FALLBACK-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `FE-E2E-CASE-TASK-DONE-VISIBILITY-01`

