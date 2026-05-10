# FE-E2E-PAYMENT-OFFSET-VISIBILITY-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Expose a visible UI path from bill detail/payment creation to payment list and offset creation where the target bill/payment can be identified and selected.

## Explicit Non-Closure

- Do not change backend payment linkage.
- Do not create payments or offsets outside visible UI.
- Do not change case receipt dialog in this task.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/api/billing.ts`
- `frontend/src/api/billing.types.ts`
- `frontend/src/modules/billing/pages/PaymentCreate.vue`
- `frontend/src/modules/billing/pages/PaymentList.vue`
- `frontend/src/modules/billing/pages/OffsetList.vue`
- `tasks/frontend/DEMO-UI/FE-E2E-PAYMENT-OFFSET-VISIBILITY-01.md`
- `artifacts/FE-E2E-PAYMENT-OFFSET-VISIBILITY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-E2E-PAYMENT-OFFSET-VISIBILITY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-E2E-PAYMENT-OFFSET-VISIBILITY-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/billing/pages/PaymentCreate.vue src/modules/billing/pages/PaymentList.vue src/modules/billing/pages/OffsetList.vue'
```

```bash
./scripts/evidence_run.sh FE-E2E-PAYMENT-OFFSET-VISIBILITY-01 task_gate ./scripts/task_validate.sh FE-E2E-PAYMENT-OFFSET-VISIBILITY-01
```

## Evidence Path

- `artifacts/FE-E2E-PAYMENT-OFFSET-VISIBILITY-01/results.jsonl`
- `artifacts/FE-E2E-PAYMENT-OFFSET-VISIBILITY-01/summary.md`
- `artifacts/FE-E2E-PAYMENT-OFFSET-VISIBILITY-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None

