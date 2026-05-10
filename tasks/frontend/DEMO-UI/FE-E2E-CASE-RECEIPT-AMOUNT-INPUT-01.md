# FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Make the case receipt `应收金额` and `实收金额` controls fillable by observable browser keyboard/form interaction and still submit numeric values to the existing backend API.

## Explicit Non-Closure

- Do not change backend CaseReceipt validation.
- Do not change payment/offset flow.
- Do not auto-fill receipt amounts from bills.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/modules/billing/components/CaseReceiptDialog.vue`
- `tasks/frontend/DEMO-UI/FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01.md`
- `artifacts/FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01 test /bin/zsh -lc 'cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- src/modules/billing/components/CaseReceiptDialog.vue'
```

```bash
./scripts/evidence_run.sh FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01 task_gate ./scripts/task_validate.sh FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01
```

## Evidence Path

- `artifacts/FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01/results.jsonl`
- `artifacts/FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01/summary.md`
- `artifacts/FE-E2E-CASE-RECEIPT-AMOUNT-INPUT-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None

