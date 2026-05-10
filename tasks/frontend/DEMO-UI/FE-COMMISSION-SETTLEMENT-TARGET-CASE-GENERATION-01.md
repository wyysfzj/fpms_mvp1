# FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: high
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Commission settlement page must provide a visible target-case path that lets the user query a case number, create or select a compatible settlement batch, and generate settlement lines for the target case even when the commission record is unassigned.

## Explicit Non-Closure

- Do not change backend commission settlement semantics in this frontend task.
- Do not change commission record list behavior beyond using existing API contracts.
- Do not generate settlement lines without a visible user click.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/api/commission.ts`
- `frontend/src/api/commission.types.ts`
- `frontend/src/modules/commission/pages/CommissionSettlement.vue`
- `frontend/tests/commission-settlement-target-source.mjs`
- `tasks/frontend/DEMO-UI/FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01.md`
- `artifacts/FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && node tests/commission-settlement-target-source.mjs'
```

```bash
./scripts/evidence_run.sh FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01 lint /bin/zsh -lc 'cd frontend && npm run lint'
```

```bash
./scripts/evidence_run.sh FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01 task_gate ./scripts/task_validate.sh FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01
```

## Evidence Path

- `artifacts/FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01/results.jsonl`
- `artifacts/FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01/summary.md`
- `artifacts/FE-COMMISSION-SETTLEMENT-TARGET-CASE-GENERATION-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None
