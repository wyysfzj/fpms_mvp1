# API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice

Commission settlement generation must support a target case whose settleable commission record has no assigned agent, using an explicit unassigned-settlement path that remains case-targeted and SQLite-compatible.

## Explicit Non-Closure

- Do not change commission formula, rule selection, bill commission application, or settlement terminal-state semantics.
- Do not settle non-settleable commissions.
- Do not implement frontend UI changes in this task.
- Do not modify Skeleton Pack assets or database schema/migrations.

## Allowed Files

- `backend/app/modules/commission/api.py`
- `backend/app/modules/commission/service.py`
- `backend/tests/test_commission_settlement_unassigned_case_api.py`
- `tasks/backend/apis_ext/API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01.md`
- `artifacts/API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01 test /bin/zsh -lc 'cd backend && source .venv/bin/activate && pytest -q tests/test_commission_settlement_unassigned_case_api.py'
```

```bash
./scripts/evidence_run.sh API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01 lint /bin/zsh -lc 'cd backend && source .venv/bin/activate && ruff check --fix app/modules/commission/api.py app/modules/commission/service.py tests/test_commission_settlement_unassigned_case_api.py && ruff format app/modules/commission/api.py app/modules/commission/service.py tests/test_commission_settlement_unassigned_case_api.py && ruff check app/modules/commission/api.py app/modules/commission/service.py tests/test_commission_settlement_unassigned_case_api.py'
```

```bash
./scripts/evidence_run.sh API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01 task_gate ./scripts/task_validate.sh API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01
```

## Evidence Path

- `artifacts/API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01/results.jsonl`
- `artifacts/API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01/summary.md`
- `artifacts/API-E2E-COMMISSION-SETTLEMENT-UNASSIGNED-CASE-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- `FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01`
