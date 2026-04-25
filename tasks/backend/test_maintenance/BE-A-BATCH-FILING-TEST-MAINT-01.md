# BE-A-BATCH-FILING-TEST-MAINT-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Task

- Task ID: BE-A-BATCH-FILING-TEST-MAINT-01
- Role: worker
- Runbook: P0-prereq-heavy-story

## Exact Closure Slice

Update stale backend batch filing tests so their case creation setup includes valid applicants after applicant-list validation became mandatory.

This task closes only:

1. Add valid applicant prerequisites to `backend/tests/test_case_batch_filing_action.py`.
2. Add valid applicant prerequisites to `backend/tests/test_case_batch_filing_query.py`.
3. Preserve existing batch filing business assertions.
4. Revalidate the existing batch filing side-effect tests.

## Explicit Non-Closure

This task does not:

- modify batch filing service/API/schema
- modify `backend/tests/test_case_batch_filing_side_effects.py`
- weaken applicant validation
- change batch filing status, submitted date, exam request, candidate query, document, or task assertions
- implement pytest automation handlers
- modify frontend or skeleton data

## Remaining Follow-Up Task IDs

- BE-A-APPLY-FEE-LIMIT-TASK-FIELDS-01

## Allowed Files

- tasks/backend/test_maintenance/BE-A-BATCH-FILING-TEST-MAINT-01.md
- backend/tests/test_case_batch_filing_action.py
- backend/tests/test_case_batch_filing_query.py
- artifacts/BE-A-BATCH-FILING-TEST-MAINT-01/**

## Verification Commands

Run from `backend/`:

```bash
python3 -m ruff check --fix tests/test_case_batch_filing_action.py tests/test_case_batch_filing_query.py
python3 -m ruff format tests/test_case_batch_filing_action.py tests/test_case_batch_filing_query.py
python3 -m ruff check tests/test_case_batch_filing_action.py tests/test_case_batch_filing_query.py
pytest tests/test_case_batch_filing_action.py -q
pytest tests/test_case_batch_filing_query.py -q
pytest tests/test_case_batch_filing_side_effects.py -q
```

Task gate:

```bash
./scripts/task_validate.sh BE-A-BATCH-FILING-TEST-MAINT-01
```

## Evidence Path

- artifacts/BE-A-BATCH-FILING-TEST-MAINT-01/results.jsonl
- artifacts/BE-A-BATCH-FILING-TEST-MAINT-01/summary.md
- artifacts/BE-A-BATCH-FILING-TEST-MAINT-01/git/diff.patch
