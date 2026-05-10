# API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Commission settlement report and line generation support target-case visibility by case number or resolved case id so `RUI202605100035` can be verified from the settlement page.

## Explicit Non-Closure

- Do not change commission rule calculation formulas.
- Do not make non-settleable commissions settleable without payment/receipt prerequisites.
- Do not change frontend settlement UI in this task.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `backend/app/modules/commission/api.py`
- `backend/app/modules/commission/service.py`
- `backend/tests/test_commission_settlement_case_filter_api.py`
- `tasks/backend/apis_ext/API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01.md`
- `artifacts/API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01 test /bin/zsh -lc 'cd backend && pytest -q tests/test_commission_settlement_case_filter_api.py'
```

```bash
./scripts/evidence_run.sh API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01 lint /bin/zsh -lc 'cd backend && ruff check --fix app/modules/commission/api.py app/modules/commission/service.py tests/test_commission_settlement_case_filter_api.py && ruff format app/modules/commission/api.py app/modules/commission/service.py tests/test_commission_settlement_case_filter_api.py && ruff check app/modules/commission/api.py app/modules/commission/service.py tests/test_commission_settlement_case_filter_api.py'
```

```bash
./scripts/evidence_run.sh API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01 task_gate ./scripts/task_validate.sh API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01
```

## Evidence Path

- `artifacts/API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01/results.jsonl`
- `artifacts/API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01/summary.md`
- `artifacts/API-E2E-COMMISSION-SETTLEMENT-CASE-FILTER-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01`

