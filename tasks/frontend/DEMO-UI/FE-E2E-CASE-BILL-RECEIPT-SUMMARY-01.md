# FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Map backend `bills` rows from `GET /cases/{case_id}/receipts` and render them in case detail `账单与收款` so a bill created from a fee draft is visible before receipt registration.

## Explicit Non-Closure

- Do not change backend summary behavior.
- Do not implement payment or offset creation here.
- Do not change CaseReceipt amount inputs.
- Do not modify Skeleton Pack assets.

## Allowed Files

- `frontend/src/api/billing.ts`
- `frontend/src/api/billing.types.ts`
- `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`
- `tasks/frontend/DEMO-UI/FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01.md`
- `artifacts/FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/cases/components/CaseReceiptsSummary.vue'
```

```bash
./scripts/evidence_run.sh FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01 task_gate ./scripts/task_validate.sh FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01
```

## Evidence Path

- `artifacts/FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01/results.jsonl`
- `artifacts/FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01/summary.md`
- `artifacts/FE-E2E-CASE-BILL-RECEIPT-SUMMARY-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None

