# API-E2E-FEE-DRAFT-CASE-NO-FILTER-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

`GET /api/v1/fees/drafts` must accept a visible `case_no` query parameter and return only fee drafts for the matching case, preserving the existing `case_id` filter behavior.

## Explicit Non-Closure

- Do not change fee draft creation, draft locking, billing, pay-list, or amount calculation behavior.
- Do not change frontend UI in this backend task.
- Do not modify Skeleton Pack assets or database schema/migrations.

## Allowed Files

- `backend/app/modules/fees/api.py`
- `backend/app/modules/fees/service.py`
- `backend/tests/test_fee_draft_case_no_filter_api.py`
- `tasks/backend/apis_ext/API-E2E-FEE-DRAFT-CASE-NO-FILTER-01.md`
- `artifacts/API-E2E-FEE-DRAFT-CASE-NO-FILTER-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh API-E2E-FEE-DRAFT-CASE-NO-FILTER-01 test /bin/zsh -lc 'cd backend && source .venv/bin/activate && pytest -q tests/test_fee_draft_case_no_filter_api.py'
```

```bash
./scripts/evidence_run.sh API-E2E-FEE-DRAFT-CASE-NO-FILTER-01 lint /bin/zsh -lc 'cd backend && source .venv/bin/activate && ruff check --fix app/modules/fees/api.py app/modules/fees/service.py tests/test_fee_draft_case_no_filter_api.py && ruff format app/modules/fees/api.py app/modules/fees/service.py tests/test_fee_draft_case_no_filter_api.py && ruff check app/modules/fees/api.py app/modules/fees/service.py tests/test_fee_draft_case_no_filter_api.py'
```

```bash
./scripts/evidence_run.sh API-E2E-FEE-DRAFT-CASE-NO-FILTER-01 task_gate ./scripts/task_validate.sh API-E2E-FEE-DRAFT-CASE-NO-FILTER-01
```

## Evidence Path

- `artifacts/API-E2E-FEE-DRAFT-CASE-NO-FILTER-01/results.jsonl`
- `artifacts/API-E2E-FEE-DRAFT-CASE-NO-FILTER-01/summary.md`
- `artifacts/API-E2E-FEE-DRAFT-CASE-NO-FILTER-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `FE-FEE-DRAFT-CASE-NO-FILTER-01`
