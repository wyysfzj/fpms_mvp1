# BE-FE-COMMISSION-QUERY-READINESS-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Add backend readiness for FE commission search by business case number:

- `GET /api/v1/commission` accepts optional `case_no`.
- `case_no` filters commission rows through the related case.
- commission list items expose `case_no` when available.
- existing filters remain compatible.

## Explicit Non-Closure

This task does not implement `bill_no` search, commission-to-bill linkage, frontend filters, migrations, model changes, settlement behavior, or commission generation changes.

## Remaining Follow-Up Task IDs

- FE-COMMISSION-CASE-NO-FILTER-01
- PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01

## Allowed Files

- tasks/backend/business_logic/BE-FE-COMMISSION-QUERY-READINESS-01.md
- backend/app/modules/commission/api.py
- backend/tests/test_commission_query_readiness.py
- artifacts/BE-FE-COMMISSION-QUERY-READINESS-01/**

## Verification Commands

- cd backend && python3 -m ruff check --fix app/modules/commission/api.py tests/test_commission_query_readiness.py
- cd backend && python3 -m ruff format app/modules/commission/api.py tests/test_commission_query_readiness.py
- cd backend && python3 -m ruff check app/modules/commission/api.py tests/test_commission_query_readiness.py
- cd backend && pytest tests/test_commission_query_readiness.py -q
- ./scripts/task_validate.sh BE-FE-COMMISSION-QUERY-READINESS-01

## Evidence Path

- artifacts/BE-FE-COMMISSION-QUERY-READINESS-01/results.jsonl
- artifacts/BE-FE-COMMISSION-QUERY-READINESS-01/summary.md
- artifacts/BE-FE-COMMISSION-QUERY-READINESS-01/git/diff.patch
