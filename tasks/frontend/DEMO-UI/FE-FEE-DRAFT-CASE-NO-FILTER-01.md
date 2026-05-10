# FE-FEE-DRAFT-CASE-NO-FILTER-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

The fee draft list "案件编号" filter must support the visible case number entered by a user and return matching draft rows for that case.

## Explicit Non-Closure

- Do not change fee draft creation, draft locking, pay-list, or billing behavior.
- Do not change backend fee draft query semantics unless systematic debugging proves there is no existing case-number filter; if so, stop and split a backend API task.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/api/fees.ts`
- `frontend/src/api/fees.types.ts`
- `frontend/src/modules/fees/pages/FeeDraftList.vue`
- `tasks/frontend/DEMO-UI/FE-FEE-DRAFT-CASE-NO-FILTER-01.md`
- `artifacts/FE-FEE-DRAFT-CASE-NO-FILTER-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-FEE-DRAFT-CASE-NO-FILTER-01 test /bin/zsh -lc 'cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-FEE-DRAFT-CASE-NO-FILTER-01 lint /bin/zsh -lc 'cd frontend && npm run lint'
```

```bash
./scripts/evidence_run.sh FE-FEE-DRAFT-CASE-NO-FILTER-01 task_gate ./scripts/task_validate.sh FE-FEE-DRAFT-CASE-NO-FILTER-01
```

## Evidence Path

- `artifacts/FE-FEE-DRAFT-CASE-NO-FILTER-01/results.jsonl`
- `artifacts/FE-FEE-DRAFT-CASE-NO-FILTER-01/summary.md`
- `artifacts/FE-FEE-DRAFT-CASE-NO-FILTER-01/git/diff.patch`

## Prerequisite Task IDs

- `API-E2E-FEE-DRAFT-CASE-NO-FILTER-01`

## Remaining Follow-Up Task IDs

- None
