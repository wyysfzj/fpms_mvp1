# FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Make the commission settlement page visibly query/report target case number and guide batch generation against settleable records without requiring hidden IDs.

## Explicit Non-Closure

- Do not change backend commission formulas.
- Do not settle non-settleable commissions by frontend-only logic.
- Do not change commission records page behavior.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/api/commission.ts`
- `frontend/src/api/commission.types.ts`
- `frontend/src/modules/commission/pages/CommissionSettlement.vue`
- `tasks/frontend/DEMO-UI/FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01.md`
- `artifacts/FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- src/api/commission.ts src/api/commission.types.ts src/modules/commission/pages/CommissionSettlement.vue'
```

```bash
./scripts/evidence_run.sh FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01 task_gate ./scripts/task_validate.sh FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01
```

## Evidence Path

- `artifacts/FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01/results.jsonl`
- `artifacts/FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01/summary.md`
- `artifacts/FE-E2E-COMMISSION-SETTLEMENT-VISIBILITY-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None

