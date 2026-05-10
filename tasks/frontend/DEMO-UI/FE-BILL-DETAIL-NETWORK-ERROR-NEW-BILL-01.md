# FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Bill detail must render a newly created bill from a locked fee draft even when currency data is blank/invalid or supplementary offset loading fails, so the visible page shows bill number/case/amount instead of a `Network Error` banner.

## Explicit Non-Closure

- Do not change bill creation business rules.
- Do not change payment, offset, bad-debt, or case receipt linkage semantics.
- Do not modify backend billing service/API unless systematic debugging proves the blocker is backend-only; if so, stop and split a backend task.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/modules/billing/pages/BillDetail.vue`
- `frontend/src/utils/money.ts`
- `frontend/tests/money-format.mjs`
- `tasks/frontend/DEMO-UI/FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01.md`
- `artifacts/FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01 test /bin/zsh -lc 'cd frontend && npm run typecheck && node tests/money-format.mjs'
```

```bash
./scripts/evidence_run.sh FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01 lint /bin/zsh -lc 'cd frontend && npm run lint'
```

```bash
./scripts/evidence_run.sh FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01 task_gate ./scripts/task_validate.sh FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01
```

## Evidence Path

- `artifacts/FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01/results.jsonl`
- `artifacts/FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01/summary.md`
- `artifacts/FE-BILL-DETAIL-NETWORK-ERROR-NEW-BILL-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None
